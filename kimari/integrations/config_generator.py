"""
Kimari Integrations -- Configuration generators for local AI tools.

Generates configuration snippets for Open WebUI, OpenClaw, Hermes,
and Continue.dev that connect to the local llama-server endpoint.

Rules:
- Default base_url: http://127.0.0.1:11435/v1
- No tokens, API keys, or password fields in any generated config
- No writing files by default
- No touching production configs
- sanitize_config strips sensitive fields even if someone adds them
"""

from __future__ import annotations

import re
from copy import deepcopy

# Sensitive key patterns to strip
_SENSITIVE_PATTERNS = re.compile(
    r"(token|api_key|apikey|password|secret|bearer|authorization)",
    re.IGNORECASE,
)


def generate_openwebui_config(base_url: str = "http://127.0.0.1:11435/v1") -> dict:
    """Return an Open WebUI connection config dict.

    Includes: base_url, type="openai", model_alias (empty).
    No token/API key fields.

    Args:
        base_url: The llama-server OpenAI-compatible endpoint.

    Returns:
        Dict with Open WebUI connection configuration.
    """
    return {
        "base_url": base_url,
        "type": "openai",
        "model_alias": "",
        "note": "Configure in Open WebUI Settings > Connections > OpenAI API",
    }


def generate_openclaw_config(base_url: str = "http://127.0.0.1:11435/v1") -> dict:
    """Return an OpenClaw config dict.

    Includes: base_url, provider="kimari-local", model_default, context_window.
    No token fields.

    Args:
        base_url: The llama-server OpenAI-compatible endpoint.

    Returns:
        Dict with OpenClaw configuration.
    """
    return {
        "base_url": base_url,
        "provider": "kimari-local",
        "model_default": "",
        "context_window": 8192,
        "note": "Configure in OpenClaw config file (e.g. ~/.config/openclaw/config.json)",
    }


def generate_hermes_config(base_url: str = "http://127.0.0.1:11435/v1") -> dict:
    """Return a Hermes agent config dict.

    Includes: base_url, provider="kimari-local", default_model.
    No token fields.

    Args:
        base_url: The llama-server OpenAI-compatible endpoint.

    Returns:
        Dict with Hermes agent configuration.
    """
    return {
        "base_url": base_url,
        "provider": "kimari-local",
        "default_model": "",
    }


def generate_continue_config(base_url: str = "http://127.0.0.1:11435/v1") -> dict:
    """Return a Continue.dev config.json format dict.

    Includes: models array with one entry (title="Kimari Local",
    provider="openai", model, apiBase=base_url). No apiKey field.

    Args:
        base_url: The llama-server OpenAI-compatible endpoint.

    Returns:
        Dict with Continue.dev configuration.
    """
    return {
        "models": [
            {
                "title": "Kimari Local",
                "provider": "openai",
                "model": "",
                "apiBase": base_url,
            }
        ]
    }


def sanitize_config(config: dict) -> dict:
    """Remove any token/API key/password fields from a config dict.

    Checks for keys containing: token, api_key, apikey, password,
    secret, bearer, authorization. Returns a cleaned copy (does not
    mutate the original).

    Args:
        config: A configuration dictionary to sanitize.

    Returns:
        A new dict with sensitive fields removed.
    """
    cleaned = deepcopy(config)

    keys_to_remove = []
    for key in cleaned:
        if _SENSITIVE_PATTERNS.search(key):
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del cleaned[key]

    # Also sanitize nested dicts and lists
    for key, value in cleaned.items():
        if isinstance(value, dict):
            cleaned[key] = sanitize_config(value)
        elif isinstance(value, list):
            cleaned[key] = [sanitize_config(item) if isinstance(item, dict) else item for item in value]

    return cleaned


def validate_local_base_url(base_url: str) -> tuple[bool, str]:
    """Validate that a base_url is localhost/127.0.0.1.

    Accepts: 127.0.0.1, localhost, [::1].
    Rejects: 0.0.0.0, any public IP, any non-local hostname.

    Args:
        base_url: The URL to validate.

    Returns:
        Tuple of (is_local, message). If not local, returns
        (False, "WARNING: base_url is not localhost -- this may
        expose your endpoint").
    """
    # Extract hostname from URL
    hostname = base_url

    # Strip scheme
    if "://" in hostname:
        hostname = hostname.split("://", 1)[1]

    # Strip port and path
    if "/" in hostname:
        hostname = hostname.split("/", 1)[0]
    if ":" in hostname:
        hostname = hostname.rsplit(":", 1)[0]

    # Strip brackets from IPv6
    hostname = hostname.strip("[]")

    local_hosts = {"127.0.0.1", "localhost", "::1", "0:0:0:0:0:0:0:1"}

    if hostname.lower() in local_hosts:
        return (True, "base_url is localhost")

    # Reject 0.0.0.0 explicitly
    if hostname == "0.0.0.0":
        return (False, "WARNING: base_url is 0.0.0.0 -- this exposes your endpoint to all interfaces")

    # Any other hostname is not local
    return (False, "WARNING: base_url is not localhost -- this may expose your endpoint")
