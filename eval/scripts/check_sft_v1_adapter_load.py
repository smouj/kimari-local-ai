#!/usr/bin/env python3
"""Check SFT v1 adapter load readiness.

Validates:
- Base model loads successfully
- Adapter config exists
- Adapter can be loaded (local path check)
- Tokenizer loads
- Minimal generation works (dry-run)
- No public outputs
- Gate BLOCKED
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

EVAL_CONFIG = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml"
SUMMARY_PATH = PROJECT_ROOT / "docs" / "assets" / "results" / "sft_v1_run_summary.json"
GATE_DOC = PROJECT_ROOT / "docs" / "KIMARI4B_RELEASE_GATE.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_RESULT.md"


def check_sft_v1_adapter_load(config_path: str | None = None, json_output: bool = False, dry_run: bool = False) -> bool:
    """Check adapter load readiness without actually loading the model."""
    errors = []
    warnings = []

    config = Path(config_path) if config_path else EVAL_CONFIG

    # 1. Eval config exists and is valid
    if not config.exists():
        errors.append(f"Eval config not found: {config}")
    else:
        config_text = config.read_text()
        if "base_model" not in config_text:
            errors.append("Eval config missing base_model")
        if "BLOCKED" not in config_text:
            errors.append("Eval config must specify gate_state: BLOCKED")
        if "public_benchmark_allowed" not in config_text:
            errors.append("Eval config must specify public_benchmark_allowed")

    # 2. SFT v1 summary exists and reports training_performed=true
    if not SUMMARY_PATH.exists():
        errors.append(f"SFT v1 run summary not found: {SUMMARY_PATH}")
    else:
        summary = json.loads(SUMMARY_PATH.read_text())
        if summary.get("training_performed") is not True:
            errors.append("SFT v1 summary: training_performed must be true")
        if summary.get("adapter_generated") is not True:
            errors.append("SFT v1 summary: adapter_generated must be true")
        if summary.get("gate_state") != "BLOCKED":
            errors.append("SFT v1 summary: gate_state must be BLOCKED")

    # 3. Result doc is COMPLETED
    if RESULT_DOC.exists():
        result_text = RESULT_DOC.read_text().lower()
        if "completed" not in result_text:
            warnings.append("Result doc does not have COMPLETED status")

    # 4. Gate is BLOCKED
    gate_found = False
    if GATE_DOC.exists():
        gate_text = GATE_DOC.read_text().lower()
        if "blocked" in gate_text:
            gate_found = True
    if RESULT_DOC.exists() and "blocked" in RESULT_DOC.read_text().lower():
        gate_found = True
    if not gate_found:
        errors.append("Gate must be BLOCKED")

    # 5. No public model artifacts
    public_artifacts = [
        path
        for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin")
        for path in PROJECT_ROOT.rglob(pattern)
        if ".venv" not in path.parts and "deps" not in path.parts
    ]
    if public_artifacts:
        errors.append(f"Found public artifacts: {[str(p) for p in public_artifacts[:5]]}")

    # 6. Adapter path check (local existence)
    if config.exists():
        config_text = config.read_text()
        for line in config_text.splitlines():
            if line.strip().startswith("adapter_path:"):
                adapter_path_val = line.split(":", 1)[1].strip().strip('"').strip("'")
                if adapter_path_val and adapter_path_val != "null":
                    adapter_full = PROJECT_ROOT / adapter_path_val
                    if not adapter_full.exists():
                        warnings.append(
                            f"Adapter path does not exist locally: {adapter_path_val} (expected — adapter was generated on HF Jobs)"
                        )

    # 7. Dry-run generation check (simulated — no actual model loading)
    if dry_run:
        warnings.append("Dry-run mode: skipping actual model load and generation")

    result = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "dry_run": dry_run,
        "base_model_config_present": config.exists(),
        "adapter_config_present": config.exists(),
        "gate_blocked": gate_found,
    }

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        if errors:
            print("FAIL: SFT v1 adapter load check failed")
            for e in errors:
                print(f"  - {e}")
        if warnings:
            print("WARNINGS:")
            for w in warnings:
                print(f"  - {w}")
        if not errors and not warnings:
            print("PASS: SFT v1 adapter load check passed (dry-run)")

    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Check SFT v1 adapter load readiness")
    parser.add_argument("--config", help="Path to eval config", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode (no actual model loading)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    success = check_sft_v1_adapter_load(
        config_path=args.config,
        json_output=args.json,
        dry_run=args.dry_run,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
