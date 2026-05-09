#!/usr/bin/env python3
"""
Kimari CLI — Command-line interface for Kimari Local AI

Controls the llama.cpp runtime, manages GPU profiles, runs diagnostics,
and provides chat/benchmark capabilities.
"""

import argparse
import json
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("[ERROR] 'requests' is required. Install with: pip install -r cli/requirements.txt")
    sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "kimari.profiles.json"
MODELS_DIR = PROJECT_ROOT / "models"
PID_FILE = PROJECT_ROOT / ".kimari-server.pid"
LOG_FILE = PROJECT_ROOT / "kimari-server.log"

KIMARI_ASCII = r"""
 ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗ █████╗
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██╔══██╗
██║     ███████║██████╔╝██║   ██║██╔██╗ ██║███████║
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██╔══██║
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║██║  ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝
   Local AI for Consumer GPUs — v0.1.0
"""


# ─── Colors ───────────────────────────────────────────────────────────────────

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    WHITE = "\033[97m"


def ok(msg: str):
    print(f"  {Color.GREEN}[OK]{Color.RESET}   {msg}")


def warn(msg: str):
    print(f"  {Color.YELLOW}[WARN]{Color.RESET} {msg}")


def fail(msg: str):
    print(f"  {Color.RED}[FAIL]{Color.RESET} {msg}")


def info(msg: str):
    print(f"  {Color.CYAN}[INFO]{Color.RESET} {msg}")


# ─── Config ───────────────────────────────────────────────────────────────────

def load_config() -> dict:
    """Load and return the Kimari profiles configuration."""
    if not CONFIG_PATH.exists():
        print(f"[ERROR] Config not found: {CONFIG_PATH}")
        print("Run this command from the kimari-local-ai root directory.")
        sys.exit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_profile(config: dict, profile_name: str) -> dict:
    """Get a specific profile from config."""
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        available = ", ".join(profiles.keys())
        print(f"[ERROR] Profile '{profile_name}' not found. Available: {available}")
        sys.exit(1)
    return profiles[profile_name]


# ─── System Detection ────────────────────────────────────────────────────────

