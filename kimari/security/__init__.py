"""
Kimari security module — local auth token management.

Provides functions for creating, reading, and deleting local auth tokens
stored in the user state directory. These tokens are prepared for future
Kimari API / reverse proxy use. llama-server does not apply auth natively.

Security note: tokens are stored locally on disk. Never print tokens in
logs — only the explicit ``show_token()`` call (and the corresponding
``kimari token show`` CLI command) should display them.
"""

from kimari.security.tokens import create_token, delete_token, get_auth_path, show_token

__all__ = [
    "get_auth_path",
    "create_token",
    "show_token",
    "delete_token",
]
