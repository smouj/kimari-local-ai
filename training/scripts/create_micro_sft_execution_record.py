#!/usr/bin/env python3
"""Create a sanitized micro SFT execution record.

Generates a JSON record capturing the outcome of a micro SFT run on HF Jobs.
The record is safe to commit: no raw logs, no tokens, no secrets.

CRITICAL RULES:
- adapter_committed is ALWAYS false
- hf_upload_performed is ALWAYS false
- gguf_generated is ALWAYS false
- raw_logs_committed is ALWAYS false
- gate_state is ALWAYS BLOCKED
- manual_review_required is ALWAYS true
- No token-like strings allowed
- No raw logs included

Usage:
    python training/scripts/create_micro_sft_execution_record.py --status pending --adapter-generated unknown --json
    python training/scripts/create_micro_sft_execution_record.py --status completed --adapter-generated true --job-id sanitized-xxx --output /tmp/micro_sft_execution_record.json
    python training/scripts/create_micro_sft_execution_record.py --status failed --adapter-generated false --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Token-like patterns to detect and redact
TOKEN_PATTERNS = [
    re.compile(r"hf_[a-zA-Z0-9]{20,}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"ghp_[a-zA-Z0-9]{20,}"),
]

VERSION = "0.1.35-alpha"


def sanitize_job_id(job_id: str) -> str:
    """Sanitize a job ID, truncating if it looks like a real HF job ID."""
    if len(job_id) > 20:
        return job_id[:8] + "..."
    return job_id


def scan_for_tokens(text: str) -> str:
    """Scan text for token-like patterns and redact them."""
    for pattern in TOKEN_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a sanitized micro SFT execution record. "
        "No tokens, no raw logs, no secrets. gate_state=BLOCKED always."
    )
    parser.add_argument(
        "--status",
        required=True,
        choices=["pending", "completed", "failed"],
        help="Execution status",
    )
    parser.add_argument(
        "--job-id",
        default="optional/sanitized",
        help="Job ID (will be sanitized if >20 chars; default: optional/sanitized)",
    )
    parser.add_argument(
        "--flavor",
        default="",
        help="HF Jobs flavor",
    )
    parser.add_argument(
        "--image",
        default="",
        help="HF Jobs image",
    )
    parser.add_argument(
        "--adapter-generated",
        default="unknown",
        choices=["true", "false", "unknown"],
        help="Whether an adapter was generated (default: unknown)",
    )
    parser.add_argument(
        "--training-stack-check-passed",
        default="unknown",
        choices=["true", "false", "unknown"],
        help="Whether training stack check passed (default: unknown)",
    )
    parser.add_argument(
        "--dataset-ready",
        default="unknown",
        choices=["true", "false", "unknown"],
        help="Whether dataset is ready (default: unknown)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/micro_sft_execution_record.json"),
        help="Output file path (default: /tmp/micro_sft_execution_record.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Also print to stdout as JSON",
    )

    args = parser.parse_args()

    # Determine micro_sft_started and micro_sft_completed based on status
    if args.status == "completed":
        micro_sft_started = True
        micro_sft_completed = True
    elif args.status == "pending":
        micro_sft_started = False
        micro_sft_completed = False
    else:  # failed
        micro_sft_started = True
        micro_sft_completed = False

    # Build the execution record — CRITICAL: some fields are ALWAYS fixed
    record = {
        "record_type": "micro_sft_execution_record",
        "version": VERSION,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": args.status,
        "job_id": sanitize_job_id(args.job_id),
        "flavor": args.flavor,
        "image": args.image,
        "training_stack_check_passed": args.training_stack_check_passed,
        "dataset_ready": args.dataset_ready,
        "micro_sft_started": micro_sft_started,
        "micro_sft_completed": micro_sft_completed,
        "adapter_generated": args.adapter_generated,
        # CRITICAL: These are ALWAYS false regardless of input
        "adapter_committed": False,
        "hf_upload_performed": False,
        "gguf_generated": False,
        "raw_logs_committed": False,
        # CRITICAL: gate_state is ALWAYS BLOCKED
        "gate_state": "BLOCKED",
        # CRITICAL: manual_review_required is ALWAYS true
        "manual_review_required": True,
        "notes": "",
    }

    # Convert to JSON string and scan for token-like patterns
    output_json = json.dumps(record, indent=2)
    output_json = scan_for_tokens(output_json)

    # Write to output file
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output_json + "\n")

    if args.json_output:
        print(output_json)
    else:
        print(f"Execution record written to: {args.output}")

    sys.exit(0)


if __name__ == "__main__":
    main()