def detect_gpu() -> Optional[dict]:
    """Detect NVIDIA GPU using nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines:
                parts = lines[0].split(", ")
                if len(parts) >= 3:
                    return {
                        "name": parts[0].strip(),
                        "vram_mb": int(parts[1].strip()),
                        "driver": parts[2].strip(),
                    }
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return None


def detect_cuda() -> bool:
    """Check if CUDA is available via nvcc or nvidia-smi."""
    return shutil.which("nvcc") is not None or shutil.which("nvidia-smi") is not None


def detect_llama_server() -> Optional[str]:
    """Find llama-server binary in PATH."""
    names = ["llama-server", "llama_server", "./llama-server"]
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def is_port_free(host: str, port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0  # 0 means connected (port in use)
    except OSError:
        return False


def recommend_profile(config: dict, gpu: Optional[dict]) -> str:
    """Recommend a GPU profile based on detected hardware."""
    if not gpu:
        return config.get("default_profile", "gtx1060")
    
    vram_gb = gpu["vram_mb"] / 1024
    profiles = config.get("profiles", {})
    
    # Try to match by GPU name first
    gpu_name_lower = gpu["name"].lower()
    for key, profile in profiles.items():
        if key in gpu_name_lower:
            return key
    
    # Fall back to VRAM-based recommendation
    if vram_gb >= 8:
        return "gtx1080"
    elif vram_gb >= 6:
        return "gtx1060"
    else:
        return "gtx1060"  # Default, may warn about VRAM


# ─── Server Management ───────────────────────────────────────────────────────

def start_server(profile_name: str, config: dict, verbose: bool = False):
    """Start llama-server with the specified profile."""
    profile = get_profile(config, profile_name)
    
    # Check model exists
    model_path = PROJECT_ROOT / profile["model"]
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        print("Place a GGUF model in the models/ directory.")
        print(f"Expected: {profile['model']}")
        sys.exit(1)
    
    # Check llama-server
    llama_server = detect_llama_server()
    if not llama_server:
        print("[ERROR] llama-server not found in PATH.")
        print("Build it first: bash scripts/linux/build-llamacpp-cuda.sh")
        sys.exit(1)
    
    # Check port
    host = profile.get("host", "127.0.0.1")
    port = profile.get("port", 11435)
    if not is_port_free(host, port):
        print(f"[ERROR] Port {port} is already in use.")
        print("Stop the existing server first: kimari stop")
        sys.exit(1)
    
    # Build command
    cmd = [
        llama_server,
        "-m", str(model_path),
        "--host", host,
        "--port", str(port),
        "-ngl", profile.get("gpu_layers", "all"),
        "-c", str(profile.get("ctx", 8192)),
        "-b", str(profile.get("batch", 256)),
        "-ub", str(profile.get("ubatch", 128)),
        "--cache-type-k", profile.get("cache_type_k", "f16"),
        "--cache-type-v", profile.get("cache_type_v", "f16"),
    ]
    
    if profile.get("threads"):
        cmd.extend(["-t", str(profile["threads"])])
    
    print(f"\n{Color.BOLD}{Color.CYAN}🚀 Starting Kimari{Color.RESET}")
    print(f"   Profile: {Color.GREEN}{profile_name}{Color.RESET} ({profile['name']})")
    print(f"   Model:   {profile['model']}")
    print(f"   Host:    {host}:{port}")
    print(f"   Context: {profile.get('ctx', 8192)} tokens")
    print(f"   Quant:   {profile['quantization']}")
    print()
    
    # Start server
    try:
        log_fh = open(LOG_FILE, "w")
        process = subprocess.Popen(
            cmd,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid if sys.platform != "win32" else None,
        )
        
        # Save PID
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))
        
        # Wait and check if it started
        print(f"   Waiting for server to start...", end=" ", flush=True)
        max_wait = 30
        for i in range(max_wait):
            time.sleep(1)
            try:
                resp = requests.get(f"http://{host}:{port}/health", timeout=2)
                if resp.status_code == 200:
                    print(f"{Color.GREEN}✓ Ready{Color.RESET}")
                    print(f"\n{Color.DIM}   API: http://{host}:{port}/v1{Color.RESET}")
                    print(f"{Color.DIM}   Log: {LOG_FILE}{Color.RESET}")
                    print()
                    info("Press Ctrl+C to stop, or run: kimari stop")
                    # Keep running until interrupted
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        stop_server()
                    return
            except requests.ConnectionError:
                pass
            if i == max_wait - 1:
                print(f"{Color.YELLOW}⚠ Timeout{Color.RESET}")
                print(f"   Server may still be starting. Check logs: {LOG_FILE}")
                print(f"   PID: {process.pid}")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    stop_server()
                return
            if process.poll() is not None:
                # Process exited
                log_fh.close()
                with open(LOG_FILE, "r") as f:
                    last_lines = f.readlines()[-10:]
                print(f"{Color.RED}✗ Failed{Color.RESET}")
                print(f"\n   Last log lines:")
                for line in last_lines:
                    print(f"   {Color.DIM}{line.rstrip()}{Color.RESET}")
                sys.exit(1)
            print(".", end="", flush=True)
    
    except FileNotFoundError:
        print(f"[ERROR] Could not execute: {llama_server}")
        sys.exit(1)


def stop_server():
    """Stop the running llama-server."""
    if not PID_FILE.exists():
        print("[WARN] No server PID file found. Server may not be running.")
        return
    
    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())
    
    try:
        if sys.platform != "win32":
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"{Color.GREEN}✓{Color.RESET} Kimari server stopped (PID: {pid})")
    except ProcessLookupError:
        print(f"[WARN] Process {pid} not found (already stopped?)")
    except PermissionError:
        print(f"[ERROR] No permission to stop process {pid}")
    finally:
        PID_FILE.unlink(missing_ok=True)


def check_status(config: dict):
    """Check the Kimari server status."""
    profile_name = config.get("default_profile", "gtx1060")
    profile = config.get("profiles", {}).get(profile_name, {})
    host = profile.get("host", "127.0.0.1")
    port = profile.get("port", 11435)
    
    try:
        resp = requests.get(f"http://{host}:{port}/health", timeout=3)
        if resp.status_code == 200:
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            print(f"\n{Color.GREEN}● Kimari Server: READY{Color.RESET}")
            print(f"  Endpoint: http://{host}:{port}")
            print(f"  Profile:  {profile_name}")
            print(f"  Model:    {profile.get('model', 'unknown')}")
            if data:
                print(f"  Status:   {json.dumps(data, indent=2)}")
        else:
            print(f"\n{Color.YELLOW}● Kimari Server: ERROR{Color.RESET}")
            print(f"  HTTP {resp.status_code}")
    except requests.ConnectionError:
        print(f"\n{Color.RED}● Kimari Server: STOPPED{Color.RESET}")
        print(f"  No response from http://{host}:{port}")
    except Exception as e:
        print(f"\n{Color.RED}● Kimari Server: ERROR{Color.RESET}")
        print(f"  {e}")


# ─── Chat ─────────────────────────────────────────────────────────────────────

def chat(message: str, config: dict, profile_name: Optional[str] = None):
    """Send a chat message to the Kimari API."""
    if not profile_name:
        profile_name = config.get("default_profile", "gtx1060")
    profile = config.get("profiles", {}).get(profile_name, {})
    host = profile.get("host", "127.0.0.1")
    port = profile.get("port", 11435)
    
    url = f"http://{host}:{port}/v1/chat/completions"
    
    payload = {
        "model": "kimari",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "max_tokens": 2048,
        "stream": False,
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            print(f"\n{Color.BOLD}{Color.CYAN}Kimari:{Color.RESET}")
            print(f"{content}\n")
            if usage:
                print(f"{Color.DIM}  Tokens: {usage.get('prompt_tokens', '?')} prompt + "
                      f"{usage.get('completion_tokens', '?')} completion = "
                      f"{usage.get('total_tokens', '?')} total{Color.RESET}")
        else:
            print(f"[ERROR] API returned {resp.status_code}: {resp.text}")
    except requests.ConnectionError:
        print("[ERROR] Cannot connect to Kimari server.")
        print("Start it first: kimari start --profile gtx1080")
    except Exception as e:
        print(f"[ERROR] {e}")


def interactive_chat(config: dict, profile_name: Optional[str] = None):
    """Run an interactive chat session."""
    if not profile_name:
        profile_name = config.get("default_profile", "gtx1060")
    profile = config.get("profiles", {}).get(profile_name, {})
    host = profile.get("host", "127.0.0.1")
    port = profile.get("port", 11435)
    
    url = f"http://{host}:{port}/v1/chat/completions"
    
    print(f"\n{Color.BOLD}Kimari Interactive Chat{Color.RESET}")
    print(f"Profile: {profile_name} | {host}:{port}")
    print(f"Type {Color.DIM}/quit{Color.RESET} or {Color.DIM}Ctrl+C{Color.RESET} to exit\n")
    
    conversation = []
    
    # Load system prompt
    system_prompt = (
        "You are Kimari, a helpful technical AI assistant specialized in programming, "
        "server administration, automation, and AI. Respond in the language the user uses. "
        "Be precise, technical, and practical. When you're not sure, say so."
    )
    conversation.append({"role": "system", "content": system_prompt})
    
    while True:
        try:
            user_input = input(f"{Color.GREEN}You>{Color.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Color.DIM}Bye!{Color.RESET}")
            break
        
        if not user_input:
            continue
        if user_input.lower() in ["/quit", "/exit", "/q"]:
            print(f"{Color.DIM}Bye!{Color.RESET}")
            break
        if user_input.lower() == "/clear":
            conversation = [{"role": "system", "content": system_prompt}]
            print(f"{Color.DIM}Conversation cleared.{Color.RESET}")
            continue
        
        conversation.append({"role": "user", "content": user_input})
        
        payload = {
            "model": "kimari",
            "messages": conversation,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False,
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                conversation.append({"role": "assistant", "content": content})
                print(f"\n{Color.CYAN}Kimari>{Color.RESET} {content}\n")
            else:
                print(f"[ERROR] API error: {resp.status_code}")
                conversation.pop()  # Remove failed user message
        except requests.ConnectionError:
            print("[ERROR] Server not responding. Start with: kimari start")
            conversation.pop()
        except Exception as e:
            print(f"[ERROR] {e}")
            conversation.pop()


# ─── Benchmark ────────────────────────────────────────────────────────────────

def run_benchmark(profile_name: str, config: dict):
    """Run a basic benchmark on the Kimari server."""
    profile = get_profile(config, profile_name)
    host = profile.get("host", "127.0.0.1")
    port = profile.get("port", 11435)
    
    # Check server
    try:
        requests.get(f"http://{host}:{port}/health", timeout=3)
    except requests.ConnectionError:
        print("[ERROR] Server not running. Start first: kimari start")
        sys.exit(1)
    
    # Benchmark prompts
    prompts = [
        "Explain Docker containers in one paragraph.",
        "Write a Python function to merge two sorted lists.",
        "What is the difference between process and thread?",
        "Responde en español: ¿Qué es una API REST?",
        "Write a TypeScript interface for a User with optional fields.",
    ]
    
    print(f"\n{Color.BOLD}{Color.CYAN}Kimari Benchmark{Color.RESET}")
    print(f"Profile: {profile_name} ({profile['name']})")
    print(f"Running {len(prompts)} prompts...\n")
    
    results = []
    for i, prompt in enumerate(prompts):
        print(f"  [{i+1}/{len(prompts)}] ", end="", flush=True)
        prompt_display = prompt[:50] + ("..." if len(prompt) > 50 else "")
        print(f"{Color.DIM}{prompt_display}{Color.RESET} ", end="", flush=True)
        
        start = time.time()
        try:
            resp = requests.post(
                f"http://{host}:{port}/v1/chat/completions",
                json={
                    "model": "kimari",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 256,
                    "stream": False,
                },
                timeout=60,
            )
            elapsed = time.time() - start
            
            if resp.status_code == 200:
                data = resp.json()
                usage = data.get("usage", {})
                completion_tokens = usage.get("completion_tokens", 0)
                tokens_per_sec = completion_tokens / elapsed if elapsed > 0 else 0
                results.append({
                    "prompt": prompt_display,
                    "tokens": completion_tokens,
                    "time_s": round(elapsed, 2),
                    "tokens_per_sec": round(tokens_per_sec, 1),
                    "status": "ok",
                })
                print(f"{Color.GREEN}✓{Color.RESET} {completion_tokens}tok in {elapsed:.1f}s ({tokens_per_sec:.1f} t/s)")
            else:
                results.append({
                    "prompt": prompt_display,
                    "status": f"http_{resp.status_code}",
                })
                print(f"{Color.RED}✗{Color.RESET} HTTP {resp.status_code}")
        except Exception as e:
            results.append({
                "prompt": prompt_display,
                "status": f"error: {str(e)[:50]}",
            })
            print(f"{Color.RED}✗{Color.RESET} {e}")
    
    # Summary
    ok_results = [r for r in results if r.get("status") == "ok"]
    if ok_results:
        avg_tps = sum(r["tokens_per_sec"] for r in ok_results) / len(ok_results)
        avg_time = sum(r["time_s"] for r in ok_results) / len(ok_results)
        total_tokens = sum(r["tokens"] for r in ok_results)
        
        print(f"\n{Color.BOLD}Summary:{Color.RESET}")
        print(f"  Avg speed:      {Color.GREEN}{avg_tps:.1f} tokens/s{Color.RESET}")
        print(f"  Avg latency:    {avg_time:.2f}s")
        print(f"  Total tokens:   {total_tokens}")
        print(f"  Success rate:   {len(ok_results)}/{len(results)}")
        
        # Save results
        results_dir = PROJECT_ROOT / "benchmarks" / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        result_file = results_dir / f"{profile_name}-bench.json"
        with open(result_file, "w") as f:
            json.dump({
                "profile": profile_name,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "summary": {
                    "avg_tokens_per_sec": round(avg_tps, 2),
                    "avg_latency_s": round(avg_time, 2),
                    "total_tokens": total_tokens,
                    "success_rate": f"{len(ok_results)}/{len(results)}",
                },
                "results": results,
            }, f, indent=2)
        print(f"\n  Results saved: {result_file}")


# ─── KimariFit ────────────────────────────────────────────────────────────────

def calculate_kimarifit(model_path: str, ctx_size: int, config: dict):
    """Calculate the KimariFit score for a given model and context."""
    model_file = Path(model_path)
    if not model_file.is_absolute():
        model_file = PROJECT_ROOT / model_path
    
    if not model_file.exists():
        print(f"[ERROR] Model not found: {model_file}")
        sys.exit(1)
    
    # Get model size in GiB
    model_size_bytes = model_file.stat().st_size
    model_size_gib = model_size_bytes / (1024 ** 3)
    
    # Detect GPU
    gpu = detect_gpu()
    if not gpu:
        print("[WARN] No GPU detected. Using default 6 GB VRAM.")
        total_vram = 6.0
    else:
        total_vram = gpu["vram_mb"] / 1024
    
    safe_vram = total_vram * 0.87
    
    # VRAM estimation formula: Mtotal ≈ S_GGUF + C/9709 + overhead
    kv_vram = ctx_size / 9709
    overhead = 1.0  # Conservative estimate
    total_estimated = model_size_gib + kv_vram + overhead
    
    # Calculate fit score
    if total_estimated <= safe_vram:
        # Score based on how much headroom remains
        utilization = total_estimated / safe_vram
        # Higher score when utilization is good (not too low, not too high)
        if utilization < 0.5:
            score = 60 + (utilization / 0.5) * 20  # 60-80
        elif utilization < 0.85:
            score = 80 + ((utilization - 0.5) / 0.35) * 20  # 80-100
        else:
            score = 100 - ((utilization - 0.85) / 0.15) * 30  # 100-70
    else:
        # Over budget
        over_pct = (total_estimated - safe_vram) / safe_vram * 100
        score = max(0, 40 - over_pct)
    
    # Quality factor based on quantization name
    model_name_lower = model_file.name.lower()
    if "q8" in model_name_lower:
        quality = 95
    elif "q6" in model_name_lower or "q5_k_m" in model_name_lower:
        quality = 85
    elif "q5" in model_name_lower:
        quality = 80
    elif "q4_k_m" in model_name_lower:
        quality = 75
    elif "iq4" in model_name_lower:
        quality = 70
    elif "q4" in model_name_lower:
        quality = 65
    elif "q3" in model_name_lower:
        quality = 50
    else:
        quality = 70  # Unknown
    
    final_score = (score * 0.7) + (quality * 0.3)
    
    print(f"\n{Color.BOLD}{Color.CYAN}KimariFit Analysis{Color.RESET}\n")
    print(f"  Model:          {model_file.name}")
    print(f"  Model size:     {model_size_gib:.2f} GiB")
    print(f"  Context:        {ctx_size:,} tokens")
    print(f"  KV cache VRAM:  {kv_vram:.2f} GiB")
    print(f"  Overhead:       {overhead:.2f} GiB")
    print(f"  Total estimated: {total_estimated:.2f} GiB")
    if gpu:
        print(f"  GPU:            {gpu['name']} ({gpu['vram_mb']} MB)")
    print(f"  Safe VRAM:      {safe_vram:.2f} GiB ({total_vram:.1f} GiB × 0.87)")
    print(f"  Utilization:    {total_estimated/safe_vram*100:.1f}%")
    print(f"\n  {Color.BOLD}KimariFit Score: {final_score:.0f}/100{Color.RESET}")
    
    if final_score >= 80:
        print(f"  {Color.GREEN}✓ Excellent fit{Color.RESET}")
    elif final_score >= 60:
        print(f"  {Color.YELLOW}~ Good fit{Color.RESET}")
    elif final_score >= 40:
        print(f"  {Color.YELLOW}⚠ Tight fit — may OOM{Color.RESET}")
    else:
        print(f"  {Color.RED}✗ Poor fit — likely OOM{Color.RESET}")


# ─── Doctor ───────────────────────────────────────────────────────────────────

def run_doctor(config: dict):
    """Run system diagnostics."""
    print(f"\n{KIMARI_ASCII}")
    print(f"  {Color.BOLD}System Diagnostics{Color.RESET}\n")
    
    ok_count = 0
    warn_count = 0
    fail_count = 0
    
    # OS
    os_name = f"{platform.system()} {platform.release()}"
    if platform.system() == "Linux":
        os_name += f" ({platform.machine()})"
    elif platform.system() == "Windows":
        os_name += f" ({platform.machine()})"
    ok(f"OS: {os_name}")
    ok_count += 1
    
    # GPU
    gpu = detect_gpu()
    if gpu:
        ok(f"GPU: {gpu['name']} ({gpu['vram_mb']} MB)")
        ok_count += 1
    else:
        warn("GPU: No NVIDIA GPU detected")
        warn_count += 1
    
    # Driver
    if gpu:
        ok(f"Driver: {gpu['driver']}")
        ok_count += 1
    else:
        warn("Driver: Cannot check (no GPU)")
        warn_count += 1
    
    # CUDA
    if detect_cuda():
        ok("CUDA: Available")
        ok_count += 1
    else:
        warn("CUDA: Not detected")
        warn_count += 1
    
    # llama-server
    llama_server = detect_llama_server()
    if llama_server:
        ok(f"llama-server: {llama_server}")
        ok_count += 1
    else:
        fail("llama-server: Not found in PATH")
        fail_count += 1
    
    # Model
    default_profile = config.get("default_profile", "gtx1060")
    profile = config.get("profiles", {}).get(default_profile, {})
    model_path = PROJECT_ROOT / profile.get("model", "models/Kimari-4B-Q4_K_M.gguf")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        ok(f"Model: {model_path.name} ({size_mb:.1f} MB)")
        ok_count += 1
    else:
        warn(f"Model: {model_path.name} not found in models/")
        warn_count += 1
    
    # Port
    host = profile.get("host", "127.0.0.1")
    port = profile.get("port", 11435)
    if is_port_free(host, port):
        ok(f"Port: {port} available")
        ok_count += 1
    else:
        warn(f"Port: {port} in use")
        warn_count += 1
    
    # Config
    ok(f"Config: {CONFIG_PATH}")
    ok_count += 1
    
    # Recommended profile
    recommended = recommend_profile(config, gpu)
    if recommended == default_profile:
        ok(f"Recommended profile: {recommended}")
        ok_count += 1
    else:
        info(f"Recommended profile: {recommended} (current: {default_profile})")
        ok_count += 1
    
    # Python
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        ok(f"Python: {py_version}")
        ok_count += 1
    else:
        warn(f"Python: {py_version} (3.10+ recommended)")
        warn_count += 1
    
    # Summary
    print(f"\n  {Color.BOLD}Result: {ok_count} OK, {warn_count} WARN, {fail_count} FAIL{Color.RESET}")
    
    if fail_count > 0:
        print(f"\n  {Color.YELLOW}Fix the errors above before starting Kimari.{Color.RESET}")
        sys.exit(1)
    elif warn_count > 0:
        print(f"\n  {Color.YELLOW}Warnings present. Kimari may work with limitations.{Color.RESET}")
    else:
        print(f"\n  {Color.GREEN}All checks passed! Ready to start.{Color.RESET}")
        print(f"  Run: {Color.CYAN}kimari start --profile {recommended}{Color.RESET}")


# ─── Models ───────────────────────────────────────────────────────────────────

def list_models():
    """List available GGUF models in the models directory."""
    if not MODELS_DIR.exists():
        print("[ERROR] models/ directory not found.")
        return
    
    gguf_files = list(MODELS_DIR.glob("*.gguf"))
    
    if not gguf_files:
        print("\n  No GGUF models found in models/")
        print("  Download a model and place it there.")
        return
    
    print(f"\n  {Color.BOLD}Available Models{Color.RESET}\n")
    for f in sorted(gguf_files):
        size_mb = f.stat().st_size / (1024 * 1024)
        size_gb = size_mb / 1024
        if size_gb >= 1:
            size_str = f"{size_gb:.2f} GiB"
        else:
            size_str = f"{size_mb:.1f} MB"
        print(f"  📦 {Color.GREEN}{f.name}{Color.RESET}  ({size_str})")


# ─── Profiles ─────────────────────────────────────────────────────────────────

def list_profiles(config: dict):
    """List configured GPU profiles."""
    profiles = config.get("profiles", {})
    default = config.get("default_profile", "gtx1060")
    
    print(f"\n  {Color.BOLD}GPU Profiles{Color.RESET}\n")
    for key, profile in profiles.items():
        is_default = key == default
        marker = f" {Color.GREEN}(default){Color.RESET}" if is_default else ""
        print(f"  {Color.CYAN}{key}{Color.RESET}{marker}")
        print(f"    Name:   {profile['name']}")
        print(f"    Model:  {profile['model']}")
        print(f"    Quant:  {profile['quantization']}")
        print(f"    Ctx:    {profile.get('ctx', 'N/A'):>6}")
        print(f"    Batch:  {profile.get('batch', 'N/A'):>6}")
        print(f"    VRAM:   {profile.get('vram_total_gb', 'N/A')} GB")
        print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="kimari",
        description="Kimari CLI — Local AI for Consumer GPUs",
    )
    parser.add_argument("-v", "--version", action="version", version="Kimari CLI v0.1.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # doctor
    subparsers.add_parser("doctor", help="Run system diagnostics")

    # start
    start_parser = subparsers.add_parser("start", help="Start Kimari server")
    start_parser.add_argument("--profile", "-p", required=True,
                               help="GPU profile (gtx1060, gtx1080, turbo)")

    # stop
    subparsers.add_parser("stop", help="Stop Kimari server")

    # status
    subparsers.add_parser("status", help="Check Kimari server status")

    # chat
    chat_parser = subparsers.add_parser("chat", help="Send a chat message")
    chat_parser.add_argument("message", nargs="?", help="Message to send (omit for interactive)")

    # bench
    bench_parser = subparsers.add_parser("bench", help="Run benchmarks")
    bench_parser.add_argument("--profile", "-p", default=None,
                               help="GPU profile to benchmark")

    # fit
    fit_parser = subparsers.add_parser("fit", help="Calculate KimariFit score")
    fit_parser.add_argument("--model", "-m", required=True, help="Path to GGUF model")
    fit_parser.add_argument("--ctx", "-c", type=int, default=8192, help="Context size")

    # models
    subparsers.add_parser("models", help="List available GGUF models")

    # profiles
    subparsers.add_parser("profiles", help="List configured GPU profiles")

    args = parser.parse_args()

    # Load config (needed for most commands)
    config = {}
    if CONFIG_PATH.exists():
        config = load_config()

    if not args.command:
        parser.print_help()
        return

    if args.command == "doctor":
        run_doctor(config)
    elif args.command == "start":
        start_server(args.profile, config)
    elif args.command == "stop":
        stop_server()
    elif args.command == "status":
        check_status(config)
    elif args.command == "chat":
        if args.message:
            chat(args.message, config)
        else:
            interactive_chat(config)
    elif args.command == "bench":
        profile = args.profile or config.get("default_profile", "gtx1080")
        run_benchmark(profile, config)
    elif args.command == "fit":
        calculate_kimarifit(args.model, args.ctx, config)
    elif args.command == "models":
        list_models()
    elif args.command == "profiles":
        list_profiles(config)


if __name__ == "__main__":
    main()
