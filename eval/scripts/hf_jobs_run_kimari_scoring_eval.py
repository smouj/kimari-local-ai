#!/usr/bin/env python3
"""Run private KimariEval scoring on HF Jobs.

Safety:
- Dry-run by default
- Real submission requires --allow-submit --yes
- No token CLI args
- No public upload
- Raw outputs are written only inside private HF Jobs artifacts, never committed
- Logs print sanitized aggregate summary only
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml"


def load_config(config_path: str) -> dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        print(f"ERROR: Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(path.read_text())


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if config.get("public_benchmark_allowed") is True:
        errors.append("public_benchmark_allowed must be false")
    if config.get("raw_outputs_commit_allowed") is True:
        errors.append("raw_outputs_commit_allowed must be false")
    if config.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")
    if config.get("manual_review_required") is not True:
        errors.append("manual_review_required must be true")
    if not config.get("adapter_repo_private"):
        errors.append("adapter_repo_private is required")
    return errors


def load_eval_items(config: dict[str, Any]) -> list[dict[str, Any]]:
    dataset_dir = PROJECT_ROOT / config.get("dataset_dir", "eval/kimari_private_v1")
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
    items: list[dict[str, Any]] = []
    for jsonl_file in sorted(dataset_dir.glob("*.jsonl")):
        for line in jsonl_file.read_text().strip().split("\n"):
            if line.strip():
                items.append(json.loads(line))
    return items


def build_scoring_script(config: dict[str, Any], subset_size: int | None = None) -> str:
    base_model = config["base_model"]
    adapter_repo = config["adapter_repo_private"]
    temperature = config.get("temperature", 0.2)
    max_tokens = config.get("max_tokens", 256)
    top_p = config.get("top_p", 0.9)
    seed = config.get("seed", 42)
    effective_subset = subset_size or config.get("subset_size", 30)

    items = load_eval_items(config)
    embedded_dataset_b64 = base64.b64encode(json.dumps(items, ensure_ascii=False).encode("utf-8")).decode("ascii")

    return f'''# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "torch>=2.5",
#     "transformers>=4.46",
#     "peft>=0.19",
#     "accelerate>=1.0",
# ]
# ///
"""Private KimariEval scoring job.

