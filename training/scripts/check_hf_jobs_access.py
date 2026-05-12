#!/usr/bin/env python3
"""Check whether the authenticated Hugging Face account has Jobs access.

Queries the HF Hub API and the ``hf`` CLI to determine if the current
credentials can access Hugging Face Jobs.  This is a **read-only,
informational** tool — it never modifies anything on HF, never exposes
tokens or billing details, and always exits with code 0.

CRITICAL SAFETY RULES
---------------------
- Never print or return HF token values
- Never print or return billing/plan/subscription information
- Never save private data to disk
- If a 403 is detected: jobs_available=False, can_continue_to_smoke=False
- Sanitize any username/org output (show name only, never email or token)
- Graceful fallback when ``huggingface_hub`` is not installed

Usage
-----
    python training/scripts/check_hf_jobs_access.py
    python training/scripts/check_hf_jobs_access.py --json
    python training/scripts/check_hf_jobs_access.py --namespace my-org --json
    python training/scripts/check_hf_jobs_access.py --timeout 30
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SCRIPT_NAME = "training/scripts/check_hf_jobs_access.py"

# Patterns that must NEVER appear in output — used to sanitise any
# accidental leakage from stderr / API responses.
_REDACT_PATTERNS = [
    re.compile(r"(hf_[a-zA-Z0-9]{20,})", re.IGNORECASE),
    re.compile(
        r"(token[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{20,}[\"']?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(api_key[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{20,}[\"']?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(Authorization[\s]*[:=][\s]*[\"']?Bearer[\s]+[a-zA-Z0-9_\-\.]{20,}[\"']?)",
        re.IGNORECASE,
    ),
    # Billing / plan / subscription — redact even if accidentally present
    re.compile(
        r"(\"plan\"[\s]*:[\s]*\"[^\"]+\")",
        re.IGNORECASE,
    ),
    re.compile(
        r"(\"subscription\"[\s]*:[\s]*\"[^\"]+\")",
        re.IGNORECASE,
    ),
    re.compile(
        r"(\"billing\"[\s]*:[\s]*\"[^\"]+\")",
        re.IGNORECASE,
    ),
]


def _sanitize(text: str) -> str:
    """Redact sensitive patterns from *text*."""
    for pattern in _REDACT_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def _sanitize_name(name: str | None) -> str | None:
    """Return a sanitised display name — just the identifier, no email."""
    if name is None:
        return None
    # Strip anything that looks like an email
    name = re.sub(r"\s*<[^>]+>", "", name)
    name = name.strip()
    return name if name else None


# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------


def _check_huggingface_hub_installed() -> tuple[bool, str | None]:
    """Try to import ``huggingface_hub``.

    Returns
    -------
    (installed, version_or_none)
    """
    try:
        import huggingface_hub  # noqa: F401

        version = getattr(huggingface_hub, "__version__", None)
        return True, version
    except ImportError:
        return False, None


def _check_authentication() -> tuple[bool, str | None, list[str]]:
    """Use ``HfApi().whoami()`` to verify the token is valid.

    Returns
    -------
    (authenticated, sanitized_username, org_name_list)
    """
    try:
        from huggingface_hub import HfApi

        api = HfApi()
        info = api.whoami()

        if info is None:
            return False, None, []

        # Extract user name — could be a dict or str depending on version
        name: str | None = None
        orgs: list[str] = []

        if isinstance(info, dict):
            name = info.get("name") or info.get("fullname")
            # Orgs may be under "orgs" or similar
            raw_orgs = info.get("orgs", info.get("organizations", []))
            if isinstance(raw_orgs, list):
                for org in raw_orgs:
                    if isinstance(org, dict):
                        org_name = org.get("name") or org.get("fullname")
                    elif isinstance(org, str):
                        org_name = org
                    else:
                        org_name = None
                    if org_name:
                        orgs.append(_sanitize_name(org_name) or "unknown")
        elif isinstance(info, str):
            name = info

        sanitized = _sanitize_name(name)
        return True, sanitized, orgs

    except Exception as exc:
        # Auth failures typically raise HTTP 401 — treat as not authenticated
        err_msg = str(exc)
        if "401" in err_msg or "Unauthorized" in err_msg:
            return False, None, []
        # Other errors — we can't determine auth status for sure
        return False, None, []


def _check_jobs_via_subprocess(
    timeout: int,
    namespace: str | None = None,
) -> tuple[bool | None, str]:
    """Run ``huggingface-cli jobs ps`` (or ``hf jobs ps``) and interpret the result.

    Returns
    -------
    (jobs_available, status_description)

    ``jobs_available`` is ``True`` if the command succeeded (exit 0),
    ``False`` on 403 / forbidden, and ``None`` on timeout or
    indeterminate failure.
    """
    # Try the newer ``hf`` CLI first, then fall back to ``huggingface-cli``
    for cmd_prefix in (["hf"], ["huggingface-cli"]):
        cmd = cmd_prefix + ["jobs", "ps"]
        if namespace:
            cmd += ["--namespace", namespace]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError:
            # This CLI binary doesn't exist — try the next one
            continue
        except subprocess.TimeoutExpired:
            return None, "Timed out waiting for HF Jobs response"

        # Sanitise stderr before inspecting (defence-in-depth)
        stderr = _sanitize(result.stderr)
        stdout = _sanitize(result.stdout)

        if result.returncode == 0:
            return True, "HF Jobs accessible (command succeeded)"

        # Non-zero exit — check for 403 / forbidden
        combined = (stderr + " " + stdout).lower()
        if "403" in combined or "forbidden" in combined or "access denied" in combined:
            return False, "403 Forbidden — HF Jobs access not enabled for this account"

        # Other errors — likely not enrolled, or sub-command not recognised
        if "unrecognized" in combined or "unknown command" in combined or "not found" in combined:
            return False, f"Jobs sub-command not available (CLI returned exit {result.returncode})"

        return False, f"CLI exited with code {result.returncode}: {stderr[:200]}"

    # Neither CLI binary found
    return False, "Neither 'hf' nor 'huggingface-cli' CLI found on PATH"


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run_check(
    namespace: str | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    """Execute all checks and return the structured result dict.

    Parameters
    ----------
    namespace
        Optional HF org namespace to scope the Jobs access check.
    timeout
        Seconds before the CLI subprocess times out.

    Returns
    -------
    A dict matching the prescribed JSON schema (see module docstring).
    """
    # Default result skeleton
    result: dict[str, Any] = {
        "authenticated": False,
        "user": None,
        "orgs": [],
        "jobs_available": False,
        "status_code_or_error": "",
        "likely_reason": "",
        "recommended_action": "",
        "can_continue_to_smoke": False,
    }

    # Step 1 — Is huggingface_hub installed?
    hub_installed, hub_version = _check_huggingface_hub_installed()

    if not hub_installed:
        result.update(
            jobs_available=False,
            status_code_or_error="huggingface_hub not installed",
            likely_reason="The huggingface_hub package is required to authenticate and check Jobs access",
            recommended_action="Install huggingface_hub: pip install huggingface_hub",
            can_continue_to_smoke=False,
        )
        return result

    # Step 2 — Authentication check
    authenticated, username, orgs = _check_authentication()
    result["authenticated"] = authenticated
    result["user"] = username
    result["orgs"] = orgs

    if not authenticated:
        result.update(
            jobs_available=False,
            status_code_or_error="Not authenticated (401 or no token)",
            likely_reason="No valid HF token found — set HF_TOKEN or run 'hf auth login'",
            recommended_action="Authenticate with Hugging Face: set HF_TOKEN env var or run 'hf auth login'",
            can_continue_to_smoke=False,
        )
        return result

    # Step 3 — Check Jobs access via subprocess
    jobs_available, status_desc = _check_jobs_via_subprocess(timeout, namespace)
    result["jobs_available"] = jobs_available
    result["status_code_or_error"] = status_desc

    if jobs_available is True:
        result.update(
            likely_reason="Account has HF Jobs access",
            recommended_action="Proceed with HF Jobs smoke test",
            can_continue_to_smoke=True,
        )
    elif jobs_available is False:
        # Determine a more specific reason
        if "403" in status_desc:
            result.update(
                likely_reason="HF Jobs access not enabled for this account",
                recommended_action="Enable HF Jobs access or use a fallback runner",
                can_continue_to_smoke=False,
            )
        else:
            result.update(
                likely_reason="HF Jobs CLI unavailable or Jobs feature not enrolled",
                recommended_action="Ensure the 'hf' CLI supports 'jobs' sub-command; check HF Jobs availability for your account",
                can_continue_to_smoke=False,
            )
    else:
        # None — timeout or indeterminate
        result.update(
            jobs_available=None,
            likely_reason="Could not determine Jobs access (timeout or unexpected error)",
            recommended_action="Check network connectivity and try again with a longer --timeout",
            can_continue_to_smoke=False,
        )

    return result


# ---------------------------------------------------------------------------
# Human-readable output
# ---------------------------------------------------------------------------


def _print_human(result: dict[str, Any]) -> None:
    """Print a human-readable summary of the check result."""
    print("=" * 60)
    print("  Kimari — Hugging Face Jobs Access Check")
    print("=" * 60)
    print()

    # Auth status
    auth = result["authenticated"]
    auth_label = "YES" if auth else "NO"
    print(f"  Authenticated:    {auth_label}")

    if auth:
        user = result["user"] or "(unknown)"
        print(f"  User:             {user}")
        orgs = result["orgs"]
        if orgs:
            print(f"  Orgs:             {', '.join(orgs)}")

    print()

    # Jobs status
    jobs = result["jobs_available"]
    if jobs is True:
        label = "YES"
    elif jobs is False:
        label = "NO"
    else:
        label = "UNKNOWN (timeout)"
    print(f"  Jobs Available:   {label}")
    print(f"  Status:           {result['status_code_or_error']}")
    print()

    if result["likely_reason"]:
        print(f"  Likely Reason:    {result['likely_reason']}")
    if result["recommended_action"]:
        print(f"  Next Step:        {result['recommended_action']}")

    smoke = result["can_continue_to_smoke"]
    smoke_label = "YES" if smoke else "NO"
    print()
    print(f"  Can Continue to Smoke Test: {smoke_label}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point — always exits with code 0."""
    parser = argparse.ArgumentParser(
        description=(
            "Check whether the authenticated Hugging Face account has Jobs access. "
            "Read-only — never modifies anything. Never exposes tokens or billing details. "
            "Always exits with code 0 (informational tool)."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )
    parser.add_argument(
        "--namespace",
        type=str,
        default=None,
        help="Optional org namespace to scope the Jobs access check",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Timeout in seconds for CLI subprocess calls (default: 15)",
    )

    args = parser.parse_args()

    result = run_check(namespace=args.namespace, timeout=args.timeout)

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        _print_human(result)

    # Always exit 0 — this is an informational tool
    sys.exit(0)


if __name__ == "__main__":
    main()
