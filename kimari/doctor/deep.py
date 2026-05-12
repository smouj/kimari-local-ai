"""
Deep diagnostic checks for ``kimari doctor --deep``.

All functions are pure/safe — no model execution, no downloads,
no GPU required, no network calls (except checking if a port is
free which is local).

Each check returns a dict with:
    - name:   str   — human-readable check name
    - status: str   — "PASS" | "WARN" | "FAIL"
    - value:  str   — short description or measurement
    - detail: str   — extra context or error message
"""

import json
import sys
from pathlib import Path

from kimari import __version__ as KIMARI_VERSION  # noqa: N812
from kimari.config.loader import load_config, validate_config
from kimari.core.constants import PROJECT_ROOT
from kimari.core.detection import (
    detect_compute_capability_from_llama_server,
    detect_cuda,
    detect_cuda_version,
    detect_gpu,
    detect_llama_server,
)
from kimari.core.paths import (
    get_kimari_home,
    get_user_config_dir,
    get_user_models_dir,
    get_user_state_dir,
)

# ─── Individual Checks ────────────────────────────────────────────────────────


def check_python() -> dict:
    """Check Python version meets minimum requirements.

    PASS if Python >= 3.10, WARN if >= 3.8, FAIL if < 3.8.
    """
    version = sys.version_info
    version_string = f"{version.major}.{version.minor}.{version.micro}"

    if version >= (3, 10):
        return {
            "name": "Python",
            "status": "PASS",
            "value": version_string,
            "detail": "",
        }
    elif version >= (3, 8):
        return {
            "name": "Python",
            "status": "WARN",
            "value": version_string,
            "detail": "Python >= 3.10 recommended",
        }
    else:
        return {
            "name": "Python",
            "status": "FAIL",
            "value": version_string,
            "detail": "Python >= 3.8 required",
        }


def check_paths() -> dict:
    """Check that key directories exist.

    Checks kimari home, models dir, state dir, and config dir.
    PASS if all exist, WARN if some missing, FAIL if all missing
    (indicates a severe setup problem).
    """
    dirs = {
        "kimari_home": get_kimari_home(),
        "models_dir": get_user_models_dir(),
        "state_dir": get_user_state_dir(),
        "config_dir": get_user_config_dir(),
    }

    missing = {name: path for name, path in dirs.items() if not path.exists()}

    if not missing:
        return {
            "name": "Paths",
            "status": "PASS",
            "value": "All key directories exist",
            "detail": "",
        }

    missing_names = sorted(missing.keys())

    # All directories missing — something is very wrong with setup
    if len(missing) == len(dirs):
        return {
            "name": "Paths",
            "status": "FAIL",
            "value": f"Missing: {', '.join(missing_names)}",
            "detail": "No key directories found — check installation",
        }

    return {
        "name": "Paths",
        "status": "WARN",
        "value": f"Missing: {', '.join(missing_names)}",
        "detail": "",
    }


def check_config() -> dict:
    """Check config file exists and is valid JSON.

    Uses kimari.config.loader functions.  PASS if valid,
    WARN if has issues, FAIL if missing or corrupt.

    Also detects incomplete config (missing version, profiles, or
    default_profile not in profiles) and suggests recovery.
    """
    try:
        config = load_config()
    except SystemExit:
        return {
            "name": "Config",
            "status": "FAIL",
            "value": "Config not found",
            "detail": "Run 'kimari config path' to locate config",
        }
    except json.JSONDecodeError as exc:
        return {
            "name": "Config",
            "status": "FAIL",
            "value": "Invalid JSON",
            "detail": str(exc),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "name": "Config",
            "status": "FAIL",
            "value": "Config error",
            "detail": str(exc),
        }

    # Check for incomplete config before schema validation
    from kimari.setup.writer import is_config_complete

    if not is_config_complete(config):
        missing = []
        if "version" not in config:
            missing.append("'version' missing")
        profiles = config.get("profiles")
        if not profiles or not isinstance(profiles, dict) or len(profiles) == 0:
            missing.append("'profiles' missing or empty")
        default = config.get("default_profile", "")
        if not default:
            missing.append("'default_profile' missing")
        elif profiles and default not in profiles:
            missing.append(f"default_profile '{default}' not in profiles")

        detail = "; ".join(missing)
        return {
            "name": "Config",
            "status": "WARN",
            "value": "User config appears incomplete",
            "detail": f"{detail} — run 'kimari setup --write --yes --reset-user-config' to regenerate",
        }

    is_valid, errors = validate_config(config)
    if is_valid:
        return {
            "name": "Config",
            "status": "PASS",
            "value": "Valid config",
            "detail": "",
        }
    return {
        "name": "Config",
        "status": "WARN",
        "value": f"Config has {len(errors)} issue(s)",
        "detail": "; ".join(errors[:3]),
    }


