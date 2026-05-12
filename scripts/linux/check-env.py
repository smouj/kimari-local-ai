#!/usr/bin/env python3
"""
check-env.py — Verify the development environment for Kimari Local AI.

Checks Python version, CUDA availability, ROCm availability (experimental),
llama-server binary, required Python packages, and configuration files.

Note: This file is maintained at scripts/common/check-env.py.
This copy exists for backward compatibility.
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def check_python():
    """Check Python version."""
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    # Python 3.10+ is required; this script only runs on 3.10+ (enforced by pyproject.toml)
    print(f"  [OK]   Python: {version}")
    return True


def check_cuda():
    """Check CUDA availability."""
    nvcc = shutil.which("nvcc")
    nvidia_smi = shutil.which("nvidia-smi")
    if nvcc:
        try:
            result = subprocess.run([nvcc, "--version"], capture_output=True, text=True, timeout=10)
            version_line = [line for line in result.stdout.split("\n") if "release" in line.lower()]
            version = version_line[0].strip() if version_line else "unknown"
            print(f"  [OK]   CUDA: {version}")
        except Exception:
            print("  [OK]   CUDA: available (version unknown)")
        return True
    elif nvidia_smi:
        print("  [OK]   CUDA: nvidia-smi found (nvcc not in PATH)")
        return True
    else:
        print("  [WARN] CUDA: not found (optional — needed for GPU inference)")
        return False


def check_rocm():
    """Check ROCm availability (experimental)."""
    hipcc = shutil.which("hipcc")
    if hipcc:
        try:
            result = subprocess.run([hipcc, "--version"], capture_output=True, text=True, timeout=10)
            version_line = [line for line in result.stdout.split("\n") if line.strip()]
            version = version_line[-1].strip() if version_line else "unknown"
            print(f"  [OK]   ROCm: {version} (experimental)")
        except Exception:
            print("  [OK]   ROCm: available (experimental, version unknown)")
        return True
    else:
        print("  [INFO] ROCm: not found (experimental — optional for AMD GPUs)")
        return True  # Not a failure, just informational


def check_llama_server():
    """Check llama-server binary."""
    llama = shutil.which("llama-server") or shutil.which("llama_server")
    if llama:
        print(f"  [OK]   llama-server: {llama}")
        return True
    else:
        # Check common locations
        for path in [
            PROJECT_ROOT / "llama-server",
            PROJECT_ROOT / "bin" / "llama-server",
            PROJECT_ROOT / "deps" / "llama.cpp" / "build" / "bin" / "llama-server",
        ]:
            if path.exists():
                print(f"  [OK]   llama-server: {path}")
                return True
        print("  [WARN] llama-server: not found (build with scripts/linux/build-llamacpp-cuda.sh)")
        return False


def check_packages():
    """Check required Python packages."""
    required = ["requests", "jsonschema", "pytest"]
    all_ok = True
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  [OK]   Package: {pkg}")
        except ImportError:
            print(f"  [WARN] Package: {pkg} (not installed)")
            all_ok = False
    return all_ok


def check_config():
    """Check configuration files."""
    all_ok = True
    for name in ["kimari.profiles.json", "kimari.models.json", "kimari.profiles.schema.json"]:
        path = PROJECT_ROOT / "config" / name
        if path.exists():
            print(f"  [OK]   Config: {name}")
        else:
            print(f"  [FAIL] Config: {name} (missing!)")
            all_ok = False
    return all_ok


def main():
    print("\n  Kimari Environment Check\n")
    results = [
        check_python(),
        check_cuda(),
        check_rocm(),
        check_llama_server(),
        check_packages(),
        check_config(),
    ]
    print()
    if all(results):
        print("  ✓ All checks passed.")
    else:
        print("  ⚠ Some checks failed or need attention.")
        print("  Kimari may work with limitations.")


if __name__ == "__main__":
    main()
