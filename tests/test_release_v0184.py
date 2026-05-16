"""Release validation tests for v0.1.84-alpha: truth/security polish."""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

VERSION = "0.1.84-alpha"


class TestModelCardV0184:
    """MODEL_CARD.md must be coherent with current project state."""

    def test_model_card_version_is_current(self):
        text = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        assert VERSION in text, f"MODEL_CARD.md must reference {VERSION}"

    def test_model_card_date_not_in_future(self):
        from datetime import date

        text = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        match = re.search(r"Last Updated.*?(\d{4}-\d{2}-\d{2})", text)
        assert match, "MODEL_CARD.md must have Last Updated date"
        doc_date = date.fromisoformat(match.group(1))
        assert doc_date <= date.today(), f"Date {match.group(1)} is in the future"

    def test_model_card_no_stale_version_refs(self):
        text = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        stale = ["v0.1.23-alpha", "v0.1.22-alpha", "v0.1.21-alpha"]
        for s in stale:
            assert s not in text, f"Stale version {s} found in MODEL_CARD.md"

    def test_model_card_no_training_not_started(self):
        text = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        assert "has not been trained" not in text, "Stale 'has not been trained' claim"
        assert "training has not begun" not in text, "Stale 'training has not begun' claim"


class TestModelLicensesV0184:
    """MODEL_LICENSES.md must be coherent with current project state."""

    def test_model_licenses_no_stale_version(self):
        text = (PROJECT_ROOT / "MODEL_LICENSES.md").read_text()
        assert "v0.1.17-alpha" not in text, "Stale v0.1.17-alpha reference"

    def test_model_licenses_no_base_model_not_selected(self):
        text = (PROJECT_ROOT / "MODEL_LICENSES.md").read_text().lower()
        assert "no base model has been selected" not in text, 'Stale "no base model selected"'

    def test_model_licenses_has_private_sft_context(self):
        text = (PROJECT_ROOT / "MODEL_LICENSES.md").read_text()
        assert "private" in text.lower() or "SmolLM3" in text, "Should mention private SFT context"


class TestModelRegistryV0184:
    """Model registry: no recommended with null sha256, no id 'recommended'."""

    @staticmethod
    def _load_registry(path):
        return json.loads(path.read_text())

    def test_no_recommended_with_null_sha256(self):
        for parent in [PROJECT_ROOT / "config", PROJECT_ROOT / "kimari" / "defaults"]:
            path = parent / "kimari.models.json"
            if path.exists():
                models = self._load_registry(path)
                for m in models.get("models", []):
                    if m.get("status") == "recommended":
                        assert m.get("sha256") is not None, f"Model {m['id']} recommended but sha256 null"

    def test_no_model_id_named_recommended(self):
        for parent in [PROJECT_ROOT / "config", PROJECT_ROOT / "kimari" / "defaults"]:
            path = parent / "kimari.models.json"
            if path.exists():
                models = self._load_registry(path)
                for m in models.get("models", []):
                    assert m.get("id") != "recommended", 'Confusing id "recommended"; use specific model id'


class TestChangeLogV0184:
    """CHANGELOG must have v0.1.84-alpha entry."""

    def test_changelog_has_v0184(self):
        text = (PROJECT_ROOT / "CHANGELOG.md").read_text()
        assert "[0.1.84-alpha]" in text, "CHANGELOG.md missing [0.1.84-alpha]"


class TestVersionsV0184:
    """Version consistency."""

    def test_pyproject_version(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert VERSION in text, f"pyproject.toml must contain {VERSION}"

    def test_init_version(self):
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert VERSION in text, f"kimari/__init__.py must contain {VERSION}"

    def test_gate_blocked(self):
        gate = (PROJECT_ROOT / "docs" / "KIMARI4B_RELEASE_GATE.md").read_text()
        assert "BLOCKED" in gate, "Release gate must remain BLOCKED"
