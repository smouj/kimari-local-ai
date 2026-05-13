"""Tests for v0.1.53-alpha release criteria.

Validates:
- Eval config exists with safety flags
- HF eval runner with dry-run default, safe flags
- Compare script exists
- Summary validator enforces safety
- Pending report placeholder
- Version bump
- Gate BLOCKED
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent / "kimari-local-ai"


def test_eval_config_exists():
    assert (PROJECT_ROOT / "eval" / "configs" / "kimari_eval_v1_baseline_vs_adapter.yaml").exists()


def test_eval_config_safety_flags():
    config_path = PROJECT_ROOT / "eval" / "configs" / "kimari_eval_v1_baseline_vs_adapter.yaml"
    config = yaml.safe_load(config_path.read_text())
    assert config["gate_state"] == "BLOCKED"
    assert config["public_benchmark_allowed"] is False
    assert config["manual_review_required"] is True
    assert config["raw_outputs_commit_allowed"] is False


def test_hf_eval_runner_exists():
    assert (PROJECT_ROOT / "eval" / "scripts" / "hf_jobs_run_kimari_eval.py").exists()


def test_hf_eval_runner_dry_run_default():
    runner = (PROJECT_ROOT / "eval" / "scripts" / "hf_jobs_run_kimari_eval.py").read_text()
    assert "--dry-run" in runner
    assert "default=True" in runner or "store_true" in runner


def test_hf_eval_runner_requires_allow_submit():
    runner = (PROJECT_ROOT / "eval" / "scripts" / "hf_jobs_run_kimari_eval.py").read_text()
    assert "--allow-submit" in runner
    assert "--yes" in runner


def test_hf_eval_runner_no_token_arg():
    runner = (PROJECT_ROOT / "eval" / "scripts" / "hf_jobs_run_kimari_eval.py").read_text()
    # Check code lines only (not docstrings/comments) for --token as an argparse argument
    code_lines = [
        line
        for line in runner.split("\n")
        if line.strip()
        and not line.strip().startswith("#")
        and not line.strip().startswith('"""')
        and not line.strip().startswith("'")
    ]
    token_args = [line for line in code_lines if '"--token"' in line and "add_argument" in line]
    assert len(token_args) == 0, f"Found --token argparse argument: {token_args}"


def test_hf_eval_runner_no_shell_true():
    runner = (PROJECT_ROOT / "eval" / "scripts" / "hf_jobs_run_kimari_eval.py").read_text()
    # Check code lines only (not docstrings) for shell=True in subprocess calls
    code_lines = [line for line in runner.split("\n") if line.strip() and not line.strip().startswith("#")]
    # Check subprocess.run calls don't use shell=True
    subprocess_calls = [line for line in code_lines if "subprocess.run" in line and "shell=True" in line]
    assert len(subprocess_calls) == 0, f"Found subprocess call with shell=True: {subprocess_calls}"


def test_hf_eval_runner_safety_flags():
    runner = (PROJECT_ROOT / "eval" / "scripts" / "hf_jobs_run_kimari_eval.py").read_text()
    assert "manual_review_required" in runner
    assert "public_benchmark_allowed" in runner
    assert "BLOCKED" in runner


def test_compare_script_exists():
    assert (PROJECT_ROOT / "eval" / "scripts" / "compare_kimari_eval_runs.py").exists()


def test_summary_validator_exists():
    assert (PROJECT_ROOT / "eval" / "scripts" / "validate_kimari_eval_summary.py").exists()


def test_summary_validator_enforces_no_raw_outputs():
    validator = (PROJECT_ROOT / "eval" / "scripts" / "validate_kimari_eval_summary.py").read_text()
    assert "raw_outputs" in validator or "FORBIDDEN_FIELDS" in validator


def test_summary_validator_enforces_gate_blocked():
    validator = (PROJECT_ROOT / "eval" / "scripts" / "validate_kimari_eval_summary.py").read_text()
    assert "BLOCKED" in validator


def test_summary_template_exists():
    assert (PROJECT_ROOT / "eval" / "templates" / "kimari_eval_summary.template.json").exists()


def test_pending_report_exists():
    assert (PROJECT_ROOT / "reports" / "evals" / "kimari_v0153_baseline_vs_adapter" / "summary.pending.json").exists()


def test_pending_report_safety():
    data = json.loads(
        (PROJECT_ROOT / "reports" / "evals" / "kimari_v0153_baseline_vs_adapter" / "summary.pending.json").read_text()
    )
    assert data["gate_state"] == "BLOCKED"
    assert data["manual_review_required"] is True
    assert data["public_benchmark_allowed"] is False
    assert data["raw_outputs_committed"] is False


def test_no_safetensors():
    safetensors = list(PROJECT_ROOT.rglob("*.safetensors"))
    assert len(safetensors) == 0


def test_no_gguf():
    gguf = [f for f in PROJECT_ROOT.rglob("*.gguf") if "deps" not in str(f) and "node_modules" not in str(f)]
    assert len(gguf) == 0


def test_version_bump():
    import re

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.53-alpha"
    assert match_i and match_i.group(1) >= "0.1.53-alpha"


def test_changelog_has_v0153():
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.53-alpha]" in changelog


def test_roadmap_has_v0153():
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.53-alpha" in roadmap


def test_org_card_has_current_version():
    org_card = (PROJECT_ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    assert "v0.1.59-alpha" in org_card or "v0.1.58-alpha" in org_card or "v0.1.57-alpha" in org_card


def test_org_card_no_stale_version():
    org_card = (PROJECT_ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    assert "v0.1.28-alpha" not in org_card


def test_org_card_kimari4b_not_released():
    org_card = (PROJECT_ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text().lower()
    assert "not released" in org_card


def test_org_card_gate_blocked():
    org_card = (PROJECT_ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    assert "BLOCKED" in org_card


def test_deployment_status_has_current_version():
    deploy = (PROJECT_ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    assert "v0.1.59-alpha" in deploy or "v0.1.58-alpha" in deploy or "v0.1.57-alpha" in deploy


def test_readme_links_hf_space():
    readme = (PROJECT_ROOT / "README.md").read_text()
    assert "kimari-fit-lab" in readme


def test_readme_kimari4b_not_released():
    readme = (PROJECT_ROOT / "README.md").read_text().lower()
    assert "not released" in readme or "not yet released" in readme


def test_space_readme_not_released():
    space = (PROJECT_ROOT / "huggingface" / "kimari-fit-lab" / "README.md").read_text().lower()
    assert "not released" in space


def test_index_html_has_kimari_eval():
    index = (PROJECT_ROOT / "docs" / "index.html").read_text()
    assert "KimariEval" in index


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
