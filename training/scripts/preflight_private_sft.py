#!/usr/bin/env python3
"""CLI preflight check for private SFT execution readiness.

Checks:
- Python version >= 3.10
- torch installed or missing (warning unless --strict)
- CUDA available if torch exists (show GPU name + VRAM if available)
- transformers/peft/trl/accelerate available or missing
- dataset build exists (dataset/build/kimari-v0/report.json)
- output_dir is gitignored
- public_release_allowed=false in run config
- hf_upload_allowed=false in run config
- preview gate BLOCKED
- no GGUF/adapters tracked in git
- recommendations if anything missing

Works WITHOUT torch installed (graceful degradation).
Do NOT import torch/transformers/etc at top level — check availability
with try/except.

Uses pyyaml for config reading. Works without pyyaml too (fallback parser).

No real training. No model downloads. No HF uploads.

Usage:
    python training/scripts/preflight_private_sft.py \\
        --run-config training/configs/private_sft_run.v0.yaml
    python training/scripts/preflight_private_sft.py \\
        --run-config training/configs/private_sft_run.v0.yaml --strict
    python training/scripts/preflight_private_sft.py \\
        --run-config training/configs/private_sft_run.v0.yaml --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_RUN_CONFIG = PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml"
DEFAULT_DATASET_REPORT = PROJECT_ROOT / "dataset" / "build" / "kimari-v0" / "report.json"


# ---------------------------------------------------------------------------
# YAML parser with pyyaml fallback
# ---------------------------------------------------------------------------


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse YAML with pyyaml fallback to simple line parser.

    Returns None if parsing fails.
    """
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
# Git helpers
# ---------------------------------------------------------------------------


def is_gitignored(path: Path) -> bool:
    """Check if a path is covered by .gitignore."""
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

    gitignore_path = PROJECT_ROOT / ".gitignore"
    if not gitignore_path.exists():
        return False

    try:
        gitignore_text = gitignore_path.read_text()
    except OSError:
        return False

    try:
        rel_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        rel_path = path

    rel_str = str(rel_path)

    for pattern in gitignore_text.splitlines():
        pattern = pattern.strip()
        if not pattern or pattern.startswith("#"):
            continue
        if pattern.endswith("/") and (rel_str.startswith(pattern) or rel_str.startswith(pattern.rstrip("/"))):
            return True
        if pattern.startswith("*."):
            suffix = pattern[1:]
            if rel_str.endswith(suffix):
                return True
        if rel_str == pattern or rel_str.startswith(pattern + "/"):
            return True

    return False


