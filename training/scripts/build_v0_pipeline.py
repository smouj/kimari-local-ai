#!/usr/bin/env python3
"""Orchestrate the full v0 training pipeline as a dry-run.

In --dry-run mode, orchestrates the following steps in order:
1. validate_training_ready — validates datasets and configs
2. build_dataset_mix — builds training-ready JSONL files
3. train_sft_lora --dry-run — validates training config
4. export_gguf_plan --dry-run — validates GGUF export plan
5. kimarifit --score-plan — validates eval scoring plan

Each step is invoked as a subprocess. The orchestrator reports
success/failure of each step. --dry-run does NOT create heavy
outputs, only validates.

--json outputs a structured result.

No network, no downloads, no actual training.

Usage:
    python training/scripts/build_v0_pipeline.py --dry-run
    python training/scripts/build_v0_pipeline.py --dry-run --output-dir dataset/build/kimari-v0 --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Pipeline step definitions
PIPELINE_STEPS = [
    {
        "name": "validate_training_ready",
        "description": "Validate datasets and configs are training-ready",
        "script": "training/scripts/validate_training_ready.py",
        "args_fn": "_validate_training_ready_args",
    },
    {
        "name": "build_dataset_mix",
        "description": "Build training-ready JSONL from source datasets",
        "script": "training/scripts/build_dataset_mix.py",
        "args_fn": "_build_dataset_mix_args",
    },
    {
        "name": "train_sft_lora",
        "description": "Validate SFT LoRA training config",
        "script": "training/scripts/train_sft_lora.py",
        "args_fn": "_train_sft_lora_args",
    },
    {
        "name": "export_gguf_plan",
        "description": "Plan GGUF export and quantization",
        "script": "training/scripts/export_gguf_plan.py",
        "args_fn": "_export_gguf_plan_args",
    },
    {
        "name": "kimarifit",
        "description": "Validate KimariFit eval scoring plan",
        "script": "eval/kimarifit.py",
        "args_fn": "_kimarifit_args",
    },
]


def _validate_training_ready_args(output_dir: Path | None, project_root: Path) -> list[str]:
    """Build args for validate_training_ready.py."""
    return [
        "--base-config",
        str(project_root / "training" / "configs" / "base_candidates.yaml"),
        "--sft",
        str(project_root / "dataset" / "v0" / "sft_v0.jsonl"),
        "--preference",
        str(project_root / "dataset" / "v0" / "preference_v0.jsonl"),
        "--holdout",
        str(project_root / "dataset" / "v0" / "eval_holdout.jsonl"),
        "--json",
    ]


def _build_dataset_mix_args(output_dir: Path | None, project_root: Path) -> list[str]:
    """Build args for build_dataset_mix.py."""
    odir = output_dir or (project_root / "dataset" / "build" / "kimari-v0")
    return [
        "--sft",
        str(project_root / "dataset" / "v0" / "sft_v0.jsonl"),
        "--preference",
        str(project_root / "dataset" / "v0" / "preference_v0.jsonl"),
        "--output-dir",
        str(odir),
        "--holdout",
        str(project_root / "dataset" / "v0" / "eval_holdout.jsonl"),
        "--report",
    ]


def _train_sft_lora_args(output_dir: Path | None, project_root: Path) -> list[str]:
    """Build args for train_sft_lora.py --dry-run."""
    config_path = project_root / "training" / "configs" / "kimari_sft_lora.v0.example.yaml"
    # Fall back to the generic example if v0 not available
    if not config_path.exists():
        config_path = project_root / "training" / "configs" / "kimari_sft_lora.example.yaml"
    return [
        "--config",
        str(config_path),
        "--dry-run",
    ]


def _export_gguf_plan_args(output_dir: Path | None, project_root: Path) -> list[str]:
    """Build args for export_gguf_plan.py --dry-run."""
    model_dir = project_root / "training" / "adapters" / "kimari-smollm3-sft-v0"
    gguf_out = model_dir / "gguf"
    return [
        "--model-dir",
        str(model_dir),
        "--output-dir",
        str(gguf_out),
        "--dry-run",
    ]


def _kimarifit_args(output_dir: Path | None, project_root: Path) -> list[str]:
    """Build args for kimarifit.py --dry-run --score-plan."""
    prompts_path = project_root / "eval" / "kimarifit_prompts.jsonl"
    return [
        "--prompts",
        str(prompts_path),
        "--dry-run",
        "--score-plan",
    ]


def run_step(
    step: dict,
    output_dir: Path | None,
    project_root: Path,
) -> dict:
    """Run a single pipeline step as a subprocess.

    Returns a dict with name, status, description, and output details.
    """
    script_path = project_root / step["script"]
    args_fn_name = step["args_fn"]
    args_fn = globals()[args_fn_name]
    step_args = args_fn(output_dir, project_root)

    # Build command
    cmd = [sys.executable, str(script_path)] + step_args

    result: dict = {
        "name": step["name"],
        "description": step["description"],
        "script": step["script"],
        "command": " ".join(cmd),
        "status": "unknown",
    }

    if not script_path.exists():
        result["status"] = "skipped"
        result["message"] = f"Script not found: {script_path}"
        return result

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=120,
        )
        result["exit_code"] = proc.returncode
        result["status"] = "passed" if proc.returncode == 0 else "failed"

        # Include last N lines of output for context
        stdout_lines = proc.stdout.strip().splitlines()
        stderr_lines = proc.stderr.strip().splitlines()
        result["stdout_tail"] = stdout_lines[-5:] if stdout_lines else []
        result["stderr_tail"] = stderr_lines[-5:] if stderr_lines else []

        if proc.returncode != 0:
            result["message"] = f"Exited with code {proc.returncode}"
            # Include relevant stderr
            if stderr_lines:
                result["error_detail"] = "\n".join(stderr_lines[-10:])

    except subprocess.TimeoutExpired:
        result["status"] = "failed"
        result["message"] = "Timed out after 120 seconds"
    except FileNotFoundError:
        result["status"] = "failed"
        result["message"] = f"Could not execute: {sys.executable}"

    return result


def main() -> None:
    """CLI entry point for v0 pipeline dry-run orchestration."""
    parser = argparse.ArgumentParser(
        description="Orchestrate the full v0 training pipeline as a dry-run. "
        "No network, no downloads, no actual training.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode — validate each step without creating heavy outputs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for pipeline artifacts (default: dataset/build/kimari-v0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )

    args = parser.parse_args()

    if not args.dry_run:
        print(
            "ERROR: This script only supports --dry-run mode. Actual pipeline execution is not implemented.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Kimari v0 Pipeline Dry-Run", file=sys.stderr)
    print("=" * 50, file=sys.stderr)

    step_results: list[dict] = []
    passed = 0
    failed = 0
    skipped = 0

    for i, step in enumerate(PIPELINE_STEPS, start=1):
        print(f"\n[{i}/{len(PIPELINE_STEPS)}] {step['name']} — {step['description']}", file=sys.stderr)

        result = run_step(step, args.output_dir, PROJECT_ROOT)
        step_results.append(result)

        status = result["status"]
        if status == "passed":
            passed += 1
            print("  PASSED", file=sys.stderr)
        elif status == "skipped":
            skipped += 1
            print(f"  SKIPPED: {result.get('message', '')}", file=sys.stderr)
        else:
            failed += 1
            print(f"  FAILED: {result.get('message', '')}", file=sys.stderr)

    # Summary
    summary = {
        "mode": "dry-run",
        "steps_total": len(PIPELINE_STEPS),
        "steps_passed": passed,
        "steps_failed": failed,
        "steps_skipped": skipped,
        "pipeline_status": "passed" if failed == 0 else "failed",
        "steps": step_results,
    }

    if args.json_output:
        print(json.dumps(summary, indent=2))
    else:
        print()
        print("=" * 50)
        print("Pipeline Summary")
        print("=" * 50)
        print(f"  Total:   {summary['steps_total']}")
        print(f"  Passed:  {passed}")
        print(f"  Failed:  {failed}")
        print(f"  Skipped: {skipped}")
        print()
        if failed == 0:
            print("  Pipeline: ALL STEPS PASSED (dry-run)")
        else:
            print("  Pipeline: SOME STEPS FAILED (dry-run)")
        print()
        print("No training was performed. No downloads. No network calls.")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
