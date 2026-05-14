"""Lifecycle manager for the Kimari Gateway Dashboard.

The dashboard is an isolated Next.js application under
``apps/gateway-dashboard``.  This module lets the Python CLI manage that app
without touching Kimari models, adapters, credentials, or user config.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import time
import urllib.error
import urllib.request
import webbrowser
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kimari.core.constants import PROJECT_ROOT

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3105
STATE_DIR = Path.home() / ".local" / "state" / "kimari" / "gateway-dashboard"
PID_FILE = STATE_DIR / "gateway-dashboard.pid"
LOG_FILE = STATE_DIR / "gateway-dashboard.log"
STATE_FILE = STATE_DIR / "gateway-dashboard.state.json"
GATE_STATE = "BLOCKED"


class DashboardError(RuntimeError):
    """Raised when dashboard lifecycle operations cannot proceed safely."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _dashboard_dir() -> Path:
    override = os.environ.get("KIMARI_GATEWAY_DASHBOARD_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return (PROJECT_ROOT / "apps" / "gateway-dashboard").resolve()


def _read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _process_matches_dashboard(pid: int) -> bool:
    """Best-effort check that a PID belongs to the dashboard/Next process."""
    if not _process_alive(pid):
        return False
    proc_cmdline = Path("/proc") / str(pid) / "cmdline"
    try:
        cmdline = proc_cmdline.read_text(errors="ignore").replace("\x00", " ")
    except OSError:
        # Non-Linux or inaccessible /proc: alive is the best portable signal.
        return True
    markers = ("kimari-gateway-dashboard", "apps/gateway-dashboard", "next start", "next-server", "npm start")
    return any(marker in cmdline for marker in markers)


def _write_state(data: dict[str, Any]) -> None:
    _ensure_state_dir()
    STATE_FILE.write_text(json.dumps({**data, "updated_at": _now()}, indent=2))


def _read_state() -> dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _require_node() -> None:
    missing = [cmd for cmd in ("node", "npm") if shutil.which(cmd) is None]
    if missing:
        raise DashboardError(f"Missing required command(s): {', '.join(missing)}. Install Node.js and npm first.")


def _require_dashboard_dir() -> Path:
    dashboard = _dashboard_dir()
    if not dashboard.exists() or not (dashboard / "package.json").exists():
        raise DashboardError(f"Gateway dashboard app not found at: {dashboard}")
    return dashboard


def _require_node_modules(dashboard: Path) -> None:
    if not (dashboard / "node_modules").exists():
        raise DashboardError("Dashboard dependencies are missing; run: kimari gateway setup")


def _is_localhost(host: str) -> bool:
    return host in {"127.0.0.1", "localhost", "::1"}


def _backend_reachable() -> bool:
    for url in ("http://127.0.0.1:11435/health", "http://127.0.0.1:11434/api/tags"):
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:  # noqa: S310 - localhost health probe only
                if 200 <= response.status < 500:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            continue
    return False


def _base_status(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> dict[str, Any]:
    pid = _read_pid()
    running = bool(pid and _process_matches_dashboard(pid))
    if pid and not running:
        with suppress(FileNotFoundError):
            PID_FILE.unlink()
        pid = None
    return {
        "dashboard": "running" if running else "stopped",
        "running": running,
        "pid": pid,
        "host": host,
        "port": port,
        "url": f"http://{host}:{port}",
        "backend_reachable": _backend_reachable(),
        "gate_state": GATE_STATE,
        "kimari_4b_released": False,
        "local_only": _is_localhost(host),
        "state_dir": str(STATE_DIR),
        "log_file": str(LOG_FILE),
    }


def setup() -> dict[str, Any]:
    """Install dashboard dependencies, initialize the DB, and build the app."""
    _require_node()
    dashboard = _require_dashboard_dir()
    _ensure_state_dir()
    commands = [["npm", "install"], ["npm", "run", "db:setup"], ["npm", "run", "build"]]
    with LOG_FILE.open("a", encoding="utf-8") as log:
        for command in commands:
            log.write(f"\n[{_now()}] $ {' '.join(command)}\n")
            result = subprocess.run(command, cwd=dashboard, stdout=log, stderr=subprocess.STDOUT, text=True, check=False)
            if result.returncode != 0:
                raise DashboardError(f"Dashboard setup failed during: {' '.join(command)}. See {LOG_FILE}")
    result = {"status": "ok", "dashboard_dir": str(dashboard), "log_file": str(LOG_FILE)}
    _write_state({"last_setup": result})
    return result


def start(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    open_browser: bool = False,
    dev: bool = False,
    dry_run: bool = False,
    setup: bool = False,
    allow_public_bind: bool = False,
) -> dict[str, Any]:
    """Start the Next.js dashboard process."""
    if not _is_localhost(host) and not allow_public_bind:
        raise DashboardError("Refusing non-local dashboard bind. Use --allow-public-bind to acknowledge the risk.")

    _require_node()
    dashboard = _require_dashboard_dir()

    if setup and not dry_run:
        globals()["setup"]()

    _require_node_modules(dashboard)
    _ensure_state_dir()

    script = "dev" if dev else "start"
    command = ["npm", "run", script]
    if dev or host != DEFAULT_HOST or port != DEFAULT_PORT:
        command.extend(["--", "-p", str(port), "-H", host])

    state = _base_status(host=host, port=port)
    if state["running"]:
        state.update({"status": "already_running"})
        return state

    if dry_run:
        result = {
            "status": "dry-run",
            "command": command,
            "cwd": str(dashboard),
            "host": host,
            "port": port,
            "url": f"http://{host}:{port}",
            "gate_state": GATE_STATE,
            "local_only": _is_localhost(host),
        }
        return result

    log = LOG_FILE.open("a", encoding="utf-8")
    log.write(f"\n[{_now()}] $ {' '.join(command)}\n")
    log.flush()
    process = subprocess.Popen(  # noqa: S603 - command is a fixed argv list, no shell
        command,
        cwd=dashboard,
        stdout=log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        text=True,
        env={**os.environ, "HOST": host, "PORT": str(port)},
    )
    PID_FILE.write_text(str(process.pid))
    result = _base_status(host=host, port=port)
    result.update({"status": "started", "pid": process.pid})
    _write_state({"last_start": result})
    if open_browser:
        webbrowser.open(result["url"])
    return result


def stop() -> dict[str, Any]:
    """Stop the dashboard process if it is running."""
    pid = _read_pid()
    if not pid or not _process_alive(pid):
        with suppress(FileNotFoundError):
            PID_FILE.unlink()
        return {"status": "stopped", "running": False, "pid": None}
    if not _process_matches_dashboard(pid):
        raise DashboardError(f"PID {pid} does not look like the Kimari Gateway Dashboard; refusing to kill it.")

    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not _process_alive(pid):
            break
        time.sleep(0.1)
    if _process_alive(pid):
        os.kill(pid, signal.SIGKILL)
    with suppress(FileNotFoundError):
        PID_FILE.unlink()
    result = {"status": "stopped", "running": False, "pid": pid}
    _write_state({"last_stop": result})
    return result


def restart(**kwargs: Any) -> dict[str, Any]:
    """Restart the dashboard with the provided start options."""
    stopped = stop()
    started = start(**kwargs)
    return {"status": "restarted", "stop": stopped, "start": started}


def status(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> dict[str, Any]:
    """Return dashboard, backend, and gate state."""
    state = _base_status(host=host, port=port)
    state["last_state"] = _read_state()
    return state


def logs(lines: int = 50) -> str:
    """Return the last N dashboard log lines."""
    if not LOG_FILE.exists():
        return ""
    content = LOG_FILE.read_text(errors="replace").splitlines()
    return "\n".join(content[-max(lines, 0) :])


def open_browser(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> dict[str, Any]:
    """Open the dashboard URL in the default browser."""
    url = f"http://{host}:{port}"
    webbrowser.open(url)
    return {"status": "opened", "url": url}


def reset(confirm: bool = False, clean_deps: bool = False) -> dict[str, Any]:
    """Clear dashboard runtime state/log/cache only; never touch models/adapters."""
    if not confirm:
        raise DashboardError("Reset requires confirmation. Re-run with --yes to clear dashboard runtime state.")
    dashboard = _require_dashboard_dir()
    removed: list[str] = []
    for path in (PID_FILE, LOG_FILE, STATE_FILE):
        if path.exists():
            path.unlink()
            removed.append(str(path))
    cache_paths = [dashboard / ".next" / "cache", dashboard / "node_modules" / ".cache"]
    if clean_deps:
        cache_paths.extend([dashboard / ".next"])
    for path in cache_paths:
        if path.exists():
            shutil.rmtree(path)
            removed.append(str(path))
    return {"status": "reset", "removed": removed, "models_touched": False, "adapters_touched": False}
