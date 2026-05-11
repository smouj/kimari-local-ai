#!/usr/bin/env python3
"""CLI post-training orchestration for private SFT runs.

Orchestrates post-training steps:
1. create_adapter_manifest (calls script as subprocess)
2. create_eval_summary (calls script as subprocess)
3. compare_runs if baseline exists (calls as subprocess)
4. verify gate still BLOCKED
5. suggest next steps
6. never commits anything
7. dry-run by default (use --no-dry-run for real execution)

No real training. No model downloads. No HF uploads. No git commits.

Usage:
    python training/scripts/postrun_private_sft.py \\
        --run-config training/configs/private_sft_run.v0.yaml \\
        --adapter-dir training/adapters/kimari-smollm3-sft-v0 \\
        --eval-result eval/results/adapter-private.json \\
        --dry-run
    python training/scripts/postrun_private_sft.py \\
        --run-config training/configs/private_sft_run.v0.yaml \\
        --adapter-dir training/adapters/kimari-smollm3-sft-v0 \\
        --eval-result eval/results/adapter-private.json \\
        --no-dry-run \\
        --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_RUN_CONFIG = PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml"
DEFAULT_ADAPTER_DIR = PROJECT_ROOT / "training" / "adapters" / "kimari-smollm3-sft-v0"
DEFAULT_EVAL_RESULT = PROJECT_ROOT / "eval" / "results" / "adapter-private.json"
DEFAULT_OUTPUT_SUMMARY = Path("/tmp/adapter-summary.json")

# Scripts called as subprocesses
SCRIPTS_DIR = PROJECT_ROOT / "training" / "scripts"
EVAL_SCRIPTS_DIR = PROJECT_ROOT / "eval" / "scripts"

BASELINE_RESULT_PATH = PROJECT_ROOT / "eval" / "results" / "baseline-smollm3-private.json"

# Next step suggestions
NEXT_STEPS = [
    "Review the adapter manifest for accuracy",
    "Run manual eval against the KimariFit rubric",
    "Check eval results for safety regressions",
    "Compare against baseline if available",
    "Do NOT commit any safetensors/bin/pt/gguf files",
    "Verify preview gate is still BLOCKED in docs/ADAPTER_PREVIEW_GATE.md",
    "If results are promising, proceed to ORPO/DPO (see docs/SFT_TO_ORPO_DECISION.md)",
    "Document findings in the private training runbook",
]


# ---------------------------------------------------------------------------
# YAML parser with pyyaml fallback
# ---------------------------------------------------------------------------


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse YAML with pyyaml fallback to simple line parser."""
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    text = path.read_text(encoding="utf-8")
    result: dict = {}
    current_list_key: str | None = None
    current_list: list | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(item)
            continue

        if ":" in stripped:
            if current_list_key is not None and current_list is not None:
                result[current_list_key] = current_list
                current_list_key = None
                current_list = None

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if not value:
                current_list_key = key
                current_list = []
            else:
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                elif value.lower() in ("null", "~", "none"):
                    result[key] = None
                else:
                    try:
                        result[key] = int(value)
                    except ValueError:
                        try:
                            result[key] = float(value)
                        except ValueError:
                            result[key] = value

    if current_list_key is not None and current_list is not None:
        result[current_list_key] = current_list

    return result


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------


def run_subcommand(cmd: list[str], dry_run: bool, label: str) -> dict:
    """Run a subcommand as subprocess (or just report if dry-run).

    Returns a dict with status, command, and output/error.
    """
    result: dict = {
        "label": label,
        "command": " ".join(cmd),
        "status": "skipped" if dry_run else "pending",
        "stdout": None,
        "stderr": None,
        "returncode": None,
    }

    if dry_run:
        result["status"] = "dry_run"
        return result

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT),
        )
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout[:2000] if proc.stdout else None
        result["stderr"] = proc.stderr[:2000] if proc.stderr else None
        result["status"] = "success" if proc.returncode == 0 else "failed"
    except FileNotFoundError:
        result["status"] = "error"
        result["stderr"] = f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["stderr"] = f"Command timed out: {cmd[0]}"

    return result


# ---------------------------------------------------------------------------
# Orchestration steps
# ---------------------------------------------------------------------------


