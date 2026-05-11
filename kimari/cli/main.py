"""
Kimari CLI — Command-line interface for Kimari Local AI.

Provides commands for server management, model downloads, diagnostics,
chat, benchmarking, and configuration management.
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("[ERROR] 'requests' is required. Install with: pip install -r cli/requirements.txt")
    sys.exit(1)

from kimari import __version__ as KIMARI_VERSION  # noqa: N812
from kimari.benchmarks.bench import run_benchmark
from kimari.benchmarks.kimarifit import calculate_kimarifit
from kimari.config.loader import (
    get_config_path,
    get_profile,
    load_config,
    migrate_config,
    show_config,
    validate_config,
)
from kimari.core.constants import (
    CONFIG_PATH,
    KIMARI_ASCII,
    LOG_FILE,
    PID_FILE,
    PROJECT_ROOT,
    STATE_DIR,
    STATE_FILE,
)
from kimari.core.detection import (
    detect_cuda,
    detect_cuda_version,
    detect_gpu,
    detect_llama_server,
    is_port_free,
    recommend_profile,
)
from kimari.core.errors import parse_log_errors, read_log_tail
from kimari.core.paths import get_user_models_dir
from kimari.core.state import (
    clear_state,
    ensure_state_dir,
    is_pid_alive,
    read_state,
    write_state,
)
from kimari.models.registry import (
    list_registry_models,
    pull_all_models,
    pull_model,
    scan_models_dir_for_gguf,
)
from kimari.profiles.manager import list_profiles
from kimari.utils.colors import Color, fail, info, ok, warn

# ─── Performance Commands ─────────────────────────────────────────────────────


def run_optimize(
    config: dict,
    profile_name: str | None = None,
    mode: str = "balanced",
    json_output: bool = False,
):
    """Analyze a profile and recommend optimal settings.

    Does NOT execute models or make network calls. Pure analysis.
    """
    from kimari.performance import (
        read_gguf_metadata,
        recommend_profile_settings,
        vram_safe_budget,
    )

    if not profile_name:
        profile_name = config.get("default_profile", "test")

    profile = get_profile(config, profile_name)
    model_size_gb = profile.get("estimated_model_size_gb", 1.0)
    vram_total_gb = profile.get("vram_total_gb", 6.0)

    # Try to read GGUF metadata for better accuracy
    model_path = _resolve_model_path(profile.get("model", ""))
    if model_path.exists():
        meta = read_gguf_metadata(str(model_path))
        if meta.get("parse_success") and meta.get("file_size_bytes") and meta["file_size_bytes"] > 0:
            model_size_gb = meta["file_size_bytes"] / (1024**3)

    # Get recommendations
    settings = recommend_profile_settings(vram_total_gb, model_size_gb, mode)

    # Build output
    result = {
        "profile": profile_name,
        "profile_name": profile.get("name", ""),
        "model": profile.get("model", ""),
        "model_size_gb": round(model_size_gb, 2),
        "vram_total_gb": vram_total_gb,
        "vram_safe_budget_gb": vram_safe_budget(vram_total_gb),
        "performance_mode": mode,
        "recommendations": {
            "ctx": settings["ctx"],
            "batch": settings["batch"],
            "ubatch": settings["ubatch"],
            "cache_type_k": settings["cache_type_k"],
            "cache_type_v": settings["cache_type_v"],
            "gpu_layers": settings["gpu_layers"],
            "flash_attn": settings["flash_attn"],
            "parallel": settings["parallel"],
        },
        "estimates": {
            "expected_vram_gb": settings["expected_vram_gb"],
            "expected_ram_gb": settings["expected_ram_gb"],
        },
        "confidence": settings["confidence"],
        "warnings": settings["warnings"],
    }

    if json_output:
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    print(f"\n{Color.BOLD}{Color.CYAN}Kimari Optimize{Color.RESET}")
    print(f"  Profile:  {Color.GREEN}{profile_name}{Color.RESET} ({profile.get('name', '')})")
    print(f"  Model:    {profile.get('model', '')}")
    print(f"  VRAM:     {vram_total_gb} GiB (safe: {vram_safe_budget(vram_total_gb):.2f} GiB)")
    print(f"  Mode:     {mode}")
    print(f"\n  {Color.BOLD}Recommendations:{Color.RESET}")
    rec = result["recommendations"]
    est = result["estimates"]
    print(f"    Context:       {rec['ctx']:,} tokens")
    print(f"    Batch:         {rec['batch']} / ubatch {rec['ubatch']}")
    print(f"    Cache K/V:     {rec['cache_type_k']} / {rec['cache_type_v']}")
    print(f"    GPU layers:    {rec['gpu_layers']}")
    print(f"    Flash Attn:    {'on' if rec['flash_attn'] else 'off'}")
    print(f"    Parallel:      {rec['parallel']}")
    print(f"\n  {Color.BOLD}Estimates:{Color.RESET}")
    print(f"    VRAM needed:   {est['expected_vram_gb']:.2f} GiB")
    print(f"    RAM needed:    {est['expected_ram_gb']:.2f} GiB")
    print(f"    Confidence:    {settings['confidence']}")

    if settings["warnings"]:
        print(f"\n  {Color.YELLOW}Warnings:{Color.RESET}")
        for w in settings["warnings"]:
            print(f"    ⚠ {w}")
    print()


def run_perf(
    config: dict,
    profile_name: str | None = None,
    dry_run: bool = True,
    json_output: bool = False,
    matrix: bool = False,
):
    """Performance diagnostic and tuning helper.

    In dry-run mode (default), shows a matrix of recommended settings.
    Does NOT execute benchmarks or start servers in dry-run mode.
    """
    from kimari.performance import recommend_profile_settings, vram_safe_budget

    if not profile_name:
        profile_name = config.get("default_profile", "test")

    profile = get_profile(config, profile_name)
    model_size_gb = profile.get("estimated_model_size_gb", 1.0)
    vram_total_gb = profile.get("vram_total_gb", 6.0)

    modes = ["safe", "balanced", "fast", "ide", "agent"] if matrix else [profile.get("performance_mode", "balanced")]

    results = []
    for mode in modes:
        settings = recommend_profile_settings(vram_total_gb, model_size_gb, mode)
        results.append({"mode": mode, **settings})

    output = {
        "profile": profile_name,
        "model": profile.get("model", ""),
        "model_size_gb": model_size_gb,
        "vram_total_gb": vram_total_gb,
        "vram_safe_budget_gb": vram_safe_budget(vram_total_gb),
        "dry_run": dry_run,
        "modes": results,
    }

    if json_output:
        print(json.dumps(output, indent=2))
        return

    # Human-readable output
    print(f"\n{Color.BOLD}{Color.CYAN}Kimari Perf{Color.RESET}")
    print(f"  Profile: {Color.GREEN}{profile_name}{Color.RESET} ({profile.get('name', '')})")
    print(f"  Model:   {profile.get('model', '')}")
    print(f"  VRAM:    {vram_total_gb} GiB (safe: {vram_safe_budget(vram_total_gb):.2f} GiB)")
    if dry_run:
        print(f"  {Color.YELLOW}[DRY RUN]{Color.RESET} Showing recommendations only\n")
    else:
        print(f"  {Color.DIM}(Requires running server for actual benchmarks){Color.RESET}\n")

    for r in results:
        mode = r["mode"]
        print(f"  {Color.BOLD}Mode: {mode}{Color.RESET}")
        print(
            f"    ctx={r['ctx']:,}  batch={r['batch']}/{r['ubatch']}  "
            f"kv={r['cache_type_k']}/{r['cache_type_v']}  "
            f"gpu={r['gpu_layers']}  flash={'on' if r['flash_attn'] else 'off'}  "
            f"parallel={r['parallel']}"
        )
        print(
            f"    vram≈{r['expected_vram_gb']:.2f} GiB  ram≈{r['expected_ram_gb']:.2f} GiB  "
            f"confidence={r['confidence']}"
        )
        if r["warnings"]:
            for w in r["warnings"]:
                print(f"    {Color.YELLOW}⚠ {w}{Color.RESET}")
        print()

    if not matrix:
        print(f"  {Color.DIM}Tip: Use --matrix to see all performance modes at once.{Color.RESET}")
        print(
            f"  {Color.DIM}Tip: Use kimari optimize --profile {profile_name} --mode <mode> for detailed analysis.{Color.RESET}"
        )


def resolve_model_path(model: str) -> Path:
    """Resolve a model path to an actual filesystem path.

    Checks in order:
    1. If *model* is an absolute path, use it directly.
    2. If *model* exists relative to the CWD, use it.
    3. If *model* exists in the user models directory, use it.
    4. If *model* exists in repo-root models/ (editable installs), use it.
    5. Otherwise, return the expected path in the user models dir
       (for error messages and first-download guidance).

    This function does **not** depend on ``PROJECT_ROOT`` as the sole
    source of truth and works correctly when Kimari is installed from
    a wheel (no repo root available).
    """
    p = Path(model)

    # 1. Absolute path — use as-is
    if p.is_absolute():
        return p

    # 2. CWD-relative — if the file exists, use it
    cwd_path = Path.cwd() / p
    if cwd_path.exists():
        return cwd_path.resolve()

    # 3. User models directory
    user_path = get_user_models_dir() / p.name
    if user_path.exists():
        return user_path

    # 4. Repo-root models/ (editable installs)
    repo_path = PROJECT_ROOT / model
    if repo_path.exists():
        return repo_path

    # 5. Default: return user models dir path (even if it doesn't exist yet)
    return user_path


def _resolve_model_path(model_rel_path: str) -> Path:
    """Backward-compatible alias for :func:`resolve_model_path`.

    Prefer calling ``resolve_model_path()`` directly in new code.
    """
    return resolve_model_path(model_rel_path)


def build_server_cmd(
    llama_server: str,
    profile: dict,
    model_override: str | None = None,
    host_override: str | None = None,
    port_override: int | None = None,
    ctx_override: int | None = None,
) -> list:
    """Build the llama-server command list for a given profile.

    Optional overrides replace the profile values when provided.
    New performance fields (flash_attn, parallel, mlock, no_mmap) are
    only added when the profile defines them.
    """
    model_path = _resolve_model_path(model_override if model_override else profile["model"])
    host = host_override if host_override else profile.get("host", "127.0.0.1")
    port = port_override if port_override else profile.get("port", 11435)
    ctx = ctx_override if ctx_override else profile.get("ctx", 8192)

    cmd = [
        llama_server,
        "-m",
        str(model_path),
        "--host",
        host,
        "--port",
        str(port),
        "-ngl",
        profile.get("gpu_layers", "all"),
        "-c",
        str(ctx),
        "-b",
        str(profile.get("batch", 256)),
        "-ub",
        str(profile.get("ubatch", 128)),
        "--cache-type-k",
        profile.get("cache_type_k", "f16"),
        "--cache-type-v",
        profile.get("cache_type_v", "f16"),
    ]

    if profile.get("threads"):
        cmd.extend(["-t", str(profile["threads"])])

    # New performance flags (only added when profile defines them)
    if profile.get("flash_attn") == "on":
        cmd.append("--flash-attn")

    if profile.get("parallel") and profile["parallel"] > 1:
        cmd.extend(["--parallel", str(profile["parallel"])])

    if profile.get("mlock") is True:
        cmd.append("--mlock")

    if profile.get("no_mmap") is True:
        cmd.append("--no-mmap")

    return cmd


def start_server(
    profile_name: str,
    config: dict,
    dry_run: bool = False,
    daemon: bool = False,
    model_override: str | None = None,
    host_override: str | None = None,
    port_override: int | None = None,
    ctx_override: int | None = None,
    strict_flags: bool = False,
):
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
        cmd = build_server_cmd(
            llama_server,
            profile,
            model_override=model_override,
            host_override=host_override,
            port_override=port_override,
            ctx_override=ctx_override,
        )
    else:
        model_path = _resolve_model_path(effective_model)
        cmd = [
            "llama-server",
            "-m",
            str(model_path),
            "--host",
            effective_host,
            "--port",
            str(effective_port),
            "-ngl",
            profile.get("gpu_layers", "all"),
            "-c",
            str(effective_ctx),
            "-b",
            str(profile.get("batch", 256)),
            "-ub",
            str(profile.get("ubatch", 128)),
            "--cache-type-k",
            profile.get("cache_type_k", "f16"),
            "--cache-type-v",
            profile.get("cache_type_v", "f16"),
        ]
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
        print("   Binary:  llama-server (not found — build or set LLAMA_SERVER)")
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
        model_path = _resolve_model_path(effective_model)
        if not model_path.exists():
            print(f"  {Color.YELLOW}[WARN]{Color.RESET} Model not found: {model_path}")
            print(f"  {Color.YELLOW}[WARN]{Color.RESET} Place a GGUF model before actually starting.\n")
        print(f"{Color.YELLOW}[DRY RUN]{Color.RESET} Would execute:\n")
        print(f"  {' '.join(cmd)}\n")
        print(f"  stdout → {LOG_FILE}")
        print(f"  state  → {STATE_FILE}")

        # Runtime flag validation
        if llama_server:
            from kimari.runtime.llama_flags import (
                detect_llama_server_help,
                filter_unsupported_flags,
                parse_supported_flags,
            )

            help_text = detect_llama_server_help(llama_server)
            if help_text:
                supported = parse_supported_flags(help_text)
                _, unsupported = filter_unsupported_flags(cmd, supported)
                if unsupported:
                    if strict_flags:
                        print(f"\n  {Color.RED}[ERROR]{Color.RESET} --strict-flags: unsupported flags detected:")
                        for flag in unsupported:
                            print(f"    ✗ {flag}")
                        print(f"\n  Your llama-server binary does not support: {', '.join(unsupported)}")
                        print("  Update llama-server or use a profile without these flags.")
                        raise SystemExit(1)
                    else:
                        print(f"\n  {Color.YELLOW}[WARN]{Color.RESET} llama-server may not support these flags:")
                        for flag in unsupported:
                            print(f"    ⚠ {flag}")
                        print("  Use --strict-flags to make this an error.")

        return

    # Real startup checks
    model_path = resolve_model_path(effective_model)
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        gguf_files = scan_models_dir_for_gguf()
        if len(gguf_files) == 1:
            print(
                f"  Found {Color.GREEN}{gguf_files[0]}{Color.RESET} — "
                f"use {Color.CYAN}--model {gguf_files[0]}{Color.RESET}"
            )
        elif len(gguf_files) > 1:
            print("  Available models in models/:")
            for f in gguf_files:
                print(f"    • {Color.GREEN}{f}{Color.RESET} — use {Color.CYAN}--model {f}{Color.RESET}")
        else:
            print(
                f"  Run {Color.CYAN}'kimari pull test'{Color.RESET} to download a test model, "
                f"or place any GGUF in models/"
            )
        write_state(
            "ERROR",
            error="MODEL_NOT_FOUND",
            profile=profile_name,
            model=effective_model,
        )
        raise SystemExit(1)

    if not llama_server:
        print("[ERROR] llama-server not found.")
        print("  Searched in order:")
        print("    1. $LLAMA_SERVER environment variable")
        print("    2. $KIMARI_LLAMA_SERVER environment variable")
        print("    3. llama-server in PATH")
        print("    4. llama_server in PATH")
        print(f"    5. {PROJECT_ROOT / 'llama-server'}")
        print(f"    6. {PROJECT_ROOT / 'bin' / 'llama-server'}")
        print(f"    7. {PROJECT_ROOT / 'deps' / 'llama.cpp' / 'build' / 'bin' / 'llama-server'}")
        print()
        print("  Build it first: bash scripts/linux/build-llamacpp-cuda.sh")
        print("  Or set LLAMA_SERVER=/path/to/llama-server")
        write_state(
            "ERROR",
            error="LLAMA_SERVER_NOT_FOUND",
            profile=profile_name,
            model=effective_model,
        )
        raise SystemExit(1)

    if not is_port_free(effective_host, effective_port):
        print(f"[ERROR] Port {effective_port} is already in use.")
        print("Stop the existing server first: kimari stop")
        write_state(
            "ERROR",
            error="PORT_BUSY",
            profile=profile_name,
            model=effective_model,
            host=effective_host,
            port=effective_port,
        )
        raise SystemExit(1)

    write_state(
        "STARTING",
        pid=None,
        profile=profile_name,
        model=effective_model,
        host=effective_host,
        port=effective_port,
    )

    try:
        with open(LOG_FILE, "w") as log_fh:
            process = subprocess.Popen(
                cmd,
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid if sys.platform != "win32" else None,
            )

            with open(PID_FILE, "w") as f:
                f.write(str(process.pid))

            print("   Waiting for server to start...", end=" ", flush=True)
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
                        write_state(
                            "READY",
                            pid=process.pid,
                            profile=profile_name,
                            model=effective_model,
                            host=effective_host,
                            port=effective_port,
                        )

                        if daemon:
                            info(f"Server running in background (PID: {process.pid})")
                            info("Logs: kimari logs")
                            info("Stop: kimari stop")
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
                    write_state(
                        "ERROR",
                        pid=process.pid,
                        profile=profile_name,
                        model=effective_model,
                        host=effective_host,
                        port=effective_port,
                        error="START_TIMEOUT",
                    )
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        stop_server()
                    return
                if process.poll() is not None:
                    error_info = parse_log_errors()
                    last_lines = read_log_tail(LOG_FILE, 10)
                    print(f"{Color.RED}✗ Failed{Color.RESET}")
                    if error_info:
                        print(f"\n   {Color.RED}Error detected:{Color.RESET} {error_info['pattern']}")
                        print(f"   {Color.YELLOW}Solution:{Color.RESET} {error_info['solution']}")
                        write_state(
                            "ERROR",
                            pid=process.pid,
                            profile=profile_name,
                            model=effective_model,
                            host=effective_host,
                            port=effective_port,
                            error=error_info["error_type"],
                        )
                    else:
                        print("\n   Last log lines:")
                        for line in last_lines:
                            print(f"   {Color.DIM}{line.rstrip()}{Color.RESET}")
                        write_state(
                            "ERROR",
                            pid=process.pid,
                            profile=profile_name,
                            model=effective_model,
                            host=effective_host,
                            port=effective_port,
                            error="UNKNOWN",
                        )
                    raise SystemExit(1)
                print(".", end="", flush=True)

    except FileNotFoundError:
        print(f"[ERROR] Could not execute: {llama_server}")
        write_state(
            "ERROR",
            error="LLAMA_SERVER_NOT_FOUND",
            profile=profile_name,
            model=effective_model,
        )
        raise SystemExit(1) from None


def stop_server():
    """Stop the running llama-server."""
    if not PID_FILE.exists():
        print("[WARN] No server PID file found. Server may not be running.")
        clear_state()
        return

    with open(PID_FILE) as f:
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

    profile_name = status_data.get("profile") or config.get("default_profile", "test")
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
            status_data["health"] = (
                resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"status": "ok"}
            )
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
        print("Start it first: kimari start")
        return

    tail_lines = read_log_tail(LOG_FILE, lines)
    for line in tail_lines:
        print(line.rstrip())

    if follow:
        print(f"\n{Color.DIM}--- Following log (Ctrl+C to stop) ---{Color.RESET}")
        try:
            with open(LOG_FILE, encoding="utf-8", errors="replace") as f:
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


def chat(message: str, config: dict, profile_name: str | None = None):
    """Send a chat message to the Kimari API."""
    if not profile_name:
        profile_name = config.get("default_profile", "test")
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
                print(
                    f"{Color.DIM}  Tokens: {usage.get('prompt_tokens', '?')} prompt + "
                    f"{usage.get('completion_tokens', '?')} completion = "
                    f"{usage.get('total_tokens', '?')} total{Color.RESET}"
                )
        else:
            print(f"[ERROR] API returned {resp.status_code}: {resp.text}")
    except requests.ConnectionError:
        print("[ERROR] Cannot connect to Kimari server.")
        print("Start it first: kimari start")
    except Exception as e:
        print(f"[ERROR] {e}")


def interactive_chat(config: dict, profile_name: str | None = None):
    """Run an interactive chat session."""
    if not profile_name:
        profile_name = config.get("default_profile", "test")
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
    if _platform.system() in ("Linux", "Windows"):
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
    default_profile = config.get("default_profile", "test")
    profile = config.get("profiles", {}).get(default_profile, {})
    model_path = _resolve_model_path(profile.get("model", "models/Kimari-4B-Q4_K_M.gguf"))
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        model_str = f"{model_path.name} ({size_mb:.1f} MB)"
        diagnostics["checks"].append({"name": "Model", "status": "ok", "value": model_str})
        if not json_output:
            ok(f"Model: {model_str}")
    else:
        diagnostics["checks"].append(
            {
                "name": "Model",
                "status": "warn",
                "value": f"{model_path.name} not found in models/",
            }
        )
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
        diagnostics["checks"].append(
            {
                "name": "Security",
                "status": "warn",
                "value": f"Host 0.0.0.0 exposes API to all interfaces (profile: {default_profile})",
            }
        )
        if not json_output:
            warn("Security: Host 0.0.0.0 exposes API to all interfaces")

    # Config
    diagnostics["checks"].append({"name": "Config", "status": "ok", "value": str(CONFIG_PATH)})
    if not json_output:
        ok(f"Config: {CONFIG_PATH}")

    # Config version
    config_version = config.get("config_version", 1)
    diagnostics["checks"].append({"name": "Config version", "status": "ok", "value": str(config_version)})
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
        diagnostics["checks"].append(
            {
                "name": "Recommended profile",
                "status": "ok",
                "value": f"{recommended} (current: {default_profile})",
            }
        )
        if not json_output:
            info(f"Recommended profile: {recommended} (current: {default_profile})")

    # Python
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    diagnostics["checks"].append({"name": "Python", "status": "ok", "value": py_version})
    if not json_output:
        ok(f"Python: {py_version}")

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
        print(f"  Run: {Color.CYAN}kimari start{Color.RESET}")


# ─── Info ────────────────────────────────────────────────────────────────────


def show_info(config: dict, json_output: bool = False):
    """Show Kimari installation information (version, paths, profiles, endpoint)."""
    state = read_state()
    llama_server = detect_llama_server()
    default_profile = config.get("default_profile", "test")
    profile = config.get("profiles", {}).get(default_profile, {})
    gpu = detect_gpu()

    info_data = {
        "kimari_version": KIMARI_VERSION,
        "project_root": str(PROJECT_ROOT),
        "config_path": str(CONFIG_PATH),
        "models_dir": str(get_user_models_dir()),
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
    print(f"  Models dir:       {get_user_models_dir()}")
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


# ─── Setup ──────────────────────────────────────────────────────────────────────


def run_setup(
    config: dict,
    dry_run: bool = False,
    write: bool = False,
    yes: bool = False,
    json_output: bool = False,
    profile_name: str | None = None,
    integration: str | None = None,
):
    """Guided setup and environment detection.

    Detects OS, Python, GPU, CUDA, ROCm, llama-server, and local models,
    then recommends a profile and next commands.

    With --write, persists the detected configuration to the user config dir.
    """
    import platform as _platform
    import shutil

    warnings: list[str] = []

    if dry_run:
        result = {
            "kimari_version": KIMARI_VERSION,
            "os": "(dry-run — not detected)",
            "python": "(dry-run — not detected)",
            "gpu": "(dry-run — not detected)",
            "cuda": "(dry-run — not detected)",
            "rocm": "(dry-run — not detected)",
            "llama_server": "(dry-run — not detected)",
            "local_models": "(dry-run — not scanned)",
            "recommended_profile": profile_name or config.get("default_profile", "test"),
            "recommended_integration": integration,
            "next_commands": ["(dry-run) kimari doctor", "(dry-run) kimari start --dry-run"],
            "warnings": ["Dry-run mode — no detection performed"],
        }
        if json_output:
            print(json.dumps(result, indent=2))
            return

        print(f"\n{Color.BOLD}{Color.CYAN}Kimari Setup{Color.RESET} (dry-run)\n")
        print("  No detection performed in dry-run mode.")
        print(f"  Run {Color.CYAN}kimari setup{Color.RESET} to detect your environment.\n")
        return

    # OS
    os_info = f"{_platform.system()} {_platform.release()}"
    if _platform.system() in ("Linux", "Windows"):
        os_info += f" ({_platform.machine()})"

    # Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info < (3, 10):  # noqa: UP036
        warnings.append(f"Python {python_version} is below minimum 3.10")

    # GPU
    gpu = detect_gpu()
    if gpu:
        gpu_info = f"{gpu['name']} ({gpu['vram_mb']} MB)"
    else:
        gpu_info = "No NVIDIA GPU detected"
        warnings.append("No NVIDIA GPU detected — CPU-only mode")

    # CUDA
    cuda_ver = detect_cuda_version()
    has_cuda = detect_cuda()
    if cuda_ver:
        cuda_info = f"CUDA {cuda_ver}"
    elif has_cuda:
        cuda_info = "Available (version unknown)"
    else:
        cuda_info = "Not detected"
        if not gpu:
            warnings.append("No CUDA detected — required for GPU acceleration")

    # ROCm (experimental)
    hipcc = shutil.which("hipcc")
    rocm_info = f"hipcc found at {hipcc} (experimental)" if hipcc else "Not detected"

    # llama-server
    llama_server = detect_llama_server()
    if llama_server:
        llama_server_info = llama_server
    else:
        llama_server_info = "Not found"
        warnings.append("llama-server not found — build it or set LLAMA_SERVER")

    # Local GGUF models
    models_dir = get_user_models_dir()
    local_models_list: list[str] = []
    if models_dir.exists():
        local_models_list = sorted(f.name for f in models_dir.glob("*.gguf"))
    # Also check repo-root models/
    repo_models = PROJECT_ROOT / "models"
    if repo_models.exists() and repo_models != models_dir:
        for f in repo_models.glob("*.gguf"):
            if f.name not in local_models_list:
                local_models_list.append(f.name)
        local_models_list.sort()
    if not local_models_list:
        warnings.append("No GGUF models found — run 'kimari pull test'")

    # Recommended profile
    recommended_profile = profile_name or recommend_profile(config, gpu)

    # Next commands
    next_commands: list[str] = []
    if not llama_server:
        next_commands.append("Build llama-server: bash scripts/linux/build-llamacpp-cuda.sh")
    if not local_models_list:
        next_commands.append("Download a model: kimari pull test")
    next_commands.append(f"Start server: kimari start --profile {recommended_profile}")

    # Integration-specific commands
    if integration == "openclaw":
        next_commands.append("Start for OpenClaw: kimari start --profile openclaw-local")
    elif integration == "hermes":
        next_commands.append("Start for Hermes: kimari start --profile hermes-local")
    elif integration == "continue":
        next_commands.append("Start for Continue.dev: kimari start --profile ide-local")

    next_commands.append("Run diagnostics: kimari doctor")

    result = {
        "kimari_version": KIMARI_VERSION,
        "os": os_info,
        "python": python_version,
        "gpu": gpu_info,
        "cuda": cuda_info,
        "rocm": rocm_info,
        "llama_server": llama_server_info,
        "local_models": local_models_list,
        "recommended_profile": recommended_profile,
        "recommended_integration": integration,
        "next_commands": next_commands,
        "warnings": warnings,
    }

    # ── Write-mode: persist detected configuration ─────────────────
    from kimari.core.paths import get_user_config_dir, get_user_config_path

    hardware_summary = {
        "os": os_info,
        "python": python_version,
        "gpu": gpu_info,
        "cuda": cuda_info,
        "rocm": rocm_info,
        "llama_server": llama_server_info,
    }
    paths_info = {
        "config_dir": str(get_user_config_dir()),
        "models_dir": str(get_user_models_dir()),
        "state_dir": str(STATE_DIR),
    }

    from kimari.setup.writer import (
        apply_setup_changes,
        build_setup_patch,
        confirm_setup_write,
        preview_setup_changes,
    )

    config_path = get_user_config_path()
    patch = build_setup_patch(
        recommended_profile=recommended_profile,
        integration=integration,
        hardware_summary=hardware_summary,
        paths_info=paths_info,
        config=config,
    )

    if write and patch["would_write"]:
        preview = preview_setup_changes(patch, config_path)
        confirmed = confirm_setup_write(preview, yes=yes)

        if confirmed:
            write_result = apply_setup_changes(patch, config_path)
            result["would_write"] = True
            result["written"] = write_result["written"]
            result["config_path"] = write_result["config_path"]
            result["backup_path"] = write_result.get("backup_path")
            result["requires_confirmation"] = preview["requires_confirmation"]
            result["confirmed"] = True
        else:
            result["would_write"] = True
            result["written"] = False
            result["config_path"] = str(config_path)
            result["backup_path"] = None
            result["requires_confirmation"] = preview["requires_confirmation"]
            result["confirmed"] = False
    else:
        result["would_write"] = patch["would_write"]
        result["written"] = False
        result["config_path"] = str(config_path)
        result["backup_path"] = None
        result["requires_confirmation"] = False
        result["confirmed"] = False

    if json_output:
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    print(f"\n{Color.BOLD}{Color.CYAN}Kimari Setup{Color.RESET}\n")
    print(f"  Version:     {KIMARI_VERSION}")
    print(f"  OS:          {os_info}")
    print(f"  Python:      {python_version}")
    print(f"  GPU:         {gpu_info}")
    print(f"  CUDA:        {cuda_info}")
    print(f"  ROCm:        {rocm_info}")
    print(
        f"  llama-server:{'  ' + llama_server_info if llama_server_info != 'Not found' else '  ' + Color.RED + llama_server_info + Color.RESET}"
    )

    print(f"\n  {Color.BOLD}Local Models:{Color.RESET}")
    if local_models_list:
        for m in local_models_list:
            print(f"    📦 {m}")
    else:
        print("    (none)")

    if integration:
        print(f"\n  {Color.BOLD}Integration:{Color.RESET} {integration}")

    print(f"\n  {Color.BOLD}Recommended Profile:{Color.RESET} {Color.GREEN}{recommended_profile}{Color.RESET}")

    # Show write-mode status
    if write:
        if result["written"]:
            print(f"\n  {Color.GREEN}✓ Configuration written{Color.RESET}")
            print(f"  Config:  {result['config_path']}")
            if result.get("backup_path"):
                print(f"  Backup:  {result['backup_path']}")
        elif result.get("confirmed") is False and result.get("would_write"):
            print(f"\n  {Color.YELLOW}⚠ Write cancelled — confirmation denied{Color.RESET}")
            print(f"  Use {Color.CYAN}--yes{Color.RESET} to skip the confirmation prompt.")
        elif result["would_write"]:
            print(f"\n  {Color.YELLOW}⚠ Would write but something went wrong{Color.RESET}")
        else:
            print(f"\n  {Color.DIM}No changes needed — configuration already matches.{Color.RESET}")
    elif patch["would_write"]:
        # Show preview of what --write would do
        preview = preview_setup_changes(patch, get_user_config_path())
        print(f"\n  {Color.BOLD}Changes that --write would make:{Color.RESET}")
        print(f"  Config:   {preview['config_path']}")
        if preview.get("backup_path"):
            print(f"  Backup:   {preview['backup_path']}")
        print(f"  Profile:  {preview['selected_profile']}")
        if preview.get("integration"):
            print(f"  Integration: {preview['integration']}")
        if preview.get("models_dir"):
            print(f"  Models:   {preview['models_dir']}")
        if preview.get("state_dir"):
            print(f"  State:    {preview['state_dir']}")
        for change in preview.get("changes", []):
            print(f"  • {change}")
        print(f"\n  {Color.DIM}Tip: Use --write to persist this configuration.{Color.RESET}")
        print(f"  {Color.DIM}     Use --write --yes to skip confirmation.{Color.RESET}")

    print(f"\n  {Color.BOLD}Next Steps:{Color.RESET}")
    for cmd in next_commands:
        print(f"    → {cmd}")

    if warnings:
        print(f"\n  {Color.YELLOW}Warnings:{Color.RESET}")
        for w in warnings:
            print(f"    ⚠ {w}")
    print()


# ─── Models ──────────────────────────────────────────────────────────────────


def list_models(
    json_output: bool = False,
    downloaded_only: bool = False,
    status_filter: str | None = None,
    verify: bool = False,
):
    """List available models (downloaded + registry)."""
    user_models = get_user_models_dir()
    repo_models = PROJECT_ROOT / "models"

    # Collect GGUF files from both directories
    gguf_files: list[Path] = []
    seen_names: set[str] = set()

    for models_dir in [user_models, repo_models]:
        if models_dir.exists():
            for f in sorted(models_dir.glob("*.gguf")):
                if f.name not in seen_names:
                    gguf_files.append(f)
                    seen_names.add(f.name)

    if json_output:
        result = []
        for f in sorted(gguf_files):
            size_mb = f.stat().st_size / (1024 * 1024)
            result.append(
                {
                    "name": f.name,
                    "path": str(f),
                    "size_mb": round(size_mb, 1),
                    "size_gb": round(size_mb / 1024, 2),
                }
            )
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
        size_str = f"{size_gb:.2f} GiB" if size_gb >= 1 else f"{size_mb:.1f} MB"
        print(f"  📦 {Color.GREEN}{f.name}{Color.RESET}  ({size_str})")

    # Also show registry models not yet downloaded
    registry_models = list_registry_models(json_output=True, downloaded_only=False, status_filter=status_filter)
    not_downloaded = [m for m in registry_models if not m.get("downloaded")]
    if not_downloaded:
        print(f"\n  {Color.DIM}Not yet downloaded (use 'kimari pull <name>'):{Color.RESET}")
        for m in not_downloaded:
            print(f"    • {Color.CYAN}{m['id']}{Color.RESET} — {m['display_name']} ({m['size_gb']} GB)")
    print()


def run_benchmark_plan(
    config: dict,
    profile_name: str | None = None,
    dry_run: bool = True,
    matrix: bool = False,
    json_output: bool = False,
):
    """Generate a benchmark plan for a profile.

    Does NOT execute benchmarks or start servers.
    In dry-run mode (default), shows estimated parameters only.
    """
    from kimari.performance.benchmark_plan import generate_benchmark_plan

    if not profile_name:
        profile_name = config.get("default_profile", "test")

    profile = get_profile(config, profile_name)
    model_size_gb = profile.get("estimated_model_size_gb", 0.7)
    vram_total_gb = profile.get("vram_total_gb", 6.0)

    plan = generate_benchmark_plan(profile_name, model_size_gb, vram_total_gb)

    if matrix:
        # Show all matrix cells in output
        pass  # Already included in plan

    if json_output:
        print(json.dumps(plan.to_dict(), indent=2))
        return

    # Human-readable output
    print(f"\n{Color.BOLD}{Color.CYAN}Kimari Benchmark{Color.RESET}")
    print(f"  Profile: {Color.GREEN}{profile_name}{Color.RESET} ({profile.get('name', '')})")
    print(f"  Model:   {profile.get('model', '')}")
    print(f"  VRAM:    {vram_total_gb} GiB")
    if dry_run:
        print(f"  {Color.YELLOW}[DRY RUN]{Color.RESET} Showing estimated plan only\n")
    else:
        print(f"  {Color.DIM}(Requires running server for actual benchmarks){Color.RESET}\n")

    rec = plan.recommended
    print(f"  {Color.BOLD}Recommended:{Color.RESET}")
    print(f"    Context:       {rec.get('recommended_ctx', 'N/A'):,} tokens")
    print(f"    Batch:         {rec.get('recommended_batch', 'N/A')} / ubatch {rec.get('recommended_ubatch', 'N/A')}")
    print(f"    Cache K/V:     {rec.get('recommended_cache_type_k', 'N/A')} / {rec.get('recommended_cache_type_v', 'N/A')}")
    print(f"    Est. VRAM:     {rec.get('estimated_vram_gb', 'N/A')} GiB")
    print(f"    Est. RAM:      {rec.get('estimated_ram_gb', 'N/A')} GiB")

    safe_cells = sum(1 for c in plan.matrix_cells if c.safe_for_profile)
    total_cells = len(plan.matrix_cells)
    print(f"\n  {Color.BOLD}Matrix:{Color.RESET} {safe_cells}/{total_cells} cells safe for {profile_name}")

    if plan.warnings:
        print(f"\n  {Color.YELLOW}Warnings:{Color.RESET}")
        for w in plan.warnings:
            print(f"    ⚠ {w}")

    print(f"\n  {Color.DIM}Tip: Use --matrix --json to see all parameter combinations.{Color.RESET}")
    print(f"  {Color.DIM}Tip: Use --measure (requires running server) for real benchmarks.{Color.RESET}")
    print()


def run_tune(
    config: dict,
    profile_name: str | None = None,
    dry_run: bool = True,
    apply: bool = False,
    json_output: bool = False,
):
    """Recommend optimal settings for a profile.

    Uses the performance estimator to recommend settings.
    Does NOT execute benchmarks or apply changes.
    """
    from kimari.performance.benchmark_plan import generate_tune_recommendation

    if apply:
        print("[ERROR] --apply is not yet available. Use --dry-run to see recommendations.")
        print("        Apply is planned, not available. Requires measured benchmarks and rollback safety first.")
        raise SystemExit(1)

    if not profile_name:
        profile_name = config.get("default_profile", "test")

    profile = get_profile(config, profile_name)
    model_size_gb = profile.get("estimated_model_size_gb", 0.7)
    vram_total_gb = profile.get("vram_total_gb", 6.0)

    result = generate_tune_recommendation(profile_name, model_size_gb, vram_total_gb)

    if json_output:
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    print(f"\n{Color.BOLD}{Color.CYAN}Kimari Tune{Color.RESET}")
    print(f"  Profile: {Color.GREEN}{profile_name}{Color.RESET} ({profile.get('name', '')})")
    print(f"  Model:   {profile.get('model', '')}")
    print(f"  VRAM:    {vram_total_gb} GiB")
    if dry_run:
        print(f"  {Color.YELLOW}[DRY RUN]{Color.RESET} Showing recommendations only\n")

    rec = result["recommended"]
    est = result["estimates"]
    print(f"  {Color.BOLD}Recommended Settings:{Color.RESET}")
    print(f"    Context:       {rec['ctx']:,} tokens")
    print(f"    Batch:         {rec['batch']} / ubatch {rec['ubatch']}")
    print(f"    Cache K/V:     {rec['cache_type_k']} / {rec['cache_type_v']}")
    print(f"    GPU layers:    {rec['gpu_layers']}")
    print(f"    Flash Attn:    {rec['flash_attn']}")
    print(f"\n  {Color.BOLD}Estimates:{Color.RESET}")
    print(f"    VRAM:          {est['vram_gb']} GiB")
    print(f"    RAM:           {est['ram_gb']} GiB")
    print(f"    Confidence:    {est['confidence']}")

    if result.get("warnings"):
        print(f"\n  {Color.YELLOW}Warnings:{Color.RESET}")
        for w in result["warnings"]:
            print(f"    ⚠ {w}")

    print(f"\n  {Color.DIM}{result['disclaimer']}{Color.RESET}")
    print(f"  {Color.DIM}--apply is blocked. Requires measured benchmarks and rollback safety first.{Color.RESET}")
    print()


# ─── Doctor Deep ──────────────────────────────────────────────────────────────


def run_doctor_deep(json_output: bool = False):
    """Run extended deep diagnostics.

    Checks Python, paths, config, models, llama-server, default profile,
    secret scanner, benchmark prompts, and preview gate status.
    No model execution, no downloads, no GPU required.
    """
    from kimari.doctor.deep import run_deep_checks

    results = run_deep_checks()

    if json_output:
        # Extract summary from last item
        summary = results[-1] if results and results[-1].get("name") == "Summary" else {}
        output = {
            "kimari_version": KIMARI_VERSION,
            "deep_check": True,
            "checks": results[:-1] if len(results) > 1 and results[-1].get("name") == "Summary" else results,
            "summary": summary.get("value", {}),
        }
        print(json.dumps(output, indent=2))
        return

    # Human-readable output
    print(f"\n{KIMARI_ASCII}")
    print(f"  {Color.BOLD}Deep Diagnostics{Color.RESET}\n")

    checks = results[:-1] if results and results[-1].get("name") == "Summary" else results
    for check in checks:
        status = check.get("status", "INFO")
        if status == "PASS":
            icon = f"{Color.GREEN}✓{Color.RESET}"
            status_str = f"{Color.GREEN}PASS{Color.RESET}"
        elif status == "WARN":
            icon = f"{Color.YELLOW}⚠{Color.RESET}"
            status_str = f"{Color.YELLOW}WARN{Color.RESET}"
        elif status == "FAIL":
            icon = f"{Color.RED}✗{Color.RESET}"
            status_str = f"{Color.RED}FAIL{Color.RESET}"
        else:
            icon = "●"
            status_str = status

        name = check.get("name", "Unknown")
        value = check.get("value", "")
        detail = check.get("detail", "")

        print(f"  {icon} {name}: {status_str} — {value}")
        if detail:
            print(f"    {Color.DIM}{detail}{Color.RESET}")

    # Summary
    summary = results[-1] if results and results[-1].get("name") == "Summary" else None
    if summary:
        sv = summary.get("value", {})
        pass_count = sv.get("pass_count", 0)
        warn_count = sv.get("warn_count", 0)
        fail_count = sv.get("fail_count", 0)
        total = sv.get("total", 0)

        print(f"\n  {Color.BOLD}Summary: {pass_count}/{total} PASS, {warn_count} WARN, {fail_count} FAIL{Color.RESET}")

        if fail_count > 0:
            print(f"  {Color.RED}Fix FAIL items before proceeding.{Color.RESET}")
            raise SystemExit(1)
        elif warn_count > 0:
            print(f"  {Color.YELLOW}Warnings present. Kimari may work with limitations.{Color.RESET}")
        else:
            print(f"  {Color.GREEN}All deep checks passed!{Color.RESET}")

    print()


# ─── Benchmark Measure ────────────────────────────────────────────────────────


def run_benchmark_measure(
    endpoint: str | None = None,
    model_name: str | None = None,
    yes: bool = False,
    output: str | None = None,
    json_output: bool = False,
):
    """Run measured benchmark against a running server.

    Requires --endpoint, --model, and --yes flags.
    Sends real HTTP requests to the server.
    Does NOT run in CI — use mocks for testing.
    """
    from datetime import datetime, timezone

    from kimari.performance.measured_benchmark import (
        measure_chat_completion,
        sanitize_benchmark_result,
    )

    # Validate required arguments
    if not endpoint:
        print("[ERROR] --endpoint is required for --measure.")
        print("  Example: kimari benchmark --measure --endpoint http://127.0.0.1:11435/v1 --model test --yes")
        raise SystemExit(1)

    if not model_name:
        print("[ERROR] --model is required for --measure.")
        print("  Example: kimari benchmark --measure --endpoint http://127.0.0.1:11435/v1 --model test --yes")
        raise SystemExit(1)

    if not yes:
        print("[ERROR] --yes is required for --measure to confirm execution.")
        print("  This sends real requests to the server endpoint.")
        print("  Example: kimari benchmark --measure --endpoint http://127.0.0.1:11435/v1 --model test --yes")
        raise SystemExit(1)

    # Load benchmark prompts
    from kimari.core.constants import PROJECT_ROOT

    prompts_path = PROJECT_ROOT / "benchmarks" / "prompts" / "local_benchmark_prompts.jsonl"
    prompts: list[dict] = []
    if prompts_path.exists():
        try:
            for line in prompts_path.read_text(encoding="utf-8").strip().splitlines():
                prompts.append(json.loads(line))
        except (json.JSONDecodeError, OSError):
            warn("Could not load benchmark prompts, using default prompt")

    if not prompts:
        prompts = [{"id": "default", "prompt": "Hello, respond with a single word.", "category": "greeting", "max_tokens": 32}]

    # Strip /v1 from endpoint if present for the base URL
    base_endpoint = endpoint.rstrip("/")
    if base_endpoint.endswith("/v1"):
        base_endpoint = base_endpoint[:-3]

    if not json_output:
        print(f"\n{Color.BOLD}{Color.CYAN}Kimari Benchmark — Measured{Color.RESET}")
        print(f"  Endpoint: {endpoint}")
        print(f"  Model:    {model_name}")
        print(f"  Prompts:  {len(prompts)}")
        print(f"  {Color.YELLOW}[EXPERIMENTAL]{Color.RESET} This sends real requests to the server.\n")

    # Run benchmarks
    results: list[dict] = []
    for i, p in enumerate(prompts):
        prompt_text = p.get("prompt", "Hello")
        max_tokens = p.get("max_tokens", 128)

        if not json_output:
            print(f"  [{i + 1}/{len(prompts)}] {p.get('id', '?')}: {prompt_text[:40]}...", end=" ", flush=True)

        result = measure_chat_completion(
            endpoint=base_endpoint,
            model=model_name,
            prompt=prompt_text,
            max_tokens=max_tokens,
            timeout=30.0,
        )

        # Add metadata
        result["prompt_id"] = p.get("id", f"prompt-{i}")
        result["category"] = p.get("category", "unknown")
        result["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Sanitize before storing
        sanitized = sanitize_benchmark_result(result)
        sanitized["prompt_id"] = result["prompt_id"]
        sanitized["category"] = result["category"]

        results.append(sanitized)

        if not json_output:
            tps = result.get("tokens_per_second")
            status = result.get("score_status", "unknown")
            if status == "measured" and tps is not None:
                print(f"{Color.GREEN}{tps:.2f} t/s{Color.RESET}")
            elif status == "error":
                err = result.get("error", "unknown error")
                print(f"{Color.RED}ERROR: {err}{Color.RESET}")
            else:
                print(f"{Color.YELLOW}{status}{Color.RESET}")

    # Build output
    measured_count = sum(1 for r in results if r.get("score_status") == "measured")
    error_count = sum(1 for r in results if r.get("score_status") == "error")

    benchmark_output = {
        "kimari_version": KIMARI_VERSION,
        "measurement_type": "measured",
        "measured": True,
        "endpoint": base_endpoint,
        "model": model_name,
        "total_prompts": len(prompts),
        "measured_count": measured_count,
        "error_count": error_count,
        "results": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Save to file if --output specified
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(benchmark_output, indent=2), encoding="utf-8")
        if not json_output:
            ok(f"Results saved to {output_path}")

    if json_output:
        print(json.dumps(benchmark_output, indent=2))
        return

    # Human-readable summary
    print(f"\n  {Color.BOLD}Results:{Color.RESET}")
    print(f"    Measured: {measured_count}/{len(prompts)}")
    if error_count:
        print(f"    Errors:   {Color.RED}{error_count}{Color.RESET}")

    if measured_count > 0:
        tps_values = [r["tokens_per_second"] for r in results if r.get("tokens_per_second") is not None]
        if tps_values:
            avg_tps = sum(tps_values) / len(tps_values)
            min_tps = min(tps_values)
            max_tps = max(tps_values)
            print(f"    Avg t/s:  {avg_tps:.2f}")
            print(f"    Min t/s:  {min_tps:.2f}")
            print(f"    Max t/s:  {max_tps:.2f}")

    if error_count > 0:
        print(f"\n  {Color.YELLOW}Some prompts failed. Check endpoint and model name.{Color.RESET}")
        print(f"  {Color.DIM}Errors are reported clearly — no stack traces.{Color.RESET}")
    elif measured_count == 0:
        print(f"\n  {Color.RED}No successful measurements. Check that the server is running.{Color.RESET}")

    print(f"\n  {Color.DIM}Do not treat this local measurement as a universal benchmark.{Color.RESET}")
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
    doctor_parser.add_argument(
        "--deep",
        action="store_true",
        help="Run extended deep diagnostics (Python, paths, config, models, scanner, prompts, gate)",
    )
    doctor_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output diagnostics as JSON",
    )

    # info
    info_parser = subparsers.add_parser("info", help="Show Kimari installation info")
    info_parser.add_argument("--json", action="store_true", dest="json_output", help="Output info as JSON")

    # start
    start_parser = subparsers.add_parser("start", help="Start Kimari server")
    start_parser.add_argument(
        "--profile",
        "-p",
        default=None,
        help="GPU profile (default: from config, currently 'test'). Options: gtx1060, gtx1080, turbo, test, docker)",
    )
    start_parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    start_parser.add_argument(
        "--daemon",
        action="store_true",
        help="Start server in background (exit after READY)",
    )
    start_parser.add_argument("--model", "-m", default=None, dest="model", help="Override profile model path")
    start_parser.add_argument("--host", default=None, dest="host", help="Override profile host (e.g. 0.0.0.0)")
    start_parser.add_argument("--port", type=int, default=None, dest="port", help="Override profile port")
    start_parser.add_argument(
        "--ctx",
        type=int,
        default=None,
        dest="ctx",
        help="Override profile context size (tokens)",
    )
    start_parser.add_argument(
        "--strict-flags",
        action="store_true",
        help="Fail if llama-server does not support flags required by the profile",
    )

    # stop
    subparsers.add_parser("stop", help="Stop Kimari server")

    # status
    status_parser = subparsers.add_parser("status", help="Check Kimari server status")
    status_parser.add_argument("--json", action="store_true", dest="json_output", help="Output status as JSON")

    # logs
    logs_parser = subparsers.add_parser("logs", help="Show server logs")
    logs_parser.add_argument(
        "--lines",
        "-n",
        type=int,
        default=50,
        help="Number of log lines to show (default: 50)",
    )
    logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow log output in real time")

    # chat
    chat_parser = subparsers.add_parser("chat", help="Send a chat message")
    chat_parser.add_argument("message", nargs="?", help="Message to send (omit for interactive)")

    # bench
    bench_parser = subparsers.add_parser("bench", help="Run benchmarks")
    bench_parser.add_argument("--profile", "-p", default=None, help="GPU profile to benchmark")
    bench_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output benchmark results as JSON only",
    )
    bench_parser.add_argument(
        "--output",
        "-o",
        default=None,
        dest="output",
        help="Save standardized benchmark results to a JSON file",
    )
    bench_parser.add_argument(
        "--vram",
        type=float,
        default=None,
        help="Override VRAM in GiB (for systems without GPU)",
    )

    # fit
    fit_parser = subparsers.add_parser("fit", help="Calculate KimariFit score")
    fit_parser.add_argument("--model", "-m", required=True, help="Path to GGUF model")
    fit_parser.add_argument("--ctx", "-c", type=int, default=8192, help="Context size")
    fit_parser.add_argument(
        "--vram",
        type=float,
        default=None,
        help="Override VRAM in GiB (for systems without GPU)",
    )

    # optimize
    optimize_parser = subparsers.add_parser("optimize", help="Recommend optimal settings for a profile")
    optimize_parser.add_argument(
        "--profile",
        "-p",
        default=None,
        help="GPU profile to optimize (default: from config)",
    )
    optimize_parser.add_argument(
        "--mode",
        "-m",
        default=None,
        help="Performance mode: safe, balanced, fast, ide, agent (default: from profile)",
    )
    optimize_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    # perf
    perf_parser = subparsers.add_parser("perf", help="Performance diagnostic and tuning helper")
    perf_parser.add_argument(
        "--profile",
        "-p",
        default=None,
        help="GPU profile to analyze (default: from config)",
    )
    perf_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show recommendations only (default: True)",
    )
    perf_parser.add_argument(
        "--matrix",
        action="store_true",
        help="Show all performance modes at once",
    )
    perf_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    # models
    models_parser = subparsers.add_parser("models", help="List available GGUF models")
    models_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    models_parser.add_argument("--downloaded", action="store_true", help="Only show downloaded models")
    models_parser.add_argument(
        "--status",
        default=None,
        dest="status_filter",
        help="Filter by status (recommended, test, experimental)",
    )
    models_parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify SHA256 hashes of downloaded models",
    )
    models_sub = models_parser.add_subparsers(dest="models_command", help="Model subcommands")

    models_hash_parser = models_sub.add_parser("hash", help="Compute SHA256 hash of a local model file")
    models_hash_parser.add_argument("path", help="Path to GGUF model file or model ID from registry")
    models_hash_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    models_verify_parser = models_sub.add_parser("verify", help="Verify SHA256 hash of a model against registry")
    models_verify_parser.add_argument("model", help="Model ID from registry or path to GGUF file")
    models_verify_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    models_pin_parser = models_sub.add_parser("pin-hash", help="Pin SHA256 hash of a model to user registry")
    models_pin_parser.add_argument("model_id", help="Model ID from registry")
    models_pin_parser.add_argument(
        "--write", action="store_true", help="Actually write to user registry (default: dry-run)"
    )
    models_pin_parser.add_argument(
        "--yes", action="store_true", help="Skip confirmation prompt (required in non-interactive mode)"
    )
    models_pin_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be pinned without writing (default behavior)"
    )
    models_pin_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    # profiles
    profiles_parser = subparsers.add_parser("profiles", help="List configured GPU profiles")
    profiles_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    # pull
    pull_parser = subparsers.add_parser("pull", help="Download a model from the registry")
    pull_parser.add_argument(
        "name",
        nargs="?",
        default=None,
        help="Model ID to download (e.g. test, recommended)",
    )
    pull_parser.add_argument(
        "--list",
        action="store_true",
        dest="list_models",
        help="List available models in the registry",
    )
    pull_parser.add_argument(
        "--all",
        action="store_true",
        dest="pull_all",
        help="Download all models from the registry",
    )
    pull_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without downloading",
    )
    pull_parser.add_argument("--force", action="store_true", help="Redownload even if file already exists")

    # config (subcommands)
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_sub = config_parser.add_subparsers(dest="config_command", help="Config subcommands")

    config_sub.add_parser("path", help="Print config file path")
    config_show_parser = config_sub.add_parser("show", help="Show full configuration")
    config_show_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    config_sub.add_parser("validate", help="Validate configuration against schema")

    config_migrate_parser = config_sub.add_parser("migrate", help="Migrate configuration to current version")
    config_migrate_parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")

    # setup
    setup_parser = subparsers.add_parser("setup", help="Guided setup and environment detection")
    setup_parser.add_argument("--dry-run", action="store_true", help="Preview without detecting")
    setup_parser.add_argument("--write", action="store_true", help="Persist detected configuration to user config dir")
    setup_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt (required in non-interactive mode)",
    )
    setup_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    setup_parser.add_argument("--profile", "-p", default=None, help="Profile to recommend")
    setup_parser.add_argument("--integration", default=None, help="Integration target (openclaw, hermes, continue)")

    # api (experimental)
    api_parser = subparsers.add_parser("api", help="Start experimental Kimari REST API")
    api_parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    api_parser.add_argument("--port", type=int, default=11436, help="API port (default: 11436)")
    api_parser.add_argument(
        "--experimental",
        action="store_true",
        help="Required to actually start the API (otherwise shows warning)",
    )
    api_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without starting the server",
    )
    api_parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    # token
    token_parser = subparsers.add_parser("token", help="Manage local auth tokens")
    token_sub = token_parser.add_subparsers(dest="token_command", help="Token subcommands")
    token_sub.add_parser("create", help="Create a new local auth token")
    token_sub.add_parser("show", help="Show the current auth token")
    token_sub.add_parser("delete", help="Delete the current auth token")

    # ─── Benchmark ──────────────────────────────────────────────────────────
    benchmark_parser = subparsers.add_parser("benchmark", help="Generate benchmark plan (dry-run by default)")
    benchmark_parser.add_argument("--profile", help="GPU profile to benchmark")
    benchmark_parser.add_argument("--dry-run", action="store_true", default=True, help="Show plan without executing (default)")
    benchmark_parser.add_argument("--measure", action="store_true", default=False, help="Run actual benchmark against a running server (experimental)")
    benchmark_parser.add_argument("--endpoint", default=None, help="Server endpoint for --measure (e.g. http://127.0.0.1:11435/v1)")
    benchmark_parser.add_argument("--model", default=None, help="Model name for --measure (e.g. test)")
    benchmark_parser.add_argument("--yes", action="store_true", help="Confirm --measure execution (required)")
    benchmark_parser.add_argument("--output", default=None, help="Save measured results to JSON file")
    benchmark_parser.add_argument("--matrix", action="store_true", help="Show full parameter matrix")
    benchmark_parser.add_argument("--json", action="store_true", help="JSON output")

    # ─── Tune ───────────────────────────────────────────────────────────────
    tune_parser = subparsers.add_parser("tune", help="Recommend optimal settings (dry-run by default)")
    tune_parser.add_argument("--profile", help="GPU profile to tune")
    tune_parser.add_argument("--dry-run", action="store_true", default=True, help="Show recommendations only (default)")
    tune_parser.add_argument("--apply", action="store_true", help="Apply recommended settings (BLOCKED)")
    tune_parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    # Ensure state directory exists
    ensure_state_dir()

    # Load config (needed for most commands)
    # Always try load_config() — it resolves user config, repo-root, and packaged defaults
    config = {}
    try:
        config = load_config()
    except SystemExit:
        config = {}

    if not args.command:
        parser.print_help()
        return

    if args.command == "doctor":
        if getattr(args, "deep", False):
            run_doctor_deep(json_output=getattr(args, "json_output", False))
        else:
            run_doctor(config, json_output=getattr(args, "json_output", False))
    elif args.command == "info":
        show_info(config, json_output=getattr(args, "json_output", False))
    elif args.command == "start":
        profile = args.profile or config.get("default_profile", "test")
        start_server(
            profile,
            config,
            dry_run=args.dry_run,
            daemon=args.daemon,
            model_override=args.model,
            host_override=args.host,
            port_override=args.port,
            ctx_override=args.ctx,
            strict_flags=args.strict_flags,
        )
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
        profile = args.profile or config.get("default_profile", "test")
        run_benchmark(
            profile,
            config,
            json_output=getattr(args, "json_output", False),
            output=getattr(args, "output", None),
            vram_override=getattr(args, "vram", None),
        )
    elif args.command == "fit":
        calculate_kimarifit(args.model, args.ctx, config, vram_override=getattr(args, "vram", None))
    elif args.command == "optimize":
        profile = args.profile or config.get("default_profile", "test")
        mode = args.mode or config.get("profiles", {}).get(profile, {}).get("performance_mode", "balanced")
        run_optimize(config, profile_name=profile, mode=mode, json_output=getattr(args, "json_output", False))
    elif args.command == "perf":
        profile = args.profile or config.get("default_profile", "test")
        run_perf(
            config,
            profile_name=profile,
            dry_run=getattr(args, "dry_run", True),
            json_output=getattr(args, "json_output", False),
            matrix=getattr(args, "matrix", False),
        )
    elif args.command == "models":
        models_cmd = getattr(args, "models_command", None)
        if models_cmd == "hash":
            from kimari.models.registry import compute_model_hash

            compute_model_hash(args.path, json_output=getattr(args, "json_output", False))
        elif models_cmd == "verify":
            from kimari.models.registry import verify_model_hash_v2

            verify_model_hash_v2(args.model, json_output=getattr(args, "json_output", False))
        elif models_cmd == "pin-hash":
            from kimari.models.registry import pin_model_hash

            # --dry-run explicitly forces write=False regardless of --write
            effective_write = getattr(args, "write", False) and not getattr(args, "dry_run", False)

            pin_model_hash(
                args.model_id,
                write=effective_write,
                json_output=getattr(args, "json_output", False),
                yes=getattr(args, "yes", False),
            )
        else:
            list_models(
                json_output=getattr(args, "json_output", False),
                downloaded_only=getattr(args, "downloaded", False),
                status_filter=getattr(args, "status_filter", None),
                verify=getattr(args, "verify", False),
            )
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
                print("  Changes:")
                for change in info["changes"]:
                    print(f"    • {change}")
                if info.get("backup_path"):
                    print(f"  Backup:       {info['backup_path']}")
    elif args.command == "setup":
        run_setup(
            config,
            dry_run=args.dry_run,
            write=getattr(args, "write", False),
            yes=getattr(args, "yes", False),
            json_output=getattr(args, "json_output", False),
            profile_name=getattr(args, "profile", None),
            integration=getattr(args, "integration", None),
        )
    elif args.command == "api":
        from kimari.api.server import run_api_command

        run_api_command(
            host=args.host,
            port=args.port,
            experimental=args.experimental,
            dry_run=args.dry_run,
            json_output=getattr(args, "json_output", False),
        )
    elif args.command == "token":
        from kimari.security.tokens import create_token, delete_token, show_token

        if args.token_command == "create":
            result = create_token()
            print(f"\n  {Color.GREEN}✓ Token created{Color.RESET}")
            print(f"  Token:   {result['token']}")
            print(f"  Preview: {result['preview']}")
            print(f"  Created: {result['created_at']}")
            print(
                f"\n  {Color.DIM}Note: This token is prepared for future Kimari API / reverse proxy use.{Color.RESET}"
            )
            print(f"  {Color.DIM}llama-server does not apply auth natively.{Color.RESET}\n")
        elif args.token_command == "show":
            result = show_token()
            if result:
                print(f"\n  Token:   {result['token']}")
                print(f"  Preview: {result['preview']}")
                print(f"  Created: {result['created_at']}")
                print(f"  Note:    {result.get('note', 'N/A')}\n")
            else:
                print("\n  No token found. Create one with: kimari token create\n")
        elif args.token_command == "delete":
            if delete_token():
                print(f"\n  {Color.GREEN}✓ Token deleted{Color.RESET}\n")
            else:
                print("\n  No token to delete.\n")
        else:
            token_parser.print_help()
    elif args.command == "benchmark":
        if args.measure:
            run_benchmark_measure(
                endpoint=args.endpoint,
                model_name=args.model,
                yes=args.yes,
                output=getattr(args, "output", None),
                json_output=args.json,
            )
        else:
            run_benchmark_plan(
                config,
                profile_name=args.profile,
                dry_run=True,
                matrix=args.matrix,
                json_output=args.json,
            )
    elif args.command == "tune":
        run_tune(
            config,
            profile_name=args.profile,
            dry_run=args.dry_run,
            apply=args.apply,
            json_output=args.json,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
