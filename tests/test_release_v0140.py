"""Tests for v0.1.40-alpha: GTX 1060 local runtime validation result, doctor CUDA improvements,
detect_cuda_version_detailed, detect_compute_capability_from_llama_server, check_gpu_cuda_info."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════════════════════
# 1. GTX 1060 local runtime result documentation
# ══════════════════════════════════════════════════════════════════════════════


class TestGTX1060RuntimeResult:
    """Test GTX 1060 local runtime validation result docs."""

    def test_gtx1060_result_doc_exists(self):
        """docs/GTX1060_LOCAL_RUNTIME_RESULT.md exists."""
        path = PROJECT_ROOT / "docs" / "GTX1060_LOCAL_RUNTIME_RESULT.md"
        assert path.exists(), "GTX 1060 local runtime result doc missing"

    def test_gtx1060_result_doc_mentions_tinyllama(self):
        """GTX 1060 result doc mentions TinyLlama test model."""
        path = PROJECT_ROOT / "docs" / "GTX1060_LOCAL_RUNTIME_RESULT.md"
        if not path.exists():
            pytest.skip("GTX 1060 result doc not found")
        content = path.read_text().lower()
        assert "tinyllama" in content, "GTX 1060 result doc should mention TinyLlama"

    def test_gtx1060_result_doc_no_kimari4b_benchmark_claim(self):
        """GTX 1060 result doc does NOT claim Kimari-4B benchmark."""
        path = PROJECT_ROOT / "docs" / "GTX1060_LOCAL_RUNTIME_RESULT.md"
        if not path.exists():
            pytest.skip("GTX 1060 result doc not found")
        content = path.read_text().lower()
        assert "kimari-4b benchmark" not in content, "Must not claim Kimari-4B benchmark"
        assert "kimari 4b benchmark" not in content, "Must not claim Kimari 4B benchmark"

    def test_gtx1060_result_doc_mentions_gtx1060(self):
        """GTX 1060 result doc mentions GTX 1060."""
        path = PROJECT_ROOT / "docs" / "GTX1060_LOCAL_RUNTIME_RESULT.md"
        if not path.exists():
            pytest.skip("GTX 1060 result doc not found")
        content = path.read_text()
        assert "GTX 1060" in content or "gtx 1060" in content.lower(), "Should mention GTX 1060"

    def test_gtx1060_result_doc_mentions_tok_per_second(self):
        """GTX 1060 result doc includes tok/s metrics."""
        path = PROJECT_ROOT / "docs" / "GTX1060_LOCAL_RUNTIME_RESULT.md"
        if not path.exists():
            pytest.skip("GTX 1060 result doc not found")
        content = path.read_text()
        assert "228" in content, "Should mention 228 tok/s prompt processing"
        assert "73" in content, "Should mention 73 tok/s generation"

    def test_gtx1060_result_doc_gate_blocked(self):
        """GTX 1060 result doc mentions gate BLOCKED."""
        path = PROJECT_ROOT / "docs" / "GTX1060_LOCAL_RUNTIME_RESULT.md"
        if not path.exists():
            pytest.skip("GTX 1060 result doc not found")
        content = path.read_text()
        assert "BLOCKED" in content, "Should mention gate BLOCKED"


# ══════════════════════════════════════════════════════════════════════════════
# 2. Benchmark result JSON
# ══════════════════════════════════════════════════════════════════════════════


class TestBenchmarkResultJSON:
    """Test GTX 1060 benchmark result JSON file."""

    def test_benchmark_json_exists(self):
        """benchmarks/results/gtx1060-tinyllama-wsl2.example.json exists."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        assert path.exists(), "Benchmark result JSON missing"

    def test_benchmark_json_valid(self):
        """Benchmark result JSON is valid JSON."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark JSON not found")
        data = json.loads(path.read_text())
        assert isinstance(data, dict), "Benchmark JSON should be a dict"

    def test_benchmark_json_kimari4b_false(self):
        """Benchmark JSON has kimari4b=false."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark JSON not found")
        data = json.loads(path.read_text())
        assert data.get("kimari4b") is False, f"kimari4b should be False, got {data.get('kimari4b')}"

    def test_benchmark_json_result_type(self):
        """Benchmark JSON has result_type=local_runtime_validation."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark JSON not found")
        data = json.loads(path.read_text())
        assert data.get("result_type") == "local_runtime_validation", (
            f"result_type should be local_runtime_validation, got {data.get('result_type')}"
        )

    def test_benchmark_json_measured_true(self):
        """Benchmark JSON has measured=true."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark JSON not found")
        data = json.loads(path.read_text())
        assert data.get("measured") is True, f"measured should be True, got {data.get('measured')}"

    def test_benchmark_json_public_claim_limited(self):
        """Benchmark JSON has public_claim_allowed=limited."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark JSON not found")
        data = json.loads(path.read_text())
        assert data.get("public_claim_allowed") == "limited", (
            f"public_claim_allowed should be limited, got {data.get('public_claim_allowed')}"
        )

    def test_benchmark_json_has_tinyllama_model(self):
        """Benchmark JSON model field mentions TinyLlama."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark JSON not found")
        data = json.loads(path.read_text())
        assert "tinyllama" in data.get("model", "").lower(), "Model should mention TinyLlama"

    def test_benchmark_json_has_performance_data(self):
        """Benchmark JSON includes CUDA performance data."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark JSON not found")
        data = json.loads(path.read_text())
        cuda = data.get("results", {}).get("cuda", {})
        assert "prompt_tokens_per_second" in cuda, "Missing prompt_tokens_per_second"
        assert "generation_tokens_per_second" in cuda, "Missing generation_tokens_per_second"


# ══════════════════════════════════════════════════════════════════════════════
# 3. Detection improvements
# ══════════════════════════════════════════════════════════════════════════════


class TestDetectionImprovements:
    """Test detection.py improvements for CUDA/compute capability."""

    def test_detect_compute_capability_from_llama_server_exists(self):
        """detect_compute_capability_from_llama_server function exists."""
        from kimari.core.detection import detect_compute_capability_from_llama_server

        assert callable(detect_compute_capability_from_llama_server)

    def test_detect_cuda_version_detailed_exists(self):
        """detect_cuda_version_detailed function exists."""
        from kimari.core.detection import detect_cuda_version_detailed

        assert callable(detect_cuda_version_detailed)

    def test_detect_cuda_version_still_works(self):
        """detect_cuda_version backward-compatible wrapper still works."""
        from kimari.core.detection import detect_cuda_version

        result = detect_cuda_version()
        # May return None if no CUDA, but should not raise
        assert result is None or isinstance(result, str)

    def test_detect_compute_capability_from_llama_server_parses_output(self):
        """detect_compute_capability_from_llama_server can parse 'compute capability 6.1'."""
        from kimari.core.detection import detect_compute_capability_from_llama_server

        with patch("kimari.core.detection.detect_llama_server", return_value="/usr/local/bin/llama-server"), \
             patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="llama-server 706fbd8\ncompute capability 6.1\n",
                    stderr="",
                )
                result = detect_compute_capability_from_llama_server()
                assert result == "6.1", f"Expected 6.1, got {result}"

    def test_detect_compute_capability_from_llama_server_no_llama(self):
        """detect_compute_capability_from_llama_server returns None if no llama-server."""
        from kimari.core.detection import detect_compute_capability_from_llama_server

        with patch("kimari.core.detection.detect_llama_server", return_value=None):
            result = detect_compute_capability_from_llama_server()
            assert result is None

    def test_detect_cuda_version_detailed_nvidia_smi_fallback(self):
        """detect_cuda_version_detailed can parse nvidia-smi CUDA Version header."""
        from kimari.core.detection import detect_cuda_version_detailed

        with patch("kimari.core.detection._nvcc_path", return_value=None), \
             patch("kimari.core.detection._nvidia_smi_path", return_value="/usr/bin/nvidia-smi"), \
             patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(
                        returncode=0,
                        stdout="+-----------------------------------------------------------------------------+\n| NVIDIA-SMI 581.57       Driver Version: 581.57       CUDA Version: 13.0     |\n+-----------------------------------------------------------------------------+",
                        stderr="",
                    )
                    result = detect_cuda_version_detailed()
                    assert result is not None, "Should detect CUDA version from nvidia-smi"
                    assert result["version"] == "13.0", f"Expected 13.0, got {result['version']}"
                    assert result["source"] == "nvidia-smi", f"Expected source nvidia-smi, got {result['source']}"


# ══════════════════════════════════════════════════════════════════════════════
# 4. Doctor deep improvements
# ══════════════════════════════════════════════════════════════════════════════


class TestDoctorDeepImprovements:
    """Test doctor deep.py improvements."""

    def test_doctor_imports_llama_server_fallback(self):
        """doctor deep.py imports detect_compute_capability_from_llama_server."""
        deep_path = PROJECT_ROOT / "kimari" / "doctor" / "deep.py"
        content = deep_path.read_text()
        assert "detect_compute_capability_from_llama_server" in content, (
            "doctor deep.py should import detect_compute_capability_from_llama_server"
        )

    def test_doctor_compute_capability_shows_source(self):
        """check_gpu_compute_capability shows detection source when using fallback."""
        from kimari.doctor.deep import check_gpu_compute_capability

        with patch.dict("sys.modules", {"torch": None}), \
             patch("kimari.doctor.deep.detect_compute_capability_from_llama_server", return_value="6.1"), \
             patch("kimari.doctor.deep.detect_gpu", return_value={"name": "NVIDIA GeForce GTX 1060 6GB", "vram_mb": 6144, "driver": "581.57"}):
                    result = check_gpu_compute_capability()
                    assert result["status"] in ("PASS", "WARN"), f"Unexpected status: {result['status']}"
                    assert "6.1" in result["value"] or "sm_61" in result["value"], (
                        f"Should show compute capability, got: {result['value']}"
                    )
                    assert "llama-server" in result["value"].lower(), (
                        f"Should show detection source, got: {result['value']}"
                    )


# ══════════════════════════════════════════════════════════════════════════════
# 5. check_training_stack improvement
# ══════════════════════════════════════════════════════════════════════════════


class TestCheckTrainingStackImprovement:
    """Test check_training_stack.py gpu_cuda_info check."""

    def test_check_gpu_cuda_info_exists(self):
        """check_gpu_cuda_info function exists in check_training_stack.py."""
        ts_path = PROJECT_ROOT / "training" / "scripts" / "check_training_stack.py"
        content = ts_path.read_text()
        assert "check_gpu_cuda_info" in content, "check_gpu_cuda_info missing from check_training_stack.py"


# ══════════════════════════════════════════════════════════════════════════════
# 6. Version and metadata
# ══════════════════════════════════════════════════════════════════════════════


class TestVersionV0140:
    """Test v0.1.40-alpha version consistency."""

    def test_pyproject_version(self):
        """pyproject.toml has version 0.1.40-alpha."""
        for line in (PROJECT_ROOT / "pyproject.toml").read_text().splitlines():
            if line.strip().startswith("version") and "python" not in line.lower():
                assert "0.1.40-alpha" in line, f"Expected 0.1.40-alpha in: {line}"
                return
        pytest.fail("version line not found in pyproject.toml")

    def test_init_version(self):
        """kimari/__init__.py has __version__ = '0.1.40-alpha'."""
        content = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert '"0.1.40-alpha"' in content or "'0.1.40-alpha'" in content, (
            "__version__ should be 0.1.40-alpha"
        )

    def test_changelog_entry(self):
        """CHANGELOG.md has [0.1.40-alpha] entry."""
        content = (PROJECT_ROOT / "CHANGELOG.md").read_text()
        assert "[0.1.40-alpha]" in content, "CHANGELOG.md missing [0.1.40-alpha]"

    def test_roadmap_marks_current(self):
        """ROADMAP.md marks v0.1.40-alpha as Current."""
        content = (PROJECT_ROOT / "ROADMAP.md").read_text()
        assert "v0.1.40-alpha (Current)" in content, "ROADMAP.md should mark v0.1.40-alpha as Current"

    def test_readme_mentions_gtx1060(self):
        """README mentions GTX 1060 local validation."""
        content = (PROJECT_ROOT / "README.md").read_text()
        assert "GTX 1060" in content, "README should mention GTX 1060"

    def test_readme_says_not_kimari4b(self):
        """README GTX section says NOT Kimari-4B."""
        content = (PROJECT_ROOT / "README.md").read_text()
        assert "NOT Kimari-4B" in content or "not Kimari-4B" in content or "NOT Kimari" in content, (
            "README should clarify NOT Kimari-4B"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 7. No false claims
# ══════════════════════════════════════════════════════════════════════════════


class TestNoFalseClaims:
    """Test no false Kimari-4B release claims."""

    def test_no_kimari4b_released_claim(self):
        """README, CHANGELOG, index.html should not claim Kimari-4B is released."""
        for fname in ("README.md", "CHANGELOG.md", "docs/index.html"):
            path = PROJECT_ROOT / fname
            if not path.exists():
                continue
            content = path.read_text()
            # Check for actual false release claims — not mentions of "false claim detection"
            # Lines that say things like "Kimari-4B is released" or "released Kimari-4B"
            # are false claims. Mentions of "false claim detection" are OK.
            for line in content.splitlines():
                line_lower = line.lower().strip()
                # Skip lines about false claim detection/scan/policy
                if any(phrase in line_lower for phrase in (
                    "false claim",
                    "no false",
                    "claim detection",
                    "claim regression",
                    "no claim",
                    "not claim",
                    "should not claim",
                )):
                    continue
                # Check for "kimari-4b released" or "kimari 4b released" as standalone claims
                if "released" in line_lower and "kimari" in line_lower and "4b" in line_lower:
                    # Allow mentions of "no weights released", "not released", "not yet released"
                    if any(phrase in line_lower for phrase in (
                        "not released",
                        "no weights released",
                        "not yet released",
                        "no public release",
                        "no weights. no public release",
                        "when kimari-4b is released",
                        "is released —",
                    )):
                        continue
                    pytest.fail(f"{fname} contains potential false release claim: {line.strip()}")

    def test_benchmark_json_not_kimari4b_benchmark(self):
        """Benchmark JSON does not claim to be a Kimari-4B benchmark."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark JSON not found")
        data = json.loads(path.read_text())
        assert data.get("kimari4b") is False, "Must not claim to be a Kimari-4B result"
        assert data.get("public_claim_allowed") == "limited", "public_claim_allowed must be limited"
