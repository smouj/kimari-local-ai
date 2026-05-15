"""
Local auth token management for Kimari.

Handles creating, reading, and deleting auth tokens stored in the
user state directory.  Tokens are generated with ``secrets.token_urlsafe``
and persisted alongside metadata (creation timestamp, preview, usage note).

These tokens are **prepared for future Kimari API / reverse proxy use**.
llama-server does not apply auth natively — the token file is a placeholder
until a reverse-proxy or application-layer auth mechanism is added.

Security guidelines
-------------------
- Never print the full token in logs; only the *preview* (first 8 chars) is safe.
- Token files are stored with ``0600`` permissions (owner read/write only).
- CLI commands should show preview by default; use ``--reveal`` to show full token.
- Tests must use ``tmp_path`` or ``monkeypatch`` — never write to the real user state directory during testing.
"""

import json
import os
import secrets
from datetime import datetime, timezone

from kimari.core.paths import get_auth_path

# ─── Token CRUD ───────────────────────────────────────────────────────────────

_AUTH_NOTE = "Prepared for future Kimari API / reverse proxy use. llama-server does not apply auth natively."


def create_token() -> dict:
    """Generate a new auth token and persist it to the user state directory.

    Returns:
        A dict with keys ``token``, ``created_at``, ``preview``, and ``note``.

    If an ``auth.json`` already exists it will be **overwritten** — call
    :func:`show_token` first if you want to check for an existing token.

    File permissions are set to 0600 (owner read/write only).
    """
    token = secrets.token_urlsafe(32)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    preview = f"{token[:8]}..."

    auth_data = {
        "token": token,
        "created_at": created_at,
        "preview": preview,
        "note": _AUTH_NOTE,
    }

    auth_path = get_auth_path()
    auth_path.parent.mkdir(parents=True, exist_ok=True)
    with open(auth_path, "w") as f:
        json.dump(auth_data, f, indent=2)
    # Lock down file permissions: owner read/write only (0600)
    os.chmod(auth_path, 0o600)

    return auth_data


def show_token() -> dict | None:
    """Read the existing auth token.

    Returns:
        The full auth dict if the file exists and is valid JSON,
        or ``None`` if no token file exists.

    Raises:
        No exceptions are propagated — corrupt or unreadable files also
        result in ``None`` (with the assumption that the caller will
        treat it as "no token configured").
    """
    auth_path = get_auth_path()
    if not auth_path.exists():
        return None
    try:
        with open(auth_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def delete_token() -> bool:
    """Delete the auth token file.

    Returns:
        ``True`` if the file was deleted, ``False`` if it did not exist.
    """
    auth_path = get_auth_path()
    if not auth_path.exists():
        return False
    auth_path.unlink()
    return True
