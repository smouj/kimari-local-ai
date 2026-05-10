"""
Tests for v0.1.10-alpha: Performance module, optimize/perf commands, new profiles, integrations.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ─── Performance estimator tests ──────────────────────────────────────────


def test_estimate_vram_usage_returns_dict():
    """estimate_vram_usage returns expected keys."""
    from kimari.performance.estimator import estimate_vram_usage

    result = estimate_vram_usage(
        model_size_gb=0.7,
        gpu_layers="all",
        total_layers=32,
        ctx_size=4096,
        cache_type_k="f16",
        cache_type_v="f16",
    )
    assert "expected_vram_gb" in result
    assert "model_gpu_part_gb" in result
    assert "kv_cache_gb" in result
    assert "confidence" in result
    assert "warnings" in result
    assert result["expected_vram_gb"] > 0


def test_estimate_vram_usage_q8_0_smaller():
    """q8_0 cache uses less VRAM than f16."""
    from kimari.performance.estimator import estimate_vram_usage

    f16_result = estimate_vram_usage(0.7, "all", 32, 4096, "f16", "f16")
    q8_result = estimate_vram_usage(0.7, "all", 32, 4096, "q8_0", "q8_0")
    assert q8_result["kv_cache_gb"] < f16_result["kv_cache_gb"]


def test_vram_safe_budget():
    """vram_safe_budget returns correct values for known GPUs."""
    from kimari.performance.estimator import vram_safe_budget

    assert vram_safe_budget(6.0) == 4.92  # 82%
    assert vram_safe_budget(8.0) == 6.88  # 86%


def test_estimate_ram_usage():
    """estimate_ram_usage returns expected keys."""
    from kimari.performance.estimator import estimate_ram_usage

    result = estimate_ram_usage(0.7, "all", 32)
    assert "expected_ram_gb" in result
    assert "offload_ratio" in result
    assert result["offload_ratio"] == 1.0  # "all" layers


# ─── Recommender tests ──────────────────────────────────────────────────


def test_recommend_profile_settings_returns_keys():
    """recommend_profile_settings returns all expected keys."""
    from kimari.performance.recommender import recommend_profile_settings

    result = recommend_profile_settings(6.0, 0.7, "balanced")
    assert "ctx" in result
    assert "batch" in result
    assert "ubatch" in result
    assert "cache_type_k" in result
    assert "cache_type_v" in result
    assert "gpu_layers" in result
    assert "flash_attn" in result
    assert "parallel" in result
    assert "expected_vram_gb" in result
    assert "expected_ram_gb" in result
    assert "warnings" in result
    assert "confidence" in result


def test_recommend_context_fits():
    """recommend_context returns a valid context size."""
    from kimari.performance.recommender import recommend_context

    result = recommend_context(6.0, 0.7, "q8_0")
    assert result["ctx"] > 0
    assert "reasoning" in result


def test_recommend_kv_cache_tight_vram():
    """recommend_kv_cache returns q8_0 for tight VRAM."""
    from kimari.performance.recommender import recommend_kv_cache

    result = recommend_kv_cache(6.0, 5.0)  # Large model, tight VRAM
    assert result["cache_type_k"] == "q8_0"


# ─── GGUF metadata tests ──────────────────────────────────────────────


def test_gguf_metadata_missing_file():
    """read_gguf_metadata returns defaults for missing file."""
    from kimari.performance.gguf_metadata import read_gguf_metadata

    result = read_gguf_metadata("/nonexistent/model.gguf")
    assert result["parse_success"] is False
    assert result["n_layer"] == 32  # Default


def test_gguf_metadata_corrupt_file():
    """read_gguf_metadata returns defaults for corrupt file."""
    import tempfile

    from kimari.performance.gguf_metadata import read_gguf_metadata

    with tempfile.NamedTemporaryFile(suffix=".gguf", delete=False) as f:
        f.write(b"CORRUPT_DATA_NOT_GGUF")
        temp_path = f.name

    result = read_gguf_metadata(temp_path)
    assert result["parse_success"] is False
    Path(temp_path).unlink(missing_ok=True)


# ─── CLI command tests ──────────────────────────────────────────────────


def _run_kimari(*args: str) -> subprocess.CompletedProcess:
    """Run kimari CLI via python -m."""
    cmd = [sys.executable, "-m", "kimari.cli.main", *list(args)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def test_optimize_test_profile_json():
    """kimari optimize --profile test --json returns valid JSON."""
    result = _run_kimari("optimize", "--profile", "test", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["profile"] == "test"
    assert "recommendations" in data
    assert "estimates" in data
    assert "confidence" in data


def test_optimize_with_mode():
    """kimari optimize --profile test --mode fast --json returns valid JSON."""
    result = _run_kimari("optimize", "--profile", "test", "--mode", "fast", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["performance_mode"] == "fast"


def test_perf_dry_run_json():
    """kimari perf --profile test --dry-run --json returns valid JSON."""
    result = _run_kimari("perf", "--profile", "test", "--dry-run", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["profile"] == "test"
    assert "modes" in data
    assert data["dry_run"] is True


def test_perf_matrix():
    """kimari perf --profile test --matrix --dry-run returns multiple modes."""
    result = _run_kimari("perf", "--profile", "test", "--matrix", "--dry-run", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["modes"]) >= 4  # safe, balanced, fast, ide, agent


# ─── build_server_cmd tests ────────────────────────────────────────────


def test_build_cmd_adds_flash_attn():
    """build_server_cmd adds --flash-attn when flash_attn='on'."""
    from kimari.cli.main import build_server_cmd

    profile = {
        "model": "models/test.gguf",
        "host": "127.0.0.1",
        "port": 11435,
        "gpu_layers": "all",
        "ctx": 4096,
        "batch": 128,
        "ubatch": 64,
        "cache_type_k": "f16",
        "cache_type_v": "f16",
        "threads": 4,
        "flash_attn": "on",
    }
    cmd = build_server_cmd("llama-server", profile)
    assert "--flash-attn" in cmd


def test_build_cmd_no_flash_attn_auto():
    """build_server_cmd does NOT add --flash-attn when flash_attn='auto'."""
    from kimari.cli.main import build_server_cmd

    profile = {
        "model": "models/test.gguf",
        "host": "127.0.0.1",
        "port": 11435,
        "gpu_layers": "all",
        "ctx": 4096,
        "batch": 128,
        "ubatch": 64,
        "cache_type_k": "f16",
        "cache_type_v": "f16",
        "threads": 4,
        "flash_attn": "auto",
    }
    cmd = build_server_cmd("llama-server", profile)
    assert "--flash-attn" not in cmd


def test_build_cmd_adds_mlock():
    """build_server_cmd adds --mlock when mlock=True."""
    from kimari.cli.main import build_server_cmd

    profile = {
        "model": "models/test.gguf",
        "host": "127.0.0.1",
        "port": 11435,
        "gpu_layers": "all",
        "ctx": 4096,
        "batch": 128,
        "ubatch": 64,
        "cache_type_k": "f16",
        "cache_type_v": "f16",
        "threads": 4,
        "mlock": True,
    }
    cmd = build_server_cmd("llama-server", profile)
    assert "--mlock" in cmd


def test_build_cmd_no_mlock_when_false():
    """build_server_cmd does NOT add --mlock when mlock=False."""
    from kimari.cli.main import build_server_cmd

    profile = {
        "model": "models/test.gguf",
        "host": "127.0.0.1",
        "port": 11435,
        "gpu_layers": "all",
        "ctx": 4096,
        "batch": 128,
        "ubatch": 64,
        "cache_type_k": "f16",
        "cache_type_v": "f16",
        "threads": 4,
        "mlock": False,
    }
    cmd = build_server_cmd("llama-server", profile)
    assert "--mlock" not in cmd


# ─── New profiles tests ────────────────────────────────────────────────


def test_new_profiles_exist():
    """All 8 new profiles exist in config."""
    from kimari.config.loader import load_config

    config = load_config()
    expected = [
        "gtx1060-safe",
        "gtx1060-fast",
        "gtx1080-balanced",
        "gtx1080-longctx",
        "ide-local",
        "agent-local",
        "openclaw-local",
        "hermes-local",
    ]
    for name in expected:
        assert name in config["profiles"], f"Profile '{name}' missing"


def test_new_profiles_have_performance_mode():
    """New profiles have performance_mode field."""
    from kimari.config.loader import load_config

    config = load_config()
    for name in ["gtx1060-safe", "ide-local", "openclaw-local"]:
        profile = config["profiles"][name]
        assert "performance_mode" in profile, f"Profile '{name}' missing performance_mode"


def test_new_profiles_have_flash_attn():
    """New profiles have flash_attn field."""
    from kimari.config.loader import load_config

    config = load_config()
    for name in ["gtx1060-safe", "ide-local", "openclaw-local"]:
        profile = config["profiles"][name]
        assert "flash_attn" in profile, f"Profile '{name}' missing flash_attn"


# ─── Integration docs tests ────────────────────────────────────────────


def test_openclaw_doc_exists():
    """docs/integrations/OPENCLAW.md exists."""
    assert (PROJECT_ROOT / "docs" / "integrations" / "OPENCLAW.md").exists()


def test_hermes_doc_exists():
    """docs/integrations/HERMES.md exists."""
    assert (PROJECT_ROOT / "docs" / "integrations" / "HERMES.md").exists()


def test_continue_doc_exists():
    """docs/integrations/CONTINUE.md exists."""
    assert (PROJECT_ROOT / "docs" / "integrations" / "CONTINUE.md").exists()


def test_openai_compatible_doc_exists():
    """docs/integrations/OPENAI_COMPATIBLE_CLIENTS.md exists."""
    assert (PROJECT_ROOT / "docs" / "integrations" / "OPENAI_COMPATIBLE_CLIENTS.md").exists()


def test_openclaw_doc_mentions_chat_completions():
    """OpenClaw doc mentions Chat Completions."""
    text = (PROJECT_ROOT / "docs" / "integrations" / "OPENCLAW.md").read_text()
    assert "chat completions" in text.lower() or "Chat Completions" in text


def test_openclaw_config_example_exists():
    """config/integrations/openclaw.kimari.example.json exists."""
    path = PROJECT_ROOT / "config" / "integrations" / "openclaw.kimari.example.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert "baseUrl" in data
    assert "127.0.0.1" in data["baseUrl"]


def test_hermes_config_example_exists():
    """config/integrations/hermes.kimari.example.yaml exists."""
    assert (PROJECT_ROOT / "config" / "integrations" / "hermes.kimari.example.yaml").exists()


def test_continue_config_example_exists():
    """config/integrations/continue.kimari.example.yaml exists."""
    assert (PROJECT_ROOT / "config" / "integrations" / "continue.kimari.example.yaml").exists()


# ─── Release check tests ───────────────────────────────────────────────


def test_release_check_script_passes():
    """scripts/release/check-release.py exits with code 0."""
    result = subprocess.run(
        [sys.executable, "scripts/release/check-release.py"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"


def test_no_responses_api_false_claim():
    """No file claims 'Responses API is supported' without qualification."""
    # Check key files for unqualified Responses API support claims
    for path in [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "CHANGELOG.md",
        PROJECT_ROOT / "docs" / "integrations" / "OPENCLAW.md",
    ]:
        if path.exists():
            text = path.read_text().lower()
            # Should NOT contain these false claims
            assert "responses api is supported" not in text, f"False claim in {path}"
            assert "responses api supported" not in text, f"False claim in {path}"


def test_default_profile_still_test():
    """default_profile is still 'test'."""
    from kimari.config.loader import load_config

    config = load_config()
    assert config["default_profile"] == "test"
