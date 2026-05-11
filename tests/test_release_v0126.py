"""Tests for v0.1.26-alpha release: secret scanner hardening, measured benchmarks, doctor deep."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ─── Helper ──────────────────────────────────────────────────────────────────


def _run_kimari(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a kimari CLI command and return the CompletedProcess."""
    cmd = [sys.executable, "-m", "kimari.cli.main", *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=timeout,
    )


# ─── 1. Secret scanner detects real HF token ────────────────────────────────


class TestSecretScannerDetectsRealHfToken:
    """Test that scan_file detects a real-looking HF token as critical."""

    def test_secret_scanner_detects_real_hf_token(self, tmp_path):
        from scripts.security.scan_for_secrets import scan_file

        # Create a temp file with a real-looking HF token
        test_file = tmp_path / "test_secrets.txt"
        test_file.write_text("export HF_TOKEN=hf_abcdef1234567890abcdef1234567890ab\n")
        findings = scan_file(test_file)
        assert len(findings) > 0, "Should detect the HF token"
        critical = [f for f in findings if f["severity"] == "critical"]
        assert len(critical) > 0, f"Expected critical finding, got: {findings}"


# ─── 2. Secret scanner allows placeholders ───────────────────────────────────


class TestSecretScannerAllowsPlaceholders:
    """Test that scan_file allows known safe placeholder strings."""

    def test_secret_scanner_allows_placeholders(self, tmp_path):
        from scripts.security.scan_for_secrets import scan_file

        placeholders = [
            "hf_...",
            "hf_your_token_here",
            "<HF_TOKEN>",
            "your-api-key",
            "sk-...",
            "<token>",
            "<API_KEY>",
        ]
        for placeholder in placeholders:
            test_file = tmp_path / f"test_{placeholder.replace('<', '').replace('>', '').replace('.', 'dot')}.txt"
            test_file.write_text(f"token = {placeholder}\n")
            findings = scan_file(test_file)
            assert len(findings) == 0, f"Placeholder '{placeholder}' should not trigger findings, got: {findings}"


# ─── 3. Secret scanner doesn't skip security guides entirely ─────────────────


class TestSecretScannerNoFullSkipSecurityGuides:
    """Test that SECURITY_GUIDE_FILES exists but scanner scans them with SAFE_PLACEHOLDERS."""

    def test_secret_scanner_no_full_skip_security_guides(self):
        # Import the module as a script (it's in scripts/, not a package)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "scan_for_secrets",
            PROJECT_ROOT / "scripts" / "security" / "scan_for_secrets.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # SECURITY_GUIDE_FILES should exist
        assert hasattr(mod, "SECURITY_GUIDE_FILES"), "SECURITY_GUIDE_FILES must exist in scanner module"
        assert len(mod.SECURITY_GUIDE_FILES) > 0, "SECURITY_GUIDE_FILES should not be empty"

        # _should_skip_file should NOT skip security guide files
        for guide_file in mod.SECURITY_GUIDE_FILES:
            guide_path = PROJECT_ROOT / "docs" / guide_file
            if guide_path.exists():
                assert not mod._should_skip_file(guide_path), (
                    f"Scanner should NOT skip security guide file: {guide_file}"
                )

        # SAFE_PLACEHOLDERS should exist
        assert hasattr(mod, "SAFE_PLACEHOLDERS"), "SAFE_PLACEHOLDERS must exist in scanner module"
        assert len(mod.SAFE_PLACEHOLDERS) > 0, "SAFE_PLACEHOLDERS should not be empty"


# ─── 4–7. Measured benchmark module tests ────────────────────────────────────