def check_models_dir() -> dict:
    """Check if models dir exists and has .gguf files.

    PASS if GGUF found, WARN if dir exists but no GGUF,
    FAIL if dir doesn't exist.
    """
    models_dir = get_user_models_dir()

    if not models_dir.exists():
        return {
            "name": "Models Dir",
            "status": "FAIL",
            "value": "Directory does not exist",
            "detail": "",
        }

    gguf_files = list(models_dir.glob("**/*.gguf"))
    if gguf_files:
        return {
            "name": "Models Dir",
            "status": "PASS",
            "value": f"{len(gguf_files)} GGUF file(s) found",
            "detail": "",
        }

    return {
        "name": "Models Dir",
        "status": "WARN",
        "value": "No GGUF files found",
        "detail": "Run 'kimari pull test' to download a model",
    }


def check_llama_server_presence() -> dict:
    """Check if llama-server binary is found.

    Uses kimari.core.detection.detect_llama_server().
    PASS if found, WARN if not found.
    """
    path = detect_llama_server()
    if path:
        return {
            "name": "llama-server",
            "status": "PASS",
            "value": path,
            "detail": "",
        }
    return {
        "name": "llama-server",
        "status": "WARN",
        "value": "Not found",
        "detail": "Build from source or set LLAMA_SERVER env var",
    }


def check_default_profile() -> dict:
    """Check default_profile is 'test'.

    During alpha, the default profile must be 'test'.
    PASS if test, WARN if something else.
    """
    try:
        config = load_config()
    except (SystemExit, Exception):  # noqa: BLE001
        return {
            "name": "Default Profile",
            "status": "WARN",
            "value": "Config not loadable",
            "detail": "Cannot check default profile",
        }

    default = config.get("default_profile", "")
    if default == "test":
        return {
            "name": "Default Profile",
            "status": "PASS",
            "value": "test",
            "detail": "",
        }
    return {
        "name": "Default Profile",
        "status": "WARN",
        "value": default or "(none)",
        "detail": "Expected 'test' during alpha",
    }


def check_secret_scanner_available() -> dict:
    """Check if scripts/security/scan_for_secrets.py exists.

    PASS if exists, WARN if not.
    """
    scanner_path = PROJECT_ROOT / "scripts" / "security" / "scan_for_secrets.py"
    if scanner_path.exists():
        return {
            "name": "Secret Scanner",
            "status": "PASS",
            "value": str(scanner_path),
            "detail": "",
        }
    return {
        "name": "Secret Scanner",
        "status": "WARN",
        "value": "Not found",
        "detail": "scripts/security/scan_for_secrets.py missing",
    }


def check_benchmark_prompts() -> dict:
    """Check if benchmarks/prompts/local_benchmark_prompts.jsonl exists and has valid JSON lines.

    PASS if exists and has valid lines, WARN if missing or empty,
    FAIL if invalid JSON.
    """
    prompts_path = PROJECT_ROOT / "benchmarks" / "prompts" / "local_benchmark_prompts.jsonl"

    if not prompts_path.exists():
        return {
            "name": "Benchmark Prompts",
            "status": "WARN",
            "value": "File not found",
            "detail": "benchmarks/prompts/local_benchmark_prompts.jsonl missing",
        }

    try:
        content = prompts_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return {
            "name": "Benchmark Prompts",
            "status": "WARN",
            "value": "Cannot read file",
            "detail": str(exc),
        }

    if not content:
        return {
            "name": "Benchmark Prompts",
            "status": "WARN",
            "value": "File is empty",
            "detail": "",
        }

    lines = content.splitlines()
    try:
        for line in lines:
            json.loads(line)
    except json.JSONDecodeError as exc:
        return {
            "name": "Benchmark Prompts",
            "status": "FAIL",
            "value": f"Invalid JSON on line {exc.lineno}",
            "detail": str(exc),
        }

    return {
        "name": "Benchmark Prompts",
        "status": "PASS",
        "value": f"{len(lines)} valid prompt(s)",
        "detail": "",
    }