Writes raw_outputs_private.json and scoring_summary.json inside the private HF
Jobs artifact bucket. Logs only sanitized aggregate metrics.
"""

import base64
import json
import math
import random
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

STOPWORDS = {{
    "the", "and", "for", "with", "that", "this", "from", "are", "you", "your", "should", "use",
    "una", "uno", "para", "con", "que", "por", "los", "las", "del", "como", "debe", "usar",
    "then", "when", "what", "how", "into", "have", "will", "can", "not", "but", "all", "any",
}}


def normalize(text):
    return re.sub(r"\\s+", " ", text.lower()).strip()


def tokens(text):
    raw = re.findall(r"[a-zA-Z0-9_+#./-]{{3,}}", text.lower())
    return [t for t in raw if t not in STOPWORDS and len(t) >= 4]


def score_answer(generated, ideal):
    gen_norm = normalize(generated)
    ideal_norm = normalize(ideal)
    exact = gen_norm == ideal_norm
    containment = ideal_norm in gen_norm or gen_norm in ideal_norm

    ideal_tokens = tokens(ideal)
    gen_tokens = tokens(generated)
    ideal_counts = Counter(ideal_tokens)
    gen_counts = Counter(gen_tokens)
    overlap = sum((ideal_counts & gen_counts).values())
    recall = overlap / max(1, sum(ideal_counts.values()))
    precision = overlap / max(1, sum(gen_counts.values()))
    f1 = 0.0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)

    # Keyword recall uses unique high-signal ideal tokens. This is a lexical proxy, not a benchmark claim.
    unique_ideal = set(ideal_tokens)
    unique_gen = set(gen_tokens)
    keyword_recall = len(unique_ideal & unique_gen) / max(1, len(unique_ideal))

    # Penalize empty/tiny answers; cap verbosity benefit.
    length_ratio = min(len(generated) / max(1, len(ideal)), 1.5)
    length_score = min(length_ratio, 1.0)

    proxy_score = round((0.45 * f1) + (0.35 * keyword_recall) + (0.20 * length_score), 4)
    return {{
        "exact_match": exact,
        "containment": containment,
        "token_precision": round(precision, 4),
        "token_recall": round(recall, 4),
        "token_f1": round(f1, 4),
        "keyword_recall": round(keyword_recall, 4),
        "length_ratio": round(length_ratio, 4),
        "proxy_score": proxy_score,
    }}


def aggregate(rows):
    n = len(rows)
    if not n:
        return {{}}
    keys = ["token_precision", "token_recall", "token_f1", "keyword_recall", "length_ratio", "proxy_score"]
    agg = {{k: round(sum(r["score"][k] for r in rows) / n, 4) for k in keys}}
    agg["exact_match_rate"] = round(sum(1 for r in rows if r["score"]["exact_match"]) / n, 4)
    agg["containment_rate"] = round(sum(1 for r in rows if r["score"]["containment"]) / n, 4)
    agg["completion_rate"] = round(sum(1 for r in rows if not r.get("has_error")) / n, 4)
    agg["total_items"] = n
    return agg


def generate_one(model, tokenizer, item, temperature, top_p, max_tokens):
    messages = [{{"role": "user", "content": item["prompt"]}}]
    input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    import torch
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
        )
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def main():
    print("=" * 60)
    print("KimariEval Private Scoring — Baseline vs Adapter")
    print("=" * 60)

    base_model = "{base_model}"
    adapter_repo = "{adapter_repo}"
    temperature = {temperature}
    max_tokens = {max_tokens}
    top_p = {top_p}
    seed = {seed}
    subset_size = {effective_subset}

    random.seed(seed)
    items = json.loads(base64.b64decode("{embedded_dataset_b64}").decode("utf-8"))
    if subset_size < len(items):
        items = random.sample(items, subset_size)
    print(f"Items: {{len(items)}}")

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

    set_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    print("Base model loaded")

    baseline_rows = []
    for i, item in enumerate(items):
        try:
            generated = generate_one(model, tokenizer, item, temperature, top_p, max_tokens)
            has_error = generated.startswith("ERROR")
        except Exception as e:
            generated = f"ERROR: {{type(e).__name__}}"
            has_error = True
        baseline_rows.append({{
            "id": item["id"],
            "tags": item.get("tags", []),
            "difficulty": item.get("difficulty", "medium"),
            "generated": generated,
            "ideal": item["ideal"],
            "has_error": has_error,
            "score": score_answer(generated, item["ideal"]),
        }})
        if (i + 1) % 10 == 0:
            print(f"  Baseline scored: {{i + 1}}/{{len(items)}}")

    model = PeftModel.from_pretrained(model, adapter_repo)
    model.eval()
    print("Adapter loaded")

    adapter_rows = []
    for i, item in enumerate(items):
        try:
            generated = generate_one(model, tokenizer, item, temperature, top_p, max_tokens)
            has_error = generated.startswith("ERROR")
        except Exception as e:
            generated = f"ERROR: {{type(e).__name__}}"
            has_error = True
        adapter_rows.append({{
            "id": item["id"],
            "tags": item.get("tags", []),
            "difficulty": item.get("difficulty", "medium"),
            "generated": generated,
            "ideal": item["ideal"],
            "has_error": has_error,
            "score": score_answer(generated, item["ideal"]),
        }})
        if (i + 1) % 10 == 0:
            print(f"  Adapter scored: {{i + 1}}/{{len(items)}}")

    baseline = aggregate(baseline_rows)
    adapter = aggregate(adapter_rows)
    deltas = {{k: round(adapter.get(k, 0) - baseline.get(k, 0), 4) for k in ["token_f1", "keyword_recall", "proxy_score", "completion_rate"]}}
    adapter_wins = sum(1 for b, a in zip(baseline_rows, adapter_rows) if a["score"]["proxy_score"] > b["score"]["proxy_score"])
    baseline_wins = sum(1 for b, a in zip(baseline_rows, adapter_rows) if b["score"]["proxy_score"] > a["score"]["proxy_score"])
    ties = len(items) - adapter_wins - baseline_wins

    raw = {{
        "warning": "PRIVATE ARTIFACT ONLY. DO NOT COMMIT RAW OUTPUTS.",
        "base_model": base_model,
        "adapter_repo_private": adapter_repo,
        "items": len(items),
        "baseline_rows": baseline_rows,
        "adapter_rows": adapter_rows,
    }}
    Path("raw_outputs_private.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False))

    summary = {{
        "run_id": f"kimari-scoring-{{int(time.time())}}",
        "base_model": base_model,
        "adapter_repo_private": adapter_repo,
        "dataset_id": "kimari_private_v1",
        "subset_size": len(items),
        "status": "completed",
        "score_status": "scored_private_proxy",
        "baseline": baseline,
        "adapter": adapter,
        "deltas_adapter_minus_baseline": deltas,
        "adapter_proxy_wins": adapter_wins,
        "baseline_proxy_wins": baseline_wins,
        "proxy_ties": ties,
        "raw_outputs_artifact": "raw_outputs_private.json",
        "raw_outputs_committed": False,
        "public_benchmark_allowed": False,
        "manual_review_required": True,
        "gate_state": "BLOCKED",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "seed": seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Private lexical proxy scoring only. Not a public benchmark. Manual review required.",
    }}
    Path("scoring_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    print("SCORING_SUMMARY_JSON_START")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("SCORING_SUMMARY_JSON_END")
    print("NO RAW OUTPUTS COMMITTED. NO PUBLIC BENCHMARK CLAIMS. GATE BLOCKED.")


if __name__ == "__main__":
    main()
'''


def build_hf_jobs_command(config: dict[str, Any], subset_size: int | None = None) -> list[str]:
    script = build_scoring_script(config, subset_size=subset_size)
    script_path = PROJECT_ROOT / "eval" / "scripts" / "_hf_jobs_scoring_inline.py"
    script_path.write_text(script)
    return [
        "hf",
        "jobs",
        "uv",
        "run",
        "--flavor",
        config.get("hf_jobs_flavor", "a10g-small"),
        "--timeout",
        f"{config.get('hf_jobs_timeout_minutes', 30)}m",
        "--secrets",
        "HF_TOKEN",
        "--detach",
        str(script_path),
    ]


def dry_run(config: dict[str, Any], subset_size: int | None = None) -> dict[str, Any]:
    items = load_eval_items(config)
    effective_subset = subset_size or config.get("subset_size", 30)
    cmd = build_hf_jobs_command(config, subset_size=effective_subset)
    return {
        "run_type": "dry-run",
        "base_model": config["base_model"],
        "adapter_repo_private": config["adapter_repo_private"],
        "total_items_available": len(items),
        "subset_size": effective_subset,
        "command": " ".join(cmd),
        "raw_outputs_committed": False,
        "public_benchmark_allowed": False,
        "gate_state": "BLOCKED",
        "notes": "Dry-run only. Raw outputs will be private artifacts if submitted.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run private KimariEval scoring on HF Jobs")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to eval config YAML")
    parser.add_argument("--subset-size", type=int, default=None, help="Subset size override")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run by default")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--print-command", action="store_true", help="Print HF Jobs command")
    parser.add_argument("--allow-submit", action="store_true", help="Allow real submission")
    parser.add_argument("--yes", action="store_true", help="Confirm real submission")
    parser.add_argument("--require-jobs-access", action="store_true", help="Check HF Jobs access")
    args = parser.parse_args()

    config = load_config(args.config)
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)

    subset_size = args.subset_size or config.get("subset_size", 30)
    if not args.allow_submit or not args.yes:
        result = dry_run(config, subset_size=subset_size)
        if args.print_command:
            print(result["command"])
        elif args.json:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
        sys.exit(0)

    if args.require_jobs_access:
        proc = subprocess.run(["hf", "jobs", "ps"], capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            print("ERROR: HF Jobs access check failed", file=sys.stderr)
            sys.exit(1)

    cmd = build_hf_jobs_command(config, subset_size=subset_size)
    print("Submitting private scoring job...")
    print(f"Command: {' '.join(cmd)}")
    print("Raw outputs: private job artifact only. Gate: BLOCKED.")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