class TestMeasuredBenchmark:
    """Tests for kimari.performance.measured_benchmark functions."""

    def test_measured_benchmark_payload_builder(self):
        from kimari.performance.measured_benchmark import build_chat_completion_payload

        payload = build_chat_completion_payload("Hello, world!", max_tokens=64)
        assert payload["model"] == "kimari"
        assert payload["messages"] == [{"role": "user", "content": "Hello, world!"}]
        assert payload["max_tokens"] == 64
        assert payload["temperature"] == 0.0

    def test_measured_benchmark_sanitizer(self):
        from kimari.performance.measured_benchmark import sanitize_benchmark_result

        result = {
            "endpoint": "http://localhost:11435/v1/chat/completions",
            "model": "test",
            "prompt_preview": "A" * 100,
            "max_tokens": 128,
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
            "tokens_per_second": 15.5,
            "ttft_ms": None,
            "elapsed_s": 1.29,
            "score_status": "measured",
            "timestamp": "2025-01-01T00:00:00Z",
            "error": None,
            # Private fields that should be removed
            "full_prompt": "Sensitive user data here",
            "choices": [{"message": {"content": "Secret response"}}],
            "raw_response": {"id": "chatcmpl-123"},
        }

        sanitized = sanitize_benchmark_result(result)

        # Allowed fields should be kept
        assert "endpoint" in sanitized
        assert "model" in sanitized
        assert "prompt_preview" in sanitized
        assert "max_tokens" in sanitized
        assert "tokens_per_second" in sanitized
        assert "score_status" in sanitized

        # Endpoint should be sanitized to host:port
        assert sanitized["endpoint"] == "localhost:11435"

        # prompt_preview should be truncated to 50 chars
        assert len(sanitized["prompt_preview"]) == 50

        # Private fields should be removed
        assert "full_prompt" not in sanitized
        assert "choices" not in sanitized
        assert "raw_response" not in sanitized

    def test_measured_benchmark_calculate_tps(self):
        from kimari.performance.measured_benchmark import calculate_tokens_per_second

        # Valid input
        assert calculate_tokens_per_second(100, 2.0) == 50.0
        assert calculate_tokens_per_second(1, 1.0) == 1.0

        # Edge cases
        assert calculate_tokens_per_second(None, 2.0) is None
        assert calculate_tokens_per_second(100, None) is None
        assert calculate_tokens_per_second(0, 2.0) is None
        assert calculate_tokens_per_second(100, 0.0) is None
        assert calculate_tokens_per_second(-1, 2.0) is None
        assert calculate_tokens_per_second(100, -1.0) is None

    def test_measured_benchmark_validate_result(self):
        from kimari.performance.measured_benchmark import validate_measured_result

        # Valid measured result
        valid_result = {
            "score_status": "measured",
            "endpoint": "http://localhost:11435",
            "model": "test",
            "tokens_per_second": 15.5,
        }
        validation = validate_measured_result(valid_result)
        assert validation["valid"] is True
        assert len(validation["missing_fields"]) == 0

        # Invalid: missing required fields
        invalid_result = {"model": "test"}
        validation = validate_measured_result(invalid_result)
        assert validation["valid"] is False
        assert len(validation["missing_fields"]) > 0

        # Result with error instead of tps is also valid
        error_result = {
            "score_status": "error",
            "endpoint": "http://localhost:11435",
            "model": "test",
            "error": "Connection failed",
        }
        validation = validate_measured_result(error_result)
        assert validation["valid"] is True

        # Non-measured score_status should produce a warning
        incomplete_result = {
            "score_status": "incomplete_response",
            "endpoint": "http://localhost:11435",
            "model": "test",
            "tokens_per_second": 15.5,
        }
        validation = validate_measured_result(incomplete_result)
        assert any("incomplete_response" in w for w in validation["warnings"])


# ─── 8. Benchmark measure requires --yes ─────────────────────────────────────


class TestBenchmarkMeasureRequiresYes:
    """Test that running benchmark --measure without --yes fails."""

    def test_benchmark_measure_requires_yes(self):
        result = _run_kimari(
            "benchmark",
            "--measure",
            "--endpoint",
            "http://127.0.0.1:11435/v1",
            "--model",
            "test",
        )
        assert result.returncode != 0, "--measure without --yes should fail"
        assert "--yes" in result.stdout or "--yes" in result.stderr, "Should mention --yes requirement"


