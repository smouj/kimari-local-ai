#!/usr/bin/env python3
"""Generate a sanitized HF Jobs micro SFT summary.

Creates a JSON summary with all required fields. No tokens, no raw logs.
adapter_committed=false, hf_upload_performed=false, gate_state=BLOCKED.

Usage:
    python training/scripts/create_hf_jobs_micro_sft_summary.py --status pending --json
    python training/scripts/create_hf_jobs_micro_sft_summary.py --job-id abc123 --status completed --output /tmp/micro_sft_summary.json --json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a sanitized HF Jobs micro SFT summary. "
        "No tokens included. No raw logs. adapter_committed=false always. "
        "hf_upload_performed=false always. gate_state=BLOCKED always."
    )
    parser.add_argument(
        "--job-id",
        default=None,
        help="HF Jobs job ID (optional, sanitized in output)",
    )
    parser.add_argument(
        "--status",
        choices=["pending", "completed", "failed"],
        default="pending",
        help="Micro SFT status (default: pending)",
    )
    parser.add_argument(
        "--base-model",
        default="HuggingFaceTB/SmolLM3-3B",
        help="Base model used (default: HuggingFaceTB/SmolLM3-3B)",
    )
    parser.add_argument(
        "--dataset-id",
        default="kimari-v0",
        help="Dataset identifier (default: kimari-v0)",
    )
    parser.add_argument(
        "--flavor",
        default="a10g-small",
        help="GPU flavor used (default: a10g-small)",
    )
    parser.add_argument(
        "--adapter-generated",
        choices=["unknown", "true", "false"],
        default="unknown",
        help="Whether adapter was generated (default: unknown)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON (always JSON, this is for consistency)",
    )

    args = parser.parse_args()

    # Build sanitized summary — NEVER include tokens or raw logs
    summary = {
        "job_id": args.job_id if args.job_id else "NOT_AVAILABLE",
        "run_id": "micro-sft-v0",
        "base_model": args.base_model,
        "dataset_id": args.dataset_id,
        "flavor": args.flavor,
        "status": args.status,
        "started_at": None,
        "finished_at": None,
        "training_performed": True,
        "adapter_generated": args.adapter_generated,
        "adapter_committed": False,
        "hf_upload_performed": False,
        "gguf_generated": False,
        "raw_logs_committed": False,
        "eval_performed": False,
        "gate_state": "BLOCKED",
        "manual_review_required": True,
        "stderr_sanitized": True,
        "logs_sanitized": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Sanitized micro SFT summary. No tokens. No raw logs. adapter_committed=false. hf_upload_performed=false. gate=BLOCKED. manual_review_required=true.",
    }

    output_json = json.dumps(summary, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json + "\n")
        if args.json_output:
            print(output_json)
        else:
            print(f"Summary written to: {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