def step_create_adapter_manifest(
    run_config_path: Path,
    adapter_dir: Path,
    dry_run: bool,
) -> dict:
    """Step 1: Create adapter manifest."""
    script = SCRIPTS_DIR / "create_adapter_manifest.py"
    manifest_output = adapter_dir / "MANIFEST.yaml"

    cmd = [
        sys.executable,
        str(script),
        "--run-config",
        str(run_config_path),
        "--adapter-dir",
        str(adapter_dir),
        "--output",
        str(manifest_output),
    ]
    if dry_run:
        cmd.append("--dry-run")

    return run_subcommand(cmd, dry_run, "create_adapter_manifest")


def step_create_eval_summary(
    eval_result_path: Path,
    output_summary: Path,
    dry_run: bool,
) -> dict:
    """Step 2: Create eval summary from eval results."""
    script = EVAL_SCRIPTS_DIR / "create_eval_summary.py"

    if not eval_result_path.exists() and not dry_run:
        return {
            "label": "create_eval_summary",
            "command": f"python {script} --input {eval_result_path} --output {output_summary}",
            "status": "skipped",
            "stdout": None,
            "stderr": f"Eval result file not found: {eval_result_path}",
            "returncode": None,
        }

    cmd = [
        sys.executable,
        str(script),
        "--input",
        str(eval_result_path),
        "--output",
        str(output_summary),
    ]

    result = run_subcommand(cmd, dry_run, "create_eval_summary")
    if not dry_run:
        result["command"] += " --json"
    return result


def step_compare_runs(
    baseline_path: Path,
    candidate_path: Path,
    dry_run: bool,
) -> dict:
    """Step 3: Compare runs if baseline exists."""
    script = EVAL_SCRIPTS_DIR / "compare_runs.py"

    if not baseline_path.exists():
        return {
            "label": "compare_runs",
            "command": f"python {script} --baseline {baseline_path} --candidate {candidate_path}",
            "status": "skipped",
            "stdout": None,
            "stderr": f"No baseline result found at {baseline_path} — comparison skipped",
            "returncode": None,
        }

    cmd = [
        sys.executable,
        str(script),
        "--baseline",
        str(baseline_path),
        "--candidate",
        str(candidate_path),
        "--json",
    ]

    return run_subcommand(cmd, dry_run, "compare_runs")


