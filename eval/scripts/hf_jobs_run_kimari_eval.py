#!/usr/bin/env python3
"""Run KimariEval baseline vs adapter evaluation on HF Jobs.

Usage:
    # Dry-run (default, no submission)
    python eval/scripts/hf_jobs_run_kimari_eval.py \\
        --config eval/configs/kimari_eval_v1_baseline_vs_adapter.yaml \\
        --dry-run --json

    # Print the HF Jobs command without submitting
    python eval/scripts/hf_jobs_run_kimari_eval.py \\
        --config eval/configs/kimari_eval_v1_baseline_vs_adapter.yaml \\
        --print-command

    # Submit for real (requires --allow-submit --yes)
    python eval/scripts/hf_jobs_run_kimari_eval.py \\
        --config eval/configs/kimari_eval_v1_baseline_vs_adapter.yaml \\
        --require-jobs-access --allow-submit --yes

Safety:
    - dry-run by default
    - Real submission requires --allow-submit --yes
    - No --token arg
    - No shell=True
    - No public upload
    - No gate transition
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str) -> dict:
    """Load eval config from YAML file."""
    path = Path(config_path)
    if not path.exists():
        print(f"ERROR: Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def validate_config(config: dict) -> list[str]:
    """Validate config safety flags."""
    errors = []
    if config.get("public_benchmark_allowed") is True:
        errors.append("public_benchmark_allowed must be false")
    if config.get("raw_outputs_commit_allowed") is True:
        errors.append("raw_outputs_commit_allowed must be false")
    if config.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")
    if config.get("manual_review_required") is not True:
        errors.append("manual_review_required must be true")
    return errors


def build_eval_script(config: dict, subset_size: int | None = None) -> str:
    """Build the inline Python eval script for HF Jobs.

    Uses PEP 723 inline dependencies (uv run compatible).
    """
    base_model = config["base_model"]
    adapter_repo = config["adapter_repo_private"]
    temperature = config.get("temperature", 0.2)
    max_tokens = config.get("max_tokens", 384)
    top_p = config.get("top_p", 0.9)
    seed = config.get("seed", 42)
    effective_subset = subset_size or config.get("subset_size", 30)

    # HF Jobs cannot see local eval/ files unless we pass them explicitly. Embed
    # the private eval prompts into the inline job script so real runs are
    # reproducible while still avoiding raw model outputs or public uploads.
    dataset_dir = PROJECT_ROOT / config.get("dataset_dir", "eval/kimari_private_v1")
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
    eval_items = []
    for jsonl_file in sorted(dataset_dir.glob("*.jsonl")):
        for line in jsonl_file.read_text().strip().split("\n"):
            if line.strip():
                eval_items.append(json.loads(line))
    embedded_dataset_b64 = base64.b64encode(json.dumps(eval_items, ensure_ascii=False).encode("utf-8")).decode("ascii")

    script = f'''# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "torch>=2.5",
#     "transformers>=4.46",
#     "peft>=0.19",
#     "accelerate>=1.0",
#     "datasets>=3.0",
# ]
# ///
"""KimariEval baseline vs adapter evaluation script for HF Jobs.

Loads Qwen2.5-1.5B-Instruct base, runs eval subset, loads adapter,
runs eval subset again, generates sanitized summary.

