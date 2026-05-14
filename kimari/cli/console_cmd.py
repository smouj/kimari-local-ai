"""Interactive Kimari console command.

Small, dependency-free status panel and menu for common Kimari tasks.
No destructive action is performed without an explicit confirmation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

import kimari
from kimari.core.detection import detect_cuda, detect_cuda_version, detect_gpu
from kimari.core.state import read_state
from kimari.models.registry import scan_models_dir_for_gguf

MENU_ITEMS = [
    "Run doctor",
    "Setup/write config",
    "Download test model",
    "Start local API",
    "Stop local API",
    "Gateway setup",
    "Gateway start/open",
    "Generate integrations",
    "Exit",
]


def _gateway_status() -> dict[str, Any]:
    try:
        from kimari.gateway.dashboard_manager import status as dashboard_status

        return dashboard_status()
    except Exception as exc:  # noqa: BLE001 - status view must not crash the console
        return {"dashboard": "unknown", "running": False, "error": str(exc)}


def collect_console_status() -> dict[str, Any]:
    """Collect a safe, read-only Kimari status snapshot."""
    gpu = detect_gpu()
    state = read_state() or {}
    models = scan_models_dir_for_gguf()
    gateway = _gateway_status()
    return {
        "version": kimari.__version__,
        "gpu": gpu or {"name": None, "vram_mb": None, "driver": None},
        "cuda": {"available": detect_cuda(), "version": detect_cuda_version()},
        "test_model_available": any("tinyllama" in model.lower() for model in models),
        "server": {
            "status": state.get("status", "STOPPED"),
            "pid": state.get("pid"),
            "host": state.get("host"),
            "port": state.get("port"),
        },
        "gateway": gateway,
        "gate": "BLOCKED",
        "kimari_4b_released": False,
        "menu_items": MENU_ITEMS,
    }


def _print_status(status: dict[str, Any]) -> None:
    gpu = status["gpu"]
    gpu_name = gpu.get("name") or "not detected"
    vram_mb = gpu.get("vram_mb")
    vram = f"{vram_mb / 1024:.1f} GiB" if isinstance(vram_mb, int) else "unknown"
    cuda = status["cuda"]
    server = status["server"]
    gateway = status["gateway"]

    print(f"\nKimari Local AI v{status['version']}")
    print("=" * 40)
    print(f"GPU:        {gpu_name} ({vram})")
    print(f"CUDA:       {'available' if cuda['available'] else 'not detected'} {cuda.get('version') or ''}".rstrip())
    print(f"Test model: {'available' if status['test_model_available'] else 'not downloaded'}")
    print(
        f"Server:     {server.get('status', 'STOPPED')} ({server.get('host') or '127.0.0.1'}:{server.get('port') or 11435})"
    )
    print(
        f"Gateway:    {gateway.get('dashboard', gateway.get('status', 'unknown'))} ({gateway.get('url', 'http://127.0.0.1:3105')})"
    )
    print("Gate:       BLOCKED")
    print("Kimari-4B:  not released")


def _confirm(prompt: str) -> bool:
    answer = input(f"{prompt} [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def _run_kimari(args: list[str]) -> int:
    return subprocess.call([sys.executable, "-m", "kimari", *args])


def _menu() -> None:
    while True:
        _print_status(collect_console_status())
        print("\nChoose an action:")
        for idx, item in enumerate(MENU_ITEMS, start=1):
            print(f"[{idx}] {item}")
        choice = input("> ").strip()
        if choice in {"9", "q", "quit", "exit"}:
            print("Bye.")
            return
        if choice == "1":
            _run_kimari(["doctor"])
        elif choice == "2":
            if _confirm("Write detected Kimari config?"):
                _run_kimari(["setup", "--write", "--yes"])
        elif choice == "3":
            if _confirm("Download the small test model?"):
                _run_kimari(["pull", "test"])
        elif choice == "4":
            if _confirm("Start the local API on 127.0.0.1?"):
                _run_kimari(["start", "--daemon"])
        elif choice == "5":
            if _confirm("Stop the local API?"):
                _run_kimari(["stop"])
        elif choice == "6":
            if _confirm("Run Gateway setup (npm install, db setup, build)?"):
                _run_kimari(["gateway", "setup", "--yes"])
        elif choice == "7":
            _run_kimari(["gateway", "start", "--open"])
        elif choice == "8":
            _run_kimari(["integrations", "generate", "--all"])
        else:
            print("Unknown choice. Pick 1-9.")


def run_console(json_output: bool = False, no_interactive: bool = False) -> None:
    """Run the Kimari console."""
    status = collect_console_status()
    if json_output:
        print(json.dumps(status, indent=2))
        return
    if no_interactive:
        _print_status(status)
        return
    _menu()
