"""Installer script safety tests for v0.1.82-alpha."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_install_sh_exists_and_has_required_flags():
    text = (REPO / "install.sh").read_text()
    assert "set -euo pipefail" in text
    for flag in ["--dev", "--with-dashboard", "--with-test-model", "--no-venv", "--yes", "--dry-run"]:
        assert flag in text
    assert "kimari setup --write --yes" in text
    assert "kimari doctor --quick" in text


def test_install_sh_is_safe_by_default():
    text = (REPO / "install.sh").read_text()
    assert "kimari pull test" in text
    assert "WITH_TEST_MODEL" in text
    assert "kimari gateway setup" in text
    assert "WITH_DASHBOARD" in text
    assert "rm -rf" not in text
    assert "curl | sudo" not in text
    assert "0.0.0.0" not in text


def test_install_ps1_exists_and_does_not_touch_execution_policy():
    text = (REPO / "install.ps1").read_text()
    assert "PowerShell" in text
    assert "Python 3.10" in text or "3.10" in text
    assert "git clone" in text
    assert "Set-ExecutionPolicy" not in text
    assert "ExecutionPolicy" not in text


def test_installers_do_not_contain_tokens_or_billing_terms():
    combined = (REPO / "install.sh").read_text() + "\n" + (REPO / "install.ps1").read_text()
    forbidden = ["hf_", "sk-", "api_key", "billing", "stripe", "OPENAI_API_KEY"]
    for token in forbidden:
        assert token.lower() not in combined.lower()
