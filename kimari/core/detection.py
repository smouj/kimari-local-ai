"""
System detection utilities for Kimari.

Detects GPU, CUDA, llama-server binary, and port availability.
"""

import os
import re
import shutil
import socket
import subprocess
from pathlib import Path

from kimari.core.constants import PROJECT_ROOT


def _nvidia_smi_path() -> str | None:
    """Find nvidia-smi, including WSL2 non-standard locations."""
    # Standard PATH lookup
    path = shutil.which("nvidia-smi")
    if path:
        return path
    # WSL2: nvidia-smi lives here but is not on PATH
    wsl_path = "/usr/lib/wsl/lib/nvidia-smi"
    if Path(wsl_path).exists():
        return wsl_path
    # Windows interop (rare)
    win_path = shutil.which("nvidia-smi.exe")
    if win_path:
        return win_path
    return None


def _nvcc_path() -> str | None:
    """Find nvcc, including WSL2 non-standard locations."""
    path = shutil.which("nvcc")
    if path:
        return path
    # Common CUDA toolkit paths
    for p in ["/usr/local/cuda/bin/nvcc", "/usr/lib/wsl/lib/nvcc"]:
        if Path(p).exists():
            return p
    return None


def detect_gpu() -> dict | None:
    """Detect NVIDIA GPU using nvidia-smi.

    Returns dict with 'name', 'vram_mb', 'driver' or None if not found.
    """
    nvidia_smi = _nvidia_smi_path()
    if not nvidia_smi:
        return None
    try:
        result = subprocess.run(
            [nvidia_smi,
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines:
                parts = lines[0].split(", ")
                if len(parts) >= 3:
                    return {
                        "name": parts[0].strip(),
                        "vram_mb": int(parts[1].strip()),
                        "driver": parts[2].strip(),
                    }
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return None


def detect_cuda_version_detailed() -> dict | None:
    """Detect CUDA version with source information via a fallback chain.

    Returns dict with 'version' and 'source' keys, or None if undetectable.

    Fallback order:
      1. nvcc --version  (source='nvcc')
      2. nvidia-smi header  (source='nvidia-smi')
      3. /usr/local/cuda/bin/nvcc  (source='nvcc')
    """
    # 1. Try nvcc from PATH
    nvcc = shutil.which("nvcc")
    if nvcc:
        try:
            result = subprocess.run(
                [nvcc, "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "release" in line.lower():
                        parts = line.split("release")
                        if len(parts) >= 2:
                            version = parts[1].strip().split(",")[0].strip()
                            return {"version": version, "source": "nvcc"}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # 2. Try nvidia-smi header ("CUDA Version: X.Y")
    nvidia_smi = _nvidia_smi_path()
    if nvidia_smi:
        try:
            result = subprocess.run(
                [nvidia_smi], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                match = re.search(r"CUDA Version:\s*(\d+\.\d+)", result.stdout)
                if match:
                    return {"version": match.group(1), "source": "nvidia-smi"}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # 3. Try /usr/local/cuda/bin/nvcc directly
    fallback_nvcc = "/usr/local/cuda/bin/nvcc"
    if Path(fallback_nvcc).exists():
        try:
            result = subprocess.run(
                [fallback_nvcc, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "release" in line.lower():
                        parts = line.split("release")
                        if len(parts) >= 2:
                            version = parts[1].strip().split(",")[0].strip()
                            return {"version": version, "source": "nvcc"}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return None


def detect_cuda_version() -> str | None:
    """Detect CUDA version (backward-compatible wrapper).

    Returns just the version string, or None if undetectable.
    For source information, use detect_cuda_version_detailed().
    """
    detailed = detect_cuda_version_detailed()
    if detailed:
        return detailed["version"]
    return None


def detect_compute_capability_from_llama_server() -> str | None:
    """Detect GPU compute capability from llama-server --version output.

    Runs llama-server --version and parses the output for a
    "compute capability N.N" pattern (e.g. "compute capability 6.1").

    Returns the compute capability string (e.g. "6.1") or None.
    Never raises — always returns None on failure.
    """
    try:
        llama_path = detect_llama_server()
        if not llama_path:
            return None
        result = subprocess.run(
            [llama_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout + result.stderr
        match = re.search(r"compute capability\s+(\d+\.\d+)", output, re.IGNORECASE)
        if match:
            return match.group(1)
    except Exception:  # noqa: BLE001
        pass
    return None


def detect_cuda() -> bool:
    """Check if CUDA is available via nvcc or nvidia-smi."""
    return _nvcc_path() is not None or _nvidia_smi_path() is not None


def detect_llama_server() -> str | None:
    """Find llama-server binary searching 7 locations in priority order."""
    # 1. LLAMA_SERVER environment variable
    env_llama = os.environ.get("LLAMA_SERVER")
    if env_llama:
        path = Path(env_llama)
        if path.exists():
            return str(path.resolve())

    # 2. KIMARI_LLAMA_SERVER environment variable
    env_kimari = os.environ.get("KIMARI_LLAMA_SERVER")
    if env_kimari:
        path = Path(env_kimari)
        if path.exists():
            return str(path.resolve())

    # 3. shutil.which("llama-server") (PATH)
    which_llama = shutil.which("llama-server")
    if which_llama:
        return which_llama

    # 4. shutil.which("llama_server") (PATH, underscore variant)
    which_llama_us = shutil.which("llama_server")
    if which_llama_us:
        return which_llama_us

    # 5. ./llama-server (relative to PROJECT_ROOT)
    rel_llama = PROJECT_ROOT / "llama-server"
    if rel_llama.exists():
        return str(rel_llama.resolve())

    # 6. ./bin/llama-server (relative to PROJECT_ROOT)
    bin_llama = PROJECT_ROOT / "bin" / "llama-server"
    if bin_llama.exists():
        return str(bin_llama.resolve())

    # 7. deps/llama.cpp/build/bin/llama-server (relative to PROJECT_ROOT)
    deps_llama = PROJECT_ROOT / "deps" / "llama.cpp" / "build" / "bin" / "llama-server"
    if deps_llama.exists():
        return str(deps_llama.resolve())

    return None


def is_port_free(host: str, port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0  # 0 means connected (port in use)
    except OSError:
        return False


def recommend_profile(config: dict, gpu: dict | None) -> str:
    """Recommend a GPU profile based on detected hardware."""
    if not gpu:
        return config.get("default_profile", "gtx1060")

    vram_gb = gpu["vram_mb"] / 1024
    profiles = config.get("profiles", {})

    # Try to match by GPU name first
    gpu_name_lower = gpu["name"].lower()
    for key, _profile in profiles.items():
        if key in gpu_name_lower:
            return key

    # Fall back to VRAM-based recommendation
    if vram_gb >= 8:
        return "gtx1080"
    elif vram_gb >= 6:
        return "gtx1060"
    else:
        return "gtx1060"  # Default, may warn about VRAM
