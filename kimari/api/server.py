"""
Kimari Experimental API — Server startup logic.

Handles the ``kimari api`` command: validates the experimental flag,
checks for optional dependencies, and starts uvicorn if appropriate.

Rules:
- Without ``--experimental``, the server MUST NOT start.
- ``--dry-run`` shows what would happen without importing uvicorn.
- ``--json`` outputs structured startup info.
- No real server is started in CI.
"""

from __future__ import annotations

import json
from typing import Any


def run_api_command(
    host: str = "127.0.0.1",
    port: int = 11436,
    experimental: bool = False,
    dry_run: bool = False,
    json_output: bool = False,
) -> None:
    """Handle the ``kimari api`` command.

    Parameters
    ----------
    host : str
        Bind address. Default ``127.0.0.1``.
    port : int
        Port number. Default ``11436``.
    experimental : bool
        Must be True to actually start the server.
    dry_run : bool
        If True, show what would happen without starting.
    json_output : bool
        If True, output structured JSON.
    """
    info: dict[str, Any] = {
        "command": "kimari api",
        "host": host,
        "port": port,
        "experimental": experimental,
        "dry_run": dry_run,
        "version": _get_version(),
    }

    # Security: warn if binding to non-localhost
    if host not in ("127.0.0.1", "localhost"):
        info["security_warning"] = (
            f"Binding to {host} exposes the API to network access. "
            "A Bearer token will be required for non-localhost access."
        )

    # Without --experimental, do not start
    if not experimental and not dry_run:
        msg = (
            "⚠  The Kimari API is EXPERIMENTAL and not yet stable.\n"
            "   To start it, you must explicitly opt in:\n\n"
            "     kimari api --experimental\n\n"
            "   Or with custom host/port:\n\n"
            "     kimari api --host 127.0.0.1 --port 11436 --experimental\n\n"
            "   For a dry run (no server started):\n\n"
            "     kimari api --dry-run\n"
        )
        if json_output:
            info["error"] = "experimental_flag_required"
            info["message"] = "The Kimari API is experimental. Use --experimental to opt in."
            print(json.dumps(info, indent=2))
        else:
            print(msg)
        return

    # Dry run: show what would happen
    if dry_run:
        info["would_start"] = experimental
        info["app_module"] = "kimari.api.app:build_app"
        info["dependencies_available"] = _check_api_deps()
        if not _check_api_deps():
            info["install_hint"] = 'pip install "kimari-local-ai[api]"'

        if json_output:
            print(json.dumps(info, indent=2))
        else:
            print("\n⚡ Kimari API — Dry Run\n")
            print(f"  Host:          {host}")
            print(f"  Port:          {port}")
            print(f"  Experimental:  {experimental}")
            print(f"  FastAPI:       {'available' if _check_api_deps() else 'NOT INSTALLED'}")
            if not _check_api_deps():
                print('\n  Install with:  pip install "kimari-local-ai[api]"')
            if experimental and _check_api_deps():
                print(f"\n  Would start:   uvicorn kimari.api.app:build_app --host {host} --port {port}")
            print()
        return

    # Real start: check dependencies
    if not _check_api_deps():
        msg = (
            "[ERROR] FastAPI is not installed.\n"
            "  Install the API optional dependency:\n\n"
            '    pip install "kimari-local-ai[api]"\n'
        )
        if json_output:
            info["error"] = "fastapi_not_installed"
            info["install_hint"] = 'pip install "kimari-local-ai[api]"'
            print(json.dumps(info, indent=2))
        else:
            print(msg)
        return

    # Actually start the server
    if json_output:
        info["status"] = "starting"
        # Print info before starting (uvicorn will take over stdout)
        print(json.dumps(info, indent=2))

    _start_uvicorn(host, port)


def _get_version() -> str:
    """Get the current Kimari version."""
    from kimari import __version__

    return __version__


def _check_api_deps() -> bool:
    """Check if FastAPI and uvicorn are importable."""
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401

        return True
    except ImportError:
        return False


def _start_uvicorn(host: str, port: int) -> None:
    """Start the uvicorn server with the Kimari FastAPI app."""
    import uvicorn

    uvicorn.run(
        "kimari.api.app:build_app",
        host=host,
        port=port,
        factory=True,
        log_level="info",
    )
