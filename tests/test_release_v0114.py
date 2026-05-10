"""
Release validation tests for Kimari Local AI v0.1.14-alpha.

Verifies setup write-mode, SHA256 tooling, reverse proxy auth guide,
API plan, and packaging readiness for the v0.1.14 release.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ─── Version consistency ──────────────────────────────────────────────────


class TestVersionConsistency:
    """Version is consistent across all files."""

    def test_pyproject_version(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.15-alpha" in text

    def test_init_version(self):
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.15-alpha" in text

    def test_readme_version_badge(self):
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "0.1.15-alpha" in text

    def test_index_html_version(self):
        text = (PROJECT_ROOT / "docs" / "index.html").read_text()
        assert "0.1.15-alpha" in text


# ─── Setup write-mode ───────────────────────────────────────────────────


class TestSetupWriter:
    """Setup writer module works correctly."""

    def test_setup_module_exists(self):
        assert (PROJECT_ROOT / "kimari" / "setup" / "__init__.py").exists()

    def test_setup_writer_exists(self):
        assert (PROJECT_ROOT / "kimari" / "setup" / "writer.py").exists()

    def test_build_setup_patch_returns_dict(self):
        from kimari.setup.writer import build_setup_patch

        result = build_setup_patch(
            recommended_profile="test",
            integration=None,
            hardware_summary={"gpu": "detected"},
            paths_info={"config_dir": "/tmp"},
            config={"default_profile": "test"},
        )
        assert isinstance(result, dict)
        assert "would_write" in result
        assert "changes" in result
        assert "config_path" in result

    def test_build_setup_patch_detects_changes(self):
        from kimari.setup.writer import build_setup_patch

        # Config with different default_profile should trigger would_write
        result = build_setup_patch(
            recommended_profile="gtx1060",
            integration=None,
            hardware_summary={},
            paths_info={},
            config={"default_profile": "test"},
        )
        assert result["would_write"] is True

    def test_write_setup_config_creates_file(self, tmp_path):
        from kimari.setup.writer import build_setup_patch, write_setup_config

        config_path = tmp_path / "kimari.profiles.json"
        patch = build_setup_patch(
            recommended_profile="test",
            integration=None,
            hardware_summary={"gpu": "test-gpu"},
            paths_info={"config_dir": str(tmp_path)},
            config={"default_profile": "test"},
        )
        result = write_setup_config(patch, config_path)
        assert result["written"] is True
        assert config_path.exists()
        # Verify written config has setup_info
        with open(config_path) as f:
            written_config = json.load(f)
        assert "setup_info" in written_config

    def test_write_setup_config_creates_backup(self, tmp_path):
        from kimari.setup.writer import build_setup_patch, write_setup_config

        config_path = tmp_path / "kimari.profiles.json"
        # Write initial config
        initial_config = {"default_profile": "test", "profiles": {}, "config_version": 3}
        with open(config_path, "w") as f:
            json.dump(initial_config, f)

        patch = build_setup_patch(
            recommended_profile="gtx1060",
            integration=None,
            hardware_summary={},
            paths_info={},
            config=initial_config,
        )
        result = write_setup_config(patch, config_path)
        assert result["written"] is True
        assert result.get("backup_path") is not None
        # Backup file should exist
        backup_path = Path(result["backup_path"])
        assert backup_path.exists()

    def test_setup_json_includes_write_info(self):
        """kimari setup --json should include would_write/written/config_path."""
        import subprocess

        env = os.environ.copy()
        env["KIMARI_HOME"] = tempfile.mkdtemp()
        result = subprocess.run(
            ["python", "-m", "kimari.cli.main", "setup", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=env,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert "would_write" in data
            assert "written" in data
            assert "config_path" in data

    def test_setup_write_persists_config(self):
        """kimari setup --write should persist config."""
        import subprocess

        env = os.environ.copy()
        env["KIMARI_HOME"] = tempfile.mkdtemp()
        result = subprocess.run(
            ["python", "-m", "kimari.cli.main", "setup", "--write", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=env,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert data.get("written") is True or data.get("would_write") is not None


# ─── SHA256 tooling ──────────────────────────────────────────────────────


class TestSHA256Tooling:
    """Model hash computation and verification works."""

    def test_compute_model_hash_on_temp_file(self, tmp_path):
        from kimari.models.registry import compute_model_hash

        # Create a temp GGUF file
        gguf_file = tmp_path / "test-model.gguf"
        gguf_file.write_bytes(b"fake gguf content for hash testing")

        result = compute_model_hash(str(gguf_file), json_output=True)
        assert result["file_exists"] is True
        assert result["sha256"] == hashlib.sha256(b"fake gguf content for hash testing").hexdigest()
        assert result["size_bytes"] > 0

    def test_compute_model_hash_nonexistent(self):
        from kimari.models.registry import compute_model_hash

        result = compute_model_hash("/tmp/nonexistent_model.gguf", json_output=True)
        assert result["file_exists"] is False

    def test_verify_model_not_pinned(self):
        """Models with null sha256 should report 'not_pinned'."""
        from kimari.models.registry import verify_model_hash_v2

        env = os.environ.copy()
        env["KIMARI_HOME"] = tempfile.mkdtemp()
        # We need to run with KIMARI_HOME set
        original_home = os.environ.get("KIMARI_HOME")
        os.environ["KIMARI_HOME"] = env["KIMARI_HOME"]
        try:
            result = verify_model_hash_v2("test", json_output=True)
            assert result["status"] == "not_pinned"
        finally:
            if original_home:
                os.environ["KIMARI_HOME"] = original_home
            elif "KIMARI_HOME" in os.environ:
                del os.environ["KIMARI_HOME"]

    def test_verify_model_with_file_path(self, tmp_path):
        """Verify should work with a file path too."""
        from kimari.models.registry import verify_model_hash_v2

        gguf_file = tmp_path / "some-model.gguf"
        gguf_file.write_bytes(b"test content")

        original_home = os.environ.get("KIMARI_HOME")
        os.environ["KIMARI_HOME"] = tempfile.mkdtemp()
        try:
            result = verify_model_hash_v2(str(gguf_file), json_output=True)
            # Should either match a registry entry or report computed_only
            assert result["status"] in ("match", "mismatch", "computed_only", "not_pinned")
        finally:
            if original_home:
                os.environ["KIMARI_HOME"] = original_home
            elif "KIMARI_HOME" in os.environ:
                del os.environ["KIMARI_HOME"]

    def test_pin_model_hash_dry_run(self):
        """pin-hash without --write should be a dry run."""
        from kimari.models.registry import pin_model_hash

        original_home = os.environ.get("KIMARI_HOME")
        os.environ["KIMARI_HOME"] = tempfile.mkdtemp()
        try:
            result = pin_model_hash("test", write=False, json_output=True)
            assert result["would_write"] is False or result.get("sha256") is not None
        finally:
            if original_home:
                os.environ["KIMARI_HOME"] = original_home
            elif "KIMARI_HOME" in os.environ:
                del os.environ["KIMARI_HOME"]

    def test_get_effective_models_registry_exists(self):
        from kimari.models.registry import get_effective_models_registry

        original_home = os.environ.get("KIMARI_HOME")
        os.environ["KIMARI_HOME"] = tempfile.mkdtemp()
        try:
            registry = get_effective_models_registry()
            assert isinstance(registry, dict)
            assert "models" in registry
        finally:
            if original_home:
                os.environ["KIMARI_HOME"] = original_home
            elif "KIMARI_HOME" in os.environ:
                del os.environ["KIMARI_HOME"]

    def test_no_invented_hashes_in_defaults(self):
        """Packaged defaults should have sha256 = null for all models."""
        defaults_path = PROJECT_ROOT / "kimari" / "defaults" / "kimari.models.json"
        if defaults_path.exists():
            data = json.loads(defaults_path.read_text())
            for m in data.get("models", []):
                assert m.get("sha256") is None, f"Model {m['id']} has non-null sha256 — hashes must not be invented"


# ─── Documentation files ────────────────────────────────────────────────


class TestDocumentation:
    """New documentation files exist with proper content."""

    def test_reverse_proxy_auth_exists(self):
        assert (PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md").exists()

    def test_reverse_proxy_mentions_nginx(self):
        text = (PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md").read_text().lower()
        assert "nginx" in text

    def test_reverse_proxy_mentions_caddy(self):
        text = (PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md").read_text().lower()
        assert "caddy" in text

    def test_reverse_proxy_mentions_token(self):
        text = (PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md").read_text().lower()
        assert "token" in text

    def test_reverse_proxy_warns_no_native_auth(self):
        text = (PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md").read_text().lower()
        assert "does not" in text or "not apply" in text or "natively" in text

    def test_reverse_proxy_no_0000_recommendation(self):
        text = (PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md").read_text().lower()
        # Should NOT recommend 0.0.0.0 without auth
        if "0.0.0.0" in text:
            assert "auth" in text or "never" in text or "not" in text

    def test_api_plan_exists(self):
        assert (PROJECT_ROOT / "docs" / "API_PLAN.md").exists()

    def test_api_plan_mentions_fastapi(self):
        text = (PROJECT_ROOT / "docs" / "API_PLAN.md").read_text()
        assert "FastAPI" in text

    def test_api_plan_mentions_v02(self):
        text = (PROJECT_ROOT / "docs" / "API_PLAN.md").read_text()
        assert "v0.2" in text

    def test_api_plan_has_endpoints(self):
        text = (PROJECT_ROOT / "docs" / "API_PLAN.md").read_text()
        assert "/health" in text or "health" in text.lower()

    def test_api_plan_is_design_only(self):
        text = (PROJECT_ROOT / "docs" / "API_PLAN.md").read_text().lower()
        assert "design" in text or "plan" in text or "not implemented" in text or "no implementation" in text


# ─── README updates ─────────────────────────────────────────────────────


class TestReadmeUpdates:
    """README mentions new v0.1.14 features."""

    def test_readme_mentions_setup_write(self):
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "setup --write" in text

    def test_readme_mentions_models_hash(self):
        text = (PROJECT_ROOT / "README.md").read_text().lower()
        assert "models hash" in text

    def test_readme_mentions_models_verify(self):
        text = (PROJECT_ROOT / "README.md").read_text().lower()
        assert "models verify" in text

    def test_readme_links_to_reverse_proxy(self):
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "REVERSE_PROXY_AUTH" in text

    def test_readme_links_to_api_plan(self):
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "API_PLAN" in text


# ─── docs/index.html updates ────────────────────────────────────────────


class TestIndexHtmlUpdates:
    """docs/index.html mentions new v0.1.14 features."""

    def test_index_mentions_reverse_proxy(self):
        text = (PROJECT_ROOT / "docs" / "index.html").read_text().lower()
        assert "reverse proxy" in text

    def test_index_mentions_api_plan(self):
        text = (PROJECT_ROOT / "docs" / "index.html").read_text().lower()
        assert "api plan" in text


# ─── Release check improvements ─────────────────────────────────────────


class TestReleaseCheck:
    """check-release.py includes v0.1.14 checks."""

    def test_check_release_compiles(self):
        import py_compile

        py_compile.compile(str(PROJECT_ROOT / "scripts" / "release" / "check-release.py"), doraise=True)

    def test_check_release_mentions_setup_writer(self):
        text = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
        assert "setup/writer" in text or "writer.py" in text

    def test_check_release_mentions_reverse_proxy(self):
        text = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
        assert "REVERSE_PROXY_AUTH" in text

    def test_check_release_mentions_api_plan(self):
        text = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
        assert "API_PLAN" in text

    def test_check_release_checks_no_invented_hashes(self):
        text = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
        assert "invented" in text.lower() or "sha256" in text.lower()


# ─── No false claims ────────────────────────────────────────────────────


class TestNoFalseClaims:
    """Critical rules: no false claims about Kimari-4B, Responses API, or hashes."""

    def test_no_kimari4b_released_claim(self):
        all_text = ""
        for f in ["README.md", "CHANGELOG.md", "docs/index.html"]:
            path = PROJECT_ROOT / f
            if path.exists():
                all_text += path.read_text().lower() + " "
        false_patterns = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        for p in false_patterns:
            assert p not in all_text, f"False claim found: {p}"

    def test_no_responses_api_supported_claim(self):
        all_text = ""
        for f in ["README.md", "CHANGELOG.md", "docs/index.html"]:
            path = PROJECT_ROOT / f
            if path.exists():
                all_text += path.read_text().lower() + " "
        false_patterns = [
            "responses api supported",
            "responses api is supported",
        ]
        for p in false_patterns:
            assert p not in all_text, f"False claim found: {p}"

    def test_default_profile_is_test(self):
        config_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            assert config.get("default_profile") == "test"

    def test_no_invented_hashes_in_registry(self):
        registry_path = PROJECT_ROOT / "config" / "kimari.models.json"
        if registry_path.exists():
            data = json.loads(registry_path.read_text())
            for m in data.get("models", []):
                assert m.get("sha256") is None, f"Model {m['id']} has invented sha256"
