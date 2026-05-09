"""
Kimari CLI — Command-line interface for Kimari Local AI.

Provides commands for server management, model downloads, diagnostics,
chat, benchmarking, and configuration management.
"""

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("[ERROR] 'requests' is required. Install with: pip install -r cli/requirements.txt")
    sys.exit(1)

from kimari import __version__ as KIMARI_VERSION
from kimari.core.constants import (
    CONFIG_PATH, LOG_FILE, PID_FILE, PROJECT_ROOT, STATE_DIR, STATE_FILE,
    KIMARI_ASCII,
)
from kimari.core.state import clear_state, ensure_state_dir, is_pid_alive, read_state, write_state
from kimari.core.errors import parse_log_errors, read_log_tail
from kimari.core.detection import (
    detect_cuda, detect_cuda_version, detect_gpu, detect_llama_server,
    is_port_free, recommend_profile,
)
from kimari.config.loader import (
    load_config, get_profile, validate_config, migrate_config,
    get_config_path, show_config,
)
from kimari.models.registry import (
    load_models_registry, list_registry_models, pull_model, pull_all_models,
    scan_models_dir_for_gguf, verify_model_hash,
)
from kimari.profiles.manager import list_profiles
from kimari.benchmarks.kimarifit import calculate_kimarifit
from kimari.benchmarks.bench import run_benchmark
from kimari.utils.colors import Color, ok, warn, fail, info


# ─── Server Management ───────────────────────────────────────────────────────

def build_server_cmd(llama_server: str, profile: dict,
                     model_override: Optional[str] = None,
                     host_override: Optional[str] = None,
                     port_override: Optional[int] = None,
                     ctx_override: Optional[int] = None) -> list:
    """Build the llama-server command list for a given profile.

    Optional overrides replace the profile values when provided.
    """
    model_path = PROJECT_ROOT / (model_override if model_override else profile["model"])
    host = host_override if host_override else profile.get("host", "127.0.0.1")
    port = port_override if port_override else profile.get("port", 11435)
    ctx = ctx_override if ctx_override else profile.get("ctx", 8192)

    cmd = [
        llama_server,
        "-m", str(model_path),
        "--host", host,
        "--port", str(port),
        "-ngl", profile.get("gpu_layers", "all"),
        "-c", str(ctx),
        "-b", str(profile.get("batch", 256)),
        "-ub", str(profile.get("ubatch", 128)),
        "--cache-type-k", profile.get("cache_type_k", "f16"),
        "--cache-type-v", profile.get("cache_type_v", "f16"),
    ]

    if profile.get("threads"):
        cmd.extend(["-t", str(profile["threads"])])

    return cmd


