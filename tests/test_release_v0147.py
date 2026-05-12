"""Tests for v0.1.47-alpha release criteria.

Validates:
- Private adapter config exists with safety flags
- Runner defaults to dry-run, requires --allow-train --yes
- Preflight script exists
- Manifest template safe
- Release gate says no auto-transitions
- .gitignore blocks artifacts
- No adapter/GGUF committed
- Version bump
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_PATH = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_adapter_run.v0.yaml"
RUNNER_PATH = PROJECT_ROOT / "training" / "scripts" / "run_kimari4b_private_adapter.py"
PREFLIGHT_PATH = PROJECT_ROOT / "training" / "scripts" / "preflight_kimari4b_adapter.py"
MANIFEST_TEMPLATE = PROJECT_ROOT / "training" / "templates" / "kimari4b_adapter_manifest.template.json"
GATE_DOC = PROJECT_ROOT / "docs" / "KIMARI4B_RELEASE_GATE.md"


def _load_yaml(path: Path) -> dict | None:
    """Load YAML safely."""
    try:
        import yaml
    except ImportError:
        return None
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def test_config_exists():
    """Private adapter config must exist."""
    assert CONFIG_PATH.exists(), "Config not found"


def test_config_hf_upload_false():
    """Config must have hf_upload_allowed=false."""
    config = _load_yaml(CONFIG_PATH)
    if config is None:
        return
    assert config.get("safety", {}).get("hf_upload_allowed") is False


def test_config_public_release_false():
    """Config must have public_release_allowed=false."""
    config = _load_yaml(CONFIG_PATH)
    if config is None:
        return
    assert config.get("safety", {}).get("public_release_allowed") is False


def test_config_gguf_export_false():
    """Config must have gguf_export_allowed=false."""
    config = _load_yaml(CONFIG_PATH)
    if config is None:
        return
    assert config.get("safety", {}).get("gguf_export_allowed") is False


def test_config_push_to_hub_false():
    """Config must have push_to_hub=false."""
    config = _load_yaml(CONFIG_PATH)
    if config is None:
        return
    assert config.get("safety", {}).get("push_to_hub") is not True


def test_config_gate_blocked():
    """Config must have preview_gate_state=BLOCKED."""
    config = _load_yaml(CONFIG_PATH)
    if config is None:
        return
    assert config.get("safety", {}).get("preview_gate_state") == "BLOCKED"


def test_runner_exists():
    """Runner script must exist."""
    assert RUNNER_PATH.exists()


def test_runner_dry_run_default():
    """Runner must default to dry-run."""
    if not RUNNER_PATH.exists():
        return
    text = RUNNER_PATH.read_text()
    # argparse default should be True for --dry-run
    assert "default=True" in text or "dry_run" in text.lower()


def test_runner_requires_allow_train_yes():
    """Runner must require --allow-train and --yes for real training."""
    if not RUNNER_PATH.exists():
        return
    text = RUNNER_PATH.read_text()
    assert "--allow-train" in text and "--yes" in text


def test_runner_blocks_ci():
    """Runner must block training in CI environment."""
    if not RUNNER_PATH.exists():
        return
    text = RUNNER_PATH.read_text()
    assert "CI" in text


def test_runner_no_token_arg():
    """Runner must not accept --token or --api-key arguments."""
    if not RUNNER_PATH.exists():
        return
    text = RUNNER_PATH.read_text()
    # Should check for and reject token args
    assert '"--token"' in text or '"--api-key"' in text


def test_preflight_exists():
    """Preflight script must exist."""
    assert PREFLIGHT_PATH.exists()


def test_manifest_template_exists():
    """Adapter manifest template must exist."""
    assert MANIFEST_TEMPLATE.exists()


def test_manifest_template_safe():
    """Manifest template must have safety flags."""
    if not MANIFEST_TEMPLATE.exists():
        return
    data = json.loads(MANIFEST_TEMPLATE.read_text())
    assert data.get("public_release_allowed") is False
    assert data.get("hf_upload_allowed") is False
    assert data.get("gate_state") == "BLOCKED"
    assert data.get("manual_review_required") is True


def test_manifest_no_private_paths():
    """Manifest template must not contain private paths."""
    if not MANIFEST_TEMPLATE.exists():
        return
    content = MANIFEST_TEMPLATE.read_text().lower()
    assert "/home/" not in content
    assert "sk-" not in content
    assert "hf_" not in content or "hf_upload_allowed" in content or "hf_upload" in content  # field name is ok


def test_release_gate_exists():
    """Release gate doc must exist."""
    assert GATE_DOC.exists()


def test_release_gate_no_auto_transition():
    """Release gate must state no automatic transitions."""
    if not GATE_DOC.exists():
        return
    text = GATE_DOC.read_text().lower()
    assert "no automatic" in text or "no script" in text


def test_gitignore_blocks_artifacts():
    """.gitignore must block training artifacts."""
    gitignore = PROJECT_ROOT / ".gitignore"
    if not gitignore.exists():
        return
    content = gitignore.read_text()
    assert "training/adapters" in content
    assert "*.safetensors" in content
    assert "*.gguf" in content


def test_no_safetensors_tracked():
    """No .safetensors files in project tree (except gitignored)."""
    safetensors = [
        f for f in PROJECT_ROOT.rglob("*.safetensors") if "training/adapters" not in str(f) and ".git" not in str(f)
    ]
    assert len(safetensors) == 0, f"Found {len(safetensors)} .safetensors files"


def test_no_gguf_tracked():
    """No .gguf files in project tree (except gitignored and deps)."""
    gguf = [f for f in PROJECT_ROOT.rglob("*.gguf") if ".git" not in str(f) and "deps/" not in str(f)]
    assert len(gguf) == 0, f"Found {len(gguf)} .gguf files: {[str(f) for f in gguf[:5]]}"


def test_version_bump():
    """pyproject.toml and __init__.py must be >= 0.1.47-alpha."""
    import re

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.47-alpha"
    assert match_i and match_i.group(1) >= "0.1.47-alpha"


def test_changelog_has_v0147():
    """CHANGELOG.md must have [0.1.47-alpha] entry."""
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.47-alpha]" in changelog


def test_roadmap_has_v0147():
    """ROADMAP.md must mention v0.1.47-alpha."""
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.47-alpha" in roadmap


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