def step_verify_gate_blocked(run_config: dict, dry_run: bool) -> dict:
    """Step 4: Verify preview gate is still BLOCKED."""
    gate_doc = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"

    blocked = True
    reason = ""

    if gate_doc.exists():
        try:
            content = gate_doc.read_text(encoding="utf-8").lower()
            if "blocked" not in content:
                blocked = False
                reason = "ADAPTER_PREVIEW_GATE.md does not contain 'BLOCKED'"
        except OSError as e:
            blocked = False
            reason = f"Could not read ADAPTER_PREVIEW_GATE.md: {e}"
    else:
        blocked = False
        reason = "ADAPTER_PREVIEW_GATE.md not found"

    # Also check run config
    pub_allowed = run_config.get("public_release_allowed")
    hf_allowed = run_config.get("hf_upload_allowed")
    if pub_allowed is True:
        blocked = False
        reason = "public_release_allowed=true in run config"
    if hf_allowed is True:
        blocked = False
        reason = "hf_upload_allowed=true in run config"

    status = "PASS" if blocked else "FAIL"
    if dry_run:
        status = "dry_run"

    return {
        "label": "verify_gate_blocked",
        "status": status,
        "blocked": blocked,
        "reason": reason or "Gate is BLOCKED as expected",
        "command": None,
    }


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run_postrun(
    run_config_path: Path,
    adapter_dir: Path,
    eval_result_path: Path,
    output_summary: Path,
    dry_run: bool,
) -> dict:
    """Run all post-training orchestration steps.

    Returns a structured dict with all step results, next steps,
    and overall status.
    """
    # Load run config
    config: dict = {}
    if run_config_path.exists():
        parsed = parse_simple_yaml(run_config_path)
        if parsed and isinstance(parsed, dict):
            config = parsed

    steps: list[dict] = []

    # Step 1: Create adapter manifest
    steps.append(step_create_adapter_manifest(run_config_path, adapter_dir, dry_run))

    # Step 2: Create eval summary
    steps.append(step_create_eval_summary(eval_result_path, output_summary, dry_run))

    # Step 3: Compare runs if baseline exists
    steps.append(step_compare_runs(BASELINE_RESULT_PATH, eval_result_path, dry_run))

    # Step 4: Verify gate still BLOCKED
    steps.append(step_verify_gate_blocked(config, dry_run))

    # Determine overall status
    failed_steps = [s for s in steps if s.get("status") in ("failed", "error", "timeout")]
    gate_failed = any(s.get("label") == "verify_gate_blocked" and s.get("status") == "FAIL" for s in steps)

    if gate_failed:
        overall = "fail"
    elif failed_steps:
        overall = "partial"
    else:
        overall = "pass"

    return {
        "steps": steps,
        "next_steps": NEXT_STEPS,
        "overall": overall,
        "dry_run": dry_run,
        "adapter_dir": str(adapter_dir),
        "eval_result": str(eval_result_path),
        "output_summary": str(output_summary),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for post-training orchestration."""
    parser = argparse.ArgumentParser(
        description="Post-training orchestration for private SFT runs. "
        "No real training. No model downloads. No HF uploads. No git commits.",
    )
    parser.add_argument(
        "--run-config",
        type=Path,
        default=DEFAULT_RUN_CONFIG,
        help="Path to private SFT run config YAML (default: training/configs/private_sft_run.v0.yaml)",
    )
    parser.add_argument(
        "--adapter-dir",
        type=Path,
        default=DEFAULT_ADAPTER_DIR,
        help="Path to adapter directory (default: training/adapters/kimari-smollm3-sft-v0)",
    )
    parser.add_argument(
        "--eval-result",
        type=Path,
        default=DEFAULT_EVAL_RESULT,
        help="Path to eval result JSON (default: eval/results/adapter-private.json)",
    )
    parser.add_argument(
        "--output-summary",
        type=Path,
        default=DEFAULT_OUTPUT_SUMMARY,
        help="Path for output summary JSON (default: /tmp/adapter-summary.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Dry-run mode (default: True)",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_false",
        dest="dry_run",
        help="Execute real post-training steps (not just dry-run)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )

    args = parser.parse_args()

    result = run_postrun(
        run_config_path=args.run_config,
        adapter_dir=args.adapter_dir,
        eval_result_path=args.eval_result,
        output_summary=args.output_summary,
        dry_run=args.dry_run,
    )

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        mode = "DRY-RUN" if result["dry_run"] else "LIVE"
        print()
        print("=" * 60)
        print(f"  Post-Training Orchestration [{mode}]")
        print("=" * 60)
        print()

        for step in result["steps"]:
            status = step["status"]
            symbol = {
                "success": "\u2713",
                "dry_run": "\u25cb",
                "skipped": "\u25cb",
                "failed": "\u2717",
                "error": "\u2717",
                "timeout": "\u2717",
                "PASS": "\u2713",
                "FAIL": "\u2717",
                "pending": "\u25cb",
            }.get(status, "?")
            label = step["label"]
            msg = ""
            if step.get("command"):
                msg = f"  cmd: {step['command']}"
            if step.get("stderr"):
                msg += f"  ({step['stderr']})"
            if step.get("reason") and status in ("PASS", "FAIL", "dry_run"):
                msg = f"  {step['reason']}"
            print(f"  {symbol} {label}")
            if msg.strip():
                print(f"    {msg.strip()}")

        print()
        print("-" * 60)
        print("  Suggested Next Steps:")
        for i, ns in enumerate(result["next_steps"], 1):
            print(f"  {i}. {ns}")

        print()
        print("=" * 60)
        overall = result["overall"]
        if overall == "pass":
            print("  Overall: ALL STEPS PASSED \u2713")
        elif overall == "partial":
            print("  Overall: PARTIAL \u26a0 — some steps failed")
        else:
            print("  Overall: FAILED \u2717 — gate check or critical step failed")
        print("=" * 60)

        if result["dry_run"]:
            print("\n  This was a dry-run. No files were written.")
            print("  Use --no-dry-run to execute real post-training steps.")

    sys.exit(0 if result["overall"] != "fail" else 1)


if __name__ == "__main__":
    main()