def git_tracked_patterns(patterns: list[str]) -> list[str]:
    """Check if any files matching given glob patterns are tracked in git."""
    found: list[str] = []
    for pattern in patterns:
        try:
            result = subprocess.run(
                ["git", "ls-files", pattern],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    if line.strip():
                        found.append(line.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    return found


# ---------------------------------------------------------------------------
# Dependency checks (graceful — never import at top level)
# ---------------------------------------------------------------------------


def check_python_version() -> dict:
    """Check Python version >= 3.10."""
    major = sys.version_info.major
    minor = sys.version_info.minor

    if major > 3 or (major == 3 and minor >= 10):
        return {
            "status": "PASS",
            "value": f"{major}.{minor}.{sys.version_info.micro}",
            "message": None,
        }
    return {
        "status": "FAIL",
        "value": f"{major}.{minor}.{sys.version_info.micro}",
        "message": f"Python {major}.{minor} is below minimum 3.10",
    }


def check_torch() -> dict:
    """Check if torch is installed. If so, check CUDA availability."""
    try:
        import torch

        cuda_available = torch.cuda.is_available()
        gpu_info: dict = {}

        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_vram = torch.cuda.get_device_properties(0).total_mem
            gpu_info = {
                "gpu_name": gpu_name,
                "vram_bytes": gpu_vram,
                "vram_gb": round(gpu_vram / (1024**3), 2),
            }

        return {
            "status": "PASS",
            "value": "installed",
            "cuda_available": cuda_available,
            "gpu_info": gpu_info if cuda_available else None,
            "message": None,
        }
    except ImportError:
        return {
            "status": "WARN",
            "value": "missing",
            "cuda_available": False,
            "gpu_info": None,
            "message": "torch is not installed — install before training",
        }


def check_package(import_name: str) -> dict:
    """Check if a single Python package is importable."""
    try:
        __import__(import_name)
        return {"status": "PASS", "value": "installed", "message": None}
    except ImportError:
        return {"status": "WARN", "value": "missing", "message": f"{import_name} is not installed"}


# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------


def run_preflight(run_config_path: Path, strict: bool) -> dict:
    """Run all preflight checks and return structured results.

    Returns a dict with:
        checks: dict of check_name -> check_result
        recommendations: list of recommendation strings
        overall: "pass" | "warn" | "fail"
        dataset_build_dir: str | None — resolved dataset build directory
        dataset_report_path: str — path to the dataset report file checked
        dataset_build_dir_source: "run_config" | "fallback" — how the path was resolved
    """
    checks: dict[str, dict] = {}
    recommendations: list[str] = []

    # Track dataset build dir resolution
    resolved_dataset_build_dir: str | None = None
    resolved_dataset_report_path: str = str(DEFAULT_DATASET_REPORT)
    dataset_build_dir_source: str = "fallback"

    # 1. Python version
    checks["python_version"] = check_python_version()

    # 2. torch
    torch_check = check_torch()
    checks["torch"] = torch_check
    if torch_check["value"] == "missing":
        recommendations.append("Install PyTorch: see https://pytorch.org/get-started/locally/")
        if strict:
            torch_check["status"] = "FAIL"

    # 3. CUDA info (if torch available)
    if torch_check["value"] == "installed":
        if torch_check["cuda_available"]:
            checks["cuda"] = {
                "status": "PASS",
                "value": True,
                "gpu_info": torch_check["gpu_info"],
                "message": None,
            }
        else:
            checks["cuda"] = {
                "status": "WARN",
                "value": False,
                "gpu_info": None,
                "message": "torch is installed but CUDA is not available — training requires a CUDA GPU",
            }
            recommendations.append("Ensure NVIDIA drivers and CUDA toolkit are installed")
    else:
        checks["cuda"] = {
            "status": "WARN",
            "value": None,
            "message": "Cannot check CUDA — torch is not installed",
        }

    # 4. transformers / peft / trl / accelerate
    for pkg in ("transformers", "peft", "trl", "accelerate"):
        pkg_check = check_package(pkg)
        checks[pkg] = pkg_check
        if pkg_check["value"] == "missing":
            recommendations.append(f"Install {pkg}: pip install {pkg}")
            if strict:
                pkg_check["status"] = "FAIL"

    # 5. Dataset build report exists
    # Try to read dataset_build_dir from run_config if available
    run_config_data: dict | None = None
    if run_config_path.exists():
        parsed = parse_simple_yaml(run_config_path)
        if parsed and isinstance(parsed, dict):
            run_config_data = parsed
            config_dataset_dir = run_config_data.get("dataset_build_dir")
            if config_dataset_dir:
                config_dir_path = Path(config_dataset_dir)
                if not config_dir_path.is_absolute():
                    config_dir_path = PROJECT_ROOT / config_dir_path
                resolved_dataset_build_dir = str(config_dir_path)
                resolved_dataset_report_path = str(config_dir_path / "report.json")
                dataset_build_dir_source = "run_config"

    dataset_report_path = Path(resolved_dataset_report_path)
    if dataset_report_path.exists():
        checks["dataset_build"] = {
            "status": "PASS",
            "value": str(dataset_report_path),
            "exists": True,
            "dataset_build_dir": resolved_dataset_build_dir,
            "dataset_report_path": str(dataset_report_path),
            "source": dataset_build_dir_source,
            "message": None,
        }
    else:
        checks["dataset_build"] = {
            "status": "WARN",
            "value": str(dataset_report_path),
            "exists": False,
            "dataset_build_dir": resolved_dataset_build_dir,
            "dataset_report_path": str(dataset_report_path),
            "source": dataset_build_dir_source,
            "message": "Dataset build report not found — run build_dataset_mix.py first",
        }
        recommendations.append(
            "Build the dataset: python training/scripts/build_dataset_mix.py --output-dir dataset/build/kimari-v0"
        )

    # 6. Load run config (reuse already-parsed data if available)
    if not run_config_path.exists():
        checks["run_config"] = {
            "status": "FAIL",
            "value": str(run_config_path),
            "message": "Run config file not found",
        }
        config: dict = {}
    elif run_config_data is not None:
        config = run_config_data
        checks["run_config"] = {
            "status": "PASS",
            "value": str(run_config_path),
            "message": None,
        }
    else:
        parsed = parse_simple_yaml(run_config_path)
        if parsed is None or not isinstance(parsed, dict):
            checks["run_config"] = {
                "status": "FAIL",
                "value": str(run_config_path),
                "message": "Failed to parse run config YAML",
            }
            config = {}
        else:
            config = parsed
            checks["run_config"] = {
                "status": "PASS",
                "value": str(run_config_path),
                "message": None,
            }

    # 7. output_dir is gitignored
    output_dir = config.get("output_dir")
    if not output_dir:
        checks["output_dir_gitignored"] = {
            "status": "FAIL",
            "value": None,
            "message": "No output_dir in run config",
        }
    else:
        od_path = Path(output_dir)
        if not od_path.is_absolute():
            od_path = PROJECT_ROOT / od_path

        if is_gitignored(od_path):
            checks["output_dir_gitignored"] = {
                "status": "PASS",
                "value": output_dir,
                "gitignored": True,
                "message": None,
            }
        else:
            checks["output_dir_gitignored"] = {
                "status": "FAIL",
                "value": output_dir,
                "gitignored": False,
                "message": "output_dir is NOT gitignored — training artifacts could be committed",
            }
            recommendations.append(f"Add {output_dir}/ to .gitignore")

    # 8. public_release_allowed=false
    pub = config.get("public_release_allowed")
    if pub is True:
        checks["public_release_allowed"] = {
            "status": "FAIL",
            "value": True,
            "message": "public_release_allowed must be false for private SFT",
        }
    elif pub is False:
        checks["public_release_allowed"] = {
            "status": "PASS",
            "value": False,
            "message": None,
        }
    else:
        checks["public_release_allowed"] = {
            "status": "WARN",
            "value": None,
            "message": "public_release_allowed not specified — assuming false",
        }

    # 9. hf_upload_allowed=false
    hf = config.get("hf_upload_allowed")
    if hf is True:
        checks["hf_upload_allowed"] = {
            "status": "FAIL",
            "value": True,
            "message": "hf_upload_allowed must be false for private SFT",
        }
    elif hf is False:
        checks["hf_upload_allowed"] = {
            "status": "PASS",
            "value": False,
            "message": None,
        }
    else:
        checks["hf_upload_allowed"] = {
            "status": "WARN",
            "value": None,
            "message": "hf_upload_allowed not specified — assuming false",
        }

    # 10. preview gate BLOCKED
    preview_gate = config.get("preview_gate")
    if preview_gate and "ADAPTER_PREVIEW_GATE.md" in str(preview_gate):
        checks["preview_gate"] = {
            "status": "PASS",
            "value": "BLOCKED (per ADAPTER_PREVIEW_GATE.md)",
            "message": None,
        }
    else:
        # Check if the doc exists as a signal
        gate_doc = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
        if gate_doc.exists():
            checks["preview_gate"] = {
                "status": "PASS",
                "value": "BLOCKED (ADAPTER_PREVIEW_GATE.md exists)",
                "message": None,
            }
        else:
            checks["preview_gate"] = {
                "status": "FAIL",
                "value": None,
                "message": "Preview gate status unknown — ADAPTER_PREVIEW_GATE.md not found",
            }
            recommendations.append("Create docs/ADAPTER_PREVIEW_GATE.md with BLOCKED state")

    # 11. No GGUF/adapters tracked in git
    gguf_tracked = git_tracked_patterns(["*.gguf"])
    adapters_tracked = git_tracked_patterns(["training/adapters/*.safetensors", "training/adapters/*.bin"])

    gguf_fail = bool(gguf_tracked)
    adapters_fail = bool(adapters_tracked)

    if gguf_fail:
        checks["gguf_tracked"] = {
            "status": "FAIL",
            "value": gguf_tracked,
            "message": f"GGUF files tracked in git: {gguf_tracked}",
        }
        recommendations.append("Remove GGUF files from git tracking: git rm --cached <file>")
    else:
        checks["gguf_tracked"] = {
            "status": "PASS",
            "value": [],
            "message": None,
        }

    if adapters_fail:
        checks["adapters_tracked"] = {
            "status": "FAIL",
            "value": adapters_tracked,
            "message": f"Adapter files tracked in git: {adapters_tracked}",
        }
        recommendations.append("Remove adapter weights from git: git rm --cached <file>")
    else:
        checks["adapters_tracked"] = {
            "status": "PASS",
            "value": [],
            "message": None,
        }

    # Determine overall status
    has_fail = any(c["status"] == "FAIL" for c in checks.values())
    has_warn = any(c["status"] == "WARN" for c in checks.values())

    if has_fail:
        overall = "fail"
    elif has_warn:
        overall = "warn"
    else:
        overall = "pass"

    return {
        "checks": checks,
        "recommendations": recommendations,
        "overall": overall,
        "strict": strict,
        "dataset_build_dir": resolved_dataset_build_dir,
        "dataset_report_path": resolved_dataset_report_path,
        "dataset_build_dir_source": dataset_build_dir_source,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for private SFT preflight checks."""
    parser = argparse.ArgumentParser(
        description="Preflight check for private SFT execution readiness. "
        "No real training. No model downloads. No HF uploads.",
    )
    parser.add_argument(
        "--run-config",
        type=Path,
        default=DEFAULT_RUN_CONFIG,
        help="Path to private SFT run config YAML (default: training/configs/private_sft_run.v0.yaml)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if torch or training dependencies are not installed",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )

    args = parser.parse_args()

    result = run_preflight(args.run_config, args.strict)

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        print()
        print("=" * 60)
        print("  Private SFT Preflight Check")
        print("=" * 60)
        print()

        for name, check in result["checks"].items():
            status = check["status"]
            symbol = {"PASS": "\u2713", "WARN": "\u26a0", "FAIL": "\u2717"}.get(status, "?")
            val_repr = check.get("value", "")
            if isinstance(val_repr, dict):
                val_repr = json.dumps(val_repr, default=str)
            elif isinstance(val_repr, list):
                val_repr = json.dumps(val_repr)
            val_str = f" {val_repr}" if val_repr and val_repr is not None else ""
            msg = f" ({check['message']})" if check.get("message") else ""
            print(f"  {symbol} {name:<28s}{val_str}{msg}")

        if result["recommendations"]:
            print()
            print("-" * 60)
            print("  Recommendations:")
            for rec in result["recommendations"]:
                print(f"  \u2192 {rec}")

        print()
        print("=" * 60)
        overall = result["overall"]
        if overall == "pass":
            print("  Overall: ALL CHECKS PASSED \u2713")
        elif overall == "warn":
            print("  Overall: PASSED WITH WARNINGS \u26a0")
        else:
            print("  Overall: FAILED \u2717 — fix issues above before training")
        print("=" * 60)

    exit_code = 0
    if result["overall"] == "fail":
        if args.strict:
            exit_code = 1
        else:
            # Non-strict: exit 0 even with failures (warnings only)
            # But still exit 1 if safety-critical checks fail
            critical = ["public_release_allowed", "hf_upload_allowed"]
            exit_code = 1 if any(result["checks"].get(c, {}).get("status") == "FAIL" for c in critical) else 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