Safety: no public upload, no raw outputs committed, no gate transition.
"""

import base64
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def main():
    print("=" * 60)
    print("KimariEval Baseline vs Adapter Evaluation")
    print("=" * 60)

    base_model = "{base_model}"
    adapter_repo = "{adapter_repo}"
    temperature = {temperature}
    max_tokens = {max_tokens}
    top_p = {top_p}
    seed = {seed}
    subset_size = {effective_subset}

    # Load embedded eval dataset. No raw model outputs are embedded or committed.
    print("\\nLoading embedded KimariEval private v1 dataset...")
    embedded_dataset_b64 = "{embedded_dataset_b64}"
    items = json.loads(base64.b64decode(embedded_dataset_b64).decode("utf-8"))

    print(f"Total items: {{len(items)}}")

    # Subset
    import random

    random.seed(seed)
    if subset_size < len(items):
        items = random.sample(items, subset_size)
    print(f"Subset: {{len(items)}} items")

    categories = {{}}
    for item in items:
        cat = item.get("tags", ["unknown"])[0] if item.get("tags") else "unknown"
        categories[cat] = categories.get(cat, 0) + 1

    # Load model
    print(f"\\nLoading base model: {{base_model}}")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    print(f"Base model loaded. Device: {{model.device}}")

    # Run baseline eval
    print(f"\\nRunning baseline evaluation ({{len(items)}} items)...")
    baseline_results = []
    for i, item in enumerate(items):
        prompt = item["prompt"]
        messages = [{{"role": "user", "content": prompt}}]
        input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                seed=seed,
            )

        generated = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)

        baseline_results.append(
            {{
                "id": item["id"],
                "tags": item.get("tags", []),
                "difficulty": item.get("difficulty", "medium"),
                "generated_length": len(generated),
                "has_error": generated.startswith("ERROR"),
            }}
        )

        if (i + 1) % 10 == 0:
            print(f"  Baseline: {{i + 1}}/{{len(items)}} done")

    print(f"Baseline evaluation complete: {{len(baseline_results)}} items")

    # Load adapter
    print(f"\\nLoading adapter: {{adapter_repo}}")
    from peft import PeftModel

    model = PeftModel.from_pretrained(model, adapter_repo)
    model.eval()
    print("Adapter loaded successfully")

    # Run adapter eval
    print(f"\\nRunning adapter evaluation ({{len(items)}} items)...")
    adapter_results = []
    for i, item in enumerate(items):
        prompt = item["prompt"]
        messages = [{{"role": "user", "content": prompt}}]
        input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                seed=seed,
            )

        generated = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)

        adapter_results.append(
            {{
                "id": item["id"],
                "tags": item.get("tags", []),
                "difficulty": item.get("difficulty", "medium"),
                "generated_length": len(generated),
                "has_error": generated.startswith("ERROR"),
            }}
        )

        if (i + 1) % 10 == 0:
            print(f"  Adapter: {{i + 1}}/{{len(items)}} done")

    print(f"Adapter evaluation complete: {{len(adapter_results)}} items")

    # Generate sanitized summary (NO raw outputs)
    baseline_completion = sum(1 for r in baseline_results if not r["has_error"])
    adapter_completion = sum(1 for r in adapter_results if not r["has_error"])

    summary = {{
        "run_id": f"kimari-eval-{{int(time.time())}}",
        "model_label": "qwen25-15b-base-vs-adapter",
        "base_model": base_model,
        "adapter_repo_private": adapter_repo,
        "dataset_id": "kimari_private_v1",
        "item_count": len(items),
        "categories": categories,
        "baseline": {{
            "completion_rate": round(baseline_completion / len(items), 4) if items else 0,
            "total_items": len(items),
            "completed_items": baseline_completion,
            "error_items": len(items) - baseline_completion,
        }},
        "adapter": {{
            "completion_rate": round(adapter_completion / len(items), 4) if items else 0,
            "total_items": len(items),
            "completed_items": adapter_completion,
            "error_items": len(items) - adapter_completion,
        }},
        "score_status": "not_scored",
        "manual_review_required": True,
        "raw_outputs_committed": False,
        "public_benchmark_allowed": False,
        "gate_state": "BLOCKED",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "seed": seed,
        "subset_size": subset_size,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Evaluation completed. Scores not computed (requires manual review). No benchmark claims. Gate BLOCKED.",
    }}

    summary_path = Path("eval_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\\nSummary written to {{summary_path}}")
    print(f"Baseline completion: {{baseline_completion}}/{{len(items)}} ({{summary['baseline']['completion_rate']}})")
    print(f"Adapter completion: {{adapter_completion}}/{{len(items)}} ({{summary['adapter']['completion_rate']}})")
    print("Score status: not_scored (manual review required)")
    print("Gate: BLOCKED")
    print("NO RAW OUTPUTS COMMITTED. NO BENCHMARK CLAIMS.")


if __name__ == "__main__":
    main()
'''
    return script


def build_hf_jobs_command(config: dict, subset_size: int | None = None) -> list[str]:
    """Build the HF Jobs command as a safe arg list (no shell=True, no .split())."""
    flavor = config.get("hf_jobs_flavor", "a10g-small")
    timeout = config.get("hf_jobs_timeout_minutes", 30)
    # docker_image intentionally not used in command - PEP 723 script is self-contained
    config.get("hf_jobs_docker_image", "pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel")

    script = build_eval_script(config, subset_size)

    # Write script to temp file for reference
    script_path = PROJECT_ROOT / "eval" / "scripts" / "_hf_jobs_eval_inline.py"
    script_path.write_text(script)

    # Build command using hf jobs uv run with PEP 723 inline script
    cmd = [
        "hf",
        "jobs",
        "uv",
        "run",
        "--flavor",
        flavor,
        "--timeout",
        f"{timeout}m",
        "--secrets",
        "HF_TOKEN",
        "--detach",
        str(script_path),
    ]

    return cmd


def dry_run(config: dict, subset_size: int | None = None) -> dict:
    """Generate a dry-run plan without submitting anything."""
    effective_subset = subset_size or config.get("subset_size", 30)

    # Load dataset to count categories
    dataset_dir = PROJECT_ROOT / config.get("dataset_dir", "eval/kimari_private_v1")
    total_items = 0
    categories = {}
    if dataset_dir.exists():
        for jsonl_file in sorted(dataset_dir.glob("*.jsonl")):
            for line in jsonl_file.read_text().strip().split("\n"):
                if line.strip():
                    item = json.loads(line)
                    total_items += 1
                    cat = item.get("tags", ["unknown"])[0]
                    categories[cat] = categories.get(cat, 0) + 1

    # Build command for reference
    cmd = build_hf_jobs_command(config, effective_subset)

    result = {
        "run_type": "dry-run",
        "base_model": config["base_model"],
        "adapter_repo_private": config["adapter_repo_private"],
        "dataset_dir": str(config.get("dataset_dir", "eval/kimari_private_v1")),
        "total_items_available": total_items,
        "subset_size": effective_subset,
        "categories_available": categories,
        "temperature": config.get("temperature", 0.2),
        "max_tokens": config.get("max_tokens", 384),
        "top_p": config.get("top_p", 0.9),
        "seed": config.get("seed", 42),
        "hf_jobs_flavor": config.get("hf_jobs_flavor", "a10g-small"),
        "hf_jobs_timeout_minutes": config.get("hf_jobs_timeout_minutes", 30),
        "docker_image": config.get("hf_jobs_docker_image", "pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel"),
        "estimated_cost_usd": round(effective_subset * 2 * 0.02, 2),  # rough: $0.02 per item per model
        "command": " ".join(cmd),
        "manual_review_required": True,
        "public_benchmark_allowed": False,
        "raw_outputs_commit_allowed": False,
        "gate_state": "BLOCKED",
        "notes": "Dry-run: no HF Jobs submitted. Estimated cost is approximate.",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run KimariEval on HF Jobs")
    parser.add_argument("--config", required=True, help="Path to eval config YAML")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default: true)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--print-command", action="store_true", help="Print HF Jobs command")
    parser.add_argument("--allow-submit", action="store_true", help="Allow real submission (requires --yes)")
    parser.add_argument("--yes", action="store_true", help="Confirm submission")
    parser.add_argument("--require-jobs-access", action="store_true", help="Check HF Jobs access")
    parser.add_argument("--subset-size", type=int, help="Override subset size from config")
    args = parser.parse_args()

    config = load_config(args.config)

    # Validate config safety
    errors = validate_config(config)
    if errors:
        for e in errors:
            print(f"  FAIL: {e}", file=sys.stderr)
        sys.exit(1)

    subset_size = args.subset_size or config.get("subset_size", 30)

    # Dry-run mode (default)
    if not args.allow_submit or not args.yes:
        result = dry_run(config, subset_size)
        if args.print_command:
            print(result["command"])
        elif args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            for k, v in result.items():
                if k != "command":
                    print(f"  {k}: {v}")
            print("\nTo submit for real, use: --allow-submit --yes")
            print("Gate: BLOCKED. No benchmark claims.")
        sys.exit(0)

    # Real submission
    if args.require_jobs_access:
        print("Checking HF Jobs access...")
        import subprocess

        result = subprocess.run(["hf", "jobs", "ps"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: HF Jobs access check failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        print("HF Jobs access: OK")

    # Build and submit
    cmd = build_hf_jobs_command(config, subset_size)
    print("\nSubmitting HF Jobs evaluation...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Subset size: {subset_size}")
    print(f"Estimated cost: ~${round(subset_size * 2 * 0.02, 2)}")
    print("Gate: BLOCKED. No benchmark claims.")
    print("\nProceeding with submission...")

    import subprocess

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
