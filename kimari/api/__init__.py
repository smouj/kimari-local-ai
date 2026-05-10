"""
Kimari Experimental API — FastAPI-based REST API for Kimari Local AI.

**WARNING**: This module is EXPERIMENTAL and not yet stable.
Do NOT rely on it for production use.

Install with: ``pip install "kimari-local-ai[api]"``
Start with: ``kimari api --experimental``
"""

from __future__ import annotations

__all__ = ["create_app", "API_HOST_DEFAULT", "API_PORT_DEFAULT"]

API_HOST_DEFAULT = "127.0.0.1"
API_PORT_DEFAULT = 11436


def create_app():
    """Create and return the FastAPI application instance.

    Requires the ``api`` optional dependency group::

        pip install "kimari-local-ai[api]"

    Returns:
        A configured FastAPI application.

    Raises:
        ImportError: If ``fastapi`` is not installed.
    """
    try:
        import fastapi  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "Kimari API requires the 'api' optional dependency. Install it with: pip install 'kimari-local-ai[api]'"
        ) from exc

    from kimari.api.app import build_app

    return build_app()
