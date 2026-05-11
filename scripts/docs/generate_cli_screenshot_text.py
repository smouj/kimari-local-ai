#!/usr/bin/env python3
"""Generate clean text blocks for terminal screenshot captures.

This CLI tool produces SAFE, generic text output that can be used as the
basis for screenshot images in documentation. It does NOT generate actual
images — only text.

Usage:
    python scripts/docs/generate_cli_screenshot_text.py --kind setup
    python scripts/docs/generate_cli_screenshot_text.py --kind optimize --json
    python scripts/docs/generate_cli_screenshot_text.py --kind preflight --output screenshot.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
VERSION = "1.0.0"

VALID_KINDS = (
    "setup",
    "optimize",
    "preflight",
    "training_preview",
    "baseline_eval",
    "postrun",
)


# ---------------------------------------------------------------------------
# Text generators — one per kind
# ---------------------------------------------------------------------------

def _generate_setup() -> str:
    return """\
$ kimari setup --json
{
  "profile": "test",
  "gpu_detected": true,
  "cuda_available": true,
  "recommended_profile": "gtx1060",
  "llama_server_found": true,
  "models_dir": "/home/user/.local/share/kimari/models",
  "config_path": "/home/user/.config/kimari/config.json"
}"""


def _generate_optimize() -> str:
    return """\
$ kimari optimize --profile test --json
{
  "profile": "test",
  "mode": "balanced",
  "vram_estimated_gb": 5.8,
  "context_window": 4096,
  "cache_type_k": "q8_0",
  "cache_type_v": "q8_0",
  "batch_size": 512,
  "ubatch_size": 128
}"""


def _generate_preflight() -> str:
    return """\
$ python training/scripts/preflight_private_sft.py --run-config training/configs/private_sft_run.v0.yaml --json
{
  "checks": {
    "python_version": {"status": "PASS", "value": "3.12.3"},
    "torch": {"status": "PASS", "value": "installed", "cuda_available": true},
    "dataset_build": {"status": "PASS", "value": "dataset/build/kimari-v0/report.json", "exists": true},
    "preview_gate": {"status": "PASS", "value": "BLOCKED"}
  },
  "overall": "pass"
}"""


def _generate_training_preview() -> str:
    return """\
$ python training/scripts/run_training_command_preview.py --json
{
  "recommended_command": "accelerate launch training/scripts/train_sft_lora.py --config training/configs/kimari_sft_lora.v0.example.yaml",
  "recommended_environment": "RunPod RTX 4090 24GB / Local A100",
  "expected_outputs": ["adapter_model.safetensors", "MANIFEST.yaml"],
  "forbidden_commit_patterns": ["*.safetensors", "*.bin", "*.pt", "*.gguf"],
  "safety_warnings": ["Do not commit adapter weights", "Preview gate must stay BLOCKED"]
}"""


def _generate_baseline_eval() -> str:
    return """\
$ python eval/scripts/run_baseline_eval_plan.py --dry-run --json
{
  "model_label": "smollm3-base",
  "prompt_count": 35,
  "categories": ["python", "bash", "docker", "linux_troubleshooting", "windows_troubleshooting", "spanish_technical", "json_mode", "openclaw_agent", "local_security", "agent_prompting"],
  "recommended_endpoint": "http://127.0.0.1:11435/v1/chat/completions",
  "score_status": "manual_review_required",
  "dry_run": true
}"""


def _generate_postrun() -> str:
    return """\
$ python training/scripts/postrun_private_sft.py --dry-run --json
{
  "steps": [
    {"label": "create_adapter_manifest", "status": "dry_run"},
    {"label": "create_eval_summary", "status": "dry_run", "command": "python eval/scripts/create_eval_summary.py --input eval/results/adapter-private.json --output /tmp/adapter-summary.json --json"},
    {"label": "compare_runs", "status": "skipped"},
    {"label": "verify_gate_blocked", "status": "dry_run", "blocked": true}
  ],
  "overall": "pass",
  "dry_run": true
}"""


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

GENERATORS = {
    "setup": _generate_setup,
    "optimize": _generate_optimize,
    "preflight": _generate_preflight,
    "training_preview": _generate_training_preview,
    "baseline_eval": _generate_baseline_eval,
    "postrun": _generate_postrun,
}


def generate_text(kind: str) -> str:
    """Return the screenshot-safe text block for *kind*."""
    generator = GENERATORS.get(kind)
    if generator is None:
        raise ValueError(f"Unknown kind: {kind!r}. Valid kinds: {', '.join(VALID_KINDS)}")
    return generator()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate clean text blocks for terminal screenshot captures.",
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=VALID_KINDS,
        help="Which CLI screenshot text to generate.",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON with kind, text, and metadata.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    text = generate_text(args.kind)

    if args.json_output:
        payload: dict[str, Any] = {
            "kind": args.kind,
            "text": text,
            "version": VERSION,
            "project_root": str(PROJECT_ROOT),
        }
        output = json.dumps(payload, indent=2)
    else:
        output = text

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")


if __name__ == "__main__":
    main()
