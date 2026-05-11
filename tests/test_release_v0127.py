"""
Release tests for v0.1.27-alpha.

Covers: console render functions, integration config generator,
improved status/doctor output, gateway wording correction,
screenshot plan script, and release hygiene.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ─── Console Render Functions ────────────────────────────────────────────────


class TestConsoleRender:
    """Tests for kimari/console/render.py functions."""

    def test_render_status_table_returns_string(self):
        from kimari.console.render import render_status_table

        data = {
            "Version": "0.1.27-alpha",
            "Config": "/tmp/config",
            "Models": "/tmp/models",
            "Default profile": "test",
            "Server": "STOPPED",
            "Gateway": "planned",
            "Preview gate": "BLOCKED",
        }
        result = render_status_table(data)
        assert isinstance(result, str)
        assert "0.1.27-alpha" in result
        assert "STOPPED" in result

    def test_render_status_table_handles_missing_keys(self):
        from kimari.console.render import render_status_table

        result = render_status_table({})
        assert isinstance(result, str)

    def test_render_doctor_table_returns_string(self):
        from kimari.console.render import render_doctor_table

        checks = [
            {"name": "Python", "status": "PASS", "value": "3.12.0", "detail": ""},
            {"name": "GPU", "status": "WARN", "value": "Not detected", "detail": "CPU-only"},
            {"name": "llama-server", "status": "FAIL", "value": "Not found", "detail": "Build it"},
        ]
        result = render_doctor_table(checks)
        assert isinstance(result, str)
        assert "PASS" in result or "\u2713" in result
        assert "WARN" in result or "\u26a0" in result
        assert "FAIL" in result or "\u2717" in result

    def test_render_gateway_summary_returns_string(self):
        from kimari.console.render import render_gateway_summary

        plan = {
            "planned_only": True,
            "security": {"default_host": "127.0.0.1", "default_port": 11436},
            "planned_endpoints": [
                {"method": "GET", "path": "/health", "status": "planned"},
            ],
        }
        result = render_gateway_summary(plan)
        assert isinstance(result, str)
        assert "11436" in result

    def test_render_next_steps_returns_string(self):
        from kimari.console.render import render_next_steps

        items = [
            "Run 'kimari doctor --deep' for full diagnostics",
            "Run 'kimari start' to start the server",
        ]
        result = render_next_steps(items)
        assert isinstance(result, str)
        assert "doctor" in result
        assert "start" in result

    def test_render_next_steps_empty_list(self):
        from kimari.console.render import render_next_steps

        result = render_next_steps([])
        assert isinstance(result, str)


# ─── Integration Config Generator ───────────────────────────────────────────


class TestIntegrationConfigGenerator:
    """Tests for kimari/integrations/config_generator.py functions."""

    def test_generate_openwebui_config(self):
        from kimari.integrations.config_generator import generate_openwebui_config

        config = generate_openwebui_config()
        assert isinstance(config, dict)
        assert "base_url" in config
        assert config["base_url"] == "http://127.0.0.1:11435/v1"

    def test_generate_openclaw_config(self):
        from kimari.integrations.config_generator import generate_openclaw_config

        config = generate_openclaw_config()
        assert isinstance(config, dict)
        assert "base_url" in config

    def test_generate_hermes_config(self):
        from kimari.integrations.config_generator import generate_hermes_config

        config = generate_hermes_config()
        assert isinstance(config, dict)
        assert "base_url" in config

    def test_generate_continue_config(self):
        from kimari.integrations.config_generator import generate_continue_config

        config = generate_continue_config()
        assert isinstance(config, dict)
        assert "models" in config or "base_url" in config

    def test_configs_contain_no_token_fields(self):
        """All generated configs must NOT contain token/API key fields."""
        from kimari.integrations.config_generator import (
            generate_continue_config,
            generate_hermes_config,
            generate_openclaw_config,
            generate_openwebui_config,
        )

        sensitive_keywords = [
            "token",
            "api_key",
            "apikey",
            "password",
            "secret",
            "bearer",
            "authorization",
        ]
        for gen_func in [
            generate_openwebui_config,
            generate_openclaw_config,
            generate_hermes_config,
            generate_continue_config,
        ]:
            config = gen_func()
            for key in config:
                assert not any(kw in key.lower() for kw in sensitive_keywords), (
                    f"{gen_func.__name__}() contains sensitive key: {key}"
                )

    def test_sanitize_config_removes_sensitive_fields(self):
        from kimari.integrations.config_generator import sanitize_config

        dirty = {
            "base_url": "http://127.0.0.1:11435/v1",
            "api_key": "sk-12345",
            "token": "hf_abc123",
            "password": "secret123",
            "name": "kimari",
        }
        clean = sanitize_config(dirty)
        assert "api_key" not in clean
        assert "token" not in clean
        assert "password" not in clean
        assert "base_url" in clean
        assert "name" in clean

    def test_validate_local_base_url_localhost(self):
        from kimari.integrations.config_generator import validate_local_base_url

        is_local, msg = validate_local_base_url("http://127.0.0.1:11435/v1")
        assert is_local is True

    def test_validate_local_base_url_localhost_name(self):
        from kimari.integrations.config_generator import validate_local_base_url

        is_local, msg = validate_local_base_url("http://localhost:11435/v1")
        assert is_local is True

    def test_validate_local_base_url_non_local_warns(self):
        from kimari.integrations.config_generator import validate_local_base_url

        is_local, msg = validate_local_base_url("http://example.com:11435/v1")
        assert is_local is False
        assert "WARNING" in msg or "not localhost" in msg.lower()

    def test_validate_local_base_url_rejects_0000(self):
        from kimari.integrations.config_generator import validate_local_base_url

        is_local, msg = validate_local_base_url("http://0.0.0.0:11435/v1")
        assert is_local is False

    def test_custom_base_url_propagated(self):
        from kimari.integrations.config_generator import generate_openwebui_config

        config = generate_openwebui_config(base_url="http://127.0.0.1:8080/v1")
        assert config["base_url"] == "http://127.0.0.1:8080/v1"


# ─── Status JSON ────────────────────────────────────────────────────────────


class TestStatusJson:
    """Tests for improved kimari status --json output."""

    def test_status_json_includes_gateway(self):
        """status --json must include gateway field."""
        result = subprocess.run(
            [sys.executable, "-m", "kimari.cli.main", "status", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert "gateway" in data

    def test_status_json_includes_preview_gate(self):
        """status --json must include preview_gate field."""
        result = subprocess.run(
            [sys.executable, "-m", "kimari.cli.main", "status", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert "preview_gate" in data
        assert data["preview_gate"] == "BLOCKED"


# ─── Doctor Deep JSON ───────────────────────────────────────────────────────


class TestDoctorDeepJson:
    """Tests for improved kimari doctor --deep --json output."""

    def test_doctor_deep_json_works(self):
        """doctor --deep --json must return valid JSON."""
        result = subprocess.run(
            [sys.executable, "-m", "kimari.cli.main", "doctor", "--deep", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert "checks" in data
        assert "summary" in data


# ─── Gateway Wording ────────────────────────────────────────────────────────


class TestGatewayWording:
    """Tests that gateway docs do not claim gateway serves OpenAI-compatible API."""

    def test_gateway_plan_py_no_openai_endpoint_claim(self):
        """gateway/plan.py must not claim gateway provides OpenAI-compatible endpoints."""
        plan_py = PROJECT_ROOT / "kimari" / "gateway" / "plan.py"
        text = plan_py.read_text()
        assert "OpenAI-compatible endpoints for" not in text, (
            "gateway/plan.py still claims gateway provides OpenAI-compatible endpoints"
        )

    def test_gateway_plan_md_clarifies_management_layer(self):
        """GATEWAY_PLAN.md must clarify gateway is management layer, not OpenAI endpoint."""
        plan_md = PROJECT_ROOT / "docs" / "GATEWAY_PLAN.md"
        text = plan_md.read_text().lower()
        assert "management and diagnostic layer" in text or "helps configure and monitor" in text, (
            "GATEWAY_PLAN.md should clarify gateway helps configure/monitor llama-server"
        )


# ─── Screenshot Plan Script ─────────────────────────────────────────────────


class TestScreenshotPlanScript:
    """Tests for scripts/docs/generate_safe_cli_screenshots_plan.py."""

    def test_screenshot_plan_script_json_output(self):
        """generate_safe_cli_screenshots_plan.py --json must produce valid JSON."""
        script = PROJECT_ROOT / "scripts" / "docs" / "generate_safe_cli_screenshots_plan.py"
        if not script.exists():
            pytest.skip("Screenshot plan script not found")
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "plans" in data or "screenshot_plans" in data or "total_plans" in data


# ─── Release Hygiene ────────────────────────────────────────────────────────


class TestReleaseHygiene:
    """Release hygiene checks for v0.1.27-alpha."""

    def test_version_consistency(self):
        """pyproject.toml and __init__.py must agree on version."""
        pyproject = PROJECT_ROOT / "pyproject.toml"
        init_file = PROJECT_ROOT / "kimari" / "__init__.py"

        pyproject_ver = ""
        for line in pyproject.read_text().splitlines():
            line = line.strip()
            if line.startswith("version") and "python" not in line.lower():
                pyproject_ver = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

        init_ver = ""
        for line in init_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("__version__"):
                init_ver = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

        assert pyproject_ver == init_ver
        assert pyproject_ver == "0.1.27-alpha"

    def test_default_profile_is_test(self):
        """default_profile must be 'test' during alpha."""
        profiles_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
        if profiles_path.exists():
            profiles = json.loads(profiles_path.read_text())
            assert profiles.get("default_profile") == "test"

    def test_no_kimari4b_released_claim(self):
        """No false claim that Kimari-4B is released."""
        critical_files = [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "CHANGELOG.md",
            PROJECT_ROOT / "docs" / "index.html",
        ]
        false_patterns = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        for fpath in critical_files:
            if not fpath.exists():
                continue
            text = fpath.read_text().lower()
            for pattern in false_patterns:
                assert pattern not in text, f"False claim '{pattern}' found in {fpath.name}"

    def test_new_docs_exist(self):
        """v0.1.27 documentation files must exist."""
        required_docs = [
            PROJECT_ROOT / "docs" / "INTEGRATION_CONFIG_GENERATOR.md",
            PROJECT_ROOT / "docs" / "GATEWAY_PROTOTYPE_PLAN.md",
            PROJECT_ROOT / "docs" / "CONSOLE_UX.md",
        ]
        for doc in required_docs:
            assert doc.exists(), f"Missing doc: {doc}"

    def test_new_modules_exist(self):
        """v0.1.27 Python modules must exist."""
        required_modules = [
            PROJECT_ROOT / "kimari" / "console" / "__init__.py",
            PROJECT_ROOT / "kimari" / "console" / "render.py",
            PROJECT_ROOT / "kimari" / "integrations" / "__init__.py",
            PROJECT_ROOT / "kimari" / "integrations" / "config_generator.py",
        ]
        for mod in required_modules:
            assert mod.exists(), f"Missing module: {mod}"

    def test_preview_gate_blocked(self):
        """Preview gate must still be BLOCKED."""
        gate_doc = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
        if gate_doc.exists():
            text = gate_doc.read_text()
            assert "BLOCKED" in text

    def test_no_tracked_gguf(self):
        """No GGUF files should be tracked in git."""
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        gguf_files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(gguf_files) == 0, f"GGUF files tracked: {gguf_files}"

    def test_screenshot_plan_script_exists(self):
        """Screenshot plan script must exist."""
        script = PROJECT_ROOT / "scripts" / "docs" / "generate_safe_cli_screenshots_plan.py"
        assert script.exists(), "generate_safe_cli_screenshots_plan.py missing"

    def test_release_check_script_passes(self):
        """check-release.py must pass."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "release" / "check-release.py"),
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=60,
        )
        assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"
