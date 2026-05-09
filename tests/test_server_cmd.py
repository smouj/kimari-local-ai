"""
Tests for Kimari server command building.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "cli"))

from kimari_cli import build_server_cmd


def _get_test_profile():
    """Return a minimal test profile dict matching the real config structure."""
    return {
        "name": "Test Model",
        "model": "models/Kimari-base-test-Q4_K_M.gguf",
        "ctx": 4096,
        "batch": 128,
        "ubatch": 64,
        "cache_type_k": "f16",
        "cache_type_v": "f16",
        "host": "127.0.0.1",
        "port": 11435,
        "gpu_layers": "all",
        "threads": 4,
        "quantization": "Q4_K_M",
    }


def test_build_server_cmd_basic():
    """Returns list starting with llama-server, has -m, --host, --port, -c, -b, -ub."""
    profile = _get_test_profile()
    cmd = build_server_cmd("/usr/bin/llama-server", profile)

    assert cmd[0] == "/usr/bin/llama-server"
    assert "-m" in cmd
    assert "--host" in cmd
    assert "--port" in cmd
    assert "-c" in cmd
    assert "-b" in cmd
    assert "-ub" in cmd


def test_build_server_cmd_model_path():
    """Model path is absolute."""
    profile = _get_test_profile()
    cmd = build_server_cmd("/usr/bin/llama-server", profile)

    # Find the model path (value after -m flag)
    m_index = cmd.index("-m")
    model_path = cmd[m_index + 1]
    assert Path(model_path).is_absolute()


def test_build_server_cmd_with_model_override():
    """--model override replaces model."""
    profile = _get_test_profile()
    cmd = build_server_cmd(
        "/usr/bin/llama-server", profile,
        model_override="models/other-model.gguf"
    )

    m_index = cmd.index("-m")
    model_path = cmd[m_index + 1]
    assert "other-model.gguf" in model_path


def test_build_server_cmd_with_host_override():
    """--host override replaces host."""
    profile = _get_test_profile()
    cmd = build_server_cmd(
        "/usr/bin/llama-server", profile,
        host_override="0.0.0.0"
    )

    host_index = cmd.index("--host")
    assert cmd[host_index + 1] == "0.0.0.0"


def test_build_server_cmd_with_port_override():
    """--port override replaces port."""
    profile = _get_test_profile()
    cmd = build_server_cmd(
        "/usr/bin/llama-server", profile,
        port_override=9999
    )

    port_index = cmd.index("--port")
    assert cmd[port_index + 1] == "9999"


def test_build_server_cmd_with_ctx_override():
    """--ctx override replaces context."""
    profile = _get_test_profile()
    cmd = build_server_cmd(
        "/usr/bin/llama-server", profile,
        ctx_override=2048
    )

    c_index = cmd.index("-c")
    assert cmd[c_index + 1] == "2048"


def test_build_server_cmd_threads():
    """Threads flag is added when profile has threads."""
    profile = _get_test_profile()
    profile["threads"] = 4
    cmd = build_server_cmd("/usr/bin/llama-server", profile)

    assert "-t" in cmd
    t_index = cmd.index("-t")
    assert cmd[t_index + 1] == "4"