# ─── 9. Benchmark measure handles endpoint failure ──────────────────────────


class TestBenchmarkMeasureHandlesEndpointFailure:
    """Test that measure_chat_completion with unreachable endpoint returns score_status=error."""

    def test_benchmark_measure_handles_endpoint_failure(self):
        from kimari.performance.measured_benchmark import measure_chat_completion

        result = measure_chat_completion(
            endpoint="http://127.0.0.1:1",  # Unreachable port
            model="test",
            prompt="Hello",
            max_tokens=10,
            timeout=2.0,
        )
        assert result["score_status"] == "error", f"Expected score_status='error', got '{result['score_status']}'"
        assert result["error"] is not None, "Should have an error message"
        assert "Traceback" not in str(result.get("error", "")), "Should not include stacktrace in error"


# ─── 10. Doctor deep JSON output ─────────────────────────────────────────────


class TestDoctorDeepJsonOutput:
    """Test that kimari doctor --deep --json produces valid JSON with expected structure."""

    def test_doctor_deep_json_output(self):
        result = _run_kimari("doctor", "--deep", "--json")
        assert result.returncode == 0, f"doctor --deep --json failed: {result.stderr}"
        data = json.loads(result.stdout)

        # Verify expected structure
        assert "kimari_version" in data, "Must include kimari_version"
        assert "deep_check" in data, "Must include deep_check"
        assert data["deep_check"] is True, "deep_check must be True"
        assert "checks" in data, "Must include checks"
        assert isinstance(data["checks"], list), "checks must be a list"
        assert len(data["checks"]) > 0, "Should have at least one check"
        assert "summary" in data, "Must include summary"

        # Each check should have name, status, value, detail
        for check in data["checks"]:
            assert "name" in check, f"Check missing 'name': {check}"
            assert "status" in check, f"Check missing 'status': {check}"
            assert "value" in check, f"Check missing 'value': {check}"


# ─── 11. Tune apply blocked ──────────────────────────────────────────────────


class TestTuneApplyBlocked:
    """Test that tune --apply exits with error."""

    def test_tune_apply_blocked(self):
        result = _run_kimari("tune", "--apply")
        assert result.returncode != 0, "--apply should be blocked and exit with error"
        combined = (result.stdout + result.stderr).lower()
        assert "not yet available" in combined or "blocked" in combined, "Should explain --apply is blocked"


# ─── 12. Benchmark prompts valid ────────────────────────────────────────────


class TestBenchmarkPromptsValid:
    """Verify benchmarks/prompts/local_benchmark_prompts.jsonl exists and each line is valid JSON."""

    def test_benchmark_prompts_valid(self):
        prompts_path = PROJECT_ROOT / "benchmarks" / "prompts" / "local_benchmark_prompts.jsonl"
        assert prompts_path.exists(), f"Benchmark prompts file missing: {prompts_path}"

        content = prompts_path.read_text(encoding="utf-8").strip()
        assert content, "Benchmark prompts file should not be empty"

        lines = content.splitlines()
        for i, line in enumerate(lines, start=1):
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                raise AssertionError(f"Invalid JSON on line {i}: {exc}") from exc


# ─── 13–15. Documentation file existence tests ──────────────────────────────


class TestDocExistence:
    """Verify required documentation files exist for v0.1.26."""

    def test_secret_scan_policy_exists(self):
        path = PROJECT_ROOT / "docs" / "SECRET_SCAN_POLICY.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_measured_benchmarks_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "MEASURED_BENCHMARKS.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_doctor_deep_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "DOCTOR_DEEP.md"
        assert path.exists(), f"Doc missing: {path}"


# ─── 16–17. Module existence tests ──────────────────────────────────────────


class TestModuleExistence:
    """Verify required modules exist for v0.1.26."""

    def test_measured_benchmark_module_exists(self):
        path = PROJECT_ROOT / "kimari" / "performance" / "measured_benchmark.py"
        assert path.exists(), f"Module missing: {path}"

    def test_doctor_deep_module_exists(self):
        path = PROJECT_ROOT / "kimari" / "doctor" / "deep.py"
        assert path.exists(), f"Module missing: {path}"


