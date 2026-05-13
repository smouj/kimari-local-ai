#!/usr/bin/env python3
"""Create sanitized summary for Kimari-4B micro SFT persisted run.

Usage:
    python training/scripts/create_hf_jobs_micro_sft_persisted_summary.py \
        --job-id <JOB_ID> \
        --status completed \
        --output docs/assets/results/hf_jobs_micro_sft_persisted_summary.json \
        --json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent / "templates" / "hf_jobs_micro_sft_persisted_summary.template.json"
)

# Fields that must be false for safety
MUST_BE_FALSE = [
    "adapter_committed_public",
    "hf_public_upload_performed",
    "gguf_generated",
    "auto_gate_transition",
]

# Fields that must be specific values
MUST_BE_VALUES = {
    "gate_state": "BLOCKED",
}


def create_summary(
    job_id: str,
    status: str,
    output: str | None = None,
    base_model: str = "Qwen/Qwen2.5-1.5B-Instruct",
    dataset_file_sha256: str = "",
    adapter_generated: bool = False,
    adapter_persisted_private: bool = False,
    adapter_private_repo: str = "",
    adapter_hash: str = "",
    adapter_size_bytes: int = 0,
    adapter_load_check: bool = False,
) -> dict:
    """Create a sanitized summary from template."""
    template = json.loads(TEMPLATE_PATH.read_text())

    summary = {
        **template,
        "run_id": "kimari4b-hfjobs-micro-sft-persisted-v0",
        "job_id": job_id,
        "status": status,
        "base_model": base_model,
        "dataset_file_sha256": dataset_file_sha256,
        "adapter_generated": adapter_generated,
        "adapter_persisted_private": adapter_persisted_private,
        "adapter_private_repo": adapter_private_repo,
        "adapter_hash": adapter_hash,
        "adapter_size_bytes": adapter_size_bytes,
        "adapter_load_check": adapter_load_check,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Safety: enforce mandatory false values
    for field in MUST_BE_FALSE:
        summary[field] = False

    # Safety: enforce mandatory specific values
    for field, value in MUST_BE_VALUES.items():
        summary[field] = value

    summary["manual_review_required"] = True

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Create micro SFT persisted summary")
    parser.add_argument("--job-id", required=True, help="HF Jobs job ID")
    parser.add_argument("--status", required=True, choices=["completed", "failed"], help="Job status")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--dataset-sha256", default="")
    parser.add_argument("--adapter-generated", action="store_true")
    parser.add_argument("--adapter-persisted", action="store_true")
    parser.add_argument("--adapter-repo", default="")
    parser.add_argument("--adapter-hash", default="")
    parser.add_argument("--adapter-size", type=int, default=0)
    parser.add_argument("--adapter-load-check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = create_summary(
        job_id=args.job_id,
        status=args.status,
        base_model=args.base_model,
        dataset_file_sha256=args.dataset_sha256,
        adapter_generated=args.adapter_generated,
        adapter_persisted_private=args.adapter_persisted,
        adapter_private_repo=args.adapter_repo,
        adapter_hash=args.adapter_hash,
        adapter_size_bytes=args.adapter_size,
        adapter_load_check=args.adapter_load_check,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
        print(f"Summary written to {output_path}")

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        for k, v in summary.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
