"""
Measured benchmarks against an OpenAI-compatible local endpoint.

Sends real chat completion requests to a running llama-server instance
and records timing/token metrics. This module performs actual HTTP calls
— it is NOT suitable for CI without mocks.

Design rules:
- Only uses ``requests`` (already a project dependency).
- Never invents metrics: if usage or timing data is missing, the field
  is set to ``None`` and ``score_status`` reflects the gap.
- ``score_status="measured"`` ONLY when a real response with usage data
  is received.
- No external dependencies beyond ``requests``.
- No model execution in tests — use mocks.
"""

from __future__ import annotations

import time
from urllib.parse import urlparse

import requests

# ─── Payload construction ─────────────────────────────────────────────


def build_chat_completion_payload(prompt: str, max_tokens: int = 128) -> dict:
    """Return a standard chat completion request payload.

    Uses deterministic settings (temperature=0.0) so that repeated
    benchmark runs produce comparable results.

    Args:
        prompt: The user prompt to send.
        max_tokens: Maximum tokens to generate.

    Returns:
        Dict suitable as the JSON body of a /v1/chat/completions request.
    """
    return {
        "model": "kimari",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }


# ─── Measurement ──────────────────────────────────────────────────────


def measure_chat_completion(
    endpoint: str,
    model: str,
    prompt: str,
    max_tokens: int = 128,
    timeout: float = 30.0,
) -> dict:
    """Send a chat completion request and measure performance.

    Performs a single non-streaming request to the given endpoint and
    records wall-clock timing plus token usage from the response.

    Args:
        endpoint: Base URL of the OpenAI-compatible server
            (e.g. ``http://localhost:11435``).
        model: Model identifier to pass in the request.
        prompt: User prompt text.
        max_tokens: Maximum tokens to generate.
        timeout: HTTP request timeout in seconds.

    Returns:
        Dict with measurement results. The ``score_status`` field
        indicates the quality of the result:

        - ``"measured"`` — successful response with usage data.
        - ``"incomplete_response"`` — response received but usage
          information is missing.
        - ``"error"`` — request failed entirely.
    """
    url = f"{endpoint.rstrip('/')}/v1/chat/completions"
    payload = build_chat_completion_payload(prompt, max_tokens)
    # Override the model in the payload with the caller-specified model
    payload["model"] = model

    result: dict = {
        "endpoint": endpoint,
        "model": model,
        "prompt_preview": prompt[:50],
        "max_tokens": max_tokens,
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "tokens_per_second": None,
        "ttft_ms": None,  # Not available for non-streaming
        "elapsed_s": None,
        "score_status": "error",
        "error": None,
    }

    start_time = time.monotonic()
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        result["error"] = f"Connection failed: {exc}"
        return result
    except requests.exceptions.Timeout:
        result["error"] = f"Request timed out after {timeout}s"
        return result
    except requests.exceptions.HTTPError as exc:
        result["error"] = f"HTTP error: {exc}"
        return result
    except requests.exceptions.RequestException as exc:
        result["error"] = f"Request failed: {exc}"
        return result
    end_time = time.monotonic()

    elapsed_s = end_time - start_time
    result["elapsed_s"] = round(elapsed_s, 4)

    # Parse response JSON
    try:
        body = response.json()
    except (ValueError, TypeError):
        result["score_status"] = "incomplete_response"
        result["error"] = "Response body is not valid JSON"
        return result

    # Extract usage information
    usage = body.get("usage")
    if usage is None:
        result["score_status"] = "incomplete_response"
        result["error"] = "Response lacks usage information"
        return result

    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")

    result["prompt_tokens"] = prompt_tokens
    result["completion_tokens"] = completion_tokens
    result["total_tokens"] = total_tokens

    # Calculate tokens per second — only if we have real data
    tps = calculate_tokens_per_second(completion_tokens, elapsed_s)
    result["tokens_per_second"] = tps

    if tps is not None:
        result["score_status"] = "measured"
        result["error"] = None
    else:
        result["score_status"] = "incomplete_response"
        result["error"] = "Cannot calculate tokens_per_second: missing completion_tokens or elapsed time"

    return result