def check_kimari_version() -> dict:
    """Check Kimari version is set.

    PASS if version is set, WARN if empty or unusual.
    """
    if KIMARI_VERSION and KIMARI_VERSION != "0.0.0":
        return {
            "name": "Kimari Version",
            "status": "PASS",
            "value": KIMARI_VERSION,
            "detail": "",
        }
    return {
        "name": "Kimari Version",
        "status": "WARN",
        "value": KIMARI_VERSION or "(unset)",
        "detail": "Version not properly set",
    }


def check_cuda_nvidia() -> dict:
    """Best-effort check for CUDA/NVIDIA GPU availability.

    PASS if GPU detected with CUDA, WARN if GPU without CUDA,
    WARN if no GPU (CPU-only mode is acceptable).
    No FAIL state — GPU is recommended, not required.
    """
    gpu = detect_gpu()
    cuda_ver = detect_cuda_version()
    has_cuda = detect_cuda()

    if gpu and cuda_ver:
        return {
            "name": "CUDA/NVIDIA",
            "status": "PASS",
            "value": f"{gpu['name']} — CUDA {cuda_ver}",
            "detail": "",
        }
    if gpu and has_cuda:
        return {
            "name": "CUDA/NVIDIA",
            "status": "PASS",
            "value": f"{gpu['name']} — CUDA available (version unknown)",
            "detail": "",
        }
    if gpu:
        return {
            "name": "CUDA/NVIDIA",
            "status": "WARN",
            "value": f"{gpu['name']} — CUDA not detected",
            "detail": "GPU found but CUDA not available — check driver installation",
        }
    return {
        "name": "CUDA/NVIDIA",
        "status": "WARN",
        "value": "No NVIDIA GPU detected",
        "detail": "CPU-only mode — performance will be limited",
    }


def check_gpu_compute_capability() -> dict:
    """Check GPU compute capability and warn about incompatible PyTorch builds.

    WARNs if GPU is Pascal (sm_61, e.g. GTX 1060) and PyTorch build is
    cu128/cu130 (which dropped sm_61 support). Recommends cu126 legacy build.

    Fallback chain for compute capability detection:
      1. PyTorch (most accurate)
      2. llama-server --version output

    No FAIL state — this is informational.
    """
    # Try to get compute capability via torch
    compute_cap = None
    gpu_name = None
    torch_version = None
    torch_cuda_version = None
    source = None

    try:
        import torch

        torch_version = torch.__version__
        if torch.cuda.is_available():
            compute_cap = torch.cuda.get_device_capability(0)
            gpu_name = torch.cuda.get_device_name(0)
            torch_cuda_version = torch.version.cuda
            source = "torch"
    except (ImportError, RuntimeError):
        pass

    # Fallback: try llama-server --version for compute capability
    if compute_cap is None:
        llama_cap = detect_compute_capability_from_llama_server()
        if llama_cap is not None:
            compute_cap = tuple(int(x) for x in llama_cap.split("."))
            if len(compute_cap) < 2:
                compute_cap = None
            else:
                source = "llama-server"

    # Also try nvidia-smi for GPU name if torch didn't work
    if gpu_name is None:
        gpu = detect_gpu()
        if gpu:
            gpu_name = gpu["name"]

    # No GPU detected at all — just report
    if compute_cap is None and gpu_name is None:
        return {
            "name": "GPU Compute Capability",
            "status": "WARN",
            "value": "No GPU detected",
            "detail": "Cannot check compute capability without GPU",
        }

    # Have compute capability
    if compute_cap is not None:
        cap_str = f"sm_{compute_cap[0]}{compute_cap[1]}"
        cap_major, cap_minor = compute_cap

        # Build value string with source attribution
        source_label = f" (via {source})" if source else ""

        # Check if Pascal (sm_61) with incompatible PyTorch
        is_pascal = cap_major == 6 and cap_minor == 1
        if is_pascal and torch_cuda_version:
            # cu126 = supports sm_61, cu128/cu130 = dropped sm_61
            cuda_ver_num = torch_cuda_version.replace(".", "")
            if int(cuda_ver_num) >= 128:
                return {
                    "name": "GPU Compute Capability",
                    "status": "WARN",
                    "value": f"{gpu_name} — {cap_str}{source_label} — PyTorch {torch_version}+cu{torch_cuda_version}",
                    "detail": (
                        f"Pascal GPU ({cap_str}) detected with PyTorch cu{torch_cuda_version}. "
                        f"PyTorch builds cu128+ dropped sm_61 support. "
                        f"Install PyTorch cu126 legacy: "
                        f"pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu126"
                    ),
                }

        # Normal case - GPU and torch compatible
        torch_info = f" — PyTorch {torch_version}+cu{torch_cuda_version}" if torch_cuda_version else ""
        return {
            "name": "GPU Compute Capability",
            "status": "PASS",
            "value": f"{gpu_name} — {cap_str}{source_label}{torch_info}",
            "detail": "",
        }

    # Have GPU name but no compute capability (torch and llama-server both failed)
    return {
        "name": "GPU Compute Capability",
        "status": "WARN",
        "value": f"{gpu_name} — compute capability unknown",
        "detail": "Install PyTorch with CUDA or ensure llama-server is available for compute capability detection",
    }


