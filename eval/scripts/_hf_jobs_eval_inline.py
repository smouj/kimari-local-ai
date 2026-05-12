# /// script
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

import json
import sys
import time
from pathlib import Path

def main():
    print("=" * 60)
    print("KimariEval Baseline vs Adapter Evaluation")
    print("=" * 60)

    base_model = "Qwen/Qwen2.5-1.5B-Instruct"
    adapter_repo = "Smouj013/kimari4b-micro-sft-adapter-v0"
    temperature = 0.2
    max_tokens = 384
    top_p = 0.9
    seed = 42
    subset_size = 30

    # Load eval dataset
    print(f"\nLoading dataset from eval/kimari_private_v1/...")
    dataset_dir = Path("eval/kimari_private_v1")
    if not dataset_dir.exists():
        print("ERROR: Dataset directory not found", file=sys.stderr)
        sys.exit(1)

    items = []
    for jsonl_file in sorted(dataset_dir.glob("*.jsonl")):
        for line in jsonl_file.read_text().strip().split("\n"):
            if line.strip():
                items.append(json.loads(line))

    print(f"Total items: {len(items)}")

    # Subset
    import random
    random.seed(seed)
    if subset_size < len(items):
        items = random.sample(items, subset_size)
    print(f"Subset: {len(items)} items")

    categories = {}
    for item in items:
        cat = item.get("tags", ["unknown"])[0] if item.get("tags") else "unknown"
        categories[cat] = categories.get(cat, 0) + 1

    # Load model
    print(f"\nLoading base model: {base_model}")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    print(f"Base model loaded. Device: {model.device}")

    # Run baseline eval
    print(f"\nRunning baseline evaluation ({len(items)} items)...")
    baseline_results = []
    for i, item in enumerate(items):
        prompt = item["prompt"]
        messages = [{"role": "user", "content": prompt}]
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

        generated = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        baseline_results.append({
            "id": item["id"],
            "tags": item.get("tags", []),
            "difficulty": item.get("difficulty", "medium"),
            "generated_length": len(generated),
            "has_error": generated.startswith("ERROR"),
        })

        if (i + 1) % 10 == 0:
            print(f"  Baseline: {i + 1}/{len(items)} done")

    print(f"Baseline evaluation complete: {len(baseline_results)} items")

    # Load adapter
    print(f"\nLoading adapter: {adapter_repo}")
    from peft import PeftModel

    model = PeftModel.from_pretrained(model, adapter_repo)
    model.eval()
    print("Adapter loaded successfully")

    # Run adapter eval
    print(f"\nRunning adapter evaluation ({len(items)} items)...")
    adapter_results = []
    for i, item in enumerate(items):
        prompt = item["prompt"]
        messages = [{"role": "user", "content": prompt}]
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

        generated = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        adapter_results.append({
            "id": item["id"],
            "tags": item.get("tags", []),
            "difficulty": item.get("difficulty", "medium"),
            "generated_length": len(generated),
            "has_error": generated.startswith("ERROR"),
        })

        if (i + 1) % 10 == 0:
            print(f"  Adapter: {i + 1}/{len(items)} done")

    print(f"Adapter evaluation complete: {len(adapter_results)} items")

    # Generate sanitized summary (NO raw outputs)
    baseline_completion = sum(1 for r in baseline_results if not r["has_error"])
    adapter_completion = sum(1 for r in adapter_results if not r["has_error"])

    summary = {
        "run_id": f"kimari-eval-{int(time.time())}",
        "model_label": "qwen25-15b-base-vs-adapter",
        "base_model": base_model,
        "adapter_repo_private": adapter_repo,
        "dataset_id": "kimari_private_v1",
        "item_count": len(items),
        "categories": categories,
        "baseline": {
            "completion_rate": round(baseline_completion / len(items), 4) if items else 0,
            "total_items": len(items),
            "completed_items": baseline_completion,
            "error_items": len(items) - baseline_completion,
        },
        "adapter": {
            "completion_rate": round(adapter_completion / len(items), 4) if items else 0,
            "total_items": len(items),
            "completed_items": adapter_completion,
            "error_items": len(items) - adapter_completion,
        },
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
    }

    summary_path = Path("eval_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nSummary written to {summary_path}")
    print(f"Baseline completion: {baseline_completion}/{len(items)} ({summary['baseline']['completion_rate']})")
    print(f"Adapter completion: {adapter_completion}/{len(items)} ({summary['adapter']['completion_rate']})")
    print(f"Score status: not_scored (manual review required)")
    print(f"Gate: BLOCKED")
    print(f"NO RAW OUTPUTS COMMITTED. NO BENCHMARK CLAIMS.")

if __name__ == "__main__":
    main()
