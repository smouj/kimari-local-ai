#!/usr/bin/env python3
"""Check state consistency across all Kimari public-facing files."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def read_version():
    pyproject = (ROOT / "pyproject.toml").read_text()
    m = re.search(r'version\s*=\s*"([^"]+)"', pyproject)
    return m.group(1) if m else None


def main():
    version = read_version()
    if not version:
        print("ERROR: Cannot find version in pyproject.toml")
        sys.exit(1)

    version_v = f"v{version}"
    errors = []
    ok = []

    # 1. pyproject.toml == __init__.py
    init_version = re.search(
        r'__version__\s*=\s*"([^"]+)"',
        (ROOT / "kimari" / "__init__.py").read_text(),
    )
    if init_version and init_version.group(1) == version:
        ok.append(f"pyproject.toml == __init__.py: {version} ✓")
    else:
        init_ver = init_version.group(1) if init_version else "???"
        errors.append(f"pyproject.toml ({version}) != __init__.py ({init_ver})")

    # 2. README version
    readme = (ROOT / "README.md").read_text()
    if version_v in readme or version in readme:
        ok.append("README version ✓")
    else:
        errors.append(f"README does not contain {version_v} or {version}")

    # 3. docs/index.html version
    index = (ROOT / "docs" / "index.html").read_text()
    if version_v in index:
        ok.append("docs/index.html version ✓")
    else:
        errors.append(f"docs/index.html does not contain {version_v}")

    # 4. HF org card version
    org_card = (ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    if version_v in org_card or version in org_card:
        ok.append("HF org card version ✓")
    else:
        errors.append(f"HF org card does not contain {version_v}")

    # 5. Deployment status version
    deploy = (ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    if version_v in deploy or version in deploy:
        ok.append("Deployment status version ✓")
    else:
        errors.append(f"Deployment status does not contain {version_v}")

    # 6. No "ephemeral vs persisted" contradiction without run history
    run_history = ROOT / "docs" / "KIMARI4B_RUN_HISTORY.md"
    if run_history.exists():
        ok.append("KIMARI4B_RUN_HISTORY.md exists ✓")
    else:
        errors.append("KIMARI4B_RUN_HISTORY.md missing")

    # 7. Environment status exists
    env_status = ROOT / "docs" / "ENVIRONMENT_STATUS.md"
    if env_status.exists():
        ok.append("ENVIRONMENT_STATUS.md exists ✓")
    else:
        errors.append("ENVIRONMENT_STATUS.md missing")

    # 8. Gate BLOCKED
    gate_files = [org_card, deploy, index]
    gate_ok = all("BLOCKED" in f.upper() for f in gate_files)
    if gate_ok:
        ok.append("Gate BLOCKED in all public docs ✓")
    else:
        errors.append("Gate BLOCKED missing from some public docs")

    # 9. Kimari-4B not released
    release_files = [readme, org_card, index]
    not_released = any("not released" in f.lower() or "Not Released" in f for f in release_files)
    if not_released:
        ok.append("Kimari-4B 'not released' claim present ✓")
    else:
        errors.append("Kimari-4B 'not released' claim missing from public docs")

    # 10. No public weights/adapters/GGUF claim
    no_weights = all("no public weights" in f.lower() or "not released" in f.lower() for f in [org_card, deploy])
    if no_weights:
        ok.append("No public weights claim in HF docs ✓")
    else:
        errors.append("Missing 'no public weights' claim in HF docs")

    # 11. Profile doc exists
    profile = ROOT / "docs" / "HUGGINGFACE_PROFILE_SMOUJ013.md"
    if profile.exists():
        ok.append("HUGGINGFACE_PROFILE_SMOUJ013.md exists ✓")
    else:
        errors.append("HUGGINGFACE_PROFILE_SMOUJ013.md missing")

    # 12. No stale "v0.1.39 as current" in index.html
    if "v0.1.39" in index and "terminal-highlight" in index:
        errors.append("Stale v0.1.39 appears as highlighted in index.html")
    else:
        ok.append("No stale version highlighted in index.html ✓")

    print(f"\nState consistency check for {version_v}")
    print("=" * 50)
    print("\n".join(ok))
    if errors:
        print("\nERRORS:")
        print("\n".join(f"  - {e}" for e in errors))
        sys.exit(1)
    else:
        print(f"\nState consistency: OK ({version_v})")
        sys.exit(0)


if __name__ == "__main__":
    main()
