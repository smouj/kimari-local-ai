#!/usr/bin/env python3
"""Generate a sanitized HF Jobs smoke test summary.

Creates a JSON summary with all required fields. No tokens, no raw logs.
training_performed=false, adapter_generated=false, hf_upload_performed=false, gate_state=BLOCKED.

Usage:
    python training/scripts/create_hf_jobs_smoke_summary.py --status pending --flavor a10g-small --image pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel --json
    python training/scripts/create_hf_jobs_smoke_summary.py --job-id abc123 --status completed --flavor a10g-small --image pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel --output /tmp/hf_jobs_smoke_summary.json --json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a sanitized HF Jobs smoke test summary. "
        "No tokens included. No raw logs. training_performed=false always."
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
        help="Smoke test status (default: pending)",
    )
    parser.add_argument(
        "--flavor",
        default="a10g-small",
        help="GPU flavor used (default: a10g-small)",
    )
    parser.add_argument(
        "--image",
        default="pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
        help="Docker image used",
    )
    parser.add_argument(
        "--gpu-detected",
        dest="gpu_detected",
        action="store_true",
        default=None,
        help="GPU was detected by nvidia-smi",
    )
    parser.add_argument(
        "--no-gpu-detected",
        dest="gpu_detected",
        action="store_false",
        help="GPU was NOT detected",
    )
    parser.add_argument(
        "--torch-cuda",
        dest="torch_cuda_available",
        action="store_true",
        default=None,
        help="torch.cuda.is_available() returned True",
    )
    parser.add_argument(
        "--no-torch-cuda",
        dest="torch_cuda_available",
        action="store_false",
        help="torch.cuda.is_available() returned False",
    )
    parser.add_argument(
        "--repo-installed",
        dest="repo_installed",
        action="store_true",
        default=None,
        help="pip install -e . succeeded",
    )
    parser.add_argument(
        "--no-repo-installed",
        dest="repo_installed",
        action="store_false",
        help="pip install -e . failed",
    )
    parser.add_argument(
        "--dataset-dryrun",
        dest="dataset_dryrun_passed",
        action="store_true",
        default=None,
        help="Dataset build dry-run passed",
    )
    parser.add_argument(
        "--no-dataset-dryrun",
        dest="dataset_dryrun_passed",
        action="store_false",
        help="Dataset build dry-run failed",
    )
    parser.add_argument(
        "--sft-dryrun",
        dest="sft_dryrun_passed",
        action="store_true",
        default=None,
        help="train_sft_lora --dry-run passed",
    )
    parser.add_argument(
        "--no-sft-dryrun",
        dest="sft_dryrun_passed",
        action="store_false",
        help="train_sft_lora --dry-run failed",
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
        "job_name": "kimari4b-smoke-v0",
        "flavor": args.flavor,
        "image": args.image,
        "started_at": None,
        "finished_at": None,
        "status": args.status,
        "gpu_detected": args.gpu_detected,
        "torch_cuda_available": args.torch_cuda_available,
        "repo_installed": args.repo_installed,
        "dataset_dryrun_passed": args.dataset_dryrun_passed,
        "sft_dryrun_passed": args.sft_dryrun_passed,
        "training_performed": False,
        "adapter_generated": False,
        "hf_upload_performed": False,
        "logs_sanitized": True,
        "gate_state": "BLOCKED",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Sanitized summary. No tokens. No raw logs. training_performed=false. gate=BLOCKED.",
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
