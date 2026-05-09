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
from datetime import datetime, timezone
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
MODELS_REGISTRY_PATH = PROJECT_ROOT / "config" / "kimari.models.json"
MODELS_DIR = PROJECT_ROOT / "models"
PID_FILE = PROJECT_ROOT / ".kimari-server.pid"
LOG_FILE = PROJECT_ROOT / "kimari-server.log"
STATE_DIR = PROJECT_ROOT / ".kimari"
STATE_FILE = STATE_DIR / "state.json"

KIMARI_VERSION = "0.1.2-alpha"

KIMARI_ASCII = f"""
 ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗ █████╗
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██╔══██╗
██║     ███████║██████╔╝██║   ██║██╔██╗ ██║███████║
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██╔══██║
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║██║  ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝
   Local AI for Consumer GPUs — v{KIMARI_VERSION}
   Created by Smouj (https://x.com/smouj013)
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


# ─── State Management ────────────────────────────────────────────────────────

def ensure_state_dir():
    """Create .kimari/ directory if it doesn't exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def write_state(status: str, pid: Optional[int] = None, profile: Optional[str] = None,
                model: Optional[str] = None, host: Optional[str] = None,
                port: Optional[int] = None, error: Optional[str] = None):
    """Write state to .kimari/state.json."""
    ensure_state_dir()
    state = {
        "status": status,
        "pid": pid,
        "profile": profile,
        "model": model,
        "host": host,
        "port": port,
        "started_at": None,
        "error": error,
        "log_file": "kimari-server.log",
    }
    if status == "READY" and pid is not None:
        state["started_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def read_state() -> Optional[dict]:
    """Read state from .kimari/state.json."""
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def clear_state():
    """Remove state file."""
    if STATE_FILE.exists():
        STATE_FILE.unlink(missing_ok=True)


def is_pid_alive(pid: int) -> bool:
    """Check if a PID is still alive."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


# ─── Error Parsing from Logs ─────────────────────────────────────────────────

ERROR_PATTERNS = [
    {
        "pattern": "CUDA out of memory",
        "error_type": "OOM",
        "solution": "Use a lower quantization profile or reduce context size",
    },
    {
        "pattern": "no kernel image is available",
        "error_type": "CUDA_ERROR",
        "solution": "Rebuild llama.cpp with -DCMAKE_CUDA_ARCHITECTURES=native",
    },
    {
        "pattern": "failed to load model",
        "error_type": "MODEL_NOT_FOUND",
        "solution": "Verify the GGUF file is valid and not corrupted",
    },
    {
        "pattern": "unknown argument",
        "error_type": "CUDA_ERROR",
        "solution": "Check llama.cpp version compatibility",
    },
    {
        "pattern": "address already in use",
        "error_type": "PORT_BUSY",
        "solution": "Stop the existing server with 'kimari stop' or change port",
    },
    {
        "pattern": "model architecture not supported",
        "error_type": "MODEL_NOT_FOUND",
        "solution": "Use a model compatible with this llama.cpp version",
    },
]


def parse_log_errors(log_path: Path = LOG_FILE) -> Optional[dict]:
    """Read kimari-server.log and detect known error patterns.

    Returns the first matched error dict with 'error_type', 'pattern', and 'solution',
    or None if no errors found.
    """
    if not log_path.exists():
        return None
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return None

    content_lower = content.lower()
    for entry in ERROR_PATTERNS:
        if entry["pattern"].lower() in content_lower:
            return {
                "error_type": entry["error_type"],
                "pattern": entry["pattern"],
                "solution": entry["solution"],
            }
    return None


def read_log_tail(log_path: Path = LOG_FILE, lines: int = 10) -> list:
    """Read the last N lines of a log file."""
    if not log_path.exists():
        return []
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        return all_lines[-lines:]
    except OSError:
        return []


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
    """Find llama-server binary searching 7 locations in priority order."""
    # 1. LLAMA_SERVER environment variable
    env_llama = os.environ.get("LLAMA_SERVER")
    if env_llama:
        path = Path(env_llama)
        if path.exists():
            return str(path.resolve())

    # 2. KIMARI_LLAMA_SERVER environment variable
    env_kimari = os.environ.get("KIMARI_LLAMA_SERVER")
    if env_kimari:
        path = Path(env_kimari)
        if path.exists():
            return str(path.resolve())

    # 3. shutil.which("llama-server") (PATH)
    which_llama = shutil.which("llama-server")
    if which_llama:
        return which_llama

    # 4. shutil.which("llama_server") (PATH, underscore variant)
    which_llama_us = shutil.which("llama_server")
    if which_llama_us:
        return which_llama_us

    # 5. ./llama-server (relative to PROJECT_ROOT)
    rel_llama = PROJECT_ROOT / "llama-server"
    if rel_llama.exists():
        return str(rel_llama.resolve())

    # 6. ./bin/llama-server (relative to PROJECT_ROOT)
    bin_llama = PROJECT_ROOT / "bin" / "llama-server"
    if bin_llama.exists():
        return str(bin_llama.resolve())

    # 7. deps/llama.cpp/build/bin/llama-server (relative to PROJECT_ROOT)
    deps_llama = PROJECT_ROOT / "deps" / "llama.cpp" / "build" / "bin" / "llama-server"
    if deps_llama.exists():
        return str(deps_llama.resolve())

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


def _scan_models_dir_for_gguf() -> list:
    """Scan models/ directory for .gguf files, return list of relative paths."""
    if not MODELS_DIR.exists():
        return []
    return sorted([str(f.relative_to(PROJECT_ROOT)) for f in MODELS_DIR.glob("*.gguf")])


def start_server(profile_name: str, config: dict, dry_run: bool = False,
                 daemon: bool = False,
                 model_override: Optional[str] = None,
                 host_override: Optional[str] = None,
                 port_override: Optional[int] = None,
                 ctx_override: Optional[int] = None):
    """Start llama-server with the specified profile.

    Optional overrides (--model, --host, --port, --ctx) replace the profile values.
    """
    profile = get_profile(config, profile_name)

    # Apply overrides to a copy of the profile dict
    effective_model = model_override if model_override else profile["model"]
    effective_host = host_override if host_override else profile.get("host", "127.0.0.1")
    effective_port = port_override if port_override else profile.get("port", 11435)
    effective_ctx = ctx_override if ctx_override else profile.get("ctx", 8192)

    # Try to find llama-server (may not exist in dry-run / CI environments)
    llama_server = detect_llama_server()

    # Build command (works even if binary doesn't exist, for --dry-run)
    if llama_server:
        cmd = build_server_cmd(llama_server, profile,
                               model_override=model_override,
                               host_override=host_override,
                               port_override=port_override,
                               ctx_override=ctx_override)
    else:
        # For dry-run without binary, show a placeholder
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
    # Show overrides being applied
    if model_override:
        print(f"   {Color.YELLOW}[OVERRIDE]{Color.RESET} --model {model_override}")
    if host_override:
        print(f"   {Color.YELLOW}[OVERRIDE]{Color.RESET} --host {host_override}")
    if port_override:
        print(f"   {Color.YELLOW}[OVERRIDE]{Color.RESET} --port {port_override}")
    if ctx_override:
        print(f"   {Color.YELLOW}[OVERRIDE]{Color.RESET} --ctx {ctx_override}")
    print()

    # --dry-run: print command and exit (skip model/port checks)
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

    # --- Real startup checks below ---

    # Check model exists — with smart fallback messages
    model_path = PROJECT_ROOT / effective_model
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        # Scan models/ for .gguf files to suggest alternatives
        gguf_files = _scan_models_dir_for_gguf()
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
        sys.exit(1)

    # Check llama-server
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
        sys.exit(1)

    # Check port
    if not is_port_free(effective_host, effective_port):
        print(f"[ERROR] Port {effective_port} is already in use.")
        print("Stop the existing server first: kimari stop")
        write_state("ERROR", error="PORT_BUSY", profile=profile_name,
                    model=effective_model, host=effective_host, port=effective_port)
        sys.exit(1)

    # Write STARTING state
    write_state("STARTING", pid=None, profile=profile_name,
                model=effective_model, host=effective_host, port=effective_port)

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
                resp = requests.get(f"http://{effective_host}:{effective_port}/health", timeout=2)
                if resp.status_code == 200:
                    print(f"{Color.GREEN}✓ Ready{Color.RESET}")
                    print(f"\n{Color.DIM}   API: http://{effective_host}:{effective_port}/v1{Color.RESET}")
                    print(f"{Color.DIM}   Log: {LOG_FILE}{Color.RESET}")
                    print(f"{Color.DIM}   State: {STATE_FILE}{Color.RESET}")
                    print()
                    # Write READY state
                    write_state("READY", pid=process.pid, profile=profile_name,
                                model=effective_model, host=effective_host, port=effective_port)

                    if daemon:
                        info(f"Server running in background (PID: {process.pid})")
                        info(f"Logs: kimari logs")
                        info(f"Stop: kimari stop")
                        return

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
                write_state("ERROR", pid=process.pid, profile=profile_name,
                            model=effective_model, host=effective_host, port=effective_port,
                            error="START_TIMEOUT")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    stop_server()
                return
            if process.poll() is not None:
                # Process exited
                log_fh.close()
                # Parse logs for errors
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
                sys.exit(1)
            print(".", end="", flush=True)

    except FileNotFoundError:
        print(f"[ERROR] Could not execute: {llama_server}")
        write_state("ERROR", error="LLAMA_SERVER_NOT_FOUND", profile=profile_name,
                    model=effective_model)
        sys.exit(1)


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

    # 1. Read .kimari/state.json
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

    # Determine host/port for health check
    profile_name = status_data.get("profile") or config.get("default_profile", "gtx1060")
    profile = config.get("profiles", {}).get(profile_name, {})
    host = status_data.get("host") or profile.get("host", "127.0.0.1")
    port = status_data.get("port") or profile.get("port", 11435)
    status_data["host"] = host
    status_data["port"] = port
    if not status_data.get("profile"):
        status_data["profile"] = profile_name

    # 2. Check if PID is still alive
    pid = status_data.get("pid")
    if pid and not is_pid_alive(pid):
        status_data["status"] = "ERROR"
        status_data["error"] = "PROCESS_DIED"

    # 3. Hit /health endpoint
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

    # 4. Hit /v1/models endpoint
    try:
        resp = requests.get(f"http://{host}:{port}/v1/models", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            status_data["models"] = [m.get("id", "unknown") for m in data.get("data", [])]
    except Exception:
        pass

    # 5. Read last 10 lines of log
    last_lines = read_log_tail(LOG_FILE, 10)
    status_data["last_log_lines"] = [line.rstrip() for line in last_lines]

    # 6. Parse log errors
    error_info = parse_log_errors()
    if error_info:
        status_data["log_errors"] = error_info
        if status_data.get("status") == "ERROR" and not status_data.get("error"):
            status_data["error"] = error_info["error_type"]

    # Calculate uptime
    if status_data.get("started_at") and status_data.get("status") == "READY":
        try:
            started = datetime.fromisoformat(status_data["started_at"].replace("Z", "+00:00"))
            uptime = (datetime.now(timezone.utc) - started).total_seconds()
            status_data["uptime_s"] = int(uptime)
        except (ValueError, TypeError):
            pass

    # Output
    if json_output:
        print(json.dumps(status_data, indent=2))
        return

    # Human-readable output
    status = status_data["status"]
    if status == "READY":
        color = Color.GREEN
        symbol = "●"
    elif status == "STOPPED":
        color = Color.RED
        symbol = "●"
    elif status == "STARTING":
        color = Color.YELLOW
        symbol = "●"
    elif status == "BUSY":
        color = Color.YELLOW
        symbol = "●"
    else:
        color = Color.RED
        symbol = "●"

    print(f"\n{color}{symbol} Kimari Server: {status}{Color.RESET}")

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


# ─── Logs ─────────────────────────────────────────────────────────────────────

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
                # Seek to end
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

def run_benchmark(profile_name: str, config: dict, json_output: bool = False,
                    output: Optional[str] = None):
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

    results = []
    for i, prompt in enumerate(prompts):
        prompt_display = prompt[:50] + ("..." if len(prompt) > 50 else "")

        if not json_output:
            print(f"  [{i+1}/{len(prompts)}] ", end="", flush=True)
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
                if not json_output:
                    print(f"{Color.GREEN}✓{Color.RESET} {completion_tokens}tok in {elapsed:.1f}s ({tokens_per_sec:.1f} t/s)")
            else:
                results.append({
                    "prompt": prompt_display,
                    "status": f"http_{resp.status_code}",
                })
                if not json_output:
                    print(f"{Color.RED}✗{Color.RESET} HTTP {resp.status_code}")
        except Exception as e:
            results.append({
                "prompt": prompt_display,
                "status": f"error: {str(e)[:50]}",
            })
            if not json_output:
                print(f"{Color.RED}✗{Color.RESET} {e}")

    # Summary
    ok_results = [r for r in results if r.get("status") == "ok"]

    # Build benchmark output data
    bench_data = {
        "profile": profile_name,
        "profile_name": profile["name"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": results,
    }

    # Build standardized benchmark output (matching templates format)
    gpu = detect_gpu()
    std_data = {
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "kimari_version": KIMARI_VERSION,
        "os": f"{platform.system()} {platform.release()}",
        "gpu_name": gpu["name"] if gpu else None,
        "driver_version": gpu["driver"] if gpu else None,
        "cuda_version": None,  # Cannot reliably detect from CLI
        "llama_cpp_ref": None,  # Cannot detect automatically
        "model_name": Path(profile["model"]).stem,
        "model_size_gb": profile.get("estimated_model_size_gb"),
        "quantization": profile.get("quantization"),
        "ctx": profile.get("ctx"),
        "batch": profile.get("batch"),
        "ubatch": profile.get("ubatch"),
        "prompt_tokens": None,  # Not measured in basic bench
        "generated_tokens": None,  # Not measured in basic bench
        "prompt_eval_tokens_per_second": None,  # Requires server-side timing
        "generation_tokens_per_second": None,  # Populated from summary if available
        "time_to_first_token_ms": None,  # Requires streaming mode
        "peak_vram_mb": None,  # Known limitation — cannot measure from CLI
        "notes": "Automated benchmark via 'kimari bench'",
    }

    # Fill in generation speed from summary if we have results
    if ok_results:
        std_data["generation_tokens_per_second"] = round(
            sum(r["tokens_per_sec"] for r in ok_results) / len(ok_results), 2
        )
        std_data["generated_tokens"] = sum(r["tokens"] for r in ok_results)

    if ok_results:
        avg_tps = sum(r["tokens_per_sec"] for r in ok_results) / len(ok_results)
        avg_time = sum(r["time_s"] for r in ok_results) / len(ok_results)
        total_tokens = sum(r["tokens"] for r in ok_results)
        bench_data["summary"] = {
            "avg_tokens_per_sec": round(avg_tps, 2),
            "avg_latency_s": round(avg_time, 2),
            "total_tokens": total_tokens,
            "success_rate": f"{len(ok_results)}/{len(results)}",
        }

        if not json_output:
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
                json.dump(bench_data, f, indent=2)
            print(f"\n  Results saved: {result_file}")

    if json_output:
        print(json.dumps(bench_data, indent=2))

    # Save standardized output to file if --output provided
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(std_data, f, indent=2)
        if not json_output:
            print(f"\n  Results saved: {output_path}")

    if json_output:
        return

    if not ok_results:
        print(f"\n  {Color.RED}All benchmarks failed.{Color.RESET}")


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

def run_doctor(config: dict, json_output: bool = False):
    """Run system diagnostics."""
    diagnostics = {
        "checks": [],
        "summary": {"ok": 0, "warn": 0, "fail": 0},
        "recommended_profile": None,
    }

    if not json_output:
        print(f"\n{KIMARI_ASCII}")
        print(f"  {Color.BOLD}System Diagnostics{Color.RESET}\n")

    # OS
    os_name = f"{platform.system()} {platform.release()}"
    if platform.system() == "Linux":
        os_name += f" ({platform.machine()})"
    elif platform.system() == "Windows":
        os_name += f" ({platform.machine()})"
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
    has_cuda = detect_cuda()
    if has_cuda:
        diagnostics["checks"].append({"name": "CUDA", "status": "ok", "value": "Available"})
        if not json_output:
            ok("CUDA: Available")
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

    # Config
    diagnostics["checks"].append({"name": "Config", "status": "ok", "value": str(CONFIG_PATH)})
    if not json_output:
        ok(f"Config: {CONFIG_PATH}")

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

    # Output
    if json_output:
        print(json.dumps(diagnostics, indent=2))
        return

    ok_count = diagnostics["summary"]["ok"]
    warn_count = diagnostics["summary"]["warn"]
    fail_count = diagnostics["summary"]["fail"]

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


# ─── Model Pull ───────────────────────────────────────────────────────────────

def load_models_registry() -> dict:
    """Load the models registry from config/kimari.models.json."""
    if not MODELS_REGISTRY_PATH.exists():
        print(f"[ERROR] Models registry not found: {MODELS_REGISTRY_PATH}")
        print("Run this command from the kimari-local-ai root directory.")
        sys.exit(1)
    with open(MODELS_REGISTRY_PATH, "r") as f:
        return json.load(f)


def list_pull_models():
    """List all models in the registry with download status."""
    registry = load_models_registry()
    models = registry.get("models", [])

    if not models:
        print("\n  No models in registry.")
        return

    print(f"\n  {Color.BOLD}Available Models for Download{Color.RESET}\n")
    for m in models:
        # Check if already downloaded
        target = PROJECT_ROOT / m["target_path"]
        downloaded = target.exists()
        status_str = f"{Color.GREEN}✓ downloaded{Color.RESET}" if downloaded else f"{Color.DIM}not downloaded{Color.RESET}"
        print(f"  {Color.CYAN}{m['id']:<20}{Color.RESET} {m['display_name']}")
        print(f"  {'':20} Size: {m['size_gb']} GB | Profile: {m.get('recommended_profile', 'N/A')} | {status_str}")
        print()


def pull_model(model_id: str, dry_run: bool = False, force: bool = False):
    """Download a model from the registry.

    Args:
        model_id: The model ID from the registry.
        dry_run: If True, show what would be downloaded without downloading.
        force: If True, redownload even if the file already exists.
    """
    registry = load_models_registry()
    models = registry.get("models", [])

    # Find model by id
    model_entry = None
    for m in models:
        if m["id"] == model_id:
            model_entry = m
            break

    if not model_entry:
        print(f"[ERROR] Model '{model_id}' not found in registry.")
        available = ", ".join(m["id"] for m in models)
        print(f"  Available: {available}")
        print(f"  Use {Color.CYAN}kimari pull --list{Color.RESET} to see all models.")
        sys.exit(1)

    url = model_entry["url"]
    filename = model_entry["filename"]
    target_path = PROJECT_ROOT / model_entry["target_path"]
    size_gb = model_entry.get("size_gb", "?")
    display_name = model_entry.get("display_name", model_id)

    # Validate filename
    if not filename.endswith(".gguf"):
        print(f"[ERROR] Invalid model filename: {filename} (must end in .gguf)")
        sys.exit(1)

    # Dry run
    if dry_run:
        print(f"\n  {Color.YELLOW}[DRY RUN]{Color.RESET} Would download model: {Color.CYAN}{display_name}{Color.RESET}")
        print(f"  URL:         {url}")
        print(f"  Target:      {target_path}")
        print(f"  Size:        {size_gb} GB")
        print(f"  License:     {model_entry.get('license_note', 'N/A')}")
        if target_path.exists():
            print(f"  {Color.YELLOW}[NOTE]{Color.RESET} File already exists (use --force to redownload)")
        print()
        return

    # Check if already downloaded
    if target_path.exists():
        if not force:
            size_mb = target_path.stat().st_size / (1024 * 1024)
            print(f"\n  {Color.GREEN}Already downloaded:{Color.RESET} {target_path}")
            print(f"  Size: {size_mb:.1f} MB")
            print(f"  Use {Color.CYAN}--force{Color.RESET} to redownload.")
            return
        else:
            print(f"\n  {Color.YELLOW}[FORCE]{Color.RESET} Deleting existing file: {target_path}")
            target_path.unlink()

    # Create models/ directory if needed
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Download
    print(f"\n  {Color.BOLD}Downloading:{Color.RESET} {Color.CYAN}{display_name}{Color.RESET}")
    print(f"  URL:    {url}")
    print(f"  Target: {target_path}")
    print(f"  Size:   {size_gb} GB")
    print()

    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()

        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0
        start_time = time.time()

        with open(target_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Show progress
                    if total_size > 0:
                        pct = downloaded / total_size * 100
                        downloaded_mb = downloaded / (1024 * 1024)
                        total_mb = total_size / (1024 * 1024)
                        print(f"\r  Progress: {pct:5.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)",
                              end="", flush=True)
                    else:
                        # No content-length, show bytes downloaded
                        downloaded_mb = downloaded / (1024 * 1024)
                        print(f"\r  Downloaded: {downloaded_mb:.1f} MB", end="", flush=True)

        elapsed = time.time() - start_time
        downloaded_mb = downloaded / (1024 * 1024)
        print()  # New line after progress

        print(f"\n  {Color.GREEN}✓ Download complete{Color.RESET}")
        print(f"  Saved:     {target_path}")
        print(f"  Size:      {downloaded_mb:.1f} MB")
        if elapsed > 0:
            speed = downloaded_mb / elapsed
            print(f"  Speed:     {speed:.1f} MB/s")
        print(f"  Time:      {elapsed:.1f}s")

    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] Download failed (HTTP {e.response.status_code}): {e}")
        # Clean up partial download
        if target_path.exists():
            target_path.unlink()
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Connection failed. Check your internet connection.")
        if target_path.exists():
            target_path.unlink()
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n  {Color.YELLOW}[INTERRUPTED]{Color.RESET} Download cancelled.")
        if target_path.exists():
            target_path.unlink()
            print(f"  Partial download removed: {target_path}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        if target_path.exists():
            target_path.unlink()
        sys.exit(1)


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

    # start
    start_parser = subparsers.add_parser("start", help="Start Kimari server")
    start_parser.add_argument("--profile", "-p", required=True,
                              help="GPU profile (gtx1060, gtx1080, turbo)")
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

    # models
    subparsers.add_parser("models", help="List available GGUF models")

    # profiles
    subparsers.add_parser("profiles", help="List configured GPU profiles")

    # pull
    pull_parser = subparsers.add_parser("pull", help="Download a model from the registry")
    pull_parser.add_argument("name", nargs="?", default=None,
                             help="Model ID to download (e.g. test, recommended)")
    pull_parser.add_argument("--list", action="store_true", dest="list_models",
                             help="List available models in the registry")
    pull_parser.add_argument("--dry-run", action="store_true",
                             help="Show what would be downloaded without downloading")
    pull_parser.add_argument("--force", action="store_true",
                             help="Redownload even if file already exists")

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
        calculate_kimarifit(args.model, args.ctx, config)
    elif args.command == "models":
        list_models()
    elif args.command == "profiles":
        list_profiles(config)
    elif args.command == "pull":
        if getattr(args, "list_models", False):
            list_pull_models()
        elif args.name:
            pull_model(args.name, dry_run=args.dry_run, force=args.force)
        else:
            # No name and no --list: show help
            pull_parser.print_help()


if __name__ == "__main__":
    main()
