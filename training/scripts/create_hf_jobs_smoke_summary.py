#!/usr/bin/env python3
"""Create sanitized HF Jobs smoke summary.

Creates a summary JSON from a completed smoke job.
No raw logs, no tokens, no private paths.

Usage:
    python training/scripts/create_hf_jobs_smoke_summary.py --job-id <ID> --status completed --output /tmp/summary.json --json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

FORBIDDEN_PATTERNS = ["/home/", "sk-", "hf_", "api_key", "password", "credential", "secret"]


def create_summary(
    job_id: str, status: str, output_path: str = "", flavor: str = "a10g-small", image: str = ""
) -> dict:
    """Create a sanitized smoke summary."""
    summary = {
        "job_id": job_id[:12] + "..." if len(job_id) > 12 else job_id,  # Truncate for privacy
        "status": status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "flavor": flavor,
        "image": image,
        "training_performed": False,
        "adapter_generated": False,
        "hf_upload_performed": False,
        "gguf_export": False,
        "push_to_hub": False,
        "gate_state": "BLOCKED",
        "manual_review_required": True,
        "notes": "HF Jobs smoke test. No training performed. No adapter generated. No upload.",
    }

    # Verify no forbidden patterns
    summary_str = json.dumps(summary, indent=2)
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in summary_str.lower() and pattern != "hf_":
            print(f"WARNING: Found forbidden pattern '{pattern}' in summary")

    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary written to: {output}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Create HF Jobs smoke summary")
    parser.add_argument("--job-id", default="pending", help="Job ID")
    parser.add_argument(
        "--status", required=True, choices=["pending", "completed", "failed", "running", "timed_out"], help="Job status"
    )
    parser.add_argument("--flavor", default="a10g-small", help="HF Jobs flavor")
    parser.add_argument("--image", default="", help="Container image")
    parser.add_argument("--output", default="", help="Output file path")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    summary = create_summary(args.job_id, args.status, args.output, args.flavor, args.image)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("HF Jobs Smoke Summary")
        print("=" * 50)
        for key, value in summary.items():
            print(f"  {key}: {value}")
        print("=" * 50)


if __name__ == "__main__":
    main()
