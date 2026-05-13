#!/usr/bin/env python3
"""Check Hugging Face Jobs access gate.

Verifies that the current HF token can submit jobs.
Does NOT submit any job. Only checks access.

Usage:
    python training/scripts/check_hf_jobs_access.py
    python training/scripts/check_hf_jobs_access.py --json
"""

from __future__ import annotations

import json
import sys


def sanitize_error(message: object) -> str:
    """Redact token-like values from error messages."""
    text = str(message)
    for marker in ("hf_", "sk-"):
        if marker in text:
            text = text.split(marker)[0] + marker + "[REDACTED]"
    return text


def check_access() -> dict:
    """Check HF Jobs access without submitting any job."""
    checks = {}

    # 1. huggingface_hub installed
    try:
        import huggingface_hub

        checks["huggingface_hub_installed"] = True
        checks["huggingface_hub_version"] = huggingface_hub.__version__
    except ImportError:
        checks["huggingface_hub_installed"] = False
        checks["huggingface_hub_version"] = None
        checks["can_continue_to_smoke"] = False
        checks["reason"] = "huggingface_hub not installed"
        return checks

    # 2. Authenticated
    try:
        from huggingface_hub import HfApi

        api = HfApi()
        whoami = api.whoami()
        checks["authenticated"] = True
        checks["username"] = whoami.get("name", "unknown")
        checks["orgs"] = [o["name"] for o in whoami.get("orgs", [])]
    except Exception as e:
        checks["authenticated"] = False
        checks["username"] = None
        checks["can_continue_to_smoke"] = False
        checks["reason"] = f"Auth failed: {sanitize_error(e)}"
        return checks

    # 3. Jobs access (try to list hardware without submitting)
    try:
        from huggingface_hub import HfApi

        api = HfApi()
        # List hardware flavors — this is read-only and doesn't submit jobs
        api.list_spaces()  # Basic read test
        checks["api_read_access"] = True
    except Exception as e:
        checks["api_read_access"] = False
        checks["reason"] = f"API read failed: {sanitize_error(e)}"

    # 4. Try to check if jobs endpoint is accessible
    try:
        import urllib.request

        req = urllib.request.Request(
            "https://huggingface.co/api/jobs",
            headers={"User-Agent": "kimari-check/0.1"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                checks["jobs_endpoint_accessible"] = resp.status == 200
        except urllib.error.HTTPError as e:
            # 403 means we can reach it but not authorized for jobs listing
            # But if we can reach it at all, the endpoint exists
            checks["jobs_endpoint_accessible"] = e.code in (200, 403, 404)
    except Exception as e:
        checks["jobs_endpoint_accessible"] = False
        checks["jobs_endpoint_error"] = sanitize_error(e)

    # 5. Try `hf jobs hardware` as a simple read-only test
    try:
        import subprocess

        result = subprocess.run(
            ["hf", "jobs", "hardware"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        checks["hf_jobs_hardware_works"] = result.returncode == 0
        if result.returncode == 0:
            checks["hardware_count"] = len([line for line in result.stdout.strip().split("\n") if line.strip()]) - 1
        else:
            checks["hardware_error"] = result.stderr[:200]
    except Exception as e:
        checks["hf_jobs_hardware_works"] = False
        checks["hardware_error"] = sanitize_error(e)

    # Decision
    can_continue = (
        checks.get("huggingface_hub_installed", False)
        and checks.get("authenticated", False)
        and checks.get("hf_jobs_hardware_works", False)
    )
    checks["can_continue_to_smoke"] = can_continue
    if not can_continue:
        reasons = []
        if not checks.get("huggingface_hub_installed"):
            reasons.append("huggingface_hub not installed")
        if not checks.get("authenticated"):
            reasons.append("not authenticated")
        if not checks.get("hf_jobs_hardware_works"):
            reasons.append("hf jobs hardware command failed")
        checks["reason"] = "; ".join(reasons)

    return checks


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Check HF Jobs access")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = check_access()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("HF Jobs Access Check")
        print("=" * 50)
        for key, value in result.items():
            if isinstance(value, bool):
                status = "✅" if value else "❌"
                print(f"  {status} {key}: {value}")
            else:
                print(f"  {key}: {value}")
        print("=" * 50)
        if result.get("can_continue_to_smoke"):
            print("RESULT: Access OK — can proceed to smoke test")
        else:
            print(f"RESULT: Access DENIED — {result.get('reason', 'unknown')}")

    sys.exit(0 if result.get("can_continue_to_smoke") else 1)


if __name__ == "__main__":
    main()
