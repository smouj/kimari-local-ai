"""
Gateway state reporting for Kimari.

Provides the ``gateway_status()`` function that returns the current state
of the planned gateway — including whether a server exists, the planned
host/port, available profiles, and llama-server detection results.

This is a **dry-run** module: no real HTTP server is started.
"""

from __future__ import annotations

from kimari.core.constants import CONFIG_PATH
from kimari.core.detection import detect_llama_server


def gateway_status(config: dict | None = None) -> dict:
    """Return the current gateway state as a dictionary.

    This function performs no network operations and starts no server.
    It reports the *planned* state of the gateway module.

    Args:
        config: Optional configuration dict (as loaded by
            ``kimari.config.loader.load_config()``).  If ``None``,
            sensible defaults are used.

    Returns:
        A dict with the following keys:

        - **gateway_available** (bool): Always ``False`` — the gateway
          server is not yet implemented.
        - **planned_host** (str): ``"127.0.0.1"``
        - **planned_port** (int): ``11436``
        - **status** (str): ``"planned"``
        - **message** (str): Human-readable status message.
        - **dependencies** (list): Required packages for the future
          gateway (``["fastapi", "uvicorn"]``).
        - **config_path** (str): Path to the active kimari config file.
        - **profiles_available** (list): Profile names from config, or
          an empty list if no config is provided.
        - **llama_server_available** (bool): Whether llama-server was
          detected on the system.
        - **model_loaded** (str | None): The model from the default
          profile if a config is provided, otherwise ``None``.
    """
    # Determine profiles from config
    profiles_available: list[str] = []
    model_loaded: str | None = None

    if config is not None:
        profiles_dict = config.get("profiles", {})
        profiles_available = list(profiles_dict.keys())

        # Resolve the default profile's model
        default_profile_name = config.get("default_profile")
        if default_profile_name and default_profile_name in profiles_dict:
            model_loaded = profiles_dict[default_profile_name].get("model")

    # Detect llama-server binary
    llama_server_path = detect_llama_server()
    llama_server_available = llama_server_path is not None

    return {
        "gateway_available": False,
        "planned_host": "127.0.0.1",
        "planned_port": 11436,
        "status": "planned",
        "message": "Gateway server is planned for a future release",
        "dependencies": ["fastapi", "uvicorn"],
        "config_path": str(CONFIG_PATH),
        "profiles_available": profiles_available,
        "llama_server_available": llama_server_available,
        "model_loaded": model_loaded,
    }
