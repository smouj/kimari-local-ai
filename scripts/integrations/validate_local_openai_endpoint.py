#!/usr/bin/env python3
"""Validate a local OpenAI-compatible endpoint.

Tests /health, /v1/models, and /v1/chat/completions.
No tokens, no private data, no long prompts.

Usage:
    python scripts/integrations/validate_local_openai_endpoint.py
    python scripts/integrations/validate_local_openai_endpoint.py --base-url http://127.0.0.1:11435/v1
    python scripts/integrations/validate_local_openai_endpoint.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def validate_endpoint(base_url: str = "http://127.0.0.1:11435/v1") -> dict:
    """Validate a local OpenAI-compatible endpoint.

    Returns a dict with health, models, chat_completions, and overall status.
    """
    # Strip /v1 suffix for health check
    health_url = base_url.rstrip("/").removesuffix("/v1")
    if not health_url.startswith("http"):
        health_url = f"http://{health_url}"
    health_url = f"{health_url}/health"

    models_url = f"{base_url.rstrip('/')}/models"
    chat_url = f"{base_url.rstrip('/')}/chat/completions"

    results: dict = {
        "base_url": base_url,
        "health": None,
        "models": None,
        "chat_completions": None,
        "overall": False,
    }

    # 1. Health check
    try:
        req = urllib.request.Request(health_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            health_data = resp.read().decode("utf-8", errors="replace")
            results["health"] = {"status": "ok", "response": health_data[:200]}
    except urllib.error.URLError as e:
        results["health"] = {"status": "error", "error": str(e)[:200]}
    except Exception as e:  # noqa: BLE001
        results["health"] = {"status": "error", "error": str(e)[:200]}

    # 2. Models check
    try:
        req = urllib.request.Request(models_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            models_data = resp.read().decode("utf-8", errors="replace")
            results["models"] = {"status": "ok", "response_length": len(models_data)}
    except urllib.error.URLError as e:
        results["models"] = {"status": "error", "error": str(e)[:200]}
    except Exception as e:  # noqa: BLE001
        results["models"] = {"status": "error", "error": str(e)[:200]}

    # 3. Chat completions (short prompt)
    chat_body = json.dumps(
        {
            "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10,
        }
    ).encode("utf-8")
    try:
        req = urllib.request.Request(
            chat_url,
            data=chat_body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            chat_data = resp.read().decode("utf-8", errors="replace")
            results["chat_completions"] = {"status": "ok", "response_length": len(chat_data)}
    except urllib.error.URLError as e:
        results["chat_completions"] = {"status": "error", "error": str(e)[:200]}
    except Exception as e:  # noqa: BLE001
        results["chat_completions"] = {"status": "error", "error": str(e)[:200]}

    # Overall status
    results["overall"] = (
        results["health"].get("status") == "ok"
        and results["models"].get("status") == "ok"
        and results["chat_completions"].get("status") == "ok"
    )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a local OpenAI-compatible endpoint. Tests /health, /v1/models, and /v1/chat/completions."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:11435/v1",
        help="Base URL to validate (default: http://127.0.0.1:11435/v1)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = validate_endpoint(args.base_url)

    if args.json:
        print(json.dumps(results, indent=2))
        sys.exit(0 if results["overall"] else 1)

    # Human-readable output
    print("\nKimari Local Endpoint Validation")
    print(f"  Base URL: {args.base_url}")
    for check in ["health", "models", "chat_completions"]:
        result = results[check]
        status = result.get("status", "unknown")
        label = check.replace("_", " ").title()
        if status == "ok":
            print(f"  ✓ {label}")
        else:
            error = result.get("error", "unknown")
            print(f"  ✗ {label}: {error}")

    if results["overall"]:
        print("\nAll checks passed!")
    else:
        print("\nSome checks failed. Is Kimari running?")

    sys.exit(0 if results["overall"] else 1)


if __name__ == "__main__":
    main()
