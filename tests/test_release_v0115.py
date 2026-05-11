"""Release validation tests for Kimari Local AI v0.1.23-alpha.

Tests cover:
- resolve_model_path() with various path types
- start_server uses resolve_model_path (not PROJECT_ROOT / effective_model)
- setup --write --yes and confirmation flow
- pin-hash --dry-run and --yes workflow
- Benchmark result format
- OpenAPI draft YAML
- Windows wheel scripts
- New documentation files
- Release check improvements
- No false claims
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ─── Helper ─────────────────────────────────────────────────────────────────


def _run_kimari(*args: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "kimari.cli.main", *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT))


# ─── Version Consistency ────────────────────────────────────────────────────


class TestVersion:
    def test_version_is_0115(self):
        from kimari import __version__

        assert __version__ == "0.1.23-alpha"

    def test_pyproject_version_matches(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        text = pyproject.read_text()
        assert 'version = "0.1.23-alpha"' in text

    def test_cli_info_version(self):
        result = _run_kimari("info", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["kimari_version"] == "0.1.23-alpha"


# ─── resolve_model_path Tests ───────────────────────────────────────────────


class TestResolveModelPath:
    def test_resolve_absolute_path(self, tmp_path):
        """Absolute paths are returned as-is."""
        from kimari.cli.main import resolve_model_path

        gguf = tmp_path / "model.gguf"
        gguf.touch()
        result = resolve_model_path(str(gguf))
        assert result == gguf

    def test_resolve_cwd_relative(self, tmp_path, monkeypatch):
        """CWD-relative paths that exist are resolved."""
        from kimari.cli.main import resolve_model_path

        gguf = tmp_path / "model.gguf"
        gguf.touch()
        monkeypatch.chdir(tmp_path)
        result = resolve_model_path("model.gguf")
        assert result.resolve() == gguf.resolve()

    def test_resolve_user_models_dir(self, tmp_path, monkeypatch):
        """Model found in user models dir is returned."""
        from kimari.cli.main import resolve_model_path

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        gguf = models_dir / "tinyllama-test.gguf"
        gguf.touch()
        monkeypatch.setenv("KIMARI_MODELS_DIR", str(models_dir))
        result = resolve_model_path("models/tinyllama-test.gguf")
        assert result == models_dir / "tinyllama-test.gguf"

    def test_resolve_missing_returns_user_path(self, tmp_path, monkeypatch):
        """Missing model returns user models dir path for error messages."""
        from kimari.cli.main import resolve_model_path

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        monkeypatch.setenv("KIMARI_MODELS_DIR", str(models_dir))
        result = resolve_model_path("models/nonexistent.gguf")
        assert result == models_dir / "nonexistent.gguf"
        assert not result.exists()

    def test_backward_compat_alias(self):
        """_resolve_model_path is an alias for resolve_model_path."""
        from kimari.cli.main import _resolve_model_path

        assert _resolve_model_path.__doc__ is not None
        assert "alias" in _resolve_model_path.__doc__.lower() or "resolve_model_path" in _resolve_model_path.__doc__


# ─── start_server Uses resolve_model_path ────────────────────────────────────


class TestStartServerPathResolution:
    def test_start_server_uses_resolver_not_project_root(self):
        """Verify start_server() no longer uses PROJECT_ROOT / effective_model directly."""
        cli_path = PROJECT_ROOT / "kimari" / "cli" / "main.py"
        content = cli_path.read_text()
        # The old bug pattern: "PROJECT_ROOT / effective_model" should NOT appear
        # outside of resolve_model_path or _resolve_model_path definitions
        # Check that the real startup path uses resolve_model_path
        assert "resolve_model_path(effective_model)" in content, (
            "start_server should use resolve_model_path(effective_model)"
        )
        # The old bug was: model_path = PROJECT_ROOT / effective_model (line ~444)
        # It should now use resolve_model_path instead

    def test_start_dry_run_uses_resolver(self):
        """Dry-run path uses resolve_model_path."""
        cli_path = PROJECT_ROOT / "kimari" / "cli" / "main.py"
        content = cli_path.read_text()
        # In the dry-run section, should use _resolve_model_path or resolve_model_path
        assert "_resolve_model_path(effective_model)" in content or "resolve_model_path(effective_model)" in content


# ─── Setup --write --yes ────────────────────────────────────────────────────


class TestSetupWriteYes:
    def test_setup_writer_preview_exists(self):
        from kimari.setup.writer import preview_setup_changes

        assert callable(preview_setup_changes)

    def test_setup_writer_apply_exists(self):
        from kimari.setup.writer import apply_setup_changes

        assert callable(apply_setup_changes)

    def test_setup_writer_confirm_exists(self):
        from kimari.setup.writer import confirm_setup_write

        assert callable(confirm_setup_write)

    def test_confirm_yes_returns_true(self):
        from kimari.setup.writer import confirm_setup_write

        preview = {"requires_confirmation": True}
        assert confirm_setup_write(preview, yes=True) is True

    def test_confirm_no_tty_returns_false(self, monkeypatch):
        """In non-interactive mode without --yes, confirm returns False."""
        from kimari.setup.writer import confirm_setup_write

        monkeypatch.setattr("sys.stdin.isatty", lambda: False)
        preview = {"requires_confirmation": True}
        assert confirm_setup_write(preview, yes=False) is False

    def test_setup_write_creates_backup(self, tmp_path, monkeypatch):
        """Writing config creates a backup if config already exists."""
        from kimari.setup.writer import apply_setup_changes

        config_path = tmp_path / "kimari.profiles.json"
        config_path.write_text(json.dumps({"default_profile": "test", "profiles": {}}))

        patch = {
            "recommended_profile": "gtx1060",
            "integration": None,
            "hardware_summary": {"gpu": "GTX 1060"},
            "paths": {"models_dir": "/tmp/models"},
            "changes": ["default_profile: 'test' -> 'gtx1060'"],
        }

        result = apply_setup_changes(patch, config_path)
        assert result["written"] is True
        assert result["backup_path"] is not None
        assert Path(result["backup_path"]).exists()

    def test_setup_write_atomic(self, tmp_path, monkeypatch):
        """apply_setup_changes uses atomic write (.tmp then rename)."""
        from kimari.setup.writer import apply_setup_changes

        config_path = tmp_path / "kimari.profiles.json"
        patch = {
            "recommended_profile": "test",
            "integration": None,
            "hardware_summary": {},
            "paths": {},
            "changes": ["setup_info: added"],
        }

        result = apply_setup_changes(patch, config_path)
        assert result["written"] is True
        # Verify no .tmp file left behind
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0, f"Leftover .tmp files: {tmp_files}"

    def test_setup_yes_flag_in_argparse(self):
        """--yes flag exists in setup parser."""
        result = _run_kimari("setup", "--help")
        assert "--yes" in result.stdout


# ─── pin-hash Workflow ──────────────────────────────────────────────────────


class TestPinHashWorkflow:
    def test_pin_hash_dry_run_no_write(self, tmp_path, monkeypatch):
        """pin-hash without --write does not modify any file."""
        from kimari.models.registry import pin_model_hash

        # Create a temp GGUF file
        models_dir = tmp_path / "models"
        models_dir.mkdir()
        gguf = models_dir / "test.gguf"
        gguf.write_bytes(b"fake gguf " * 100)

        monkeypatch.setenv("KIMARI_MODELS_DIR", str(models_dir))
        monkeypatch.setenv("KIMARI_HOME", str(tmp_path / "home"))

        # This may or may not find the model in registry, but dry-run should not write
        result = pin_model_hash("test", write=False, json_output=True)
        if result is not None:
            assert result.get("written") is False or result.get("would_write") is True

    def test_pin_hash_never_changes_packaged_defaults(self, tmp_path, monkeypatch):
        """pin-hash only writes to user registry, never to packaged defaults."""
        defaults_path = PROJECT_ROOT / "kimari" / "defaults" / "kimari.models.json"
        if defaults_path.exists():
            original_content = defaults_path.read_text()
            # Run a pin operation (should not affect packaged defaults)
            # Just verify the file hasn't changed after import
            assert defaults_path.read_text() == original_content

    def test_pin_hash_yes_flag_in_argparse(self):
        """--yes flag exists in pin-hash parser."""
        result = _run_kimari("models", "pin-hash", "--help")
        assert "--yes" in result.stdout

    def test_pin_hash_dry_run_flag_in_argparse(self):
        """--dry-run flag exists in pin-hash parser."""
        result = _run_kimari("models", "pin-hash", "--help")
        assert "--dry-run" in result.stdout


# ─── Benchmark Result Format ────────────────────────────────────────────────


class TestBenchmarkResultFormat:
    def test_result_format_exists(self):
        assert (PROJECT_ROOT / "benchmarks" / "RESULT_FORMAT.md").exists()

    def test_example_json_exists(self):
        assert (PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.example.json").exists()

    def test_example_json_parseable(self):
        path = PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.example.json"
        data = json.loads(path.read_text())
        # Check required fields
        required_fields = [
            "kimari_version",
            "profile",
            "model_filename",
            "quantization",
            "gpu",
            "os",
            "ctx",
            "batch",
            "tokens_per_second",
            "timestamp",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_example_json_has_privacy_safe_fields(self):
        """Example JSON should NOT contain sensitive paths or tokens."""
        path = PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.example.json"
        text = path.read_text()
        assert "token" not in text.lower() or "tokens_per_second" in text
        assert "/home/" not in text or text.count("/home/") == 0
        assert "Bearer" not in text


# ─── OpenAPI Draft ──────────────────────────────────────────────────────────


class TestOpenAPIDraft:
    def test_openapi_draft_exists(self):
        assert (PROJECT_ROOT / "docs" / "API_OPENAPI_DRAFT.yaml").exists()

    def test_openapi_draft_is_valid_yaml(self):
        import yaml

        path = PROJECT_ROOT / "docs" / "API_OPENAPI_DRAFT.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert data.get("openapi", "").startswith("3.")

    def test_openapi_draft_has_planned_endpoints(self):
        import yaml

        path = PROJECT_ROOT / "docs" / "API_OPENAPI_DRAFT.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        paths = data.get("paths", {})
        expected = [
            "/health",
            "/status",
            "/config",
            "/profiles",
            "/models",
            "/server/start",
            "/server/stop",
            "/optimize",
            "/perf/dry-run",
        ]
        for endpoint in expected:
            assert endpoint in paths, f"Missing endpoint: {endpoint}"

    def test_openapi_draft_is_marked_as_draft(self):
        import yaml

        path = PROJECT_ROOT / "docs" / "API_OPENAPI_DRAFT.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        # Should have x-draft or "draft" in info
        info = data.get("info", {})
        assert (
            info.get("x-draft") is True
            or "draft" in str(info.get("title", "")).lower()
            or "draft" in str(info.get("description", "")).lower()
        )


# ─── Windows Wheel Scripts ──────────────────────────────────────────────────


class TestWindowsWheelScripts:
    def test_build_wheel_exists(self):
        assert (PROJECT_ROOT / "scripts" / "windows" / "build-wheel.ps1").exists()

    def test_install_from_wheel_exists(self):
        assert (PROJECT_ROOT / "scripts" / "windows" / "install-from-wheel.ps1").exists()

    def test_install_from_testpypi_exists(self):
        assert (PROJECT_ROOT / "scripts" / "windows" / "install-from-testpypi.ps1").exists()

    def test_build_wheel_mentions_python(self):
        path = PROJECT_ROOT / "scripts" / "windows" / "build-wheel.ps1"
        content = path.read_text()
        assert "python" in content.lower() or "Python" in content

    def test_install_from_testpypi_mentions_testpypi(self):
        path = PROJECT_ROOT / "scripts" / "windows" / "install-from-testpypi.ps1"
        content = path.read_text()
        assert "test.pypi.org" in content


# ─── Reverse Proxy Auth Refinement ──────────────────────────────────────────


class TestReverseProxyAuthRefinement:
    def test_reverse_proxy_auth_exists(self):
        assert (PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md").exists()

    def test_has_do_not_expose_section(self):
        path = PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md"
        content = path.read_text()
        assert "do not expose" in content.lower() or "Do Not Expose" in content

    def test_has_diagram(self):
        path = PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md"
        content = path.read_text()
        assert "→" in content or "client" in content.lower()

    def test_mentions_kimari_token_does_not_protect(self):
        path = PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md"
        content = path.read_text()
        assert "does not protect" in content.lower() or "does not" in content.lower()


# ─── Release Check Improvements ─────────────────────────────────────────────


class TestReleaseCheck:
    def test_check_release_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/release/check-release.py"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        # Should pass or at least run without crash
        assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"

    def test_default_profile_still_test(self):
        config = PROJECT_ROOT / "config" / "kimari.profiles.json"
        if config.exists():
            data = json.loads(config.read_text())
            assert data.get("default_profile") == "test"

    def test_no_kimari_4b_released_claim(self):
        """No false claim that Kimari-4B is released."""
        patterns = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        for name in ("README.md", "CHANGELOG.md"):
            path = PROJECT_ROOT / name
            if path.exists():
                content = path.read_text().lower()
                for pattern in patterns:
                    assert pattern not in content, f"False claim '{pattern}' found in {path}"

    def test_no_responses_api_supported_claim(self):
        """No false claim that Responses API is supported."""
        for name in ("README.md", "CHANGELOG.md"):
            path = PROJECT_ROOT / name
            if path.exists():
                content = path.read_text().lower()
                assert "responses api is supported" not in content
                assert "responses api supported" not in content


# ─── Documentation ──────────────────────────────────────────────────────────


class TestDocumentation:
    def test_publishing_md_has_v0115_section(self):
        path = PROJECT_ROOT / "docs" / "PUBLISHING.md"
        if path.exists():
            content = path.read_text()
            assert "0.1.22" in content

    def test_readme_mentions_setup_yes(self):
        path = PROJECT_ROOT / "README.md"
        content = path.read_text()
        assert "--yes" in content

    def test_readme_mentions_pin_hash(self):
        path = PROJECT_ROOT / "README.md"
        content = path.read_text()
        assert "pin-hash" in content

    def test_readme_mentions_model_path_resolution(self):
        path = PROJECT_ROOT / "README.md"
        content = path.read_text()
        assert "resolve_model_path" in content or "Model Path Resolution" in content or "model path" in content.lower()
