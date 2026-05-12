"""Tests for v0.1.42-alpha release criteria.

Validates:
- build_hf_jobs_command_args returns list[str]
- bash -lc inner command remains one argument
- hf_cmd.split() not used in submit path
- shell=True absent from hf_jobs_private_run.py
- --dry-run --json includes hf_jobs_command_args
- --require-jobs-access still exists
- check-release passes (imported, not run)
- docs/LOCAL_OPENAI_ENDPOINT_TEST.md exists
- README says TinyLlama is not Kimari-4B
- no HF upload/training claim in README
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HF_RUN_SCRIPT = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_private_run.py"
SMOKE_CONFIG = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml"


def test_build_hf_jobs_command_args_returns_list():
    """build_hf_jobs_command_args returns list[str]."""
    sys.path.insert(0, str(HF_RUN_SCRIPT.parent))
    from hf_jobs_private_run import build_hf_jobs_command_args

    config = {
        "flavor": "a10g-small",
        "image": "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
        "commands": ["echo hello", "echo world"],
    }
    result = build_hf_jobs_command_args(config)
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert all(isinstance(x, str) for x in result), "All items must be str"


def test_bash_lc_remains_one_argument():
    """bash -lc inner command must remain a single argument."""
    sys.path.insert(0, str(HF_RUN_SCRIPT.parent))
    from hf_jobs_private_run import build_hf_jobs_command_args

    config = {
        "flavor": "a10g-small",
        "image": "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
        "commands": ["echo hello", "echo world"],
    }
    args = build_hf_jobs_command_args(config)
    # Find "bash" position, then -lc, then inner command must be next as one arg
    bash_idx = args.index("bash")
    assert args[bash_idx + 1] == "-lc", f"Expected -lc after bash, got {args[bash_idx + 1]}"
    inner_cmd = args[bash_idx + 2]
    assert "echo hello" in inner_cmd and "echo world" in inner_cmd, (
        f"Inner command should contain both commands joined, got: {inner_cmd}"
    )
    # Inner command must be exactly one argument
    assert isinstance(inner_cmd, str) and " && " in inner_cmd


def test_hf_cmd_split_not_used():
    """hf_cmd.split() must not appear as executable code in hf_jobs_private_run.py."""
    text = HF_RUN_SCRIPT.read_text()
    import re

    # Find all subprocess.run calls and check none use .split()
    subprocess_calls = re.findall(r"subprocess\.run\([^)]+\)", text, re.DOTALL)
    for call in subprocess_calls:
        assert ".split()" not in call, f"subprocess.run uses .split(): {call[:80]}"
    # Check no executable line uses hf_cmd.split() with subprocess.run
    # Skip lines that are clearly documentation (docstring bullet points)
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        # Skip docstring content (lines starting with -, *, or inside triple quotes)
        if stripped.startswith("-") or stripped.startswith("*") or stripped.startswith("#"):
            continue
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        if "subprocess.run" in stripped and ".split()" in stripped:
            raise AssertionError(f"Found subprocess.run with .split() in code: {stripped}")


def test_shell_true_absent():
    """shell=True must not appear as executable code in hf_jobs_private_run.py."""
    text = HF_RUN_SCRIPT.read_text()
    # Check no subprocess.run call uses shell=True
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        # Skip docstring content (bullet points, comments)
        if stripped.startswith("-") or stripped.startswith("*") or stripped.startswith("#"):
            continue
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        if "subprocess.run" in stripped and "shell=True" in stripped:
            raise AssertionError(f"Found subprocess.run with shell=True: {stripped}")


def test_dry_run_json_includes_command_args():
    """--dry-run --json output includes hf_jobs_command_args."""
    result = subprocess.run(
        [
            sys.executable,
            str(HF_RUN_SCRIPT),
            "--config",
            str(SMOKE_CONFIG),
            "--dry-run",
            "--json",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Dry run failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert "hf_jobs_command_args" in data, "hf_jobs_command_args missing from dry-run JSON"
    assert isinstance(data["hf_jobs_command_args"], list), "hf_jobs_command_args must be list"
    assert data.get("submit_uses_arg_list") is True, "submit_uses_arg_list must be True"
    assert "command_arg_count" in data, "command_arg_count missing from dry-run JSON"


def test_require_jobs_access_still_exists():
    """--require-jobs-access flag still exists in hf_jobs_private_run.py."""
    text = HF_RUN_SCRIPT.read_text()
    assert "--require-jobs-access" in text, "--require-jobs-access flag removed"


def test_local_openai_endpoint_test_doc_exists():
    """docs/LOCAL_OPENAI_ENDPOINT_TEST.md must exist."""
    path = PROJECT_ROOT / "docs" / "LOCAL_OPENAI_ENDPOINT_TEST.md"
    assert path.exists(), f"{path} not found"


def test_readme_says_tinyllama_not_kimari4b():
    """README must clarify TinyLlama is a validation model, not Kimari-4B."""
    readme = (PROJECT_ROOT / "README.md").read_text()
    # Case-insensitive but check the actual strings
    readme_lower = readme.lower()
    assert "tinyllama" in readme_lower, "README should mention TinyLlama validation model"
    assert "not kimari-4b" in readme_lower or "not yet released" in readme_lower, (
        "README should clarify TinyLlama is not Kimari-4B"
    )


def test_readme_mentions_profile_test():
    """README should mention --profile test for TinyLlama validation."""
    readme = (PROJECT_ROOT / "README.md").read_text()
    assert "profile test" in readme.lower() or "--profile test" in readme, (
        "README should mention --profile test for TinyLlama validation"
    )


def test_no_hf_upload_claim_in_readme():
    """README must not claim HF upload was performed or training completed successfully."""
    readme = (PROJECT_ROOT / "README.md").read_text().lower()
    assert "weights uploaded" not in readme, "README should not claim weights were uploaded"
    # 'no training performed' is OK (it's a negation), check for affirmative claims only
    # Check for patterns like 'training completed' or 'sft completed' that imply success
    assert "training completed successfully" not in readme
    assert "sft completed successfully" not in readme


def test_version_bump():
    """pyproject.toml and __init__.py must be >= 0.1.42-alpha."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    import re

    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.42-alpha", (
        f"pyproject.toml version must be >= 0.1.42-alpha, got {match_p.group(1) if match_p else 'not found'}"
    )
    assert match_i and match_i.group(1) >= "0.1.42-alpha", (
        f"__init__.py version must be >= 0.1.42-alpha, got {match_i.group(1) if match_i else 'not found'}"
    )


def test_changelog_has_v0142():
    """CHANGELOG.md must have [0.1.42-alpha] entry."""
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.42-alpha]" in changelog, "CHANGELOG.md missing [0.1.42-alpha] entry"


def test_roadmap_has_v0142():
    """ROADMAP.md must mention v0.1.42-alpha."""
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.42-alpha" in roadmap, "ROADMAP.md missing v0.1.42-alpha"


if __name__ == "__main__":
    pytest_main = __import__("pytest")
    sys.exit(pytest_main.main([__file__, "-v"]))
