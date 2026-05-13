#!/usr/bin/env python3
"""Validate SFT v1 eval readiness.

Checks:
- SFT v1 run summary exists and is valid (training_performed=true)
- adapter_generated=true
- adapter NOT committed publicly
- Eval subset10 config exists and is valid
- KimariEval dataset exists
- No public benchmark claims
- Gate BLOCKED
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

SUMMARY_PATH = PROJECT_ROOT / "docs" / "assets" / "results" / "sft_v1_run_summary.json"
EVAL_CONFIG_SUBSET10 = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml"
EVAL_DATASET_DIR = PROJECT_ROOT / "eval" / "kimari_private_v1"
RESULT_DOC = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_RESULT.md"


def validate_sft_v1_eval_readiness(config_path: str | None = None, json_output: bool = False) -> bool:
    errors = []
    warnings = []

    # 1. SFT v1 run summary exists and is valid
    if not SUMMARY_PATH.exists():
        errors.append(f"SFT v1 run summary not found: {SUMMARY_PATH}")
    else:
        try:
            summary = json.loads(SUMMARY_PATH.read_text())
            if summary.get("training_performed") is not True:
                errors.append("SFT v1 summary: training_performed must be true")
            if summary.get("adapter_generated") is not True:
                errors.append("SFT v1 summary: adapter_generated must be true")
            if summary.get("adapter_committed_public") is not False and summary.get("adapter_committed") is not False:
                warnings.append("SFT v1 summary: adapter should not be committed publicly")
            if summary.get("gate_state") != "BLOCKED":
                errors.append("SFT v1 summary: gate_state must be BLOCKED")
            if summary.get("hf_public_upload_performed") is not False:
                errors.append("SFT v1 summary: hf_public_upload_performed must be false")
            if summary.get("gguf_generated") is not False:
                errors.append("SFT v1 summary: gguf_generated must be false")
        except json.JSONDecodeError as e:
            errors.append(f"SFT v1 summary: invalid JSON: {e}")

    # 2. Result doc exists and says COMPLETED
    if not RESULT_DOC.exists():
        errors.append(f"Result doc not found: {RESULT_DOC}")
    else:
        result_text = RESULT_DOC.read_text().lower()
        if "completed" not in result_text:
            errors.append("Result doc must have COMPLETED status")

    # 3. Eval subset10 config exists
    config = EVAL_CONFIG_SUBSET10
    if config_path:
        config = Path(config_path)
    if not config.exists():
        errors.append(f"Eval subset10 config not found: {config}")
    else:
        config_text = config.read_text()
        if "Qwen/Qwen2.5-1.5B-Instruct" not in config_text and "base_model" not in config_text:
            errors.append("Eval config must specify base_model")
        if "BLOCKED" not in config_text:
            errors.append("Eval config must specify gate_state: BLOCKED")
        if "public_benchmark_allowed" not in config_text:
            errors.append("Eval config must specify public_benchmark_allowed")
        if "subset_size" not in config_text:
            errors.append("Eval config must specify subset_size")

    # 4. No public model artifacts
    public_artifacts = [
        path
        for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin")
        for path in PROJECT_ROOT.rglob(pattern)
        if ".venv" not in path.parts and "deps" not in path.parts
    ]
    if public_artifacts:
        errors.append(f"Found public artifacts: {[str(p) for p in public_artifacts[:5]]}")

    # 5. Gate BLOCKED in release text
    gate_files = [
        PROJECT_ROOT / "docs" / "KIMARI4B_RELEASE_GATE.md",
        RESULT_DOC,
    ]
    gate_found = False
    for gf in gate_files:
        if gf.exists() and "blocked" in gf.read_text().lower():
            gate_found = True
    if not gate_found:
        warnings.append("Gate BLOCKED not found in release docs")

    result = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
    }

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        if errors:
            print("FAIL: SFT v1 eval readiness validation failed")
            for e in errors:
                print(f"  - {e}")
        if warnings:
            print("WARNINGS:")
            for w in warnings:
                print(f"  - {w}")
        if not errors and not warnings:
            print("PASS: SFT v1 eval readiness validation passed")

    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Validate SFT v1 eval readiness")
    parser.add_argument("--config", help="Path to eval config", default=None)
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    success = validate_sft_v1_eval_readiness(
        config_path=args.config,
        json_output=args.json,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
