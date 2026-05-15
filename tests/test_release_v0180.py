"""Release validation tests for v0.1.80-alpha."""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_pyproject_version():
    content = (REPO / "pyproject.toml").read_text()
    assert 'version = "0.1.80-alpha"' in content


def test_init_version():
    content = (REPO / "kimari" / "__init__.py").read_text()
    assert '__version__ = "0.1.80-alpha"' in content


def test_dashboard_package_version():
    import json

    pkg = json.loads((REPO / "apps" / "gateway-dashboard" / "package.json").read_text())
    assert pkg["version"] == "0.1.80-alpha"


def test_dashboard_exists():
    assert (REPO / "apps" / "gateway-dashboard" / "src" / "app" / "api" / "health" / "route.ts").exists()


def test_eval_dataset_exists():
    assert (REPO / "eval" / "kimari_private_v1" / "refusal_safety.jsonl").exists()


def test_training_configs_exist():
    assert (REPO / "training" / "configs" / "kimari4b_smollm3_sft_v2.yaml").exists()