def check_packaged_defaults() -> dict:
    """Check if packaged defaults (models, profiles, schema) exist.

    PASS if all three exist, WARN if some missing.
    """
    defaults_dir = PROJECT_ROOT / "kimari" / "defaults"
    required = {
        "models": defaults_dir / "kimari.models.json",
        "profiles": defaults_dir / "kimari.profiles.json",
        "schema": defaults_dir / "kimari.profiles.schema.json",
    }

    missing = {name: str(path) for name, path in required.items() if not path.exists()}

    if not missing:
        return {
            "name": "Packaged Defaults",
            "status": "PASS",
            "value": "All defaults available",
            "detail": "",
        }
    return {
        "name": "Packaged Defaults",
        "status": "WARN",
        "value": f"Missing: {', '.join(sorted(missing.keys()))}",
        "detail": "Some packaged defaults not found",
    }


def check_gateway_availability() -> dict:
    """Check if gateway module is available (design/dry-run only).

    PASS if gateway module exists, WARN if not.
    This never starts a server — just checks module presence.
    """
    gateway_init = PROJECT_ROOT / "kimari" / "gateway" / "__init__.py"
    if gateway_init.exists():
        return {
            "name": "Gateway Module",
            "status": "PASS",
            "value": "Available (dry-run only)",
            "detail": "Gateway server is planned for a future release",
        }
    return {
        "name": "Gateway Module",
        "status": "WARN",
        "value": "Not available",
        "detail": "kimari/gateway/ module not found",
    }


def check_integration_docs() -> dict:
    """Check if Open WebUI/OpenClaw integration docs exist.

    PASS if integration docs found, WARN if missing.
    """
    docs = {
        "Open WebUI/OpenClaw Quick Config": PROJECT_ROOT / "docs" / "OPENWEBUI_OPENCLAW_QUICK_CONFIG.md",
        "OpenClaw Integration": PROJECT_ROOT / "docs" / "integrations" / "OPENCLAW.md",
        "Hermes Integration": PROJECT_ROOT / "docs" / "integrations" / "HERMES.md",
        "OpenAI Compatible Clients": PROJECT_ROOT / "docs" / "integrations" / "OPENAI_COMPATIBLE_CLIENTS.md",
    }

    found = {name for name, path in docs.items() if path.exists()}
    missing = {name for name, path in docs.items() if not path.exists()}

    if not missing:
        return {
            "name": "Integration Docs",
            "status": "PASS",
            "value": f"All {len(found)} docs available",
            "detail": "",
        }
    if found:
        return {
            "name": "Integration Docs",
            "status": "WARN",
            "value": f"Missing: {', '.join(sorted(missing))}",
            "detail": "",
        }
    return {
        "name": "Integration Docs",
        "status": "WARN",
        "value": "No integration docs found",
        "detail": "",
    }


