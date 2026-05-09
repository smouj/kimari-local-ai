"""
Benchmark runner for Kimari.

Runs inference benchmarks against the Kimari API and produces structured
JSON output with performance metrics.
"""

import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    requests = None  # type: ignore

from kimari import __version__ as KIMARI_VERSION
from kimari.config.loader import get_profile
from kimari.core.constants import PROJECT_ROOT
from kimari.core.detection import detect_gpu, detect_cuda_version
from kimari.utils.colors import Color


# Standard benchmark prompts (English + Spanish technical)
BENCHMARK_PROMPTS = [
    "Explain Docker containers in one paragraph.",
    "Write a Python function to merge two sorted lists.",
    "What is the difference between process and thread?",
    "Responde en español: ¿Qué es una API REST?",
    "Write a TypeScript interface for a User with optional fields.",
    "Explica brevemente la diferencia entre GPU y CPU para inferencia.",
    "Write a bash script that finds all .log files older than 7 days.",
    "What is the purpose of the KV cache in transformer models?",
]


def _detect_llama_cpp_version() -> Optional[str]:
    """Try to detect llama.cpp version from llama-server --version."""
    try:
        result = subprocess.run(
            ["llama-server", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        output = (result.stdout or "") + (result.stderr or "")
        # Extract version-like string from output
        for line in output.strip().splitlines():
            line = line.strip()
            if line:
                return line
        return None
    except Exception:
        return None


def run_benchmark(profile_name: str, config: dict, json_output: bool = False,
                   output: Optional[str] = None,
                   vram_override: Optional[float] = None):
    """Run a basic benchmark on the Kimari server."""
    if requests is None:
        print("[ERROR] 'requests' is required. Install with: pip install -r cli/requirements.txt")
        raise SystemExit(1)

    profile = get_profile(config, profile_name)
    host = profile.get("host", "127.0.0.1")
    port = profile.get("port", 11435)

    # Check server
    try:
        requests.get(f"http://{host}:{port}/health", timeout=3)
    except requests.ConnectionError:
        print("[ERROR] Server not running. Start first: kimari start")
        raise SystemExit(1)

    results = []
    for i, prompt in enumerate(BENCHMARK_PROMPTS):
        prompt_display = prompt[:50] + ("..." if len(prompt) > 50 else "")

        if not json_output:
            print(f"  [{i+1}/{len(BENCHMARK_PROMPTS)}] ", end="", flush=True)
            print(f"{Color.DIM}{prompt_display}{Color.RESET} ", end="", flush=True)

        start = time.time()
        try:
            resp = requests.post(
                f"http://{host}:{port}/v1/chat/completions",
                json={
                    "model": "kimari",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 256,
                    "stream": True,  # Use streaming for time-to-first-token measurement
                },
                timeout=60,
                stream=True,
            )
            resp.raise_for_status()

            # Measure time to first token
            first_token_time = None
            full_content = ""
            chunks = 0

            for line in resp.iter_lines():
                if line:
                    line_str = line.decode("utf-8", errors="replace")
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                            if "content" in delta:
                                if first_token_time is None:
                                    first_token_time = time.time() - start
                                full_content += delta["content"]
                                chunks += 1
                        except json.JSONDecodeError:
                            pass

            elapsed = time.time() - start

            # Estimate tokens (rough: 4 chars per token for English)
            completion_tokens = max(chunks, len(full_content) // 4)
            tokens_per_sec = completion_tokens / elapsed if elapsed > 0 else 0

            results.append({
                "prompt": prompt_display,
                "tokens": completion_tokens,
                "time_s": round(elapsed, 2),
                "tokens_per_sec": round(tokens_per_sec, 1),
                "time_to_first_token_ms": round(first_token_time * 1000, 1) if first_token_time else None,
                "status": "ok",
            })
            if not json_output:
                ttft = f" TTFT: {first_token_time*1000:.0f}ms" if first_token_time else ""
                print(f"{Color.GREEN}✓{Color.RESET} {completion_tokens}tok in {elapsed:.1f}s ({tokens_per_sec:.1f} t/s){ttft}")

        except Exception as e:
            results.append({
                "prompt": prompt_display,
                "status": f"error: {str(e)[:50]}",
            })
            if not json_output:
                print(f"{Color.RED}✗{Color.RESET} {e}")

    # Summary
    ok_results = [r for r in results if r.get("status") == "ok"]

    # Build standardized benchmark output
    gpu = detect_gpu()
    cuda_ver = detect_cuda_version()

    std_data = {
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "kimari_version": KIMARI_VERSION,
        "os": f"{platform.system()} {platform.release()}",
        "gpu_name": gpu["name"] if gpu else None,
        "vram_total_mb": int(vram_override * 1024) if vram_override is not None else (gpu["vram_mb"] if gpu else None),
        "driver_version": gpu["driver"] if gpu else None,
        "cuda_version": cuda_ver,
        "model_name": Path(profile["model"]).stem,
        "model_size_gb": profile.get("estimated_model_size_gb"),
        "quantization": profile.get("quantization"),
        "ctx": profile.get("ctx"),
        "batch": profile.get("batch"),
        "ubatch": profile.get("ubatch"),
        "prompt_tokens": None,
        "generated_tokens": sum(r["tokens"] for r in ok_results) if ok_results else None,
        "tokens_per_second": round(
            sum(r["tokens_per_sec"] for r in ok_results) / len(ok_results), 2
        ) if ok_results else None,
        "time_to_first_token_ms": round(
            sum(r["time_to_first_token_ms"] for r in ok_results
                if r.get("time_to_first_token_ms") is not None) /
            len([r for r in ok_results if r.get("time_to_first_token_ms") is not None]), 1
        ) if any(r.get("time_to_first_token_ms") is not None for r in ok_results) else None,
        "peak_vram_mb": None,  # Known limitation — cannot measure from CLI
        "llama_cpp_version": _detect_llama_cpp_version(),
        "notes": "Automated benchmark via 'kimari bench'" + (" (VRAM manually overridden)" if vram_override is not None else ""),
    }

    # Build detailed bench data
    bench_data = {
        "profile": profile_name,
        "profile_name": profile["name"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": results,
        "standardized": std_data,
    }

    if ok_results:
        avg_tps = sum(r["tokens_per_sec"] for r in ok_results) / len(ok_results)
        avg_time = sum(r["time_s"] for r in ok_results) / len(ok_results)
        total_tokens = sum(r["tokens"] for r in ok_results)

        bench_data["summary"] = {
            "avg_tokens_per_sec": round(avg_tps, 2),
            "avg_latency_s": round(avg_time, 2),
            "total_tokens": total_tokens,
            "success_rate": f"{len(ok_results)}/{len(results)}",
        }

        if not json_output:
            print(f"\n{Color.BOLD}Summary:{Color.RESET}")
            print(f"  Avg speed:      {Color.GREEN}{avg_tps:.1f} tokens/s{Color.RESET}")
            print(f"  Avg latency:    {avg_time:.2f}s")
            print(f"  Total tokens:   {total_tokens}")
            print(f"  Success rate:   {len(ok_results)}/{len(results)}")

            # Save results
            results_dir = PROJECT_ROOT / "benchmarks" / "results"
            results_dir.mkdir(parents=True, exist_ok=True)
            date_str = time.strftime("%Y%m%d-%H%M%S")
            result_file = results_dir / f"{profile_name}-{date_str}.json"
            with open(result_file, "w") as f:
                json.dump(bench_data, f, indent=2)
            print(f"\n  Results saved: {result_file}")

    if json_output:
        print(json.dumps(bench_data, indent=2))

    # Save standardized output to file if --output provided
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(std_data, f, indent=2)
        if not json_output:
            print(f"\n  Results saved: {output_path}")

    if json_output:
        return

    if not ok_results:
        print(f"\n  {Color.RED}All benchmarks failed.{Color.RESET}")