def start_server(profile_name: str, config: dict, dry_run: bool = False,
                 daemon: bool = False,
                 model_override: Optional[str] = None,
                 host_override: Optional[str] = None,
                 port_override: Optional[int] = None,
                 ctx_override: Optional[int] = None):
    """Start llama-server with the specified profile."""
    profile = get_profile(config, profile_name)

    # Apply overrides
    effective_model = model_override if model_override else profile["model"]
    effective_host = host_override if host_override else profile.get("host", "127.0.0.1")
    effective_port = port_override if port_override else profile.get("port", 11435)
    effective_ctx = ctx_override if ctx_override else profile.get("ctx", 8192)

    # Security warning for 0.0.0.0
    if effective_host == "0.0.0.0" and profile_name != "docker":
        warn("Binding to 0.0.0.0 exposes the API to all network interfaces.")
        print("  If you don't need external access, use 127.0.0.1 instead.")
        print("  The 'docker' profile is designed for this purpose.")

    llama_server = detect_llama_server()

    # Build command
    if llama_server:
        cmd = build_server_cmd(llama_server, profile,
                               model_override=model_override,
                               host_override=host_override,
                               port_override=port_override,
                               ctx_override=ctx_override)
    else:
        model_path = PROJECT_ROOT / effective_model
        cmd = ["llama-server",
               "-m", str(model_path),
               "--host", effective_host,
               "--port", str(effective_port),
               "-ngl", profile.get("gpu_layers", "all"),
               "-c", str(effective_ctx),
               "-b", str(profile.get("batch", 256)),
               "-ub", str(profile.get("ubatch", 128)),
               "--cache-type-k", profile.get("cache_type_k", "f16"),
               "--cache-type-v", profile.get("cache_type_v", "f16")]
        if profile.get("threads"):
            cmd.extend(["-t", str(profile["threads"])])

    print(f"\n{Color.BOLD}{Color.CYAN}🚀 Starting Kimari{Color.RESET}")
    print(f"   Profile: {Color.GREEN}{profile_name}{Color.RESET} ({profile['name']})")
    print(f"   Model:   {effective_model}")
    print(f"   Host:    {effective_host}:{effective_port}")
    print(f"   Context: {effective_ctx} tokens")
    print(f"   Quant:   {profile['quantization']}")
    if llama_server:
        print(f"   Binary:  {llama_server}")
    else:
        print(f"   Binary:  llama-server (not found — build or set LLAMA_SERVER)")
    if model_override:
        print(f"   {Color.YELLOW}[OVERRIDE]{Color.RESET} --model {model_override}")
    if host_override:
        print(f"   {Color.YELLOW}[OVERRIDE]{Color.RESET} --host {host_override}")
    if port_override:
        print(f"   {Color.YELLOW}[OVERRIDE]{Color.RESET} --port {port_override}")
    if ctx_override:
        print(f"   {Color.YELLOW}[OVERRIDE]{Color.RESET} --ctx {ctx_override}")
    print()

    # Dry run
    if dry_run:
        model_path = PROJECT_ROOT / effective_model
        if not model_path.exists():
            print(f"  {Color.YELLOW}[WARN]{Color.RESET} Model not found: {model_path}")
            print(f"  {Color.YELLOW}[WARN]{Color.RESET} Place a GGUF model before actually starting.\n")
        print(f"{Color.YELLOW}[DRY RUN]{Color.RESET} Would execute:\n")
        print(f"  {' '.join(cmd)}\n")
        print(f"  stdout → {LOG_FILE}")
        print(f"  state  → {STATE_FILE}")
        return

    # Real startup checks
    model_path = PROJECT_ROOT / effective_model
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        gguf_files = scan_models_dir_for_gguf()
        if len(gguf_files) == 1:
            print(f"  Found {Color.GREEN}{gguf_files[0]}{Color.RESET} — "
                  f"use {Color.CYAN}--model {gguf_files[0]}{Color.RESET}")
        elif len(gguf_files) > 1:
            print(f"  Available models in models/:")
            for f in gguf_files:
                print(f"    • {Color.GREEN}{f}{Color.RESET} — "
                      f"use {Color.CYAN}--model {f}{Color.RESET}")
        else:
            print(f"  Run {Color.CYAN}'kimari pull test'{Color.RESET} to download a test model, "
                  f"or place any GGUF in models/")
        write_state("ERROR", error="MODEL_NOT_FOUND", profile=profile_name,
                    model=effective_model)
        raise SystemExit(1)

    if not llama_server:
        print("[ERROR] llama-server not found.")
        print("  Searched in order:")
        print(f"    1. $LLAMA_SERVER environment variable")
        print(f"    2. $KIMARI_LLAMA_SERVER environment variable")
        print(f"    3. llama-server in PATH")
        print(f"    4. llama_server in PATH")
        print(f"    5. {PROJECT_ROOT / 'llama-server'}")
        print(f"    6. {PROJECT_ROOT / 'bin' / 'llama-server'}")
        print(f"    7. {PROJECT_ROOT / 'deps' / 'llama.cpp' / 'build' / 'bin' / 'llama-server'}")
        print()
        print("  Build it first: bash scripts/linux/build-llamacpp-cuda.sh")
        print("  Or set LLAMA_SERVER=/path/to/llama-server")
        write_state("ERROR", error="LLAMA_SERVER_NOT_FOUND", profile=profile_name,
                    model=effective_model)
        raise SystemExit(1)

    if not is_port_free(effective_host, effective_port):
        print(f"[ERROR] Port {effective_port} is already in use.")
        print("Stop the existing server first: kimari stop")
        write_state("ERROR", error="PORT_BUSY", profile=profile_name,
                    model=effective_model, host=effective_host, port=effective_port)
        raise SystemExit(1)

    write_state("STARTING", pid=None, profile=profile_name,
                model=effective_model, host=effective_host, port=effective_port)

    try:
        log_fh = open(LOG_FILE, "w")
        process = subprocess.Popen(
            cmd,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid if sys.platform != "win32" else None,
        )

        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))

        print(f"   Waiting for server to start...", end=" ", flush=True)
        max_wait = 30
        for i in range(max_wait):
            time.sleep(1)
            try:
                resp = requests.get(f"http://{effective_host}:{effective_port}/health", timeout=2)
                if resp.status_code == 200:
                    print(f"{Color.GREEN}✓ Ready{Color.RESET}")
                    print(f"\n{Color.DIM}   API: http://{effective_host}:{effective_port}/v1{Color.RESET}")
                    print(f"{Color.DIM}   Log: {LOG_FILE}{Color.RESET}")
                    print(f"{Color.DIM}   State: {STATE_FILE}{Color.RESET}")
                    print()
                    write_state("READY", pid=process.pid, profile=profile_name,
                                model=effective_model, host=effective_host, port=effective_port)

                    if daemon:
                        info(f"Server running in background (PID: {process.pid})")
                        info(f"Logs: kimari logs")
                        info(f"Stop: kimari stop")
                        return

                    info("Press Ctrl+C to stop, or run: kimari stop")
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
                write_state("ERROR", pid=process.pid, profile=profile_name,
                            model=effective_model, host=effective_host, port=effective_port,
                            error="START_TIMEOUT")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    stop_server()
                return
            if process.poll() is not None:
                log_fh.close()
                error_info = parse_log_errors()
                last_lines = read_log_tail(LOG_FILE, 10)
                print(f"{Color.RED}✗ Failed{Color.RESET}")
                if error_info:
                    print(f"\n   {Color.RED}Error detected:{Color.RESET} {error_info['pattern']}")
                    print(f"   {Color.YELLOW}Solution:{Color.RESET} {error_info['solution']}")
                    write_state("ERROR", pid=process.pid, profile=profile_name,
                                model=effective_model, host=effective_host, port=effective_port,
                                error=error_info["error_type"])
                else:
                    print(f"\n   Last log lines:")
                    for line in last_lines:
                        print(f"   {Color.DIM}{line.rstrip()}{Color.RESET}")
                    write_state("ERROR", pid=process.pid, profile=profile_name,
                                model=effective_model, host=effective_host, port=effective_port,
                                error="UNKNOWN")
                raise SystemExit(1)
            print(".", end="", flush=True)

    except FileNotFoundError:
        print(f"[ERROR] Could not execute: {llama_server}")
        write_state("ERROR", error="LLAMA_SERVER_NOT_FOUND", profile=profile_name,
                    model=effective_model)
        raise SystemExit(1)


