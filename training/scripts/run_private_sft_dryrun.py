#!/usr/bin/env python3
"""CLI dry-run validation for private SFT training.

Reads a private SFT run config YAML and validates:
- Dataset build exists or gives commands to build it
- Base model is defined (not TBD)
- public_release_allowed is false
- hf_upload_allowed is false
- output_dir is gitignored

Prints: commands_to_run, expected_outputs, blocked_public_actions,
readiness_status.

No actual training, no downloads, no network.

Usage:
    python training/scripts/run_private_sft_dryrun.py \\
        --run-config training/configs/private_sft_run.v0.yaml
    python training/scripts/run_private_sft_dryrun.py \\
        --run-config training/configs/private_sft_run.v0.yaml --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse YAML with PyYAML fallback to simple parser.

    Returns None if parsing fails.
    """
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    # Simple fallback parser for flat/mostly-flat YAML
    text = path.read_text()
    result: dict = {}
    current_list_key: str | None = None
    current_list: list | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List item under a key
        if stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(item)
            continue

        # Key: value
        if ":" in stripped:
            # Close any previous list
            if current_list_key is not None and current_list is not None:
                result[current_list_key] = current_list
                current_list_key = None
                current_list = None

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if not value:
                # Could be a list start
                current_list_key = key
                current_list = []
            else:
                # Try boolean conversion
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                else:
                    try:
                        result[key] = int(value)
                    except ValueError:
                        try:
                            result[key] = float(value)
                        except ValueError:
                            result[key] = value

    # Close any trailing list
    if current_list_key is not None and current_list is not None:
        result[current_list_key] = current_list

    return result


