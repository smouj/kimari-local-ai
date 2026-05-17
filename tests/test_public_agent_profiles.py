"""Tests for public low-VRAM agent profiles (agent-qwen1060, agent-qwen1080, agent-smollm1060)."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROFILES_PATH = REPO / "config" / "kimari.profiles.json"
MODELS_PATH = REPO / "config" / "kimari.models.json"

NEW_AGENT_PROFILES = ["agent-qwen1060", "agent-qwen1080", "agent-smollm1060"]


def _profiles() -> dict:
    return json.loads(PROFILES_PATH.read_text())["profiles"]


def _models() -> list:
    return json.loads(MODELS_PATH.read_text())["models"]


def test_agent_profiles_exist():
    profiles = _profiles()
    for name in NEW_AGENT_PROFILES:
        assert name in profiles, f"Profile {name} not found"


def test_agent_profiles_not_kimari4b():
    """Agent profiles must NOT point to Kimari-4B (unpublished)."""
    profiles = _profiles()
    for name in NEW_AGENT_PROFILES:
        model = profiles[name]["model"]
        assert "Kimari" not in model, f"Profile {name} points to Kimari model: {model}"
        assert "kimari" not in model.lower(), f"Profile {name} points to kimari model: {model}"


def test_agent_profiles_not_tinyllama():
    """Agent profiles must NOT use TinyLlama (test-only model)."""
    profiles = _profiles()
    for name in NEW_AGENT_PROFILES:
        model = profiles[name]["model"]
        assert "tinyllama" not in model.lower(), f"Profile {name} uses TinyLlama: {model}"


def test_agent_profiles_parallel_is_one():
    profiles = _profiles()
    for name in NEW_AGENT_PROFILES:
        assert profiles[name]["parallel"] == 1, f"Profile {name} has parallel != 1"


def test_gtx1060_profiles_ctx_limit():
    """GTX 1060 profiles must use ctx <= 4096 to stay within 6 GB VRAM."""
    profiles = _profiles()
    for name in ["agent-qwen1060", "agent-smollm1060"]:
        assert profiles[name]["ctx"] <= 4096, f"Profile {name} has ctx > 4096"


def test_gtx1080_profile_ctx():
    """GTX 1080 agent profile can use 8K context."""
    profiles = _profiles()
    assert profiles["agent-qwen1080"]["ctx"] == 8192


def test_agent_profiles_bind_localhost():
    """Agent profiles must bind to 127.0.0.1 only."""
    profiles = _profiles()
    for name in NEW_AGENT_PROFILES:
        assert profiles[name]["host"] == "127.0.0.1", f"Profile {name} does not bind to localhost"


def test_agent_profiles_performance_mode():
    profiles = _profiles()
    for name in NEW_AGENT_PROFILES:
        assert profiles[name]["performance_mode"] == "agent", f"Profile {name} is not agent mode"


def test_agent_profiles_models_exist_in_registry():
    """Models referenced by agent profiles must exist in kimari.models.json."""
    profiles = _profiles()
    models = _models()
    model_filenames = {m["filename"] for m in models}
    for name in NEW_AGENT_PROFILES:
        model_path = profiles[name]["model"]
        filename = model_path.replace("models/", "")
        assert filename in model_filenames, f"Model {filename} for profile {name} not in models registry"


def test_qwen_profiles_use_qwen3_model():
    profiles = _profiles()
    for name in ["agent-qwen1060", "agent-qwen1080"]:
        assert "Qwen3-4B" in profiles[name]["model"], f"Profile {name} does not use Qwen3-4B"


def test_smollm_profile_uses_smollm_model():
    profiles = _profiles()
    assert "SmolLM3" in profiles["agent-smollm1060"]["model"]


def test_recommended_profiles_updated():
    """Models registry should point to agent profiles, not Kimari-4B-requiring ones."""
    models = _models()
    for m in models:
        if m["id"] == "recommended":
            assert m["recommended_profile"] == "agent-qwen1060", (
                f"Qwen3-4B recommended_profile should be agent-qwen1060, got {m['recommended_profile']}"
            )
        if m["id"] == "smollm3-3b-q4":
            assert m["recommended_profile"] == "agent-smollm1060", (
                f"SmolLM3 recommended_profile should be agent-smollm1060, got {m['recommended_profile']}"
            )


def test_no_invented_hashes():
    """Models with sha256 must not have placeholder or fake hashes."""
    models = _models()
    for m in models:
        if m.get("sha256") is not None:
            # If a hash exists, it must be a valid 64-char hex string
            assert len(m["sha256"]) == 64, f"Model {m['id']} has invalid sha256 length"
            assert all(c in "0123456789abcdef" for c in m["sha256"]), f"Model {m['id']} has non-hex sha256"


def test_dashboard_readme_node_version():
    """Dashboard README must not say Node 18+ since Next 16 needs 20.9+."""
    readme = (REPO / "apps" / "gateway-dashboard" / "README.md").read_text()
    assert "18+" not in readme or "20.9+" in readme, (
        "Dashboard README still references Node 18+ without 20.9+ correction"
    )


def test_run_agents_now_doc_exists():
    assert (REPO / "docs" / "RUN_AGENTS_NOW.md").exists(), "docs/RUN_AGENTS_NOW.md does not exist"


def test_readme_does_not_claim_kimari4b_published():
    """README must not claim Kimari-4B is published as an available model."""
    readme = (REPO / "README.md").read_text()
    lower = readme.lower()
    # These exact phrases should NOT appear (claiming it's currently available)
    assert "kimari-4b is available" not in lower
    assert "kimari-4b weights are available" not in lower
    assert "kimari-4b has been released" not in lower
    # "Kimari-4B is not public yet" or "when Kimari-4B is published" are acceptable (conditional/future)
    assert "Kimari-4B is not public yet" in readme or "not released" in lower


def test_public_model_registry_urls_use_expected_upstream_filenames():
    """Public model registry must use exact upstream GGUF filenames and valid repos."""
    models = _models()
    for m in models:
        if m["id"] == "recommended":
            assert m["filename"] == "Qwen3-4B-Q4_K_M.gguf", (
                f"Qwen3 filename should be Qwen3-4B-Q4_K_M.gguf, got {m['filename']}"
            )
            assert m["target_path"] == f"models/{m['filename']}", (
                f"target_path must match models/{{filename}}, got {m['target_path']}"
            )
            assert m["url"].endswith(f"/{m['filename']}"), f"URL must end with filename, got {m['url']}"
            assert "Qwen/Qwen3-4B-GGUF" in m["url"], f"Qwen3 URL must use Qwen/Qwen3-4B-GGUF repo, got {m['url']}"

        if m["id"] == "smollm3-3b-q4":
            assert m["filename"] == "SmolLM3-Q4_K_M.gguf", (
                f"SmolLM3 filename should be SmolLM3-Q4_K_M.gguf, got {m['filename']}"
            )
            assert m["target_path"] == f"models/{m['filename']}", (
                f"target_path must match models/{{filename}}, got {m['target_path']}"
            )
            assert m["url"].endswith(f"/{m['filename']}"), f"URL must end with filename, got {m['url']}"
            assert "ggml-org/SmolLM3-3B-GGUF" in m["url"], (
                f"SmolLM3 URL must use ggml-org/SmolLM3-3B-GGUF repo, got {m['url']}"
            )
            assert m["source"] == "ggml-org/SmolLM3-3B-GGUF", (
                f"SmolLM3 source must be ggml-org/SmolLM3-3B-GGUF, got {m['source']}"
            )


def test_no_old_lowercase_filenames_remain():
    """No references to old lowercase filenames should remain in config files."""
    old_names = ["qwen3-4b-q4_k_m.gguf", "smolm3-3b-q4_k_m.gguf"]
    for name in old_names:
        models_text = MODELS_PATH.read_text()
        profiles_text = PROFILES_PATH.read_text()
        assert name not in models_text, f"Old filename {name} still in kimari.models.json"
        assert name not in profiles_text, f"Old filename {name} still in kimari.profiles.json"


def test_profile_model_paths_match_registry_target_paths():
    """Each agent profile model path must exactly match a model's target_path in the registry."""
    profiles = _profiles()
    models = _models()
    target_paths = {m["target_path"] for m in models}
    for name in NEW_AGENT_PROFILES:
        model_path = profiles[name]["model"]
        assert model_path in target_paths, f"Profile {name} model path {model_path} not found in registry target_paths"