def stop_server():
    """Stop the running llama-server."""
    if not PID_FILE.exists():
        print("[WARN] No server PID file found. Server may not be running.")
        clear_state()
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
        clear_state()


# ─── Status ──────────────────────────────────────────────────────────────────

def check_status(config: dict, json_output: bool = False):
    """Check the Kimari server status from multiple sources."""
    status_data = {
        "status": "STOPPED",
        "pid": None,
        "profile": None,
        "model": None,
        "host": None,
        "port": None,
        "uptime_s": None,
        "started_at": None,
        "health": None,
        "models": [],
        "last_log_lines": [],
        "log_errors": None,
    }

    state = read_state()
    if state:
        status_data["profile"] = state.get("profile")
        status_data["model"] = state.get("model")
        status_data["host"] = state.get("host")
        status_data["port"] = state.get("port")
        status_data["started_at"] = state.get("started_at")
        status_data["status"] = state.get("status", "STOPPED")
        pid = state.get("pid")
        if pid:
            status_data["pid"] = pid

    profile_name = status_data.get("profile") or config.get("default_profile", "gtx1060")
    profile = config.get("profiles", {}).get(profile_name, {})
    host = status_data.get("host") or profile.get("host", "127.0.0.1")
    port = status_data.get("port") or profile.get("port", 11435)
    status_data["host"] = host
    status_data["port"] = port
    if not status_data.get("profile"):
        status_data["profile"] = profile_name

    pid = status_data.get("pid")
    if pid and not is_pid_alive(pid):
        status_data["status"] = "ERROR"
        status_data["error"] = "PROCESS_DIED"

    try:
        resp = requests.get(f"http://{host}:{port}/health", timeout=3)
        if resp.status_code == 200:
            status_data["health"] = resp.json() if resp.headers.get(
                "content-type", ""
            ).startswith("application/json") else {"status": "ok"}
            if status_data.get("status") not in ("ERROR",):
                status_data["status"] = "READY"
        else:
            status_data["health"] = {"error": f"HTTP {resp.status_code}"}
            if status_data.get("status") == "READY":
                status_data["status"] = "ERROR"
    except requests.ConnectionError:
        status_data["health"] = {"error": "connection refused"}
        if status_data.get("status") == "READY":
            status_data["status"] = "STOPPED"
    except Exception as e:
        status_data["health"] = {"error": str(e)}

    try:
        resp = requests.get(f"http://{host}:{port}/v1/models", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            status_data["models"] = [m.get("id", "unknown") for m in data.get("data", [])]
    except Exception:
        pass

    last_lines = read_log_tail(LOG_FILE, 10)
    status_data["last_log_lines"] = [line.rstrip() for line in last_lines]

    error_info = parse_log_errors()
    if error_info:
        status_data["log_errors"] = error_info
        if status_data.get("status") == "ERROR" and not status_data.get("error"):
            status_data["error"] = error_info["error_type"]

    if status_data.get("started_at") and status_data.get("status") == "READY":
        try:
            started = datetime.fromisoformat(status_data["started_at"].replace("Z", "+00:00"))
            uptime = (datetime.now(timezone.utc) - started).total_seconds()
            status_data["uptime_s"] = int(uptime)
        except (ValueError, TypeError):
            pass

    if json_output:
        print(json.dumps(status_data, indent=2))
        return

    # Human-readable output
    status = status_data["status"]
    if status == "READY":
        color = Color.GREEN
    elif status == "STOPPED":
        color = Color.RED
    else:
        color = Color.YELLOW

    print(f"\n{color}● Kimari Server: {status}{Color.RESET}")

    if status_data.get("pid"):
        print(f"  PID:         {status_data['pid']}")
    print(f"  Endpoint:    http://{host}:{port}")
    if status_data.get("profile"):
        print(f"  Profile:     {status_data['profile']}")
    if status_data.get("model"):
        print(f"  Model:       {status_data['model']}")
    if status_data.get("uptime_s") is not None:
        uptime = status_data["uptime_s"]
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            print(f"  Uptime:      {hours}h {minutes}m {seconds}s")
        elif minutes > 0:
            print(f"  Uptime:      {minutes}m {seconds}s")
        else:
            print(f"  Uptime:      {seconds}s")
    if status_data.get("started_at"):
        print(f"  Started:     {status_data['started_at']}")
    if status_data.get("models"):
        print(f"  Loaded models: {', '.join(status_data['models'])}")
    if status_data.get("health"):
        health = status_data["health"]
        if "error" in health:
            print(f"  Health:      {Color.RED}{health['error']}{Color.RESET}")
        else:
            print(f"  Health:      {Color.GREEN}OK{Color.RESET}")
    if status_data.get("log_errors"):
        err = status_data["log_errors"]
        print(f"\n  {Color.RED}Log error detected:{Color.RESET} {err['pattern']}")
        print(f"  {Color.YELLOW}Solution:{Color.RESET} {err['solution']}")
    if status_data.get("error"):
        print(f"  Error:       {Color.RED}{status_data['error']}{Color.RESET}")


# ─── Logs ────────────────────────────────────────────────────────────────────

def show_logs(lines: int = 50, follow: bool = False):
    """Show kimari-server.log contents."""
    if not LOG_FILE.exists():
        print("[WARN] No log file found at:", LOG_FILE)
        print("Start the server first: kimari start --profile <profile>")
        return

    tail_lines = read_log_tail(LOG_FILE, lines)
    for line in tail_lines:
        print(line.rstrip())

    if follow:
        print(f"\n{Color.DIM}--- Following log (Ctrl+C to stop) ---{Color.RESET}")
        try:
            with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip(), end="\n")
                        sys.stdout.flush()
                    else:
                        time.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\n{Color.DIM}Stopped following.{Color.RESET}")


