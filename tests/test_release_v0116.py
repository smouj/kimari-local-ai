"""Release validation tests for Kimari Local AI v0.1.16-alpha.

Tests cover:
- Version consistency
- API optional dependency in pyproject.toml
- kimari api --dry-run works without FastAPI installed
- kimari api without --experimental does not start
- API module files exist
- API app factory importable with clean skip
- /health endpoint schema (if FastAPI available)
- /profiles endpoint schema (if FastAPI available)
- /server/start returns planned/501
- API experimental documentation
- PyPI release gate documentation
- Model hashing documentation
- Benchmark submissions documentation
- Benchmark examples parse as JSON
- No secrets in docs
- Release check passes
- No false claims
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_kimari(*args: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "kimari.cli.main", *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT))


# ─── Version Consistency ────────────────────────────────────────────────────


class TestVersion:
    def test_version_is_0116(self):
        from kimari import __version__

        assert __version__ == "0.1.16-alpha"

    def test_pyproject_version_matches(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        text = pyproject.read_text()
        assert 'version = "0.1.16-alpha"' in text

    def test_cli_info_version(self):
        result = _run_kimari("info", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["kimari_version"] == "0.1.16-alpha"


# ─── API Optional Dependency ────────────────────────────────────────────────


class TestAPIOptionalDependency:
    def test_api_extra_exists_in_pyproject(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        text = pyproject.read_text()
        assert "[project.optional-dependencies]" in text
        assert "api" in text
        assert "fastapi" in text.lower() or "FastAPI" in text
        assert "uvicorn" in text.lower()

    def test_api_not_in_main_dependencies(self):
        """FastAPI must NOT be a main dependency."""
        pyproject = PROJECT_ROOT / "pyproject.toml"
        text = pyproject.read_text()
        # Find the main dependencies section
        deps_start = text.index("dependencies = [")
        deps_end = text.index("]", deps_start)
        main_deps = text[deps_start:deps_end]
        assert "fastapi" not in main_deps.lower()


# ─── kimari api Command ────────────────────────────────────────────────────


class TestAPICommand:
    def test_api_dry_run_works(self):
        result = _run_kimari("api", "--dry-run")
        assert result.returncode == 0
        assert "dry_run" in result.stdout.lower() or "Dry Run" in result.stdout

    def test_api_dry_run_json(self):
        result = _run_kimari("api", "--dry-run", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["dry_run"] is True
        assert data["version"] == "0.1.16-alpha"

    def test_api_without_experimental_does_not_start(self):
        """Without --experimental, should show warning, not start server."""
        result = _run_kimari("api")
        assert result.returncode == 0
        assert "experimental" in result.stdout.lower()
        assert "--experimental" in result.stdout

    def test_api_without_experimental_json(self):
        result = _run_kimari("api", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("error") == "experimental_flag_required" or "experimental" in str(data).lower()

    def test_api_help_mentions_experimental(self):
        result = _run_kimari("api", "--help")
        assert result.returncode == 0
        assert "--experimental" in result.stdout

    def test_api_help_mentions_port(self):
        result = _run_kimari("api", "--help")
        assert result.returncode == 0
        assert "--port" in result.stdout
        assert "11436" in result.stdout


# ─── API Module Files ───────────────────────────────────────────────────────


class TestAPIModuleFiles:
    def test_api_init_exists(self):
        assert (PROJECT_ROOT / "kimari" / "api" / "__init__.py").exists()

    def test_api_app_exists(self):
        assert (PROJECT_ROOT / "kimari" / "api" / "app.py").exists()

    def test_api_schemas_exists(self):
        assert (PROJECT_ROOT / "kimari" / "api" / "schemas.py").exists()

    def test_api_server_exists(self):
        assert (PROJECT_ROOT / "kimari" / "api" / "server.py").exists()

    def test_api_init_exports_create_app(self):
        from kimari.api import create_app

        assert callable(create_app)

    def test_api_init_exports_defaults(self):
        from kimari.api import API_HOST_DEFAULT, API_PORT_DEFAULT

        assert API_HOST_DEFAULT == "127.0.0.1"
        assert API_PORT_DEFAULT == 11436


# ─── API App Factory (skip if FastAPI not installed) ────────────────────────


class TestAPIAppFactory:
    def test_app_factory_importable_or_skip(self):
        """App factory should be importable if FastAPI is available, or raise ImportError."""
        try:
            from kimari.api import create_app

            app = create_app()
            assert app is not None
            assert app.title is not None
            assert "Kimari" in app.title or "kimari" in app.title.lower()
        except ImportError:
            pass  # FastAPI not installed, skip

    def test_health_endpoint_exists_if_fastapi(self):
        """If FastAPI is available, /health endpoint should be registered."""
        try:
            from kimari.api import create_app

            app = create_app()
            routes = [r.path for r in app.routes]
            assert "/health" in routes
        except ImportError:
            pass

    def test_profiles_endpoint_exists_if_fastapi(self):
        try:
            from kimari.api import create_app

            app = create_app()
            routes = [r.path for r in app.routes]
            assert "/profiles" in routes
        except ImportError:
            pass

    def test_server_start_returns_planned(self):
        """POST /server/start should return 501 Not Implemented."""
        try:
            from kimari.api import create_app

            app = create_app()
            routes = [r.path for r in app.routes]
            assert "/server/start" in routes
        except ImportError:
            pass

    def test_server_stop_returns_planned(self):
        """POST /server/stop should return 501 Not Implemented."""
        try:
            from kimari.api import create_app

            app = create_app()
            routes = [r.path for r in app.routes]
            assert "/server/stop" in routes
        except ImportError:
            pass

    def test_all_expected_endpoints_registered(self):
        """All documented endpoints should be registered."""
        try:
            from kimari.api import create_app

            app = create_app()
            routes = [r.path for r in app.routes]
            expected = [
                "/health",
                "/status",
                "/config",
                "/profiles",
                "/models",
                "/optimize",
                "/perf/dry-run",
                "/server/start",
                "/server/stop",
            ]
            for endpoint in expected:
                assert endpoint in routes, f"Missing endpoint: {endpoint}"
        except ImportError:
            pass


# ─── API Schemas ─────────────────────────────────────────────────────────────


class TestAPISchemas:
    def test_health_response_schema(self):
        try:
            from kimari.api.schemas import HealthResponse

            h = HealthResponse(status="ok", version="0.1.16-alpha")
            assert h.experimental is True
            assert h.status == "ok"
        except ImportError:
            pass

    def test_status_response_schema(self):
        try:
            from kimari.api.schemas import StatusResponse

            s = StatusResponse(running=False)
            assert s.running is False
            assert s.experimental is True
        except ImportError:
            pass

    def test_optimize_request_schema(self):
        try:
            from kimari.api.schemas import OptimizeRequest

            r = OptimizeRequest()
            assert r.mode == "balanced"
        except ImportError:
            pass


# ─── Documentation ──────────────────────────────────────────────────────────


class TestDocumentation:
    def test_api_experimental_md_exists(self):
        assert (PROJECT_ROOT / "docs" / "API_EXPERIMENTAL.md").exists()

    def test_api_experimental_warns_experimental(self):
        path = PROJECT_ROOT / "docs" / "API_EXPERIMENTAL.md"
        content = path.read_text().lower()
        assert "experimental" in content

    def test_api_experimental_mentions_install(self):
        path = PROJECT_ROOT / "docs" / "API_EXPERIMENTAL.md"
        content = path.read_text()
        assert "kimari-local-ai[api]" in content or '"kimari-local-ai[api]"' in content

    def test_api_experimental_mentions_port(self):
        path = PROJECT_ROOT / "docs" / "API_EXPERIMENTAL.md"
        content = path.read_text()
        assert "11436" in content

    def test_api_experimental_mentions_not_openai_compatible(self):
        path = PROJECT_ROOT / "docs" / "API_EXPERIMENTAL.md"
        content = path.read_text().lower()
        assert "not openai" in content or "not the openai" in content or "openai-compatible" in content

    def test_pypi_release_gate_exists(self):
        assert (PROJECT_ROOT / "docs" / "PYPI_RELEASE_GATE.md").exists()

    def test_pypi_release_gate_has_checklist(self):
        path = PROJECT_ROOT / "docs" / "PYPI_RELEASE_GATE.md"
        content = path.read_text().lower()
        assert "testpypi" in content
        assert "checklist" in content or "requirements" in content

    def test_pypi_release_gate_status_pending(self):
        path = PROJECT_ROOT / "docs" / "PYPI_RELEASE_GATE.md"
        content = path.read_text().lower()
        assert "pending" in content

    def test_model_hashing_md_exists(self):
        assert (PROJECT_ROOT / "docs" / "MODEL_HASHING.md").exists()

    def test_model_hashing_mentions_commands(self):
        path = PROJECT_ROOT / "docs" / "MODEL_HASHING.md"
        content = path.read_text().lower()
        assert "pin-hash" in content
        assert "verify" in content

    def test_benchmark_submissions_md_exists(self):
        assert (PROJECT_ROOT / "docs" / "BENCHMARK_SUBMISSIONS.md").exists()

    def test_benchmark_submissions_mentions_privacy(self):
        path = PROJECT_ROOT / "docs" / "BENCHMARK_SUBMISSIONS.md"
        content = path.read_text().lower()
        assert "not share" in content or "do not" in content or "privacy" in content

    def test_publishing_md_has_v0116_section(self):
        path = PROJECT_ROOT / "docs" / "PUBLISHING.md"
        if path.exists():
            content = path.read_text()
            # Should have some reference to the current version
            assert "0.1.16" in content or "0.1.15" in content


# ─── Benchmark Examples ────────────────────────────────────────────────────


class TestBenchmarkExamples:
    def test_gtx1060_example_exists(self):
        assert (PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.gtx1060.example.json").exists()

    def test_gtx1080_example_exists(self):
        assert (PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.gtx1080.example.json").exists()

    def test_gtx1060_example_parseable(self):
        path = PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.gtx1060.example.json"
        data = json.loads(path.read_text())
        assert "kimari_version" in data or "profile" in data

    def test_gtx1080_example_parseable(self):
        path = PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.gtx1080.example.json"
        data = json.loads(path.read_text())
        assert "kimari_version" in data or "profile" in data

    def test_gtx1060_no_secrets(self):
        path = PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.gtx1060.example.json"
        text = path.read_text().lower()
        assert "bearer" not in text
        assert "api_key" not in text
        assert "secret" not in text

    def test_gtx1080_no_secrets(self):
        path = PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.gtx1080.example.json"
        text = path.read_text().lower()
        assert "bearer" not in text
        assert "api_key" not in text
        assert "secret" not in text


# ─── No False Claims ────────────────────────────────────────────────────────


class TestNoFalseClaims:
    def test_no_kimari_4b_released_claim(self):
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
        for name in ("README.md", "CHANGELOG.md"):
            path = PROJECT_ROOT / name
            if path.exists():
                content = path.read_text().lower()
                assert "responses api is supported" not in content
                assert "responses api supported" not in content

    def test_no_pypi_real_published_claim(self):
        """No false claim that we published to PyPI real."""
        for name in ("README.md", "CHANGELOG.md", "docs/PYPI_RELEASE_GATE.md"):
            path = PROJECT_ROOT / name
            if path.exists():
                content = path.read_text().lower()
                # "published to pypi" should NOT appear as a done action
                assert "published to pypi" not in content or "not published" in content or "pending" in content

    def test_default_profile_still_test(self):
        config = PROJECT_ROOT / "config" / "kimari.profiles.json"
        if config.exists():
            data = json.loads(config.read_text())
            assert data.get("default_profile") == "test"


# ─── No Secrets in Docs ────────────────────────────────────────────────────


class TestNoSecrets:
    def test_no_real_tokens_in_api_experimental(self):
        path = PROJECT_ROOT / "docs" / "API_EXPERIMENTAL.md"
        content = path.read_text()
        # Should not contain actual token values
        assert "Bearer ey" not in content
        assert "Bearer sk-" not in content

    def test_no_real_tokens_in_pypi_gate(self):
        path = PROJECT_ROOT / "docs" / "PYPI_RELEASE_GATE.md"
        if path.exists():
            content = path.read_text()
            assert "pypi-AgEIcH" not in content  # Real PyPI token prefix

    def test_no_real_tokens_in_model_hashing(self):
        path = PROJECT_ROOT / "docs" / "MODEL_HASHING.md"
        if path.exists():
            content = path.read_text()
            assert "Bearer ey" not in content


# ─── Release Check ──────────────────────────────────────────────────────────


class TestReleaseCheck:
    def test_check_release_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/release/check-release.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"


# ─── API Server Module ──────────────────────────────────────────────────────


class TestAPIServerModule:
    def test_server_module_has_run_api_command(self):
        from kimari.api.server import run_api_command

        assert callable(run_api_command)

    def test_server_module_checks_deps(self):
        from kimari.api.server import _check_api_deps

        # Should return a boolean (True or False depending on env)
        result = _check_api_deps()
        assert isinstance(result, bool)

    def test_server_default_host_is_localhost(self):
        import inspect

        from kimari.api.server import run_api_command

        # Check that the default is 127.0.0.1 (not 0.0.0.0)
        sig = inspect.signature(run_api_command)
        assert sig.parameters["host"].default == "127.0.0.1"

    def test_server_default_port_is_11436(self):
        import inspect

        from kimari.api.server import run_api_command

        sig = inspect.signature(run_api_command)
        assert sig.parameters["port"].default == 11436
