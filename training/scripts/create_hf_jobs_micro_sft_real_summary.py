#!/usr/bin/env python3
"""Create sanitized micro SFT real summary."""

from __future__ import annotations

import argparse
import json
import time

FORBIDDEN = ["/home/", "sk-", "api_key", "password", "credential"]


def create_summary(job_id: str, status: str, output_path: str = "", **kwargs) -> dict:
    """Create a sanitized micro SFT summary."""
    summary = {
        "run_id": kwargs.get("run_id", "kimari4b-hfjobs-micro-sft-v0"),
        "job_id": job_id[:16] + "..." if len(job_id) > 16 else job_id,
        "status": status,
        "flavor": kwargs.get("flavor", "a10g-small"),
        "gpu_name": kwargs.get("gpu_name", ""),
        "gpu_vram_gb": kwargs.get("gpu_vram_gb", 0),
        "base_model": kwargs.get("base_model", "Qwen/Qwen2.5-3B-Instruct"),
        "dataset_name": kwargs.get("dataset_name", "kimari-fit-v0"),
        "dataset_hash": kwargs.get("dataset_hash", ""),
        "dataset_count": kwargs.get("dataset_count", 72),
        "max_steps": kwargs.get("max_steps", 20),
        "steps_completed": kwargs.get("steps_completed", 0),
        "final_loss": kwargs.get("final_loss", 0),
        "training_performed": kwargs.get("training_performed", True),
        "adapter_generated": kwargs.get("adapter_generated", True),
        "adapter_committed": False,
        "hf_upload_performed": False,
        "push_to_hub": False,
        "gguf_generated": False,
        "gate_state": "BLOCKED",
        "manual_review_required": True,
        "auto_gate_transition": False,
        "estimated_cost_usd": kwargs.get("estimated_cost_usd", 0.50),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "notes": "Micro SFT run. Adapter generated in HF Jobs ephemeral storage. Not committed to git. Not uploaded to HF. Gate BLOCKED.",
    }

    # Verify no forbidden patterns
    summary_str = json.dumps(summary, indent=2)
    for pattern in FORBIDDEN:
        if pattern.lower() in summary_str.lower() and pattern not in ["api_key"]:
            print(f"WARNING: Found forbidden pattern '{pattern}' in summary")

    if output_path:
        from pathlib import Path

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary written to: {out}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Create micro SFT summary")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--status", required=True, choices=["completed", "failed", "running", "timed_out"])
    parser.add_argument("--output", default="")
    parser.add_argument("--run-id", default="kimari4b-hfjobs-micro-sft-v0")
    parser.add_argument("--flavor", default="a10g-small")
    parser.add_argument("--gpu-name", default="")
    parser.add_argument("--gpu-vram-gb", type=float, default=0)
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-3B-Instruct")
    parser.add_argument("--dataset-name", default="kimari-fit-v0")
    parser.add_argument("--dataset-hash", default="")
    parser.add_argument("--dataset-count", type=int, default=72)
    parser.add_argument("--max-steps", type=int, default=20)
    parser.add_argument("--steps-completed", type=int, default=0)
    parser.add_argument("--final-loss", type=float, default=0)
    parser.add_argument("--training-performed", type=bool, default=True)
    parser.add_argument("--adapter-generated", type=bool, default=True)
    parser.add_argument("--estimated-cost-usd", type=float, default=0.50)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = create_summary(
        args.job_id,
        args.status,
        args.output,
        run_id=args.run_id,
        flavor=args.flavor,
        gpu_name=args.gpu_name,
        gpu_vram_gb=args.gpu_vram_gb,
        base_model=args.base_model,
        dataset_name=args.dataset_name,
        dataset_hash=args.dataset_hash,
        dataset_count=args.dataset_count,
        max_steps=args.max_steps,
        steps_completed=args.steps_completed,
        final_loss=args.final_loss,
        training_performed=args.training_performed,
        adapter_generated=args.adapter_generated,
        estimated_cost_usd=args.estimated_cost_usd,
    )

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("Micro SFT Summary")
        print("=" * 50)
        for k, v in summary.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