# ─── Chat ────────────────────────────────────────────────────────────────────

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
        print("Start it first: kimari start --profile <profile>")
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
                conversation.pop()
        except requests.ConnectionError:
            print("[ERROR] Server not responding. Start with: kimari start")
            conversation.pop()
        except Exception as e:
            print(f"[ERROR] {e}")
            conversation.pop()


# ─── Doctor ──────────────────────────────────────────────────────────────────

def run_doctor(config: dict, json_output: bool = False):
    """Run system diagnostics."""
    diagnostics = {
        "kimari_version": KIMARI_VERSION,
        "checks": [],
        "summary": {"ok": 0, "warn": 0, "fail": 0},
        "recommended_profile": None,
    }

    if not json_output:
        print(f"\n{KIMARI_ASCII}")
        print(f"  {Color.BOLD}System Diagnostics{Color.RESET}\n")

    # OS
    import platform as _platform
    os_name = f"{_platform.system()} {_platform.release()}"
    if _platform.system() == "Linux":
        os_name += f" ({_platform.machine()})"
    elif _platform.system() == "Windows":
        os_name += f" ({_platform.machine()})"
    diagnostics["checks"].append({"name": "OS", "status": "ok", "value": os_name})
    if not json_output:
        ok(f"OS: {os_name}")

    # GPU
    gpu = detect_gpu()
    if gpu:
        gpu_str = f"{gpu['name']} ({gpu['vram_mb']} MB)"
        diagnostics["checks"].append({"name": "GPU", "status": "ok", "value": gpu_str})
        if not json_output:
            ok(f"GPU: {gpu_str}")
    else:
        diagnostics["checks"].append({"name": "GPU", "status": "warn", "value": "No NVIDIA GPU detected"})
        if not json_output:
            warn("GPU: No NVIDIA GPU detected")

    # Driver
    if gpu:
        diagnostics["checks"].append({"name": "Driver", "status": "ok", "value": gpu["driver"]})
        if not json_output:
            ok(f"Driver: {gpu['driver']}")
    else:
        diagnostics["checks"].append({"name": "Driver", "status": "warn", "value": "Cannot check (no GPU)"})
        if not json_output:
            warn("Driver: Cannot check (no GPU)")

    # CUDA
    cuda_ver = detect_cuda_version()
    has_cuda = detect_cuda()
    if cuda_ver:
        cuda_str = f"CUDA {cuda_ver}"
        diagnostics["checks"].append({"name": "CUDA", "status": "ok", "value": cuda_str})
        if not json_output:
            ok(f"CUDA: {cuda_str}")
    elif has_cuda:
        diagnostics["checks"].append({"name": "CUDA", "status": "ok", "value": "Available (version unknown)"})
        if not json_output:
            ok("CUDA: Available (version unknown)")
    else:
        diagnostics["checks"].append({"name": "CUDA", "status": "warn", "value": "Not detected"})
        if not json_output:
            warn("CUDA: Not detected")

    # llama-server
    llama_server = detect_llama_server()
    if llama_server:
        diagnostics["checks"].append({"name": "llama-server", "status": "ok", "value": llama_server})
        if not json_output:
            ok(f"llama-server: {llama_server}")
    else:
        diagnostics["checks"].append({"name": "llama-server", "status": "fail", "value": "Not found in PATH"})
        if not json_output:
            fail("llama-server: Not found in PATH")

    # Model
    default_profile = config.get("default_profile", "gtx1060")
    profile = config.get("profiles", {}).get(default_profile, {})
    model_path = PROJECT_ROOT / profile.get("model", "models/Kimari-4B-Q4_K_M.gguf")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        model_str = f"{model_path.name} ({size_mb:.1f} MB)"
        diagnostics["checks"].append({"name": "Model", "status": "ok", "value": model_str})
        if not json_output:
            ok(f"Model: {model_str}")
    else:
        diagnostics["checks"].append({"name": "Model", "status": "warn", "value": f"{model_path.name} not found in models/"})
        if not json_output:
            warn(f"Model: {model_path.name} not found in models/")

    # Port
    host = profile.get("host", "127.0.0.1")
    port = profile.get("port", 11435)
    if is_port_free(host, port):
        diagnostics["checks"].append({"name": "Port", "status": "ok", "value": f"{port} available"})
        if not json_output:
            ok(f"Port: {port} available")
    else:
        diagnostics["checks"].append({"name": "Port", "status": "warn", "value": f"{port} in use"})
        if not json_output:
            warn(f"Port: {port} in use")

    # Security: host binding warning
    if host == "0.0.0.0":
        diagnostics["checks"].append({
            "name": "Security",
            "status": "warn",
            "value": f"Host 0.0.0.0 exposes API to all interfaces (profile: {default_profile})"
        })
        if not json_output:
            warn(f"Security: Host 0.0.0.0 exposes API to all interfaces")

    # Config
    diagnostics["checks"].append({"name": "Config", "status": "ok", "value": str(CONFIG_PATH)})
    if not json_output:
        ok(f"Config: {CONFIG_PATH}")

    # Config version
    config_version = config.get("config_version", 1)
    diagnostics["checks"].append({
        "name": "Config version",
        "status": "ok",
        "value": str(config_version)
    })
    if not json_output:
        ok(f"Config version: {config_version}")

    # Recommended profile
    recommended = recommend_profile(config, gpu)
    diagnostics["recommended_profile"] = recommended
    if recommended == default_profile:
        diagnostics["checks"].append({"name": "Recommended profile", "status": "ok", "value": recommended})
        if not json_output:
            ok(f"Recommended profile: {recommended}")
    else:
        diagnostics["checks"].append({"name": "Recommended profile", "status": "ok", "value": f"{recommended} (current: {default_profile})"})
        if not json_output:
            info(f"Recommended profile: {recommended} (current: {default_profile})")

    # Python
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        diagnostics["checks"].append({"name": "Python", "status": "ok", "value": py_version})
        if not json_output:
            ok(f"Python: {py_version}")
    else:
        diagnostics["checks"].append({"name": "Python", "status": "warn", "value": f"{py_version} (3.10+ recommended)"})
        if not json_output:
            warn(f"Python: {py_version} (3.10+ recommended)")

    # State dir
    diagnostics["checks"].append({"name": "State dir", "status": "ok", "value": str(STATE_DIR)})
    if not json_output:
        ok(f"State dir: {STATE_DIR}")

    # Compute summary
    for check in diagnostics["checks"]:
        status = check.get("status", "ok")
        if status == "ok":
            diagnostics["summary"]["ok"] += 1
        elif status == "warn":
            diagnostics["summary"]["warn"] += 1
        elif status == "fail":
            diagnostics["summary"]["fail"] += 1

    if json_output:
        print(json.dumps(diagnostics, indent=2))
        return

    ok_count = diagnostics["summary"]["ok"]
    warn_count = diagnostics["summary"]["warn"]
    fail_count = diagnostics["summary"]["fail"]

    print(f"\n  {Color.BOLD}Result: {ok_count} OK, {warn_count} WARN, {fail_count} FAIL{Color.RESET}")

    if fail_count > 0:
        print(f"\n  {Color.YELLOW}Fix the errors above before starting Kimari.{Color.RESET}")
        raise SystemExit(1)
    elif warn_count > 0:
        print(f"\n  {Color.YELLOW}Warnings present. Kimari may work with limitations.{Color.RESET}")
    else:
        print(f"\n  {Color.GREEN}All checks passed! Ready to start.{Color.RESET}")
        print(f"  Run: {Color.CYAN}kimari start --profile {recommended}{Color.RESET}")


