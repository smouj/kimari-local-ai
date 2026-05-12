#!/usr/bin/env python3
"""Check training stack compatibility for Kimari Local AI.

Inspects the local Python environment and installed packages to determine
compatibility with the SFT LoRA training pipeline. Checks versions, imports,
and API signatures — especially TrainingArguments and SFTTrainer parameter
acceptance.

CRITICAL RULES:
- No model downloads
- No training
- No network calls
- Exit code 0 always (informational tool)
- Each check is independent — if one import fails, continue to the next

Usage:
    python training/scripts/check_training_stack.py
    python training/scripts/check_training_stack.py --json
    python training/scripts/check_training_stack.py --verbose
    python training/scripts/check_training_stack.py --json --verbose
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from typing import Any  # noqa: UP035, I001

# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_python_version() -> dict[str, Any]:
    """Check Python version is >= 3.10."""
    version_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    passed = sys.version_info >= (3, 10)
    return {
        "name": "python_version",
        "passed": passed,
        "value": version_str,
        "message": (
            f"Python {version_str} meets requirement (>= 3.10)"
            if passed
            else f"Python {version_str} does NOT meet requirement (>= 3.10)"
        ),
    }


def _try_import(module_name: str) -> dict[str, Any]:
    """Try to import a module and return its version.

    Returns a check dict with passed=True/False, the version string if
    available, and a descriptive message. Never raises.
    """
    try:
        mod = __import__(module_name)
        version = getattr(mod, "__version__", "unknown")
        return {
            "name": f"{module_name}_import",
            "passed": True,
            "value": version,
            "message": f"{module_name} {version} imported successfully",
        }
    except ImportError:
        return {
            "name": f"{module_name}_import",
            "passed": False,
            "value": None,
            "message": f"{module_name} is not installed",
        }


def check_sft_trainer_import() -> dict[str, Any]:
    """Check SFTTrainer can be imported from trl."""
    try:
        from trl import SFTTrainer  # noqa: F401

        version = getattr(trl_mod, "__version__", "unknown") if (trl_mod := __import__("trl")) else "unknown"
        return {
            "name": "sft_trainer_import",
            "passed": True,
            "value": version,
            "message": f"SFTTrainer imported from trl {version}",
        }
    except ImportError:
        return {
            "name": "sft_trainer_import",
            "passed": False,
            "value": None,
            "message": "SFTTrainer cannot be imported from trl (trl not installed or version too old)",
        }
    except Exception as exc:
        return {
            "name": "sft_trainer_import",
            "passed": False,
            "value": None,
            "message": f"SFTTrainer import failed: {exc}",
        }


def _inspect_init_params(cls: type) -> set[str] | None:
    """Inspect a class __init__ signature and return parameter names.

    Returns None if inspection fails.
    """
    try:
        sig = inspect.signature(cls.__init__)
        return set(sig.parameters.keys())
    except (ValueError, TypeError):
        return None


def check_training_arguments_signature() -> dict[str, Any]:
    """Inspect TrainingArguments.__init__ signature and report parameters.

    Reports which key parameters it accepts.
    """
    try:
        from transformers import TrainingArguments

        params = _inspect_init_params(TrainingArguments)
        if params is None:
            return {
                "name": "training_arguments_signature",
                "passed": False,
                "value": None,
                "message": "TrainingArguments imported but signature inspection failed",
            }

        accepts_max_seq_length = "max_seq_length" in params
        return {
            "name": "training_arguments_signature",
            "passed": True,
            "value": f"{len(params)} parameters",
            "message": (
                f"TrainingArguments has {len(params)} parameters; accepts max_seq_length={accepts_max_seq_length}"
            ),
        }
    except ImportError:
        return {
            "name": "training_arguments_signature",
            "passed": False,
            "value": None,
            "message": "TrainingArguments not available (transformers not installed)",
        }
    except Exception as exc:
        return {
            "name": "training_arguments_signature",
            "passed": False,
            "value": None,
            "message": f"TrainingArguments inspection failed: {exc}",
        }


def check_training_arguments_accepts_max_seq_length() -> dict[str, Any]:
    """Check whether TrainingArguments accepts max_seq_length parameter."""
    try:
        from transformers import TrainingArguments

        params = _inspect_init_params(TrainingArguments)
        if params is None:
            return {
                "name": "training_arguments_accepts_max_seq_length",
                "passed": False,
                "value": None,
                "message": "Could not inspect TrainingArguments signature",
            }

        accepts = "max_seq_length" in params
        # We consider it a "pass" (True) when TrainingArguments does NOT accept
        # max_seq_length, because that matches the expected modern API.
        # The check result reports the raw boolean; interpretation is in compatibility.
        return {
            "name": "training_arguments_accepts_max_seq_length",
            "passed": True,
            "value": accepts,
            "message": (f"TrainingArguments {'accepts' if accepts else 'does NOT accept'} max_seq_length"),
        }
    except ImportError:
        return {
            "name": "training_arguments_accepts_max_seq_length",
            "passed": False,
            "value": None,
            "message": "transformers not installed, cannot inspect TrainingArguments",
        }
    except Exception as exc:
        return {
            "name": "training_arguments_accepts_max_seq_length",
            "passed": False,
            "value": None,
            "message": f"Inspection failed: {exc}",
        }


def check_sft_trainer_param(param_name: str) -> dict[str, Any]:
    """Check whether SFTTrainer.__init__ accepts a specific parameter."""
    try:
        from trl import SFTTrainer

        params = _inspect_init_params(SFTTrainer)
        if params is None:
            return {
                "name": f"sft_trainer_accepts_{param_name}",
                "passed": False,
                "value": None,
                "message": "Could not inspect SFTTrainer signature",
            }

        accepts = param_name in params
        return {
            "name": f"sft_trainer_accepts_{param_name}",
            "passed": True,
            "value": accepts,
            "message": f"SFTTrainer {'accepts' if accepts else 'does NOT accept'} {param_name}",
        }
    except ImportError:
        return {
            "name": f"sft_trainer_accepts_{param_name}",
            "passed": False,
            "value": None,
            "message": "trl not installed, cannot inspect SFTTrainer",
        }
    except Exception as exc:
        return {
            "name": f"sft_trainer_accepts_{param_name}",
            "passed": False,
            "value": None,
            "message": f"Inspection failed: {exc}",
        }


def check_gpu_arch_compatibility() -> dict[str, Any]:
    """Check GPU compute capability vs PyTorch CUDA arch support.

    WARNs if Pascal GPU (sm_61, e.g. GTX 1060) detected with PyTorch
    cu128/cu130 build (which dropped sm_61 support). Recommends cu126.
    """
    compute_cap = None
    gpu_name = None
    torch_version = None
    torch_cuda_version = None

    try:
        import torch

        torch_version = torch.__version__
        if torch.cuda.is_available():
            compute_cap = torch.cuda.get_device_capability(0)
            gpu_name = torch.cuda.get_device_name(0)
            torch_cuda_version = torch.version.cuda
    except (ImportError, RuntimeError):
        pass

    # No GPU detected
    if compute_cap is None:
        return {
            "name": "gpu_arch_compatibility",
            "passed": True,
            "value": "No CUDA GPU detected or PyTorch CUDA unavailable",
            "message": "GPU arch check skipped (no CUDA GPU or PyTorch not available with CUDA)",
        }

    cap_str = f"sm_{compute_cap[0]}{compute_cap[1]}"
    cap_major, cap_minor = compute_cap

    # Check if Pascal (sm_61) with incompatible PyTorch
    is_pascal = cap_major == 6 and cap_minor == 1
    if is_pascal and torch_cuda_version:
        cuda_ver_num = torch_cuda_version.replace(".", "")
        if int(cuda_ver_num) >= 128:
            return {
                "name": "gpu_arch_compatibility",
                "passed": False,
                "value": f"{gpu_name} ({cap_str}) with PyTorch {torch_version}+cu{torch_cuda_version}",
                "message": (
                    f"Pascal GPU ({cap_str}) detected with PyTorch cu{torch_cuda_version}. "
                    f"PyTorch builds cu128+ dropped sm_61 support. "
                    f"Install PyTorch cu126 legacy: "
                    f"pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu126"
                ),
            }

    # Normal case - compatible
    torch_info = f" (PyTorch {torch_version}+cu{torch_cuda_version})" if torch_cuda_version else ""
    return {
        "name": "gpu_arch_compatibility",
        "passed": True,
        "value": f"{gpu_name} ({cap_str}){torch_info}",
        "message": "GPU compute capability is compatible with installed PyTorch",
    }


def check_gpu_cuda_info() -> dict[str, Any]:
    """Check GPU/CUDA info even when PyTorch is not installed.

    Uses kimari.core.detection functions as fallbacks so that GPU and CUDA
    information is available without requiring torch.  If torch *is* present
    it is used as the primary source for compute capability and the CUDA
    build tag.

    Returns a check dict with:
      name:              "gpu_cuda_info"
      passed:            True (always — informational)
      value:             Human-readable summary string
      message:           Descriptive message
      gpu_name:          GPU name or None
      compute_capability: e.g. "sm_61" or None
      compute_cap_source: "torch" | "llama-server" | None
      torch_cuda_build:  e.g. "cu126" or None
      cuda_version_source: e.g. "12.0 (via nvcc)" or None
    """
    # Lazy imports from kimari.core.detection — may not be on sys.path
    detect_gpu = None
    detect_cuda_version_detailed = None
    detect_compute_capability_from_llama_server = None

    try:
        from kimari.core.detection import (
            detect_compute_capability_from_llama_server as _detect_cc_llama,
        )
        from kimari.core.detection import (
            detect_cuda_version_detailed as _detect_cuda_detailed,
        )
        from kimari.core.detection import (
            detect_gpu as _detect_gpu,
        )

        detect_gpu = _detect_gpu
        detect_cuda_version_detailed = _detect_cuda_detailed
        detect_compute_capability_from_llama_server = _detect_cc_llama
    except ImportError:
        pass

    # ---- GPU name ----
    gpu_name: str | None = None
    if detect_gpu is not None:
        try:
            gpu_info = detect_gpu()
            if gpu_info:
                gpu_name = gpu_info.get("name")
        except Exception:  # noqa: BLE001
            pass

    # ---- CUDA version with source ----
    cuda_version_source: str | None = None
    if detect_cuda_version_detailed is not None:
        try:
            cuda_detail = detect_cuda_version_detailed()
            if cuda_detail:
                cuda_version_source = f"{cuda_detail['version']} (via {cuda_detail['source']})"
        except Exception:  # noqa: BLE001
            pass

    # ---- Compute capability — try torch first, then llama-server ----
    compute_capability: str | None = None
    compute_cap_source: str | None = None
    torch_cuda_build: str | None = None

    # Try torch
    try:
        import torch

        if torch.cuda.is_available():
            cap = torch.cuda.get_device_capability(0)
            compute_capability = f"sm_{cap[0]}{cap[1]}"
            compute_cap_source = "torch"
            # Torch CUDA build tag (e.g. "cu126")
            if torch.version.cuda:
                torch_cuda_build = f"cu{torch.version.cuda.replace('.', '')}"
    except (ImportError, RuntimeError):
        pass

    # Fallback: llama-server
    if compute_capability is None and detect_compute_capability_from_llama_server is not None:
        try:
            cc_str = detect_compute_capability_from_llama_server()
            if cc_str:
                compute_capability = f"sm_{cc_str.replace('.', '')}"
                compute_cap_source = "llama-server"
        except Exception:  # noqa: BLE001
            pass

    # ---- Build the result ----
    # If nothing was detected at all, return a minimal "nothing found" result
    if gpu_name is None and compute_capability is None and cuda_version_source is None:
        return {
            "name": "gpu_cuda_info",
            "passed": True,
            "value": "No GPU/CUDA detected",
            "message": "No GPU/CUDA detected",
            "gpu_name": None,
            "compute_capability": None,
            "compute_cap_source": None,
            "torch_cuda_build": None,
            "cuda_version_source": None,
        }

    # Assemble human-readable value string
    parts: list[str] = []
    if gpu_name:
        parts.append(gpu_name)
    if compute_capability:
        cc_part = f"{compute_capability} (via {compute_cap_source})"
        parts.append(cc_part)
    if torch_cuda_build:
        parts.append(f"PyTorch {torch_cuda_build}")
    if cuda_version_source:
        parts.append(f"CUDA {cuda_version_source}")

    value_str = ", ".join(parts)

    return {
        "name": "gpu_cuda_info",
        "passed": True,
        "value": value_str,
        "message": "GPU and CUDA detection completed",
        "gpu_name": gpu_name,
        "compute_capability": compute_capability,
        "compute_cap_source": compute_cap_source,
        "torch_cuda_build": torch_cuda_build,
        "cuda_version_source": cuda_version_source,
    }


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------


def run_all_checks(verbose: bool = False) -> dict[str, Any]:
    """Run all compatibility checks and return the structured result."""
    checks: list[dict[str, Any]] = []

    # 1. Python version
    checks.append(check_python_version())

    # 2-7. Core library imports
    for module in ("torch", "transformers", "datasets", "peft", "trl", "accelerate"):
        checks.append(_try_import(module))

    # 8. SFTTrainer import
    checks.append(check_sft_trainer_import())

    # 9. TrainingArguments signature
    checks.append(check_training_arguments_signature())

    # 10. TrainingArguments accepts max_seq_length
    checks.append(check_training_arguments_accepts_max_seq_length())

    # 11-14. SFTTrainer parameter checks
    for param in ("tokenizer", "processing_class", "dataset_text_field", "max_seq_length"):
        checks.append(check_sft_trainer_param(param))

    # 15. GPU arch compatibility (Pascal/cu128+ check)
    checks.append(check_gpu_arch_compatibility())

    # 16. GPU/CUDA info (works without PyTorch)
    checks.append(check_gpu_cuda_info())

    # Build compatibility dict from the param checks
    compatibility: dict[str, Any] = {}
    for check in checks:
        name = check["name"]
        if name == "training_arguments_accepts_max_seq_length":
            compatibility["training_arguments_accepts_max_seq_length"] = check["value"]
        elif name.startswith("sft_trainer_accepts_"):
            param_name = name.replace("sft_trainer_accepts_", "")
            compatibility[f"sft_trainer_accepts_{param_name}"] = check["value"]
        elif name == "gpu_cuda_info":
            compatibility["gpu_cuda_info"] = {
                "gpu_name": check.get("gpu_name"),
                "compute_capability": check.get("compute_capability"),
                "compute_cap_source": check.get("compute_cap_source"),
                "torch_cuda_build": check.get("torch_cuda_build"),
                "cuda_version_source": check.get("cuda_version_source"),
            }

    # Determine ready_for_training
    # True only if ALL core imports succeed AND TrainingArguments does NOT
    # accept max_seq_length (confirming the compat fix is needed).
    core_import_names = {
        "torch_import",
        "transformers_import",
        "datasets_import",
        "peft_import",
        "trl_import",
        "accelerate_import",
        "sft_trainer_import",
    }
    all_core_imports_ok = all(c.get("passed") is True for c in checks if c["name"] in core_import_names)
    ta_no_max_seq = compatibility.get("training_arguments_accepts_max_seq_length") is False
    ready_for_training = all_core_imports_ok and ta_no_max_seq

    # Collect warnings
    warnings: list[str] = []
    if not all_core_imports_ok:
        missing = [
            c["name"].replace("_import", "") for c in checks if c["name"] in core_import_names and not c["passed"]
        ]
        warnings.append(f"Missing core imports: {', '.join(missing)}")
    if compatibility.get("training_arguments_accepts_max_seq_length") is True:
        warnings.append(
            "TrainingArguments accepts max_seq_length — older transformers API detected. "
            "Passing max_seq_length to TrainingArguments may work but is deprecated."
        )
    if compatibility.get("training_arguments_accepts_max_seq_length") is None and all_core_imports_ok:
        warnings.append("Could not determine if TrainingArguments accepts max_seq_length")
    if compatibility.get("sft_trainer_accepts_tokenizer") is False:
        warnings.append(
            "SFTTrainer does NOT accept tokenizer — may need processing_class parameter instead "
            "(trl >= 0.8.0 renamed tokenizer to processing_class)"
        )
    if compatibility.get("sft_trainer_accepts_processing_class") is True:
        warnings.append(
            "SFTTrainer accepts processing_class — use processing_class instead of tokenizer "
            "for trl >= 0.8.0 compatibility"
        )
    if compatibility.get("sft_trainer_accepts_max_seq_length") is True:
        warnings.append("SFTTrainer accepts max_seq_length — pass it to SFTTrainer, not TrainingArguments")

    # GPU arch warning
    gpu_arch_check = next((c for c in checks if c["name"] == "gpu_arch_compatibility"), None)
    if gpu_arch_check and not gpu_arch_check.get("passed"):
        warnings.append(gpu_arch_check.get("message", "GPU arch compatibility issue detected"))

    # Python version warning
    # Note: pyproject.toml requires Python >= 3.10, but we keep this check
    # for environments where the script is run directly without pip enforcement.

    # Verbose: add detailed parameter info to checks
    if verbose:
        try:
            from transformers import TrainingArguments

            params = _inspect_init_params(TrainingArguments)
            if params:
                for c in checks:
                    if c["name"] == "training_arguments_signature":
                        c["detail"] = f"All parameters: {sorted(params)}"
        except ImportError:
            pass

        try:
            from trl import SFTTrainer

            params = _inspect_init_params(SFTTrainer)
            if params:
                for c in checks:
                    if c["name"] == "sft_trainer_accepts_tokenizer":
                        c["detail"] = f"All SFTTrainer parameters: {sorted(params)}"
        except ImportError:
            pass

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    return {
        "script": "training/scripts/check_training_stack.py",
        "python_version": python_version,
        "checks": checks,
        "compatibility": compatibility,
        "ready_for_training": ready_for_training,
        "warnings": warnings,
    }


def print_human_output(result: dict[str, Any], verbose: bool = False) -> None:
    """Print a human-readable table of check results."""
    print("=" * 70)
    print("  Kimari Training Stack Compatibility Check")
    print("=" * 70)
    print()

    # Header
    print(f"  {'Status':<8} {'Check':<48} {'Value'}")
    print(f"  {'------':<8} {'-----':<48} {'-----'}")

    for check in result["checks"]:
        passed = check["passed"]
        if passed:
            status = "PASS"
        elif check["value"] is None and not check["passed"]:
            status = "FAIL"
        else:
            # passed=False but we got a value (e.g., param check that succeeded
            # in inspection but the answer is "no" — still informational)
            status = "WARN" if check.get("value") is not None else "FAIL"

        name = check["name"]
        value = check.get("value")
        value_str = str(value) if value is not None else "—"
        print(f"  {status:<8} {name:<48} {value_str}")

        if verbose and check.get("detail"):
            print(f"  {'':8} {check['detail']}")

    # Compatibility section
    print()
    print("-" * 70)
    print("  Compatibility Details")
    print("-" * 70)
    for key, value in result["compatibility"].items():
        if isinstance(value, dict):
            # Nested dict (e.g. gpu_cuda_info) — display sub-fields
            label = key.replace("_", " ")
            print(f"  {label}:")
            for sub_key, sub_value in value.items():
                sub_label = sub_key.replace("_", " ")
                display = "—" if sub_value is None else str(sub_value)
                print(f"    {sub_label}: {display}")
        else:
            if value is None:
                display = "unknown (library not available)"
            elif isinstance(value, bool):
                display = str(value)
            else:
                display = str(value)
            label = key.replace("_", " ").replace("accepts ", "accepts ")
            print(f"  {label}: {display}")

    # Warnings
    if result["warnings"]:
        print()
        print("-" * 70)
        print("  Warnings")
        print("-" * 70)
        for w in result["warnings"]:
            print(f"  WARNING: {w}")

    # Ready for training
    print()
    print("=" * 70)
    if result["ready_for_training"]:
        print("  READY FOR TRAINING: All core imports OK, compat fix confirmed needed.")
    else:
        print("  NOT READY FOR TRAINING: See issues above.")
    print("=" * 70)


def main() -> None:
    """CLI entry point for training stack compatibility check."""
    parser = argparse.ArgumentParser(
        description="Check training stack compatibility. "
        "No model downloads. No training. No network calls. Exit 0 always.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information (e.g., full parameter lists)",
    )

    args = parser.parse_args()

    result = run_all_checks(verbose=args.verbose)

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_human_output(result, verbose=args.verbose)

    # Always exit 0 — this is an informational tool
    sys.exit(0)


if __name__ == "__main__":
    main()