def check_preview_gate_blocked() -> dict:
    """Check that the preview gate is BLOCKED during alpha.

    Always returns PASS with value "BLOCKED" during alpha.
    FAIL if any doc says gate is APPROVED that isn't conditional
    (checks ADAPTER_PREVIEW_GATE.md for unconditional APPROVED
    claims).
    """
    gate_doc = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"

    if not gate_doc.exists():
        return {
            "name": "Preview Gate",
            "status": "PASS",
            "value": "BLOCKED",
            "detail": "Gate doc not found (assumed BLOCKED)",
        }

    try:
        content = gate_doc.read_text(encoding="utf-8")
    except OSError:
        return {
            "name": "Preview Gate",
            "status": "PASS",
            "value": "BLOCKED",
            "detail": "",
        }

    # Scan for unconditional APPROVED claims.
    # "APPROVED_FOR_PRIVATE_TESTING" and "APPROVED_FOR_PUBLIC_PREVIEW"
    # are conditional state names — they require explicit human decisions
    # and are part of the state machine, so they are always conditional.
    # We look for standalone "APPROVED" that represents an unconditional claim.
    for line in content.splitlines():
        stripped = line.strip()
        upper = stripped.upper()

        # Skip lines that are part of conditional state names
        if "APPROVED_FOR_PRIVATE_TESTING" in upper:
            continue
        if "APPROVED_FOR_PUBLIC_PREVIEW" in upper:
            continue

        # If "APPROVED" remains, check for unconditional claims
        if "APPROVED" in upper:
            # Skip conditional / hypothetical language
            if any(
                phrase in upper
                for phrase in (
                    "MAY BE APPROVED",
                    "CAN BE APPROVED",
                    "TO BE APPROVED",
                    "MAY BE",
                    "CAN BE",
                    "REQUIRE",
                )
            ):
                continue

            # Check for clear unconditional approval claims
            if any(phrase in upper for phrase in ("STATUS: APPROVED", "IS APPROVED", "STATE: APPROVED")):
                return {
                    "name": "Preview Gate",
                    "status": "FAIL",
                    "value": "NOT BLOCKED",
                    "detail": f"Unconditional APPROVED found: {stripped[:80]}",
                }

    return {
        "name": "Preview Gate",
        "status": "PASS",
        "value": "BLOCKED",
        "detail": "",
    }


# ─── Orchestrator ─────────────────────────────────────────────────────────────


def run_deep_checks(project_root: Path | None = None) -> list[dict]:
    """Run all deep diagnostic checks in order and return results with summary.

    Parameters
    ----------
    project_root:
        Reserved for future use / testing.  Individual checks currently
        resolve paths through ``kimari.core.constants.PROJECT_ROOT`` and
        ``kimari.core.paths``.  Pass ``None`` (default) for normal
        operation; in tests, monkeypatch ``PROJECT_ROOT`` instead.

    Returns
    -------
    list[dict]
        A list of result dicts (one per check) followed by a summary
        dict.  Each result dict has keys: ``name``, ``status``
        (``PASS``/``WARN``/``FAIL``), ``value``, ``detail``.  The
        summary dict has ``name="Summary"`` with a ``value`` dict
        containing ``total``, ``pass_count``, ``warn_count``,
        ``fail_count``.
    """
    # project_root is accepted for API stability but individual checks
    # use their own path resolution.  Tests should monkeypatch
    # kimari.core.constants.PROJECT_ROOT or the paths module functions.
    _ = project_root  # noqa: F841 – intentionally unused for now

    checks = [
        check_python(),
        check_kimari_version(),
        check_paths(),
        check_config(),
        check_models_dir(),
        check_packaged_defaults(),
        check_llama_server_presence(),
        check_cuda_nvidia(),
        check_gpu_compute_capability(),
        check_default_profile(),
        check_secret_scanner_available(),
        check_benchmark_prompts(),
        check_gateway_availability(),
        check_integration_docs(),
        check_preview_gate_blocked(),
    ]

    pass_count = sum(1 for c in checks if c["status"] == "PASS")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")

    summary = {
        "name": "Summary",
        "status": "INFO",
        "value": {
            "total": len(checks),
            "pass_count": pass_count,
            "warn_count": warn_count,
            "fail_count": fail_count,
        },
        "detail": "",
    }

    return checks + [summary]