# ─── Info ────────────────────────────────────────────────────────────────────

def show_info(config: dict, json_output: bool = False):
    """Show Kimari installation information (version, paths, profiles, endpoint)."""
    state = read_state()
    llama_server = detect_llama_server()
    default_profile = config.get("default_profile", "gtx1060")
    profile = config.get("profiles", {}).get(default_profile, {})
    gpu = detect_gpu()

    info_data = {
        "kimari_version": KIMARI_VERSION,
        "project_root": str(PROJECT_ROOT),
        "config_path": str(CONFIG_PATH),
        "models_dir": str(PROJECT_ROOT / "models"),
        "state_dir": str(STATE_DIR),
        "llama_server_path": llama_server,
        "default_profile": default_profile,
        "available_profiles": list(config.get("profiles", {}).keys()),
        "current_model": profile.get("model"),
        "endpoint": f"http://{profile.get('host', '127.0.0.1')}:{profile.get('port', 11435)}/v1",
        "gpu": gpu,
        "config_version": config.get("config_version", 1),
        "server_status": state.get("status") if state else "STOPPED",
    }

    if json_output:
        print(json.dumps(info_data, indent=2))
        return

    print(f"\n  {Color.BOLD}Kimari Info{Color.RESET}\n")
    print(f"  Version:          {KIMARI_VERSION}")
    print(f"  Project root:     {PROJECT_ROOT}")
    print(f"  Config path:      {CONFIG_PATH}")
    print(f"  Config version:   {config.get('config_version', 1)}")
    print(f"  Models dir:       {PROJECT_ROOT / 'models'}")
    print(f"  State dir:        {STATE_DIR}")
    print(f"  llama-server:     {llama_server or 'not found'}")
    print(f"  Default profile:  {default_profile}")
    print(f"  Current model:    {profile.get('model', 'N/A')}")
    print(f"  Endpoint:         http://{profile.get('host', '127.0.0.1')}:{profile.get('port', 11435)}/v1")
    print(f"  Server status:    {state.get('status', 'STOPPED') if state else 'STOPPED'}")
    if gpu:
        print(f"  GPU:              {gpu['name']} ({gpu['vram_mb']} MB)")
    print(f"  Profiles:         {', '.join(config.get('profiles', {}).keys())}")
    print()