# ─── Calculation helpers ──────────────────────────────────────────────


def calculate_tokens_per_second(completion_tokens: int, elapsed_seconds: float) -> float | None:
    """Calculate tokens per second from completion tokens and elapsed time.

    Returns ``None`` if either value is missing or non-positive.
    Does NOT invent metrics — both inputs must be real, positive values.

    Args:
        completion_tokens: Number of completion tokens from the response.
        elapsed_seconds: Wall-clock time in seconds.

    Returns:
        Tokens per second, or ``None`` if the calculation is not possible.
    """
    if completion_tokens is None or elapsed_seconds is None:
        return None
    if completion_tokens <= 0 or elapsed_seconds <= 0:
        return None
    return round(completion_tokens / elapsed_seconds, 2)


# ─── Sanitization ─────────────────────────────────────────────────────


def sanitize_benchmark_result(result: dict) -> dict:
    """Remove private data from a benchmark result.

    Strips full prompt text, full response/choices content, and any
    other fields that could contain user data. Keeps only the fields
    needed for performance reporting.

    The endpoint is reduced to just ``host:port`` — the ``/v1/...`` path
    is removed to avoid exposing internal routing details.

    Args:
        result: Raw benchmark result dict.

    Returns:
        Sanitized dict safe for logging, storage, or sharing.
    """
    # Allowed fields — anything else is dropped
    allowed_keys = {
        "endpoint",
        "model",
        "prompt_preview",
        "max_tokens",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "tokens_per_second",
        "ttft_ms",
        "elapsed_s",
        "score_status",
        "timestamp",
        "error",
    }

    sanitized: dict = {}
    for key in allowed_keys:
        if key in result:
            sanitized[key] = result[key]

    # Sanitize endpoint: keep only host:port, strip path
    if "endpoint" in sanitized and sanitized["endpoint"]:
        try:
            parsed = urlparse(sanitized["endpoint"])
            host_port = f"{parsed.hostname}"
            if parsed.port:
                host_port = f"{host_port}:{parsed.port}"
            sanitized["endpoint"] = host_port
        except Exception:
            # If URL parsing fails, keep original
            pass

    # Ensure prompt_preview is at most 50 chars
    if "prompt_preview" in sanitized and sanitized["prompt_preview"]:
        sanitized["prompt_preview"] = sanitized["prompt_preview"][:50]

    return sanitized


# ─── Validation ───────────────────────────────────────────────────────


def validate_measured_result(result: dict) -> dict:
    """Validate that a measured result has the required fields.

    Checks for the presence and quality of essential benchmark fields.

    Args:
        result: Benchmark result dict to validate.

    Returns:
        Dict with:

        - ``valid`` (bool): True if all required fields are present.
        - ``missing_fields`` (list): Names of missing required fields.
        - ``warnings`` (list): Quality warnings about the result.
    """
    required_fields = ["score_status", "endpoint", "model"]
    # At least one of tokens_per_second or error must be present
    missing_fields: list[str] = []
    for field in required_fields:
        if field not in result or result[field] is None:
            missing_fields.append(field)

    # Check that we have either tokens_per_second or error
    has_tps = "tokens_per_second" in result and result["tokens_per_second"] is not None
    has_error = "error" in result and result["error"] is not None
    if not has_tps and not has_error:
        missing_fields.append("tokens_per_second or error")

    warnings: list[str] = []

    # Warn if score_status is not "measured"
    score_status = result.get("score_status")
    if score_status and score_status != "measured":
        warnings.append(f"score_status is '{score_status}', not 'measured'")

    # Warn if tokens_per_second is 0 or negative
    tps = result.get("tokens_per_second")
    if tps is not None and tps <= 0:
        warnings.append(f"tokens_per_second is {tps}, expected a positive value")

    valid = len(missing_fields) == 0

    return {
        "valid": valid,
        "missing_fields": missing_fields,
        "warnings": warnings,
    }
