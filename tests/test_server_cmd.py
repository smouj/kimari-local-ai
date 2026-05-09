"""
Tests for build_server_cmd and server command construction.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kimari.cli.main import build_server_cmd


def test_build_server_cmd_basic(sample_profile):
    """build_server_cmd produces a valid command list."""
    cmd = build_server_cmd("/usr/bin/llama-server", sample_profile)
    assert cmd[0] == "/usr/bin/llama-server"
    assert "-m" in cmd
    assert "--host" in cmd
    assert "--port" in cmd
    assert "-c" in cmd
    assert "-b" in cmd
    assert "-ub" in cmd


def test_build_server_cmd_model_path(sample_profile):
    """build_server_cmd includes the model path."""
    cmd = build_server_cmd("/usr/bin/llama-server", sample_profile)
    model_idx = cmd.index("-m")
    model_path = cmd[model_idx + 1]
    assert "Kimari-base-test-Q4_K_M.gguf" in model_path


def test_build_server_cmd_host_port(sample_profile):
    """build_server_cmd includes host and port from profile."""
    cmd = build_server_cmd("/usr/bin/llama-server", sample_profile)
    host_idx = cmd.index("--host")
    port_idx = cmd.index("--port")
    assert cmd[host_idx + 1] == "127.0.0.1"
    assert cmd[port_idx + 1] == "11435"


def test_build_server_cmd_model_override(sample_profile):
    """build_server_cmd respects model override."""
    cmd = build_server_cmd("/usr/bin/llama-server", sample_profile,
                           model_override="models/custom.gguf")
    model_idx = cmd.index("-m")
    assert "custom.gguf" in cmd[model_idx + 1]


def test_build_server_cmd_host_override(sample_profile):
    """build_server_cmd respects host override."""
    cmd = build_server_cmd("/usr/bin/llama-server", sample_profile,
                           host_override="0.0.0.0")
    host_idx = cmd.index("--host")
    assert cmd[host_idx + 1] == "0.0.0.0"


def test_build_server_cmd_port_override(sample_profile):
    """build_server_cmd respects port override."""
    cmd = build_server_cmd("/usr/bin/llama-server", sample_profile,
                           port_override=9999)
    port_idx = cmd.index("--port")
    assert cmd[port_idx + 1] == "9999"


def test_build_server_cmd_ctx_override(sample_profile):
    """build_server_cmd respects ctx override."""
    cmd = build_server_cmd("/usr/bin/llama-server", sample_profile,
                           ctx_override=2048)
    ctx_idx = cmd.index("-c")
    assert cmd[ctx_idx + 1] == "2048"


def test_build_server_cmd_cache_types(sample_profile):
    """build_server_cmd includes cache type flags."""
    cmd = build_server_cmd("/usr/bin/llama-server", sample_profile)
    assert "--cache-type-k" in cmd
    assert "--cache-type-v" in cmd