# ─── Models ──────────────────────────────────────────────────────────────────

def list_models(json_output: bool = False, downloaded_only: bool = False,
                status_filter: Optional[str] = None, verify: bool = False):
    """List available models (downloaded + registry)."""
    if not (PROJECT_ROOT / "models").exists():
        print("[ERROR] models/ directory not found.")
        return

    gguf_files = list((PROJECT_ROOT / "models").glob("*.gguf"))

    if json_output:
        result = []
        for f in sorted(gguf_files):
            size_mb = f.stat().st_size / (1024 * 1024)
            result.append({
                "name": f.name,
                "path": str(f.relative_to(PROJECT_ROOT)),
                "size_mb": round(size_mb, 1),
                "size_gb": round(size_mb / 1024, 2),
            })
        print(json.dumps(result, indent=2))
        return

    if not gguf_files:
        print("\n  No GGUF models found in models/")
        print("  Download a model: kimari pull test")
        return

    print(f"\n  {Color.BOLD}Downloaded Models{Color.RESET}\n")
    for f in sorted(gguf_files):
        size_mb = f.stat().st_size / (1024 * 1024)
        size_gb = size_mb / 1024
        if size_gb >= 1:
            size_str = f"{size_gb:.2f} GiB"
        else:
            size_str = f"{size_mb:.1f} MB"
        print(f"  📦 {Color.GREEN}{f.name}{Color.RESET}  ({size_str})")

    # Also show registry models not yet downloaded
    registry_models = list_registry_models(json_output=True, downloaded_only=False,
                                            status_filter=status_filter)
    not_downloaded = [m for m in registry_models if not m.get("downloaded")]
    if not_downloaded:
        print(f"\n  {Color.DIM}Not yet downloaded (use 'kimari pull <name>'):{Color.RESET}")
        for m in not_downloaded:
            print(f"    • {Color.CYAN}{m['id']}{Color.RESET} — {m['display_name']} ({m['size_gb']} GB)")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="kimari",
        description="Kimari CLI — Local AI for Consumer GPUs",
    )
    parser.add_argument("-v", "--version", action="version", version=f"Kimari CLI v{KIMARI_VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # doctor
    doctor_parser = subparsers.add_parser("doctor", help="Run system diagnostics")
    doctor_parser.add_argument("--json", action="store_true", dest="json_output",
                               help="Output diagnostics as JSON")

    # info
    info_parser = subparsers.add_parser("info", help="Show Kimari installation info")
    info_parser.add_argument("--json", action="store_true", dest="json_output",
                             help="Output info as JSON")

    # start
    start_parser = subparsers.add_parser("start", help="Start Kimari server")
    start_parser.add_argument("--profile", "-p", required=True,
                              help="GPU profile (gtx1060, gtx1080, turbo, test, docker)")
    start_parser.add_argument("--dry-run", action="store_true",
                              help="Print command without executing")
    start_parser.add_argument("--daemon", action="store_true",
                              help="Start server in background (exit after READY)")
    start_parser.add_argument("--model", "-m", default=None, dest="model",
                              help="Override profile model path")
    start_parser.add_argument("--host", default=None, dest="host",
                              help="Override profile host (e.g. 0.0.0.0)")
    start_parser.add_argument("--port", type=int, default=None, dest="port",
                              help="Override profile port")
    start_parser.add_argument("--ctx", type=int, default=None, dest="ctx",
                              help="Override profile context size (tokens)")

    # stop
    subparsers.add_parser("stop", help="Stop Kimari server")

    # status
    status_parser = subparsers.add_parser("status", help="Check Kimari server status")
    status_parser.add_argument("--json", action="store_true", dest="json_output",
                               help="Output status as JSON")

    # logs
    logs_parser = subparsers.add_parser("logs", help="Show server logs")
    logs_parser.add_argument("--lines", "-n", type=int, default=50,
                             help="Number of log lines to show (default: 50)")
    logs_parser.add_argument("--follow", "-f", action="store_true",
                             help="Follow log output in real time")

    # chat
    chat_parser = subparsers.add_parser("chat", help="Send a chat message")
    chat_parser.add_argument("message", nargs="?", help="Message to send (omit for interactive)")

    # bench
    bench_parser = subparsers.add_parser("bench", help="Run benchmarks")
    bench_parser.add_argument("--profile", "-p", default=None,
                              help="GPU profile to benchmark")
    bench_parser.add_argument("--json", action="store_true", dest="json_output",
                              help="Output benchmark results as JSON only")
    bench_parser.add_argument("--output", "-o", default=None, dest="output",
                              help="Save standardized benchmark results to a JSON file")

    # fit
    fit_parser = subparsers.add_parser("fit", help="Calculate KimariFit score")
    fit_parser.add_argument("--model", "-m", required=True, help="Path to GGUF model")
    fit_parser.add_argument("--ctx", "-c", type=int, default=8192, help="Context size")
    fit_parser.add_argument("--vram", type=float, default=None,
                            help="Override VRAM in GiB (for systems without GPU)")

    # models
    models_parser = subparsers.add_parser("models", help="List available GGUF models")
    models_parser.add_argument("--json", action="store_true", dest="json_output",
                                help="Output as JSON")
    models_parser.add_argument("--downloaded", action="store_true",
                                help="Only show downloaded models")
    models_parser.add_argument("--status", default=None, dest="status_filter",
                                help="Filter by status (recommended, test, experimental)")
    models_parser.add_argument("--verify", action="store_true",
                                help="Verify SHA256 hashes of downloaded models")

    # profiles
    profiles_parser = subparsers.add_parser("profiles", help="List configured GPU profiles")
    profiles_parser.add_argument("--json", action="store_true", dest="json_output",
                                  help="Output as JSON")

    # pull
    pull_parser = subparsers.add_parser("pull", help="Download a model from the registry")
    pull_parser.add_argument("name", nargs="?", default=None,
                             help="Model ID to download (e.g. test, recommended)")
    pull_parser.add_argument("--list", action="store_true", dest="list_models",
                             help="List available models in the registry")
    pull_parser.add_argument("--all", action="store_true", dest="pull_all",
                             help="Download all models from the registry")
    pull_parser.add_argument("--dry-run", action="store_true",
                             help="Show what would be downloaded without downloading")
    pull_parser.add_argument("--force", action="store_true",
                             help="Redownload even if file already exists")

    # config (subcommands)
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_sub = config_parser.add_subparsers(dest="config_command", help="Config subcommands")

    config_path_parser = config_sub.add_parser("path", help="Print config file path")
    config_show_parser = config_sub.add_parser("show", help="Show full configuration")
    config_show_parser.add_argument("--json", action="store_true", dest="json_output",
                                    help="Output as JSON")

    config_validate_parser = config_sub.add_parser("validate", help="Validate configuration against schema")

    config_migrate_parser = config_sub.add_parser("migrate", help="Migrate configuration to current version")
    config_migrate_parser.add_argument("--dry-run", action="store_true",
                                       help="Show changes without applying them")

    args = parser.parse_args()

    # Ensure state directory exists
    ensure_state_dir()

    # Load config (needed for most commands)
    config = {}
    if CONFIG_PATH.exists():
        config = load_config()

    if not args.command:
        parser.print_help()
        return

    if args.command == "doctor":
        run_doctor(config, json_output=getattr(args, "json_output", False))
    elif args.command == "info":
        show_info(config, json_output=getattr(args, "json_output", False))
    elif args.command == "start":
        start_server(args.profile, config,
                     dry_run=args.dry_run,
                     daemon=args.daemon,
                     model_override=args.model,
                     host_override=args.host,
                     port_override=args.port,
                     ctx_override=args.ctx)
    elif args.command == "stop":
        stop_server()
    elif args.command == "status":
        check_status(config, json_output=getattr(args, "json_output", False))
    elif args.command == "logs":
        show_logs(lines=args.lines, follow=args.follow)
    elif args.command == "chat":
        if args.message:
            chat(args.message, config)
        else:
            interactive_chat(config)
    elif args.command == "bench":
        profile = args.profile or config.get("default_profile", "gtx1080")
        run_benchmark(profile, config,
                      json_output=getattr(args, "json_output", False),
                      output=getattr(args, "output", None))
    elif args.command == "fit":
        calculate_kimarifit(args.model, args.ctx, config,
                            vram_override=getattr(args, "vram", None))
    elif args.command == "models":
        list_models(json_output=getattr(args, "json_output", False),
                    downloaded_only=getattr(args, "downloaded", False),
                    status_filter=getattr(args, "status_filter", None),
                    verify=getattr(args, "verify", False))
    elif args.command == "profiles":
        list_profiles(config, json_output=getattr(args, "json_output", False))
    elif args.command == "pull":
        if getattr(args, "list_models", False):
            list_registry_models()
        elif getattr(args, "pull_all", False):
            pull_all_models(dry_run=args.dry_run, force=args.force)
        elif args.name:
            pull_model(args.name, dry_run=args.dry_run, force=args.force)
        else:
            pull_parser.print_help()
    elif args.command == "config":
        if not args.config_command:
            config_parser.print_help()
            return
        if args.config_command == "path":
            print(str(get_config_path()))
        elif args.config_command == "show":
            show_config(json_output=getattr(args, "json_output", False))
        elif args.config_command == "validate":
            is_valid, errors = validate_config(config)
            if is_valid:
                ok("Configuration is valid.")
            else:
                fail("Configuration validation failed:")
                for e in errors:
                    print(f"  • {e}")
                raise SystemExit(1)
        elif args.config_command == "migrate":
            dry_run = getattr(args, "dry_run", False)
            changed, info = migrate_config(dry_run=dry_run)
            if not changed:
                ok("Configuration is already up to date.")
            else:
                if dry_run:
                    print(f"\n  {Color.YELLOW}[DRY RUN]{Color.RESET} Migration preview:")
                else:
                    print(f"\n  {Color.GREEN}Migration complete.{Color.RESET}")
                print(f"  From version: {info['from_version']}")
                print(f"  To version:   {info['to_version']}")
                print(f"  Changes:")
                for change in info["changes"]:
                    print(f"    • {change}")
                if info.get("backup_path"):
                    print(f"  Backup:       {info['backup_path']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