def is_gitignored(path: Path) -> bool:
    """Check if a path is covered by .gitignore.

    Uses git check-ignore if available, otherwise checks
    the root .gitignore file for matching patterns.
    """
    try:
        result = subprocess.run(
            ["git", "check-ignore", str(path)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: check .gitignore patterns manually
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if not gitignore_path.exists():
        return False

    try:
        gitignore_text = gitignore_path.read_text()
    except OSError:
        return False

    # Convert the path to a relative path from project root
    try:
        rel_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        rel_path = path

    rel_str = str(rel_path)

    for pattern in gitignore_text.splitlines():
        pattern = pattern.strip()
        if not pattern or pattern.startswith("#"):
            continue
        # Simple prefix matching for directory patterns
        if pattern.endswith("/") and (rel_str.startswith(pattern) or rel_str.startswith(pattern.rstrip("/"))):
            return True
        # Wildcard matching for *.ext patterns
        if pattern.startswith("*."):
            suffix = pattern[1:]  # e.g. ".gguf"
            if rel_str.endswith(suffix):
                return True
        # Exact match
        if rel_str == pattern or rel_str.startswith(pattern + "/"):
            return True

    return False


def validate_private_sft_config(config: dict, config_path: Path) -> dict:
    """Validate a private SFT run config and return structured results.

    Returns a dict with:
        commands_to_run: list of commands that would be executed
        expected_outputs: list of expected output artifacts
        blocked_public_actions: list of blocked public-facing actions
        readiness_status: "ready" | "not_ready" | "partial"
        warnings: list of warnings
        checks: dict of individual check results
    """
    commands_to_run: list[str] = []
    expected_outputs: list[str] = []
    blocked_public_actions: list[str] = []
    warnings: list[str] = []
    checks: dict[str, dict] = {}

    all_pass = True

    # Check 1: base_model is defined (not TBD, not empty)
    base_model = config.get("base_model") or config.get("base_model_or_adapter")
    if not base_model or base_model == "TBD":
        checks["base_model"] = {
            "status": "FAIL",
            "message": "Base model is not defined (found TBD or empty)",
        }
        all_pass = False
    else:
        checks["base_model"] = {
            "status": "PASS",
            "value": base_model,
        }

    # Check 2: dataset_path exists or give build commands
    dataset_path = config.get("dataset_path") or config.get("preference_dataset_path")
    if not dataset_path or dataset_path == "TBD":
        checks["dataset_path"] = {
            "status": "FAIL",
            "message": "Dataset path is not defined",
        }
        all_pass = False
    else:
        dp = Path(dataset_path)
        if not dp.is_absolute():
            dp = PROJECT_ROOT / dp

        if dp.exists():
            checks["dataset_path"] = {
                "status": "PASS",
                "value": dataset_path,
                "exists": True,
            }
        else:
            checks["dataset_path"] = {
                "status": "WARN",
                "value": dataset_path,
                "exists": False,
                "message": "Dataset path does not exist on disk — build it first",
            }
            # Provide commands to build the dataset
            build_cmd = (
                "python training/scripts/build_dataset_mix.py "
                "--sft dataset/v0/sft_v0.jsonl "
                "--preference dataset/v0/preference_v0.jsonl "
                "--output-dir dataset/build/kimari-v0 "
                "--holdout dataset/v0/eval_holdout.jsonl"
            )
            commands_to_run.append(build_cmd)
            warnings.append(f"Dataset not found at {dataset_path} — run build_dataset_mix.py first")

    # Check 3: eval_dataset_path
    eval_dataset_path = config.get("eval_dataset_path")
    if eval_dataset_path and eval_dataset_path != "TBD":
        edp = Path(eval_dataset_path)
        if not edp.is_absolute():
            edp = PROJECT_ROOT / edp
        if not edp.exists():
            warnings.append(f"Eval dataset not found at {eval_dataset_path}")

    # Check 4: public_release_allowed is false
    public_allowed = config.get("public_release_allowed")
    if public_allowed is True:
        checks["public_release_allowed"] = {
            "status": "FAIL",
            "message": "public_release_allowed must be false for private SFT",
        }
        blocked_public_actions.append("public_release — config has public_release_allowed=true")
        all_pass = False
    elif public_allowed is False:
        checks["public_release_allowed"] = {
            "status": "PASS",
            "value": False,
        }
        blocked_public_actions.append("public_release — blocked by config (public_release_allowed=false)")
    else:
        checks["public_release_allowed"] = {
            "status": "WARN",
            "message": "public_release_allowed not specified — assuming false for private SFT",
        }
        blocked_public_actions.append("public_release — assumed blocked (key not specified)")

    # Check 5: hf_upload_allowed is false
    hf_upload = config.get("hf_upload_allowed")
    if hf_upload is True:
        checks["hf_upload_allowed"] = {
            "status": "FAIL",
            "message": "hf_upload_allowed must be false for private SFT",
        }
        blocked_public_actions.append("HF upload — config has hf_upload_allowed=true")
        all_pass = False
    elif hf_upload is False:
        checks["hf_upload_allowed"] = {
            "status": "PASS",
            "value": False,
        }
        blocked_public_actions.append("HF upload — blocked by config (hf_upload_allowed=false)")
    else:
        checks["hf_upload_allowed"] = {
            "status": "WARN",
            "message": "hf_upload_allowed not specified — assuming false for private SFT",
        }
        blocked_public_actions.append("HF upload — assumed blocked (key not specified)")

    # Check 6: output_dir is gitignored
    output_dir = config.get("output_dir")
    if not output_dir:
        checks["output_dir_gitignored"] = {
            "status": "FAIL",
            "message": "No output_dir specified in config",
        }
        all_pass = False
    else:
        od = Path(output_dir)
        if not od.is_absolute():
            od = PROJECT_ROOT / od

        if is_gitignored(od):
            checks["output_dir_gitignored"] = {
                "status": "PASS",
                "value": output_dir,
                "gitignored": True,
            }
        else:
            checks["output_dir_gitignored"] = {
                "status": "FAIL",
                "value": output_dir,
                "gitignored": False,
                "message": "output_dir is NOT gitignored — training artifacts could be committed",
            }
            warnings.append(f"output_dir {output_dir} is not gitignored — add to .gitignore")
            all_pass = False

    # Build commands_to_run and expected_outputs
    if base_model and base_model != "TBD":
        config_flag = f"--config {config_path}"
        commands_to_run.append(f"python training/scripts/train_sft_lora.py {config_flag} --dry-run")

        # Build expected outputs from output_dir
        if output_dir:
            expected_outputs.extend(
                [
                    f"{output_dir}/adapter_config.json",
                    f"{output_dir}/adapter_model.safetensors",
                    f"{output_dir}/tokenizer.json",
                    f"{output_dir}/trainer_state.json",
                    f"{output_dir}/training_args.bin",
                ]
            )

        # GGUF export plan
        if output_dir:
            commands_to_run.append(
                f"python training/scripts/export_gguf_plan.py "
                f"--model-dir {output_dir} --output-dir {output_dir}/gguf --dry-run"
            )
            expected_outputs.extend(
                [
                    f"{output_dir}/gguf/model-f16.gguf",
                    f"{output_dir}/gguf/model-q4_k_m.gguf",
                ]
            )

    # Determine readiness status
    if all_pass and not warnings:
        readiness_status = "ready"
    elif all_pass and warnings:
        readiness_status = "partial"
    else:
        readiness_status = "not_ready"

    return {
        "commands_to_run": commands_to_run,
        "expected_outputs": expected_outputs,
        "blocked_public_actions": blocked_public_actions,
        "readiness_status": readiness_status,
        "warnings": warnings,
        "checks": checks,
    }


def main() -> None:
    """CLI entry point for private SFT dry-run validation."""
    parser = argparse.ArgumentParser(
        description="CLI dry-run validation for private SFT training. No actual training, no downloads, no network.",
    )
    parser.add_argument(
        "--run-config",
        type=Path,
        required=True,
        help="Path to private_sft_run.v0.yaml config file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )

    args = parser.parse_args()

    # Load config
    config_path = args.run_config
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading config: {config_path}", file=sys.stderr)
    config = parse_simple_yaml(config_path)

    if config is None:
        print(f"ERROR: Failed to parse config file: {config_path}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(config, dict):
        print("ERROR: Config file does not contain a valid YAML mapping.", file=sys.stderr)
        sys.exit(1)

    # Validate
    result = validate_private_sft_config(config, config_path)

    # Output
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 60)
        print("  Private SFT Dry-Run Validation")
        print("=" * 60)
        print()

        # Checks
        print("Checks:")
        for name, check in result["checks"].items():
            status = check["status"]
            symbol = {"PASS": "OK", "WARN": "!!", "FAIL": "XX"}.get(status, "??")
            value_str = f" ({check.get('value', '')})" if "value" in check else ""
            msg = f" — {check.get('message', '')}" if "message" in check else ""
            print(f"  [{symbol}] {name}{value_str}{msg}")

        # Commands to run
        print("\nCommands to Run:")
        for cmd in result["commands_to_run"]:
            print(f"  $ {cmd}")

        # Expected outputs
        print("\nExpected Outputs:")
        for out in result["expected_outputs"]:
            print(f"  - {out}")

        # Blocked actions
        print("\nBlocked Public Actions:")
        for action in result["blocked_public_actions"]:
            print(f"  [BLOCKED] {action}")

        # Warnings
        if result["warnings"]:
            print("\nWarnings:")
            for warning in result["warnings"]:
                print(f"  WARNING: {warning}")

        # Readiness
        print()
        print("=" * 60)
        readiness = result["readiness_status"]
        if readiness == "ready":
            print("  Readiness: READY — all checks passed")
        elif readiness == "partial":
            print("  Readiness: PARTIAL — passed with warnings (review above)")
        else:
            print("  Readiness: NOT READY — fix failures above before training")
        print("=" * 60)
        print("\nNo training was performed. No downloads. No network calls.")

    sys.exit(0 if result["readiness_status"] != "not_ready" else 1)


if __name__ == "__main__":
    main()
