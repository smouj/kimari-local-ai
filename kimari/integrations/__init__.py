"""
Kimari Integrations -- Configuration generators for local AI tools.

Generates configuration snippets for Open WebUI, OpenClaw, Hermes,
and Continue.dev that connect to the local llama-server endpoint.
No tokens, no writing to production configs by default.
"""

from kimari.integrations.config_generator import (
    generate_continue_config,
    generate_hermes_config,
    generate_openclaw_config,
    generate_openwebui_config,
    sanitize_config,
    validate_local_base_url,
)

__all__ = [
    "generate_continue_config",
    "generate_hermes_config",
    "generate_openclaw_config",
    "generate_openwebui_config",
    "sanitize_config",
    "validate_local_base_url",
]