# ─── 18. Benchmark results gitignored ────────────────────────────────────────


class TestBenchmarkResultsGitignored:
    """Verify benchmarks/results/*.json is in .gitignore."""

    def test_benchmark_results_gitignored(self):
        gitignore_path = PROJECT_ROOT / ".gitignore"
        assert gitignore_path.exists(), ".gitignore missing"
        content = gitignore_path.read_text()
        assert "benchmarks/results/*.json" in content, ".gitignore must contain 'benchmarks/results/*.json'"


# ─── 19. No measured results committed ──────────────────────────────────────


class TestNoMeasuredResultsCommitted:
    """Run git ls-files to check no benchmark results are committed."""

    def test_no_measured_results_committed(self):
        result = subprocess.run(
            ["git", "ls-files", "benchmarks/results/"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        files = [f for f in result.stdout.strip().splitlines() if f and not f.endswith(".gitkeep")]
        assert len(files) == 0, f"Measured benchmark results should not be committed: {files}"


# ─── 20. Release check passes ───────────────────────────────────────────────


class TestReleaseCheck:
    """Run check-release.py and verify exit code 0."""

    def test_release_check_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/release/check-release.py"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=60,
        )
        assert result.returncode == 0, f"Release check failed:\n{result.stdout}\n{result.stderr}"


# ─── 21. Version consistency ────────────────────────────────────────────────


class TestVersionConsistency:
    """Verify pyproject.toml and __init__.py both say '0.1.26-alpha'."""

    def test_version_consistency(self):
        from kimari import __version__

        assert __version__ == "0.1.26-alpha", f"__version__ is {__version__}, expected 0.1.26-alpha"

        pyproject = PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text()
        assert "0.1.26-alpha" in content, "pyproject.toml must contain '0.1.26-alpha'"


# ─── 22. Gateway dry-run ────────────────────────────────────────────────────


class TestGatewayDryRun:
    """Test that kimari gateway --dry-run --json works and returns valid JSON with expected fields."""

    def test_gateway_dry_run(self):
        result = _run_kimari("gateway", "--dry-run", "--json")
        assert result.returncode == 0, f"gateway --dry-run --json failed: {result.stderr}"
        data = json.loads(result.stdout)

        # Top-level fields
        assert data["mode"] == "dry-run", f"Expected mode='dry-run', got '{data.get('mode')}'"

        # Status sub-object
        status = data.get("status", {})
        assert "status" in status, "status sub-object must include 'status' key"
        assert "planned_host" in status, "status sub-object must include 'planned_host' key"
        assert "planned_port" in status, "status sub-object must include 'planned_port' key"
        assert "gateway_available" in status, "status sub-object must include 'gateway_available' key"
        assert "message" in status, "status sub-object must include 'message' key"

        # Plan sub-object
        plan = data.get("plan", {})
        assert "planned_endpoints" in plan, "plan sub-object must include 'planned_endpoints' key"
        assert "security" in plan, "plan sub-object must include 'security' key"
        assert "planned_only" in plan, "plan sub-object must include 'planned_only' key"
        assert plan["planned_only"] is True, "planned_only must be True"


# ─── 23. Gateway status ─────────────────────────────────────────────────────


class TestGatewayStatus:
    """Test that kimari gateway --status --json works and returns gateway status."""

    def test_gateway_status(self):
        result = _run_kimari("gateway", "--status", "--json")
        assert result.returncode == 0, f"gateway --status --json failed: {result.stderr}"
        data = json.loads(result.stdout)

        assert "status" in data, "Must include 'status' key"
        assert data["status"] == "planned", f"Expected status='planned', got '{data['status']}'"
        assert "planned_host" in data, "Must include 'planned_host'"
        assert "planned_port" in data, "Must include 'planned_port'"
        assert "gateway_available" in data, "Must include 'gateway_available'"
        assert data["gateway_available"] is False, "gateway_available must be False"
        assert "dependencies" in data, "Must include 'dependencies'"
        assert "llama_server_available" in data, "Must include 'llama_server_available'"


# ─── 24. Gateway plan ───────────────────────────────────────────────────────


class TestGatewayPlan:
    """Test that kimari gateway --plan --json works and returns planned endpoints."""

    def test_gateway_plan(self):
        result = _run_kimari("gateway", "--plan", "--json")
        assert result.returncode == 0, f"gateway --plan --json failed: {result.stderr}"
        data = json.loads(result.stdout)

        assert "planned_endpoints" in data, "Must include 'planned_endpoints'"
        assert isinstance(data["planned_endpoints"], list), "planned_endpoints must be a list"
        assert len(data["planned_endpoints"]) > 0, "Should have at least one planned endpoint"

        for ep in data["planned_endpoints"]:
            assert "method" in ep, f"Endpoint missing 'method': {ep}"
            assert "path" in ep, f"Endpoint missing 'path': {ep}"
            assert "description" in ep, f"Endpoint missing 'description': {ep}"
            assert "status" in ep, f"Endpoint missing 'status': {ep}"

        assert "security" in data, "Must include 'security'"
        assert data["security"]["bind_localhost_only"] is True, "Security must enforce localhost-only binding"
        assert "relationship" in data, "Must include 'relationship'"
        assert data["planned_only"] is True, "planned_only must be True"


# ─── 25. Gateway never starts a real server ─────────────────────────────────


class TestGatewayNoServer:
    """Verify gateway module never starts a real server (status is 'planned', not 'running')."""

    def test_gateway_no_server(self):
        from kimari.gateway.state import gateway_status

        status = gateway_status()
        assert status["status"] == "planned", (
            f"Gateway status must be 'planned', not 'running' — got '{status['status']}'"
        )
        assert status["gateway_available"] is False, (
            "gateway_available must be False — no real server should exist"
        )

        from kimari.gateway.plan import gateway_plan

        plan = gateway_plan()
        assert plan["planned_only"] is True, "planned_only must be True — no server is started"


# ─── 26. Update check offline ───────────────────────────────────────────────


class TestUpdateCheckOffline:
    """Test that kimari update check --json works offline and returns current version info."""

    def test_update_check_offline(self):
        result = _run_kimari("update", "check", "--json")
        assert result.returncode == 0, f"update check --json failed: {result.stderr}"
        data = json.loads(result.stdout)

        assert "current_version" in data, "Must include 'current_version'"
        assert data["current_version"] == "0.1.26-alpha", (
            f"Expected current_version='0.1.26-alpha', got '{data['current_version']}'"
        )
        assert "online" in data, "Must include 'online'"
        assert data["online"] is False, "Default check should be offline"
        assert "latest_github_tag" in data, "Must include 'latest_github_tag'"
        assert data["latest_github_tag"] is None, "Offline check should not return a GitHub tag"
        assert "recommended_action" in data, "Must include 'recommended_action'"


# ─── 27. Update check never auto-updates ────────────────────────────────────


class TestUpdateCheckNeverAutoUpdates:
    """Verify that build_update_report() returns auto_update=False."""

    def test_update_check_never_auto_updates(self):
        from kimari.update.check import build_update_report

        report = build_update_report(online=False)
        assert "auto_update" in report, "Report must include 'auto_update' key"
        assert report["auto_update"] is False, "auto_update must always be False"

        # Also check the note confirms this policy
        assert "note" in report, "Report must include 'note' key"
        assert "auto-update" in report["note"].lower() or "auto update" in report["note"].lower(), (
            f"Note should mention no auto-update, got: {report['note']}"
        )


# ─── 28. Update parse_version ───────────────────────────────────────────────


class TestUpdateParseVersion:
    """Test parse_version('0.1.26-alpha') returns correct dict."""

    def test_update_parse_version(self):
        from kimari.update.check import parse_version

        result = parse_version("0.1.26-alpha")
        assert result["major"] == 0, f"Expected major=0, got {result['major']}"
        assert result["minor"] == 1, f"Expected minor=1, got {result['minor']}"
        assert result["patch"] == 26, f"Expected patch=26, got {result['patch']}"
        assert result["pre"] == "alpha", f"Expected pre='alpha', got {result['pre']}"
        assert result["full"] == "0.1.26-alpha", f"Expected full='0.1.26-alpha', got {result['full']}"

        # Also test a version without pre-release suffix
        result_stable = parse_version("1.2.3")
        assert result_stable["major"] == 1
        assert result_stable["minor"] == 2
        assert result_stable["patch"] == 3
        assert result_stable["pre"] is None, f"Expected pre=None for stable, got {result_stable['pre']}"


# ─── 29. Status includes gateway and preview_gate ───────────────────────────


class TestStatusIncludesGatewayAndGate:
    """Test that kimari status --json includes 'gateway' and 'preview_gate' fields."""

    def test_status_includes_gateway_and_gate(self):
        result = _run_kimari("status", "--json")
        assert result.returncode == 0, f"status --json failed: {result.stderr}"
        data = json.loads(result.stdout)

        assert "gateway" in data, "status --json must include 'gateway' field"
        assert data["gateway"] == "planned", f"Expected gateway='planned', got '{data['gateway']}'"

        assert "preview_gate" in data, "status --json must include 'preview_gate' field"
        assert data["preview_gate"] == "BLOCKED", f"Expected preview_gate='BLOCKED', got '{data['preview_gate']}'"


# ─── 30. Doctor deep new checks ─────────────────────────────────────────────


class TestDoctorDeepNewChecks:
    """Test that doctor --deep includes the 5 new checks."""

    def test_doctor_deep_new_checks(self):
        result = _run_kimari("doctor", "--deep", "--json")
        assert result.returncode == 0, f"doctor --deep --json failed: {result.stderr}"
        data = json.loads(result.stdout)

        assert "checks" in data, "Must include 'checks'"
        check_names = [c["name"] for c in data["checks"]]

        required_new_checks = [
            "Kimari Version",
            "CUDA/NVIDIA",
            "Packaged Defaults",
            "Gateway Module",
            "Integration Docs",
        ]
        for name in required_new_checks:
            assert name in check_names, f"doctor --deep must include '{name}' check, got: {check_names}"


# ─── 31. Gateway module files ───────────────────────────────────────────────


class TestGatewayModuleFiles:
    """Test that kimari/gateway/__init__.py, state.py, plan.py exist."""

    def test_gateway_init_exists(self):
        path = PROJECT_ROOT / "kimari" / "gateway" / "__init__.py"
        assert path.exists(), f"Module missing: {path}"

    def test_gateway_state_exists(self):
        path = PROJECT_ROOT / "kimari" / "gateway" / "state.py"
        assert path.exists(), f"Module missing: {path}"

    def test_gateway_plan_exists(self):
        path = PROJECT_ROOT / "kimari" / "gateway" / "plan.py"
        assert path.exists(), f"Module missing: {path}"


# ─── 32. Update module files ────────────────────────────────────────────────


class TestUpdateModuleFiles:
    """Test that kimari/update/__init__.py, check.py exist."""

    def test_update_init_exists(self):
        path = PROJECT_ROOT / "kimari" / "update" / "__init__.py"
        assert path.exists(), f"Module missing: {path}"

    def test_update_check_exists(self):
        path = PROJECT_ROOT / "kimari" / "update" / "check.py"
        assert path.exists(), f"Module missing: {path}"


# ─── 33. New documentation files ────────────────────────────────────────────


class TestDocFilesNew:
    """Test that new v0.1.26 documentation files exist."""

    def test_gateway_plan_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "GATEWAY_PLAN.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_update_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "UPDATE.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_install_matrix_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "INSTALL_MATRIX.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_openwebui_openclaw_quick_config_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "OPENWEBUI_OPENCLAW_QUICK_CONFIG.md"
        assert path.exists(), f"Doc missing: {path}"
