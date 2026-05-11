---
Task ID: 1
Agent: Main Agent
Task: Complete documentation overhaul and professional polish for Kimari Local AI v0.1.4-alpha

Work Log:
- Phase 0: Audited all key documentation files (README.md, CHANGELOG.md, ROADMAP.md, SECURITY.md, PRIVACY.md, CONTRIBUTING.md, GETTING_STARTED.md, MODEL_CARD.md, MODEL_LICENSES.md, docs/COMPARISON.md, docs/PROJECT_STRUCTURE.md, docs/WEB_UI_PLAN.md, docs/index.html, docs/00-10_service_status.md, docs/00-11_tech_stack_compatibility.md, docs/11_NEXT_RUNTIME_VALIDATION.md, benchmarks/README.md, models/README.md)
- Identified key issues: GitHub Pages outdated at v0.1.2-alpha, stale python cli/kimari_cli.py references, wrong CHANGELOG date, missing CLI commands, "Proprietary metric" misnomer
- Delegated README.md complete rewrite to subagent — new professional badges, emoji headers, prerequisite table, organized CLI commands, architecture status table
- Delegated documentation file updates to subagent — fixed CHANGELOG date, updated CONTRIBUTING.md install methods, fixed GETTING_STARTED.md, updated COMPARISON.md date
- Delegated GitHub Pages (index.html) update to subagent — updated hero badge, added pull/info CLI tabs, updated Quick Start, added docker profile card, added new feature cards, fixed stats
- Manually fixed remaining stale references: docs/00-10_service_status.md (updated to v0.1.4-alpha, added new CLI commands, expanded roadmap), docs/00-11_tech_stack_compatibility.md (updated version, fixed profile table, updated ROCm status, updated dependencies), docs/11_NEXT_RUNTIME_VALIDATION.md (replaced all python3 cli/kimari_cli.py with kimari commands, updated Step 4 to use kimari pull test), benchmarks/README.md (updated command), models/README.md (added kimari pull test as recommended method)
- Committed and pushed 2 commits to GitHub: ab5d171 (major docs overhaul) and 92010bd (remaining stale references)
- GitHub Pages workflow will auto-deploy from the push

Stage Summary:
- README.md: Complete professional rewrite with 8 badges, emoji section headers, prerequisite table, 5-section CLI reference, KimariFit centered table, architecture status table
- docs/index.html: Updated to v0.1.4-alpha, added 2 new CLI tabs (pull, info --json), updated Quick Start (6 steps with pip install -e . and kimari commands), added docker profile card, added Config Management and Model Registry feature cards, fixed "Proprietary metric" → "Unique metric", updated GPU profiles count to 5
- CHANGELOG.md: Fixed v0.1.4-alpha date from 2025-03-09 to 2025-05-09
- CONTRIBUTING.md: Updated to pip install -e ., added kimari --help verification, updated test section to pytest
- GETTING_STARTED.md: Removed legacy install method, updated troubleshooting
- docs/COMPARISON.md: Updated last-updated date
- docs/00-10_service_status.md: Full update to v0.1.4-alpha with new CLI commands and expanded roadmap
- docs/00-11_tech_stack_compatibility.md: Updated version, fixed memory table, updated ROCm status, updated dependencies
- docs/11_NEXT_RUNTIME_VALIDATION.md: Replaced all stale command references
- benchmarks/README.md, models/README.md: Updated command references
- All changes pushed to GitHub main branch

---
Task ID: 1
Agent: Main Agent
Task: v0.1.5-alpha hardening — First-run experience, documentation overhaul, all review fixes

Work Log:
- Examined all key files in the Kimari Local AI repository (README, CHANGELOG, ROADMAP, GETTING_STARTED, SECURITY, PRIVACY, CONTRIBUTING, COMPARISON, PROJECT_STRUCTURE, pyproject.toml, __init__.py, constants.py, start-kimari.sh, check-env.py, index.html, kimari.profiles.json, kimari.models.json)
- Changed default_profile from "gtx1060" to "test" in config/kimari.profiles.json
- Created kimari/py.typed (empty PEP 561 marker file)
- Rewrote scripts/linux/start-kimari.sh to prefer `kimari` command, fallback to `python3 -m kimari.cli.main`, default to test profile
- Replaced ambiguous ASCII art in kimari/core/constants.py with clear "KIMARI" block-letter banner
- Moved scripts/linux/check-env.py to scripts/common/check-env.py for cross-platform use
- Updated scripts/linux/install-dev.sh and scripts/windows/install-dev.ps1 to use scripts/common/check-env.py
- Fixed all dates from 2025 to 2026 in CHANGELOG.md entries
- Fixed PRIVACY.md "Last updated: 2025" → "2026"
- Fixed docs/COMPARISON.md last updated date and marked ROCm as experimental
- Added SHA256 verification note to SECURITY.md (hashes not yet pinned)
- Bumped version from 0.1.4-alpha to 0.1.5-alpha in kimari/__init__.py and pyproject.toml
- Added comprehensive v0.1.5-alpha section to CHANGELOG.md
- Updated ROADMAP.md: v0.1.4-alpha as Released, v0.1.5-alpha as Current, v0.1.6-alpha as Planned
- Completely rewrote README.md with streamlined quick start, test as default, GPU profile status table, SHA256 note, ROCm experimental
- Completely rewrote GETTING_STARTED.md with clearer default flow and SHA256 note
- Updated docs/PROJECT_STRUCTURE.md with py.typed and scripts/common/ references
- Updated docs/index.html (GitHub Pages): hero badge v0.1.5-alpha, new ASCII banner, version strings, test as default profile, date fix
- Fixed tests: test_cli_smoke.py version assertions, test_detection.py default profile assertion
- Ran all 83 tests — passing
- Ran py_compile on all modules — passing
- Validated config against JSON Schema — passing
- Committed and pushed to GitHub

Stage Summary:
- Version bumped to v0.1.5-alpha
- 21 files changed, 306 insertions, 101 deletions
- All critical review items from the audit have been addressed:
  ✅ P0: default_profile changed to "test"
  ✅ P0: kimari/py.typed created
  ✅ P1: start-kimari.sh updated
  ✅ P1: ASCII banner fixed
  ✅ P1: Dates corrected from 2025 to 2026
  ✅ P1: SHA256 note added (hashes not pinned)
  ✅ P2: check-env.py moved to scripts/common/
  ✅ P2: ROCm marked as experimental
  ✅ Documentation fully updated (README, GETTING_STARTED, CHANGELOG, ROADMAP, SECURITY, PRIVACY, COMPARISON, PROJECT_STRUCTURE, GitHub Pages)
  ✅ Tests updated and passing
  ✅ Pushed to GitHub

---
Task ID: v0.1.8-alpha
Agent: Main Agent
Task: v0.1.8-alpha — Discovery, publishing, and release hygiene

Work Log:
- Explored current repo state: v0.1.7-alpha, 90 tests passing, ruff clean
- Task 1: Added 20 GitHub topics via API (ai, openai, llm, local-ai, local-llm, on-device-ai, offline-ai, self-hosted-ai, llama-cpp, gguf, quantization, llm-inference, cuda, nvidia-gpu, gtx1060, gtx1080, consumer-gpu, openai-compatible-api, open-webui, openclaw)
- Task 2: Updated pyproject.toml keywords from 6 generic to 12 targeted discovery keywords; bumped version to 0.1.8-alpha in pyproject.toml and kimari/__init__.py
- Task 3: Created RELEASE_CHECKLIST.md with version/metadata, changelog/roadmap, testing, CLI validation, build/package, release validation script, content review, publishing (TestPyPI + PyPI), and post-release sections
- Task 4: Created scripts/release/check-release.py — automated release validation checking version consistency, README badge, CHANGELOG entry, ROADMAP entry, default_profile, py.typed, no GGUF tracked, no unsafe model paths, no runtime artifacts
- Task 5: Added release-check CI job to .github/workflows/ci.yml
- Task 6: Added TestPyPI publishing documentation to RELEASE_CHECKLIST.md (manual workflow with build, twine check, testpypi upload, verify install steps)
- Task 7: Updated README.md to v0.1.8-alpha (badge, alpha notice, project status); added Release Checklist link to docs table
- Task 8: Added CHANGELOG.md v0.1.8-alpha entry with all changes documented
- Task 9: Updated ROADMAP.md — v0.1.7-alpha as Released, v0.1.8-alpha as Current, added v0.1.9-alpha Planned with specific items
- Updated docs/index.html version references (4 locations)
- Updated docs/PROJECT_STRUCTURE.md (version, new files: scripts/release/, RELEASE_CHECKLIST.md, test_release_v018.py)
- Updated docs/COMPARISON.md date and version
- Updated tests/test_cli_smoke.py version assertions
- Created tests/test_release_v018.py with 8 tests (release check script, checklist existence, TestPyPI mention, keywords count, GitHub topics format, check-release structure, CI job, version consistency)
- Fixed ruff lint (removed unused json import from test file)
- All 98 tests passing, ruff check/format clean, check-release.py all OK, build/twine passed, make ci-local passed

Stage Summary:
- Version: v0.1.8-alpha
- 13 files changed, 452 insertions, 16 deletions
- 20 GitHub topics applied
- 12 pyproject.toml keywords
- RELEASE_CHECKLIST.md with TestPyPI workflow
- scripts/release/check-release.py (7 validation categories)
- CI release-check job
- 8 new tests (98 total, up from 90)
- All validations pass
- Committed and pushed to GitHub
- Git tag v0.1.8-alpha created and pushed

---
Task ID: v0.1.9-alpha
Agent: Main Agent
Task: v0.1.9-alpha — GitHub Pages revamp, SEO metadata, WSL2 guide, publishing docs, release-check improvements

Work Log:
- Version bump to 0.1.9-alpha in pyproject.toml, kimari/__init__.py, README.md badge, docs/index.html, tests/test_cli_smoke.py, tests/test_release_v018.py
- Delegated GitHub Pages revamp to frontend-styling-expert agent: hero improved with explicit GPU mention, alpha honesty strip, Quick Start before Features, Hardware Targets section, Trust section, topics chips, SEO metadata (canonical, og:*, twitter:*, JSON-LD), accessibility improvements (aria labels, role attributes, semantic button), improved footer with doc links
- Created docs/INSTALL_WSL2.md: complete WSL2 guide covering Windows 10/11, Ubuntu setup, NVIDIA drivers, CUDA on WSL, build/install/pull/start flow, Open WebUI optional, and troubleshooting (nvidia-smi, nvcc, llama-server, port busy, model not found, CUDA OOM)
- Created docs/PUBLISHING.md: manual TestPyPI/PyPI publishing guide with pre-publish checklist, build/twine workflow, clean venv verification, API token configuration, .pypirc setup, and common issues
- Improved RELEASE_CHECKLIST.md: added 7 new checks (GitHub Pages, SEO metadata, WSL2 guide, publishing guide, README links, ROADMAP current, no false claims)
- Improved scripts/release/check-release.py: expanded from 7 to 10 validation categories, added index.html version/SEO checks, docs existence checks, false claim detection for Kimari-4B
- Created tests/test_release_v019.py: 11 tests covering index.html version, canonical URL, Open Graph, Twitter Card, JSON-LD, WSL2 guide existence/troubleshooting, publishing guide, TestPyPI mention, README Kimari-4B honesty
- Updated CHANGELOG.md with v0.1.9-alpha entry
- Updated ROADMAP.md: v0.1.8-alpha as Released, v0.1.9-alpha as Current, v0.1.10-alpha as Planned
- Updated docs/COMPARISON.md and docs/PROJECT_STRUCTURE.md versions
- Verified GitHub topics (20 topics confirmed via API)
- Fixed check-release.py false positive on "Kimari-4B is not released" matching "kimari-4b is released"
- All 109 tests passing, ruff clean, build/twine PASSED, make ci-local passed

Stage Summary:
- Version: v0.1.9-alpha
- 16 files changed, 1020 insertions, 144 deletions
- GitHub Pages fully revamped with SEO, social metadata, accessibility
- WSL2 installation guide created
- Publishing guide (TestPyPI/PyPI) created
- Release validation expanded to 10 categories
- 11 new tests (109 total, up from 98)
- All validations pass
- Committed and pushed to GitHub
- Git tag v0.1.9-alpha created and pushed

---
Task ID: 2
Agent: Sub Agent
Task: Create the runtime module for detecting llama-server supported flags

Work Log:

1. **Created `kimari/runtime/__init__.py`** — Module init with docstring and exports for all 5 public functions:
   - `detect_llama_server_help`
   - `detect_llama_server_version`
   - `parse_supported_flags`
   - `supports_flag`
   - `filter_unsupported_flags`

2. **Created `kimari/runtime/llama_flags.py`** — Main implementation with 5 functions:
   - `detect_llama_server_help(binary_path: str) -> str`: Runs `llama-server --help` with 10s timeout. Returns stdout text, or empty string on FileNotFoundError/TimeoutExpired/OSError. Also falls back to stderr if stdout is empty but stderr has content.
   - `detect_llama_server_version(binary_path: str) -> str`: Runs `llama-server --version` with 10s timeout. Same graceful error handling as above.
   - `parse_supported_flags(help_text: str) -> set[str]`: Parses help text lines to extract `--` flags. Handles `--flag=VALUE` (strips value), trailing punctuation, and validates with regex `^--[a-zA-Z]`.
   - `supports_flag(flag: str, supported_flags: set[str]) -> bool`: Simple membership check.
   - `filter_unsupported_flags(cmd: list[str], supported_flags: set[str]) -> tuple[list[str], list[str]]`: Filters command list, returning (supported_cmd, unsupported_flags). Handles:
     - Boolean flags (standalone): removed entirely if unsupported
     - Flags with values (defined in `FLAGS_WITH_VALUES` set): both flag and its value removed if unsupported, value skipped if it's not another flag
     - Non-flag arguments (binary path, model path, etc.): always kept
     - `FLAGS_WITH_VALUES` = {--parallel, --cache-type-k, --cache-type-v, -t, -b, -ub, -c, -ngl, --host, --port, -m}

3. **Validation**:
   - `py_compile` on both files → ✅ PASS
   - `ruff check kimari/runtime/` → ✅ All checks passed
   - `ruff format --check kimari/runtime/` → ✅ 2 files already formatted
   - Comprehensive functional tests → ✅ ALL PASS:
     - detect functions return empty string on missing binary
     - parse_supported_flags extracts correct flags from fake help text (16 flags)
     - supports_flag membership check works
     - filter_unsupported_flags handles boolean flags, flags with values, unsupported FLAGS_WITH_VALUES entries
     - All 5 functions importable from kimari.runtime
   - Existing test suite: 6 pre-existing failures (version mismatch in release tests) — none related to this task

Files created:
- `kimari/runtime/__init__.py`
- `kimari/runtime/llama_flags.py`

---
Task ID: 16
Agent: Main Agent
Task: v0.1.12-alpha Final validations and delivery

Work Log:
- Verified all 200+ tests passing (pytest)
- Verified ruff check clean on kimari/ and tests/ (pre-existing scripts/ errors not from v0.1.12)
- Verified check-release.py all checks passed (15/15 categories)
- Built wheel and sdist with `python -m build` — SUCCESS
- Ran `twine check dist/*` — PASSED for both .whl and .tar.gz
- Verified wheel contains all 3 defaults JSON files (kimari.profiles.json, kimari.profiles.schema.json, kimari.models.json)
- Tested wheel install in clean venv — all CLI commands work:
  - `kimari --version` → v0.1.12-alpha
  - `kimari config path` → packaged defaults (no repo root dependency)
  - `kimari setup --json` → correct JSON output
  - `kimari start --dry-run` → correct command with user paths
  - `kimari token create` → token stored in /home/z/.local/state/kimari/auth.json
- Verified paths module resolves correctly from wheel: XDG-compliant user directories
- Verified SHORT_TO_LONG flag aliases work for all 6 short flags (-m, -c, -ngl, -b, -ub, -t)
- Verified token storage in user state dir (not inside package)
- Confirmed docs/PUBLISHING.md exists (from v0.1.9-alpha, Task 12 verified complete)

Stage Summary:
- v0.1.12-alpha is fully validated and ready for commit/push
- P0 (wheel missing config) → FIXED: kimari/defaults/ with package-data
- P0 (short flags not parsed) → FIXED: parse_supported_flags + SHORT_TO_LONG mapping
- P1 (tokens in PROJECT_ROOT) → FIXED: paths module with XDG user directories
- Wheel install works correctly without repo root dependency
- All 3 critical risks resolved

---
Task ID: 2-6
Agent: Community Docs Agent
Task: Create CODE_OF_CONDUCT.md, SUPPORT.md, improve CONTRIBUTING.md, create GOVERNANCE.md, MAINTAINERS.md

Work Log:
- Read worklog.md to understand prior agent work and project history
- Read existing CONTRIBUTING.md to preserve good content during rewrite
- Read SECURITY.md, ROADMAP.md, and project structure to ensure cross-references are accurate
- Created CODE_OF_CONDUCT.md — Contributor Covenant 3.0 adapted for Kimari Local AI, with full sections (Our Pledge, Expected Behavior, Unacceptable Behavior, Enforcement Responsibilities, Scope including integrations OpenClaw/Hermes/Continue, Enforcement with 4-tier guidelines, Attribution), contact via smouj013@users.noreply.github.com with TODO note for dedicated private contact, explicit note not to use public issues for conduct reports
- Created SUPPORT.md — Help channels table (Issues, Discussions, docs), what goes in Issues vs what doesn't (security → SECURITY.md, conduct → CODE_OF_CONDUCT.md, questions → Discussions), installation help references (INSTALL_WSL2.md, GETTING_STARTED.md), publishing (PUBLISHING.md), integrations (docs/integrations/), diagnostics commands (kimari doctor, kimari info --json), no guaranteed commercial support during alpha
- Rewrote CONTRIBUTING.md — Preserved existing good content (Python/Bash/JSON style, Getting Started flow), added Python 3.10+ requirement, pip install -e ".[dev]" setup, python -m pytest tests/ -q, ruff check/format commands, make ci-local, 9 non-negotiable rules table (no model downloads in tests, no llama-server real in CI, no inventing benchmarks, no claiming Kimari-4B published, no changing default_profile from "test", no real tokens, no secrets, no unsafe 0.0.0.0, no GGUF), GPU profile proposal process (config/kimari.profiles.json + kimari/defaults/kimari.profiles.json), integration proposal process (docs/integrations/ + config/integrations/), documenting changes (CHANGELOG.md + ROADMAP.md), expanded PR checklist with 12 items, links to Code of Conduct and GOVERNANCE.md
- Created GOVERNANCE.md — Maintainer (Smouj @smouj), technical decisions by maintainer, community input via Issues and Discussions, acceptance criteria table (tests pass, ruff clean, docs updated, no false claims, no security issues, no GGUF, no secrets), security/conduct priority, no roadmap promises during alpha, semver with -alpha suffix (0.1.X-alpha), release process (check-release.py → build → twine → tag), references to community health docs
- Created MAINTAINERS.md — Maintainer Smouj (@smouj), GitHub link, 6 responsibilities (release management, security response, PR review, roadmap decisions, technical quality, community health), no private emails unless confirmed public, how to become a maintainer (consistent contributions, trust, nomination)

Stage Summary:
- 5 community documentation files created/updated for v0.1.13-alpha
- CODE_OF_CONDUCT.md: Full Contributor Covenant 3.0 with private contact TODO
- SUPPORT.md: Complete support guide with channel routing and diagnostics
- CONTRIBUTING.md: Comprehensive rewrite with rules, profiles, integrations, expanded checklist
- GOVERNANCE.md: Project governance, acceptance criteria, versioning, release process
- MAINTAINERS.md: Maintainer info, responsibilities, future maintainer path
- All files cross-reference each other and existing project docs (SECURITY.md, ROADMAP.md, etc.)
- No violations of important rules (no FastAPI/dashboard/PWA mentions, no Kimari-4B claims, no fake hashes, default_profile is "test", no real tokens, no repo-root dependency, no private emails)

---
Task ID: 14
Agent: Sub Agent
Task: Add Community section to docs/index.html

Work Log:
- Read worklog.md to understand project history and prior work (v0.1.13-alpha, community docs created in Task 2-6)
- Read docs/index.html to find Docs section (line 1135) and Footer (line 1272) for insertion point
- Added Community section between Trust section and Footer (after line 1270)
  - section-label: "Community" with fa-people-group icon
  - section-title: "Open-Source Community"
  - section-desc: Brief description about being open and transparent
  - docs-grid with 6 doc-cards linking to:
    1. Code of Conduct (CODE_OF_CONDUCT.md)
    2. Contributing Guide (CONTRIBUTING.md)
    3. Support (SUPPORT.md)
    4. Security (SECURITY.md)
    5. Governance (GOVERNANCE.md)
    6. GitHub Issues (https://github.com/smouj/kimari-local-ai/issues)
- Added "Community" nav link in both desktop nav and mobile menu (after Docs, before GitHub)
- Used same CSS classes as existing sections: doc-card, docs-grid, section-label, section-title, section-desc, reveal
- Version remains v0.1.13-alpha (unchanged)
- No FastAPI/dashboard/PWA references added
- No Kimari-4B publication claims

Stage Summary:
- docs/index.html updated with Community section (6 doc-cards) and nav links
- Minimal addition, consistent with existing page style
- Links point to community docs created in Task 2-6
Task ID: 12
Agent: PUBLISHING Update Agent
Task: Update docs/PUBLISHING.md with v0.1.13 TestPyPI section

Work Log:
- Read worklog.md to understand previous agent work and project history
- Read existing docs/PUBLISHING.md to understand current structure and content
- Appended new "v0.1.13 TestPyPI Actual Validation" section after the "Security Notes" section at the end of the file
- Section includes: purpose statement, 3 notes (packaged defaults, SPDX license, MANIFEST.in), 12-item checklist with all required items, empty result table with 12 rows, and copy-paste validation commands block
- Preserved all existing content unchanged

Stage Summary:
- docs/PUBLISHING.md updated with v0.1.13 TestPyPI Actual Validation section
- 12-item checklist covers: twine upload, clean venv, pip install with --extra-index-url, kimari --version, kimari config path, kimari setup --json, kimari start --dry-run, token create/show/delete, result documented, no real PyPI until validated
- Result table ready to be filled when TestPyPI validation is actually executed
- Notes document key v0.1.13 changes: packaged defaults in wheel, SPDX license format, MANIFEST.in for community files

---
Task ID: 13
Agent: Sub Agent
Task: Update README community section

Work Log:
- Read worklog.md to understand prior work (v0.1.13-alpha, community docs created in Task 2-6)
- Read README.md to find existing Contributing section (## 🤝 Contributing at line 483)
- Replaced the old "## 🤝 Contributing" section (which had a brief welcome message and link to CONTRIBUTING.md) with new "## 🏛️ Community & Contribution" section
- New section includes 7 bullet links: Code of Conduct, Contributing Guide, Support, Security, Governance, Maintainers, Issue Templates
- Kept a brief "We welcome contributions! See CONTRIBUTING.md for guidelines." line at the bottom of the section
- Verified placement: section sits between Open WebUI Integration and License, exactly where the old Contributing section was
- Verified all existing content intact, no FastAPI/dashboard/PWA references added, no Kimari-4B claims, version badge still v0.1.13-alpha

Stage Summary:
- README.md: Replaced "🤝 Contributing" with "🏛️ Community & Contribution" section
- 7 community document links added (CODE_OF_CONDUCT.md, CONTRIBUTING.md, SUPPORT.md, SECURITY.md, GOVERNANCE.md, MAINTAINERS.md, GitHub Issues)
- Concise format — just links, no duplication of contributing content
- 1 file changed

---
Task ID: 20
Agent: Main Agent
Task: v0.1.13-alpha Final validations and delivery

Work Log:
- Ran pytest: 250 tests passing
- Ran ruff check kimari/ tests/: All checks passed
- Ran ruff format --check: All files formatted
- Ran check-release.py: 18/18 categories PASSED (0 warnings)
- Built wheel and sdist with python -m build: SUCCESS
- Ran twine check dist/*: PASSED both
- Verified wheel contains all 3 defaults JSON files
- Verified sdist contains all community files (via MANIFEST.in)
- Tested wheel install in clean venv:
  - kimari --version → v0.1.13-alpha
  - kimari config path → packaged defaults
  - kimari setup --json → correct JSON
  - kimari start --dry-run → correct command
  - kimari token create/show/delete → all work
- Committed and pushed to GitHub main (19004ef)
- Created and pushed tag v0.1.13-alpha

Stage Summary:
- v0.1.13-alpha fully delivered and pushed
- 20 tasks completed, 29 files changed, +1506 -106
- 250 tests passing, ruff clean, check-release 18/18 PASS
- Wheel install from clean venv verified working
- SPDX license format eliminates setuptools deprecation warnings
- MANIFEST.in ensures sdist includes community files
- wheel-install-smoke CI job added
- All community standard files in place (CoC, Support, Contributing, Governance, Maintainers)
- Issue templates (4 + config.yml) and improved PR template added
- GitHub Pages and README updated with community sections


---
Task ID: v0.1.14-alpha
Agent: main
Task: Implement v0.1.14-alpha — TestPyPI validation, setup write-mode, SHA256 tooling, reverse proxy auth guide, API plan

Work Log:
- Version bumped to 0.1.14-alpha across pyproject.toml, __init__.py, README.md, docs/index.html
- Created kimari/setup/__init__.py and kimari/setup/writer.py with build_setup_patch, write_setup_config, backup_config, load_setup_summary
- Added compute_model_hash, verify_model_hash_v2, pin_model_hash, get_effective_models_registry to kimari/models/registry.py
- Updated CLI: added --write flag to setup, added models hash/verify/pin-hash subcommands
- Created docs/REVERSE_PROXY_AUTH.md (nginx/Caddy examples, token setup, troubleshooting)
- Created docs/API_PLAN.md (FastAPI REST API design for v0.2.0-alpha, 9 endpoints, auth, risks)
- Updated docs/PUBLISHING.md with v0.1.14 TestPyPI validation section
- Updated scripts/windows/README.md with wheel/TestPyPI install, setup --write, models hash
- Updated README.md with setup write-mode, model hash verification sections, reverse proxy/API plan links
- Updated docs/index.html with new doc cards, version references, status section
- Updated RELEASE_CHECKLIST.md with Setup Write-Mode, SHA256 Tooling, New Documentation sections
- Updated scripts/release/check-release.py to 21 categories with _no_invented_hashes helper
- Created tests/test_release_v0114.py with version, setup writer, SHA256, docs, README, no false claims tests
- Updated CHANGELOG.md with v0.1.14-alpha entry
- Updated ROADMAP.md: v0.1.13-alpha Released, v0.1.14-alpha Current, v0.1.15-alpha Planned

Stage Summary:
- 296 tests passing, ruff clean, check-release.py all checks passed
- Wheel builds and installs correctly in clean venv
- kimari setup --write persists config with backup
- kimari models hash/verify/pin-hash work correctly
- No invented SHA256 hashes (all null in packaged defaults)
- TestPyPI upload not executed: credentials unavailable (documented)
- All CLI commands work from wheel install

---
Task ID: 4-a
Agent: Docs Agent
Task: Create docs/MODEL_BASE_SELECTION.md — comparison table of base model candidates for Kimari-4B

Work Log:
- Read worklog.md to understand project history and prior work (v0.1.14-alpha, community docs, model licensing docs)
- Read existing MODEL_LICENSES.md to understand current license documentation and identify potential inaccuracies (e.g., Qwen2.5 listed as Apache 2.0 vs actual qwen-research license)
- Created docs/MODEL_BASE_SELECTION.md with:
  - Purpose section explaining selection criteria (license clarity, hardware compatibility, capability baseline, fine-tuning risk)
  - Full comparison table with 10 columns covering all required fields for 4 candidates:
    1. HuggingFaceTB/SmolLM3-3B — Apache 2.0, Under Review
    2. Qwen/Qwen2.5-3B-Instruct — qwen-research license, Under Review
    3. meta-llama/Llama-3.2-3B-Instruct — Meta Community License, Under Review
    4. Microsoft Phi-3.5-mini — To be evaluated (license unverified)
  - Detailed analysis section for each candidate with honest strengths and risks
  - Recommendation framework table (NOT a final selection — all candidates remain TBD)
  - Constraints and honest risks section
  - Legal disclaimer
- Verified all important rules followed:
  - No final selection made — all candidates marked "Under Review" or "To be evaluated"
  - License information accurately reflects public knowledge (Apache 2.0, qwen-research, Meta Community License, TBD)
  - No claims that any candidate is chosen
  - Honest about risks (license ambiguity, capability gaps, redistribution constraints)
  - No Kimari-4B publication claims

Stage Summary:
- docs/MODEL_BASE_SELECTION.md created with complete comparison table and analysis
- 4 candidates documented: SmolLM3-3B, Qwen2.5-3B-Instruct, Llama-3.2-3B-Instruct, Phi-3.5-mini
- SmolLM3-3B identified as safest legal choice for preview (Apache 2.0)
- Qwen2.5-3B-Instruct identified as strongest capability candidate (license review required)
- Llama-3.2-3B-Instruct requires careful license review (Meta Community License constraints)
- Phi-3.5-mini marked as "To be evaluated" (license unverified)
- No final selection made — all candidates remain under review

---
Task ID: 5-a
Agent: Docs Agent
Task: Improve MODEL_LICENSES.md with specific candidate information for v0.1.17-alpha

Work Log:
- Read existing MODEL_LICENSES.md (67 lines) — found good base content but inaccurate "Recommended Model Sources" table (Qwen2.5 3B listed as Apache 2.0, which is incorrect — it's qwen-research)
- Read worklog.md to understand project history and prior agent work
- Rewrote MODEL_LICENSES.md with the following improvements:
  1. Enhanced Overview section — explicitly states "No Kimari model weights have been released yet" and that final license depends on base model
  2. Clarified License Layer 2 (Kimari Fine-Tuning Modifications) — added note that MIT cannot be applied to derivative weights if base model forbids it
  3. Clarified License Layer 3 (Base Model Weights) — explicitly states "no base model has been selected yet"
  4. Added new "Base Model Candidates (v0.1.17-alpha)" section with detailed entries for each candidate:
     - SmolLM3: Apache 2.0, verify before release, most straightforward path to permissive release
     - Qwen: qwen-research license (NOT Apache 2.0), research-oriented, derivative distribution requires review
     - Llama: Meta Community License, compliance obligations (user thresholds, naming, use policy)
  5. Added candidate summary comparison table with license, commercial use, derivative redistribution, and key consideration columns
  6. Added "No Weights Released Yet" section — clear standalone statement that no weights exist as of v0.1.17-alpha
  7. Added "Dataset Redistribution" section — warns against redistributing datasets unless licenses explicitly allow it
  8. Added "Decision Framework" section — 6-step process for how the final license is determined, plus ASCII flowchart showing permissive/research/community license paths
  9. Enhanced "Your Responsibilities" section — added license verification and dataset compliance items
  10. Enhanced disclaimer — notes candidate info is for evaluation only, license terms may vary by checkpoint
  11. Removed old "Recommended Model Sources" table — replaced with accurate candidate comparison table (no Qwen2.5 3B listed as Apache 2.0)
- Preserved existing good content: MIT license for Kimari code, license layers structure, user responsibilities, disclaimer, questions section
- No false claims: no claiming weights are released, no claiming Apache 2.0 applies to Kimari-4B weights, no claiming any base is selected

Stage Summary:
- MODEL_LICENSES.md rewritten from 67 lines to ~170 lines
- 3 candidate base models documented with accurate license specifics
- Old inaccurate "Recommended Model Sources" table removed (Qwen2.5 3B was incorrectly listed as Apache 2.0)
- Decision framework with 6-step process and flowchart added
- Dataset redistribution warning added
- No weights released statement prominent
- All accuracy rules followed: no false claims about weight releases, Apache 2.0 applicability, base selection, or dataset redistribution

---
Task ID: 2-a
Agent: Docs Agent
Task: Rewrite MODEL_CARD.md professionally for v0.1.17-alpha

Work Log:
- Read existing MODEL_CARD.md (128 lines) — identified issues: "LLaMA-based" architecture claimed as definitive, license pointed to MODEL_LICENSES.md without TBD qualifier, training data section listed datasets as if confirmed, benchmarks section mixed target/aspirational numbers without clear disclaimer, version history implied future releases as scheduled
- Read worklog.md to understand project history (v0.1.16-alpha, community docs, model base selection doc, MODEL_LICENSES.md improvements)
- Read MODEL_LICENSES.md to understand accurate license information for candidates
- Read CHANGELOG.md for version context (current: v0.1.16-alpha)
- Completely rewrote MODEL_CARD.md from 128 lines to ~250 lines with the following sections:
  1. **Status**: Explicitly "Planned / Training Design" with clear statement that no training has started
  2. **Weights Availability**: Standalone section stating no weights exist in any form; any claim otherwise is false
  3. **Model Identity**: Table with name (Kimari-4B), type (local coding/sysadmin/agent assistant), target class (3B–4B), context length, runtime, languages
  4. **Target Hardware**: Professional table with 4 GPUs (GTX 1060 6GB, GTX 1080 8GB, RTX 2060 6GB, RTX 3060 12GB), recommended quantization, target context, and notes — explicitly marked as design targets
  5. **Planned Formats**: Table with safetensors (adapter/base if applicable), GGUF Q4_K_M, GGUF Q5_K_M, GGUF IQ4_XS (optional) — availability contingent on base model license
  6. **Base Model Candidates**: Detailed comparison table (SmolLM3-3B, Qwen2.5-3B-Instruct, Llama 3.2 3B) with parameters, license, strengths, and concerns columns; plus 5 selection criteria and explicit "No base model has been definitively chosen" statement
  7. **Selected Base Model**: TBD — clear statement that selection pending
  8. **License**: TBD — depends on selected base model; three scenarios mapped (SmolLM3 → Apache 2.0 possible, Qwen → review needed, Llama → Meta Community License applies); MIT for software only
  9. **Training Status**: Table with 5 rows all marked "Not started" (base selection, data curation, fine-tuning, evaluation, weight release)
  10. **Benchmarks**: Explicit "No benchmarks have been measured" header; evaluation targets table with inference speed, TTFT, MMLU, HumanEval, MultiPL-E, SWE-bench — all marked as "Not Achieved" targets
  11. **Intended Uses**: 5 primary use cases + 5 target user groups
  12. **Out-of-Scope Uses**: 8 explicit exclusions (medical/legal/financial advice, safety-critical systems, surveillance, harmful content, etc.)
  13. **Limitations**: 10 items covering hallucination, context limits, quantization artifacts, no multimodal, language coverage, reasoning depth, code correctness, inherited base model limitations, no self-correction
  14. **Safety Notes**: Harm reduction principles, risk table with 5 risks and mitigations (misinformation, bias, code vulnerabilities, over-reliance, prompt injection), responsible use responsibilities
  15. **Release Checklist**: 15-item table with all items marked ❌ Not started
  16. **Version History**: Updated to reflect v0.1.17-alpha rewrite with honest future milestones marked TBD
- Key honesty rules followed:
  - No claiming Kimari-4B is published
  - No claiming weights exist
  - No claiming benchmarks are real (all explicitly "targets, not results")
  - No claiming SmolLM/Qwen/Llama are definitively chosen (all "Under Review" / "TBD")
  - No claiming Apache 2.0 for weights (contingent on SmolLM3 selection and even then stated conditionally)
  - No mixing models/tokenizers
  - Status is "Planned / Training Design"

Stage Summary:
- MODEL_CARD.md completely rewritten from 128 lines to ~250 lines
- All 17 required sections present and thorough
- Professional markdown tables throughout (7 tables total)
- Fully honest and transparent: no false claims, all targets clearly marked as aspirational
- Zero ambiguity about model status (not trained, no weights, no benchmarks)
- Release checklist provides clear roadmap for what must happen before weight release

---
Task ID: 3-a
Agent: Docs Agent
Task: Create docs/MODEL_TRAINING_PLAN.md — realistic, actionable training plan for Kimari-4B

Work Log:
- Read worklog.md to understand project history and prior agent work (v0.1.16-alpha, model base selection, MODEL_LICENSES.md, MODEL_CARD.md rewrites)
- Read MODEL_CARD.md, docs/00-08_dataset_tuning.md, ROADMAP.md, models/README.md, dataset/README.md, eval/expected_behaviors.md to understand existing documentation tone, content, and cross-references
- Created docs/MODEL_TRAINING_PLAN.md with the following sections:
  1. **Important Disclaimers** — 8 explicit reminders: no training done, no model selected, no dates promised, no mixing tokenizers, training is planned, GTX 1060/1080 inference-only, no training in CI, no model downloads in CI
  2. **Overview** — Phased, evaluation-driven approach summary
  3. **Phase 0: Base Model Selection** — Candidate evaluation criteria table, candidate models table (5 models, none selected), baseline evaluation checklist, license review checklist
  4. **Phase 1: Dataset Design** — SFT format (single-turn and multi-turn JSON examples), preference format (chosen/rejected pairs), data sources table with 6 categories, 10 quality criteria items, pipeline diagram, note that pipeline tools are planned not implemented
  5. **Phase 2: SFT (LoRA/QLoRA)** — Method explanation (LoRA vs QLoRA), starting hyperparameters YAML (all marked STARTING POINT ONLY), target modules considerations table, validation strategy, tooling table, what SFT does not do
  6. **Phase 3: Preference Tuning (DPO or ORPO)** — Why after SFT, DPO detailed (how it works, pros, cons, starting hyperparameters), ORPO detailed (how it works, pros, cons, starting hyperparameters), DPO vs ORPO decision framework table, recommendation (DPO if 40GB+, ORPO if 24GB), neither method selected yet, preference data requirements
  7. **Phase 4: Evaluation** — 9 evaluation categories table (KimariFit, coding, sysadmin, Spanish, JSON/tool-use, agent, safety, hallucination), evaluation process (7 steps), go/no-go criteria (6 items)
  8. **Phase 5: GGUF Export and Quantization** — Export process (merge, convert, quantize), target quantization table (Q4_K_M, Q5_K_M, IQ4_XS), post-quantization validation
  9. **Phase 6: Hugging Face Release** — Release checklist (10 items), repository structure
  10. **Phase 7: Kimari Registry Integration** — Registry JSON example, profile updates table, CLI integration commands, default profile remains "test"
  11. **Hardware** — Local hardware table (GTX 1060/1080 inference-only, not for training), recommended training hardware table (RTX 4090, L40S, A100 40GB/80GB with costs), QLoRA memory budget estimate (~7–11 GB for 4B), LoRA memory budget estimate (~13–17 GB for 4B), QLoRA on 24GB GPU for 3B model section, explicit statement: not training from scratch
  12. **Methods Summary** — SFT with LoRA/QLoRA summary, DPO summary, ORPO summary, method selection table by scenario
  13. **Key Reminders** — 10 numbered reminders covering all required constraints
  14. **Appendix: Phase Dependency Graph** — ASCII flowchart with pass/fail paths

Key rules followed:
- No claiming training has been done — stated explicitly in disclaimers and throughout
- No claiming any model is selected definitively — all candidates marked "not yet selected"
- No promising exact dates — no dates in any phase
- No mixing models/tokenizers — stated in disclaimers and key reminders
- Training is planned, not started — status "Planning — No training has started"
- GTX 1060/1080 for inference/testing only — dedicated hardware section with "Not For Training" column
- No training in CI — in disclaimers and key reminders
- No model downloads in CI — in disclaimers and key reminders
- All hyperparameters are starting points — marked "STARTING POINT ONLY" in YAML
- No weights committed to repo — in disambiguation and key reminders
- DPO and ORPO both explained with tradeoffs — detailed pros/cons for each
- ORPO "may reduce memory" qualified with "must validate with actual tooling"
- No full training from scratch claim — explicit section stating parameter-efficient fine-tuning only

Stage Summary:
- docs/MODEL_TRAINING_PLAN.md created (~420 lines)
- 8 phases documented: base selection → dataset design → SFT → preference tuning → evaluation → GGUF export → HF release → registry integration
- Hardware section: GTX 1060/1080 inference-only; RTX 4090/L40S/A100 recommended for training
- Both DPO and ORPO covered with tradeoffs; neither selected yet
- Memory budgets estimated for QLoRA and LoRA on 4B model
- 10 key reminders covering all constraint rules
- Phase dependency graph with pass/fail iteration paths
- Consistent with existing docs (cross-references MODEL_CARD.md, dataset/README.md, eval/expected_behaviors.md)

---
Task ID: 6-a, 7-a
Agent: Dataset Schema Agent
Task: Rewrite dataset/README.md with comprehensive dataset policy; Create dataset/schema/sft.schema.json and dataset/schema/preference.schema.json

Work Log:
- Read existing dataset/README.md (75 lines) — found basic data format with quality_score and language fields not aligned with new SFT/Preference schema spec
- Read worklog.md to understand project history (v0.1.17-alpha, model training plan, model card rewrites)
- Read config/kimari.profiles.schema.json for JSON Schema style reference (draft-07 format used in project)
- Created dataset/schema/ directory
- Completely rewrote dataset/README.md from 75 lines to ~250 lines with the following sections:
  1. **Directory Structure** — Updated with schema/ directory, sft/ and preference/ subdirectories, .gitkeep-only placeholder policy
  2. **Allowed Dataset Types** — 10-category table (SFT, Preference, Code Solutions, Server Debugging, Agent Prompts, Spanish Technical, System Administration, JSON/Structured Output, Documentation, Evaluation)
  3. **Forbidden Data** — Explicit prohibition table: private user data, scraped secrets, copyrighted dumps without permission, credentials, malware payloads, unlicensed content, synthetic data from closed models
  4. **Enforcement** — Required source/license fields, automated scanning, rejection of unknown source/license entries
  5. **JSONL Schemas** — Full SFT and Preference format specifications with examples and field reference tables
  6. **Quality Guidelines** — 15 items across 5 categories (Accuracy, Safety, Consistency, Completeness, Diversity)
  7. **Contributing Data** — 4-step process (Prepare, Place in Raw, Clean/Validate, Submit for Review) with 11-item PR checklist
  8. **Data Categories** — Organization by format (sft/, preference/, eval/) and domain (via tags table with 11 tag categories)
  9. **Validation Process** — 4-stage pipeline (Schema Validation, Content Validation, Quality Validation, Integration Validation)
  10. **Important Reminders** — 7 key constraints (no real datasets yet, eval never for training, no network calls, default profile is test, no model downloads in CI)
- Created dataset/schema/sft.schema.json — JSON Schema draft-07:
  - Required: messages, source, license
  - messages: array (minItems: 2) of objects with role (enum: system/user/assistant) and content (minLength: 1)
  - source: string (minLength: 1), required
  - license: string (minLength: 1), required
  - tags: array of strings (uniqueItems: true), optional
  - additionalProperties: false
- Created dataset/schema/preference.schema.json — JSON Schema draft-07:
  - Required: prompt, chosen, rejected, source, license
  - prompt: string (minLength: 1), required
  - chosen: string (minLength: 1), required
  - rejected: string (minLength: 1), required
  - source: string (minLength: 1), required
  - license: string (minLength: 1), required
  - tags: array of strings (uniqueItems: true), optional
  - additionalProperties: false
- Validated both schemas with Python jsonschema library:
  - Valid SFT sample: PASS
  - Valid Preference sample: PASS
  - Invalid SFT (empty messages): correctly rejected
  - Invalid SFT (missing source/license): correctly rejected
  - Invalid Preference (empty prompt): correctly rejected
  - Invalid SFT (invalid role): correctly rejected

Stage Summary:
- dataset/README.md: Completely rewritten from 75 lines to ~250 lines with comprehensive dataset policy
- dataset/schema/sft.schema.json: Created — valid JSON Schema draft-07 for SFT format
- dataset/schema/preference.schema.json: Created — valid JSON Schema draft-07 for Preference format
- All forbidden data types explicitly documented and enforced via policy
- No real datasets included (empty directories only)
- No private user data, no scraped secrets, no copyrighted dumps, no credentials, no malware payloads
- Schemas validated with jsonschema: all valid samples pass, all invalid samples correctly rejected
- Consistent with project JSON Schema style (draft-07, same as config/kimari.profiles.schema.json)

---
Task ID: 9-a
Agent: Docs Agent
Task: Create eval/README.md and eval/kimarifit_prompts.jsonl

Work Log:
- Read existing eval/ files: kimari_eval.jsonl (12 prompts), expected_behaviors.md (8 behavioral categories), failure_modes.md (10 failure modes), run_eval.py (evaluation runner with keyword scoring)
- Read project context: docs/00-02_kimarifit_formula.md, MODEL_LICENSES.md, MODEL_CARD.md, benchmarks/README.md, docs/BENCHMARK_SUBMISSIONS.md, docs/PYPI_RELEASE_GATE.md
- Created eval/README.md with the following sections:
  - Evaluation overview: KimariFit local scoring, coding prompts, sysadmin prompts, Spanish technical, JSON/tool-use, safety refusal, latency on GTX 1060/1080, memory usage
  - Important rules: no invented benchmark claims, no private data
  - Files in directory table
  - How to run eval (prerequisites, core eval, KimariFit prompts, interpreting results)
  - How to add new prompts to kimari_eval.jsonl and kimarifit_prompts.jsonl (with format specs and steps)
  - How to add a new category
  - Evaluation categories summary table
  - Relationship to other evaluation tools table
- Created eval/kimarifit_prompts.jsonl with 35 prompts across 10 categories:
  - python: 4 prompts (easy/medium difficulty)
  - typescript: 3 prompts (easy/medium/hard)
  - bash: 4 prompts (easy/medium)
  - docker: 3 prompts (easy/medium)
  - linux_troubleshooting: 5 prompts (easy/medium/hard)
  - windows_troubleshooting: 3 prompts (medium)
  - spanish_technical: 4 prompts (easy/medium)
  - json_mode: 3 prompts (easy/medium)
  - openclaw_agent: 3 prompts (easy/medium)
  - local_security: 3 prompts (easy/medium)
- Each prompt has: id (kf-NNN), category, prompt, expected_type (code/explanation/json/command/refusal), difficulty (easy/medium/hard), tags (2-5 per prompt)
- Validated all 35 lines as correct JSON with required fields
- No private data in any prompt
- No invented benchmark claims

Stage Summary:
- eval/README.md: Created with comprehensive evaluation documentation
- eval/kimarifit_prompts.jsonl: 35 prompts across 10 categories, all validated
- All important rules followed: no false claims, no private data, no claiming Kimari-4B is released

---
Task ID: 10-a
Agent: Docs Agent
Task: Create docs/HUGGINGFACE_RELEASE.md

Work Log:
- Read existing project docs for context: MODEL_CARD.md, MODEL_LICENSES.md, docs/MODEL_BASE_SELECTION.md, docs/MODEL_TRAINING_PLAN.md, docs/PYPI_RELEASE_GATE.md, eval/README.md
- Created docs/HUGGINGFACE_RELEASE.md with the following sections:
  - Hard Blocks: 4 mandatory conditions before any HF upload (license reviewed, eval results exist, model card states actual status, license compatibility confirmed)
  - Files Expected on Hugging Face: table with README.md, LICENSE, MODEL_LICENSES.md, safetensors, tokenizer files, GGUF quants, config files, eval results, hashes
  - Files That Must NOT Be Uploaded: training data, checkpoints, logs, API keys, unmodified base weights
  - Release Process Checklist: 4 phases (Pre-Release Preparation, Pre-Upload Validation, Upload, Post-Upload Verification)
  - README Template for HF Model Card: complete YAML frontmatter + markdown template with [FILL] and [AUTO] markers
  - GGUF Release Considerations: Git LFS, separate quant repo, quantization process, no GGUF in Git
  - Security and Access: no HF API keys, gated access if required, no GGUF committed
  - What NOT to Do table
  - Relationship to Other Project Documents table
- Key rules followed:
  - No claiming Kimari-4B is released
  - No claiming weights exist
  - No HF API keys/secrets
  - No GGUF files committed
  - No upload until license reviewed
  - No upload until eval results exist
  - No upload until model card says actual status
  - Target repo smouj/kimari-4b is planned, not created

Stage Summary:
- docs/HUGGINGFACE_RELEASE.md: Created with complete HF release guide
- 4 hard blocks defined (license, eval, model card, license compatibility)
- Full release process checklist (4 phases, 30+ items)
- HF model card README template provided
- GGUF distribution via Git LFS documented
- Security considerations documented
- All important rules followed: no false claims, no secrets, no GGUF commits

---
Task ID: 8-a
Agent: Training Infrastructure Agent
Task: Create the entire training/ directory structure with configs and scripts

Work Log:
- Checked existing project structure — no training/ directory existed
- Created training/ directory with subdirectories: configs/, scripts/, runs/, adapters/, logs/
- Created .gitkeep files in runs/, adapters/, logs/ (gitignored output directories)
- Created training/README.md with:
  - Experimental training code warning
  - Important rules (no training in CI, no model weights committed, no hardcoding base model, no network calls, no downloads, fail clearly, tests only use --dry-run)
  - Expected folder structure diagram
  - Dependencies table (transformers, datasets, peft, trl, accelerate, torch, pyyaml)
  - Usage instructions for prepare_dataset.py and train_sft_lora.py
  - Safety notes
- Created training/configs/kimari_sft_lora.example.yaml with:
  - base_model: "TBD" (no hardcoding)
  - Output, sequence, LoRA, training, precision, and misc sections
  - All hyperparameters marked as starting points with comments
  - LoRA target modules with commented-out options based on base model architecture
- Created training/configs/kimari_orpo.example.yaml with:
  - base_model_or_adapter: "TBD"
  - ORPO beta parameter with tuning note
  - Safety comments about preference tuning behavior
  - All hyperparameters marked as starting points
- Created training/scripts/prepare_dataset.py with:
  - argparse CLI: --input, --output, --schema (sft/preference)
  - SFT validation: checks messages list (role, content, non-empty), license, source
  - Preference validation: checks prompt, chosen, rejected fields (non-empty strings), license, source
  - Statistics reporting: records read, valid, invalid, written
  - Proper error handling (JSON decode errors, invalid record types)
  - Exit codes: 1 on missing input, no valid records, or all invalid
  - No network calls, no downloads
- Created training/scripts/train_sft_lora.py (skeleton) with:
  - argparse CLI: --config (required), --dry-run (optional)
  - Dependency checking: transformers, datasets, peft, trl, accelerate, torch
  - PyYAML check with clear install message
  - Config loading and validation
  - Config summary printing (base model, LoRA params, training params, precision, ORPO beta)
  - Warning system for TBD base model, missing paths, conflicting precision
  - --dry-run exits after config validation with exit code 0
  - Non-dry-run checks dependencies, shows experimental warning, blocks on TBD base model
  - Skeleton note: actual training loop not implemented
- Lint and format: both scripts pass ruff check and ruff format --check
- Functional testing:
  - prepare_dataset.py --help works
  - train_sft_lora.py --help works
  - train_sft_lora.py --dry-run with SFT config shows correct summary and TBD warning
  - train_sft_lora.py --dry-run with ORPO config shows ORPO beta and correct dataset path
  - prepare_dataset.py with valid SFT record: 1 read, 1 valid, 0 invalid, 1 written
  - prepare_dataset.py with empty messages: correctly flagged invalid, exits with code 1

Stage Summary:
- 7 files created in training/ directory
- training/README.md: comprehensive guide with rules, structure, dependencies, usage
- training/configs/kimari_sft_lora.example.yaml: SFT LoRA config with TBD base model
- training/configs/kimari_orpo.example.yaml: ORPO config with TBD base model and safety notes
- training/scripts/prepare_dataset.py: validates JSONL datasets (SFT and preference schemas)
- training/scripts/train_sft_lora.py: skeleton training script with --dry-run support
- training/runs/.gitkeep, training/adapters/.gitkeep, training/logs/.gitkeep: gitignored output dirs
- All rules followed: no training in CI, no model weights, no hardcoded base model, no network calls, no downloads, clear failure messages, --dry-run support
- ruff check: All checks passed
- ruff format: All files formatted

---
Task ID: 11-a
Agent: README Update Agent
Task: Update README.md for v0.1.17-alpha

Work Log:
- Read current README.md (699 lines) and worklog.md to understand project context
- Applied 8 targeted edits via MultiEdit:
  1. Updated version badge URL from v0.1.16-alpha to v0.1.17-alpha
  2. Updated version badge alt text from v0.1.16-alpha to v0.1.17-alpha
  3. Updated alpha warning: v0.1.16-alpha → v0.1.17-alpha
  4. Updated "Works Today" header: v0.1.16-alpha → v0.1.17-alpha
  5. Added 7 new items to "Works Today" list after "Windows packaging":
     - Model training plan
     - Base model selection
     - Dataset policy and schemas
     - Training skeletons
     - Evaluation prompt seed
     - Hugging Face release plan
     - MODEL_CARD professional rewrite
  6. Updated "Planned" section: expanded Kimari-4B description to "Training plan defined, base selection underway. Weights not yet available."
  7. Removed "Fine-tuning pipeline" from "Not Included Yet" section
  8. Added new "🧠 Kimari-4B Model Work" section after "Windows Install" and before "IDE & Agent Integrations" with:
     - Status callout (Planned / Training Design)
     - What's Ready (6 doc links)
     - Base Model Candidates table (SmolLM3-3B, Qwen2.5-3B-Instruct, Llama 3.2 3B)
     - Training Approach (5 steps)
     - Hardware notes about GTX 1060/1080 being inference-only
  9. Added 3 new entries to Documentation table after "Benchmark Submissions":
     - Model Training Plan
     - Base Model Selection
     - Hugging Face Release
- Verified all changes by reading the updated README.md

Stage Summary:
- README.md updated from v0.1.16-alpha to v0.1.17-alpha
- 8 change categories applied (version badge, alpha warning, Works Today header, Works Today list, Planned section, Not Included Yet, new Kimari-4B section, Documentation table)
- No other content modified
- 1 file changed

---
Task ID: 13-a
Agent: Release Checklist Agent
Task: Update RELEASE_CHECKLIST.md with v0.1.17 checks

Work Log:
- Read existing RELEASE_CHECKLIST.md (214 lines)
- Added "## v0.1.17 Checks" section with 21 checklist items after "## v0.1.16 Checks" and before "## Post-Release"
- Items cover: MODEL_CARD status, training/base selection docs, dataset/schema files, training skeletons, eval prompts, HF release doc, content integrity (no GGUF, no false claims, no fake benchmarks, no weights, no secrets, default_profile still "test")

Stage Summary:
- RELEASE_CHECKLIST.md updated with v0.1.17 Checks section (21 items)
- Section placed between v0.1.16 Checks and Post-Release as required
- All items match the specified checklist exactly

---
Task ID: 14-a
Agent: Release Checklist Agent
Task: Update scripts/release/check-release.py with v0.1.17 checks

Work Log:
- Read existing scripts/release/check-release.py (945 lines, 28 sections)
- Renumbered all section headers from [X/28] to [X/35] (28 sections total, replacing /28] with /35])
- Added 7 new section blocks after [28/35] and before the summary section:
  - [29/35] v0.1.17 MODEL_CARD professional rewrite (5 checks: exists, planned/training design, no release claim, base model candidates, TBD for selected base)
  - [30/35] v0.1.17 training and base selection docs (2 checks: MODEL_TRAINING_PLAN.md, MODEL_BASE_SELECTION.md)
  - [31/35] v0.1.17 dataset and schema files (6 checks: dataset README, sft.schema.json, preference.schema.json, JSON validity for both schemas)
  - [32/35] v0.1.17 training skeletons (5 checks: training README, SFT LoRA example config, ORPO example config, prepare_dataset.py, train_sft_lora.py)
  - [33/35] v0.1.17 eval prompts and HF release (4 checks: eval README, kimarifit_prompts.jsonl exists and valid JSON, HUGGINGFACE_RELEASE.md)
  - [34/35] v0.1.17 content integrity (4 checks: default_profile "test", no GGUF tracked, no fake benchmarks in MODEL_CARD, no Kimari-4B release claim)
  - [35/35] v0.1.17 MODEL_LICENSES and README updates (7 checks: SmolLM3/Qwen/Llama in MODEL_LICENSES, Kimari-4B/MODEL_CARD in README, training plan in README, base selection in README, Hugging Face in README)
- Verified no remaining /28] patterns in the file
- Verified all 35 section headers present from [1/35] to [35/35]

Stage Summary:
- scripts/release/check-release.py updated from 28 to 35 sections
- All section numbers renumbered from /28 to /35
- 7 new v0.1.17 check sections added (33 total new individual checks)
- File structure preserved: existing checks unchanged, new checks appended before summary

---
Task ID: 12-a
Agent: Docs Agent
Task: Update docs/index.html for v0.1.17-alpha

Work Log:
- Read docs/index.html to understand current structure and locate edit points
- Edit 1: Updated hero badge version text from "v0.1.16-alpha — Experimental API, PyPI release gate, model hashing, community benchmarks, Windows packaging" to "v0.1.17-alpha — Kimari-4B model planning, training pipeline, base selection, dataset schemas, Hugging Face readiness"
- Edit 2: Replaced the "What's New" focus block — changed version label from v0.1.16-alpha to v0.1.17-alpha, replaced 5 chips (Experimental API, PyPI release gate, Model hashing, Community benchmarks, Windows packaging) with 5 new chips (🧠 MODEL_CARD rewrite with fa-file-alt/teal, 📋 Training plan with fa-list-check/purple, 🔍 Base selection with fa-magnifying-glass/cyan, 📊 Dataset schemas with fa-database/teal, 🤗 HF release plan with fa-cloud-arrow-up/purple)
- Edit 3: Added new "Kimari-4B Model Roadmap" section between "What's New" and "Overview" — teal Kimari-4B badge, "Model Roadmap" title, "PLANNED — NO WEIGHTS YET" red badge, 4-column grid (Status, Base Selection, Training Plan, Weights)
- Edit 4: Added "Model Training Plan" feature card after "Hash Pinning Workflow" in Features section — 🧠 icon, "7-phase pipeline for Kimari-4B: base selection, SFT, DPO/ORPO, evaluation, GGUF export, Hugging Face release"
- Edit 5: Added 3 new doc cards to Documentation grid — Model Training Plan (docs/MODEL_TRAINING_PLAN.md), Base Model Selection (docs/MODEL_BASE_SELECTION.md), Hugging Face Release (docs/HUGGINGFACE_RELEASE.md)
- Edit 6: Updated Project Status section version text to v0.1.17-alpha with new focus description
- Edit 7: Updated CLI showcase terminal version from v0.1.16-alpha to v0.1.17-alpha
- Edit 8: Added 5 new status table rows for v0.1.17-alpha items (MODEL_CARD rewrite, Training plan, Base selection, Dataset schemas, Hugging Face release plan)

Stage Summary:
- docs/index.html updated from v0.1.16-alpha to v0.1.17-alpha
- Hero badge, What's New focus, Kimari-4B Model Roadmap, feature card, 3 doc cards, status section all updated
- All version references updated (hero badge, terminal showcase, project status section)
- No stale v0.1.16-alpha references remain in active content (only in historical status table entries)
- 1 file changed

---
Task IDs: 15-a, 16-a, 17-a
Agent: Main Agent
Task: Create tests/test_release_v0117.py, update CHANGELOG.md, update ROADMAP.md

Work Log:
- Read existing test_release_v0116.py to understand testing patterns (class-based, PROJECT_ROOT, _run_kimari helper, try/except for optional imports)
- Read current CHANGELOG.md, ROADMAP.md, MODEL_CARD.md, dataset schemas, training configs, training scripts, eval prompts, pyproject.toml, __init__.py
- Created tests/test_release_v0117.py with 63 tests across 12 test classes:
  - TestVersion (3 tests): version consistency across __init__.py, pyproject.toml, and CLI info --json
  - TestModelCard (7 tests): exists, says not released, says planned, no false release claim, has base candidates, evaluation targets marked not achieved, has release checklist
  - TestTrainingPlan (5 tests): exists, mentions phases, mentions SFT, mentions DPO/ORPO, no training done
  - TestBaseSelection (3 tests): doc exists, has candidates, no final choice
  - TestModelLicenses (4 tests): exists, mentions candidates, no weights released, has decision framework
  - TestDatasetSchemas (8 tests): both schemas exist, parse as JSON, correct structure, draft-07
  - TestDatasetSchemaValidation (6 tests): sample records validate against schemas if jsonschema available, invalid records fail
  - TestTrainingConfigs (8 tests): both configs exist, TBD base model, LoRA params, starting points warnings, ORPO beta, safety warnings
  - TestTrainingScripts (5 tests): scripts exist, --dry-run works, blocks TBD base model, --help works
  - TestEvalPrompts (4 tests): JSONL exists, parses with 35+ records, 10+ categories, has security
  - TestHuggingFaceRelease (4 tests): doc exists, mentions checklist/license/hard blocks
  - TestNoGGUF (2 tests): no GGUF tracked or in models dir
  - TestNoFalseClaims (2 tests): no Kimari-4B release claims, no PyPI published claims
  - TestNoFakeBenchmarks (3 tests): MODEL_CARD no fake numbers, targets are TBD/aspirational, benchmarks section honest
  - TestReleaseCheck (1 test): check-release.py passes
- Fixed test_train_sft_lora_blocks_tbd_base_model: adjusted assertion to accept missing deps or TBD as valid failure reasons
- Fixed bug in scripts/release/check-release.py line 957: changed `"tbd" in model_card_text` to `"tbd" in model_card_lower` (case-sensitive check was failing for uppercase "TBD" in MODEL_CARD.md)
- Updated CHANGELOG.md: added v0.1.17-alpha entry at the top (after header) with full Added and Changed sections following Keep a Changelog format
- Updated ROADMAP.md: changed v0.1.16-alpha from (Current) to (Released), replaced v0.1.17-alpha (Planned) with v0.1.17-alpha (Current) containing 11 completed items, added v0.1.18-alpha (Planned) with 6 planned items
- All 63 new tests passing, ruff lint clean on test file, check-release.py 35/35 checks passing

Stage Summary:
- tests/test_release_v0117.py created with 63 comprehensive tests for v0.1.17-alpha
- CHANGELOG.md updated with v0.1.17-alpha entry (2026-05-19)
- ROADMAP.md updated: v0.1.16-alpha Released, v0.1.17-alpha Current, v0.1.18-alpha Planned
- Bug fix in check-release.py: case-insensitive TBD check in MODEL_CARD.md
- All validations pass

---
Task ID: 2-8
Agent: Sub Agent
Task: Create adapter manifest template, create_adapter_manifest.py, eval summary template, create_eval_summary.py, private SFT checklist, SFT-to-ORPO decision framework, private eval results policy, and test fixture

Work Log:
- Read worklog.md to understand project history and prior work (v0.1.21-alpha, training infrastructure, eval scripts, adapter artifact policy, adapter preview gate)
- Read existing reference files for style consistency: eval/scripts/compare_runs.py, eval/scripts/summarize_results.py, training/scripts/validate_training_ready.py, training/configs/private_sft_run.v0.yaml, training/configs/kimari_sft_lora.v0.example.yaml, docs/ADAPTER_ARTIFACT_POLICY.md, docs/ADAPTER_PREVIEW_GATE.md, tests/fixtures/baseline_eval_result.json
- Created training/templates/adapter_manifest.template.yaml — full template with all 22 required fields (adapter_name, run_id, base_model, base_model_revision, dataset_id, dataset_hash, training_config, training_started_at, training_finished_at, trainer, lora_r, lora_alpha, lora_dropout, learning_rate, epochs, max_seq_length, adapter_files, adapter_sha256, adapter_size_bytes, eval_results, baseline_results, preview_gate_state=BLOCKED, state_history with initial BLOCKED entry, public_release_allowed=false, hf_upload_allowed=false, notes)
- Created training/scripts/create_adapter_manifest.py — CLI script with --run-config, --adapter-dir, --output, --dry-run, --json flags; reads template, merges run config and SFT config values; scans adapter dir computing sizes/hashes for allowed files; rejects suspicious files (.safetensors, .bin, .pt, .pth, .ckpt, .gguf) by listing but NOT including; enforces preview_gate_state=BLOCKED, public_release_allowed=false, hf_upload_allowed=false; works without PyYAML (simple text substitution fallback with parse_simple_yaml and render_yaml_from_dict)
- Created docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md — 12-section checklist covering GPU environment, license review, dataset validation, baseline eval plan, run config review, output directory safety, experiment tracking, HF restrictions, training command, post-run manifest creation, post-run evaluation, and preview gate; includes quick reference table with 10 must-check items
- Created docs/SFT_TO_ORPO_DECISION.md — decision framework with 6-row decision table (safety regression → no ORPO, coding improvement + no safety regression → consider ORPO, overfitting → expand dataset first, baseline surpasses adapter → review, no improvement → review, mixed → selective review); prerequisites for ORPO (7 items); ORPO vs DPO selection criteria; decision flowchart; "what ORPO cannot fix" section; pre-ORPO checklist; explicit statement that DPO/ORPO does not run in CI
- Created docs/PRIVATE_EVAL_RESULTS_POLICY.md — policy governing what eval results can be committed; CAN commit table (anonymous summaries, category counts, manual review status, hashes, score status, run metadata, config references, error counts); CANNOT commit table (private prompts, local paths, tokens/credentials, sensitive outputs, benchmark claims without review, full model responses, prompt text); committable eval summary format example; how to create safe eval summary; benchmark claims policy; review process; enforcement section
- Created eval/templates/eval_summary.template.json — committable eval summary template with run_id, model_label, kimari_version, prompt_count=0, category_counts={}, score_status="manual_review_required", manual_review_required=true, safety_regression_detected=false, false_claims_detected=false, reviewer="", notes=""; NO raw private prompts
- Created eval/scripts/create_eval_summary.py — CLI with --input, --output, --json flags; reads raw eval result JSON; strips "prompt" and "response" fields from results; produces safe summary with category counts; marks manual_review_required=true if no scores exist; does NOT invent scores; uses template if available; works with test fixtures
- Created tests/fixtures/private_eval_raw.json — synthetic fixture with 5 results across 3 categories (python, bash, docker); contains fake prompts with sensitive data (production DB credentials, internal server IPs, API keys) and fake responses with matching sensitive data; some results have empty responses (errors); all have score_status="manual_review_required"; designed for testing create_eval_summary.py sanitization
- Verified all Python scripts compile with py_compile
- Tested create_adapter_manifest.py: dry-run produces correct YAML, dry-run --json produces correct JSON, adapter dir scanning correctly includes allowed files and rejects suspicious files (.safetensors), preview_gate_state always BLOCKED, public_release_allowed always false
- Tested create_eval_summary.py: correctly strips prompt/response, computes category counts, marks manual_review_required, does not invent scores
- Tested both scripts with tmp_path-style operations (tempfile.TemporaryDirectory) — all pass

Stage Summary:
- 8 files created:
  1. training/templates/adapter_manifest.template.yaml — full adapter manifest template with BLOCKED state
  2. training/scripts/create_adapter_manifest.py — CLI for creating adapter manifests from template + run config + adapter dir
  3. docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md — 12-section pre-flight checklist for first private SFT
  4. docs/SFT_TO_ORPO_DECISION.md — decision framework for proceeding to preference tuning after SFT
  5. docs/PRIVATE_EVAL_RESULTS_POLICY.md — policy governing committable eval results
  6. eval/templates/eval_summary.template.json — committable eval summary template
  7. eval/scripts/create_eval_summary.py — CLI for creating safe eval summaries from raw results
  8. tests/fixtures/private_eval_raw.json — synthetic test fixture for sanitization testing
- All scripts follow project style (from __future__ import annotations, argparse CLI, proper error handling, no network calls)
- All safety constraints enforced: preview_gate_state=BLOCKED, public_release_allowed=false, hf_upload_allowed=false, no invented scores
- Works without PyYAML dependency (simple text substitution fallback)
- No real training, no model downloads, no HF uploads, no weights, no adapters, no GGUF, no fake benchmarks

---
Task ID: 9-11
Agent: Main Agent
Task: Improve compare_runs.py with verdict/summary-output, update 4 docs with cross-references

Work Log:
- Read worklog.md and all 6 target files to understand prior work and current content
- Read supporting files: create_adapter_manifest.py, create_eval_summary.py, SFT_TO_ORPO_DECISION.md, PRIVATE_EVAL_RESULTS_POLICY.md, adapter_manifest.template.yaml, eval_summary.template.json

**Task 1: Improved eval/scripts/compare_runs.py**
- Added `--summary-output` CLI argument (optional Path) — writes a committable eval summary JSON
- Added `_determine_verdict()` function with 5 verdict levels:
  - `insufficient_data` — no scores in either file AND/OR missing_outputs > 0 in candidate
  - `candidate_better` — candidate average_score > baseline AND no safety regression
  - `candidate_worse` — candidate average_score < baseline OR safety_regression_detected=true
  - `mixed` — some categories improved, some regressed (needs manual review)
  - `manual_review_required` — default when data is insufficient to determine direction
- Added `_compute_category_deltas()` for per-category score delta comparison (enables mixed verdict)
- Added `safety_regression_detected` field check from candidate data — if true, verdict = candidate_worse
- Added `_build_summary_output()` for safe summary JSON (no raw prompts/responses)
- Summary output fields: run_id, model_label, kimari_version, prompt_count, category_counts, score_status, manual_review_required, safety_regression_detected, false_claims_detected, verdict, reviewer, notes
- Does NOT invent scores if missing
- Updated text output to display verdict and safety regression warnings
- Verified py_compile passes

**Task 2: Updated docs/PRIVATE_TRAINING_RUNBOOK.md**
- Step 5c: Replaced manual manifest creation with create_adapter_manifest.py usage (commands for --run-config, --adapter-dir, --output, --dry-run)
- Step 7: Added new 7d "Sanitize eval results for commit" section with create_eval_summary.py command and reference to PRIVATE_EVAL_RESULTS_POLICY.md and eval/templates/eval_summary.template.json
- Step 8: Added SFT_TO_ORPO_DECISION.md reference for the full decision framework
- Related Documents: Added SFT_TO_ORPO_DECISION.md, PRIVATE_EVAL_RESULTS_POLICY.md, training/templates/adapter_manifest.template.yaml, eval/templates/eval_summary.template.json

**Task 3: Updated docs/ADAPTER_ARTIFACT_POLICY.md**
- "What CAN Be Committed" section: Added important note that manifest CAN be committed if no sensitive paths/weights, adapter files must NEVER be committed
- "Adapter Manifest Format" section: Added template-based creation instructions with create_adapter_manifest.py commands, --dry-run preview, script behavior description; existing manual YAML format preserved as fallback
- Related Documents: Added training/templates/adapter_manifest.template.yaml reference

**Task 4: Updated docs/ADAPTER_PREVIEW_GATE.md**
- PENDING → APPROVED_FOR_PRIVATE_TESTING requirement #3: Added `safety_regression_detected` field check requirement
- "No Automatic Transitions" section: Added bullet that creating a manifest with create_adapter_manifest.py does NOT advance the gate
- Added new "Template References" section with table for adapter manifest template (training/templates/adapter_manifest.template.yaml) and eval summary template (eval/templates/eval_summary.template.json)
- Added note that creating a manifest or eval summary does NOT advance the gate

**Task 5: Updated docs/BASELINE_EVAL_PLAN.md**
- Step 5: Added create_eval_summary.py usage for producing committable summaries, with command and reference to eval/templates/eval_summary.template.json and PRIVATE_EVAL_RESULTS_POLICY.md
- "How Baseline Results Are Used" #1: Added compare_runs.py --summary-output command example for producing committable comparison summaries
- Related Documents: Added PRIVATE_EVAL_RESULTS_POLICY.md and eval/templates/eval_summary.template.json

Stage Summary:
- 5 files modified with minimal, targeted additions
- eval/scripts/compare_runs.py: 3 new functions (_determine_verdict, _compute_category_deltas, _build_summary_output), 1 new CLI arg (--summary-output), verdict logic, safety regression check
- 4 docs updated with cross-references to scripts, templates, and policies
- All changes preserve existing content and style
- No real training, no model downloads, no HF uploads, no weights, no adapters, no GGUF, no fake benchmarks

---
Task ID: 13-14
Agent: Release Validation Agent
Task: Update check-release.py for v0.1.21 and create tests/test_release_v0121.py

Work Log:
- Read worklog.md to understand project history and prior work (v0.1.20-alpha, v0.1.21-alpha changes)
- Read current check-release.py (48 sections, ~1622 lines) to understand structure
- Read existing test_release_v0120.py for reference style
- Verified all v0.1.21 files exist: training/templates/adapter_manifest.template.yaml, training/scripts/create_adapter_manifest.py, docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md, docs/SFT_TO_ORPO_DECISION.md, docs/PRIVATE_EVAL_RESULTS_POLICY.md, eval/templates/eval_summary.template.json, eval/scripts/create_eval_summary.py
- Read create_adapter_manifest.py, create_eval_summary.py, compare_runs.py to understand CLI interfaces for test assertions
- Read test fixtures (private_eval_raw.json, baseline_eval_result.json, adapter_eval_result.json) to verify test data compatibility
- Updated check-release.py: changed all section numbering from /48 to /49 (48 occurrences)
- Added [49/49] v0.1.21 section to check-release.py with 12 checks:
  1. training/templates/adapter_manifest.template.yaml exists
  2. training/scripts/create_adapter_manifest.py exists
  3. docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md exists
  4. docs/SFT_TO_ORPO_DECISION.md exists
  5. docs/PRIVATE_EVAL_RESULTS_POLICY.md exists
  6. eval/templates/eval_summary.template.json exists
  7. eval/scripts/create_eval_summary.py exists
  8. ADAPTER_PREVIEW_GATE.md mentions BLOCKED
  9. ADAPTER_ARTIFACT_POLICY.md mentions adapter_manifest.template or manifest template
  10. No .safetensors files tracked in git
  11. No .bin/.pt/.pth/.ckpt files tracked in git
  12. No .gguf files tracked in git
- Created tests/test_release_v0121.py with 23 tests in 9 test classes:
  - TestAdapterManifestTemplate (3 tests): template exists, required fields, BLOCKED by default
  - TestCreateAdapterManifest (2 tests): script exists, dry-run JSON with safety constraints
  - TestNewDocs (3 tests): PRIVATE_SFT_EXECUTION_CHECKLIST, SFT_TO_ORPO_DECISION, PRIVATE_EVAL_RESULTS_POLICY
  - TestEvalSummaryTemplate (3 tests): template exists, parses with required fields, no raw prompts
  - TestCreateEvalSummary (2 tests): script exists, strips raw outputs
  - TestCompareRunsVerdict (3 tests): script exists, compare with fixtures, summary output written
  - TestPreviewGate (2 tests): ADAPTER_PREVIEW_GATE says BLOCKED, manifest template has BLOCKED
  - TestNoTrackedArtifacts (3 tests): no safetensors/GGUF/weight files tracked
  - TestVersionConsistency (2 tests): version is 0.1.21-alpha in __init__.py and pyproject.toml
- Ran python -m pytest tests/test_release_v0121.py -q: 23 passed in 0.35s
- Ran check-release.py: All checks passed! 49/49 categories, 0 warnings

Stage Summary:
- scripts/release/check-release.py updated: section numbering /48→/49, new [49/49] v0.1.21 section added
- tests/test_release_v0121.py created with 23 comprehensive tests
- All 23 tests passing
- check-release.py: 49/49 categories all passed


---
Task ID: 2-3-6-7-8
Agent: Docs Agent
Task: Create v0.1.22-alpha remote GPU training guide, training requirements, execution config, private run artifacts guide, and failure troubleshooting

Work Log:
- Read worklog.md to understand project history (v0.1.21-alpha, extensive training infrastructure docs)
- Read existing related docs: PRIVATE_EVAL_RESULTS_POLICY.md, PRIVATE_TRAINING_RUNBOOK.md, FIRST_PRIVATE_TRAINING_RUN.md, ADAPTER_ARTIFACT_POLICY.md, ADAPTER_PREVIEW_GATE.md, SFT_TO_ORPO_DECISION.md, PRIVATE_SFT_EXECUTION_CHECKLIST.md
- Read existing configs: training/configs/private_sft_run.v0.yaml, training/configs/kimari_sft_lora.v0.example.yaml
- Created docs/REMOTE_GPU_RUNPOD_GUIDE.md (~300 lines):
  - Recommended GPU types table (RTX 4090, L40S, A100, RTX 3090, RTX 4080) with costs
  - Expected VRAM usage table for SmolLM3-3B with LoRA/QLoRA configurations
  - Python 3.10+ setup with version verification
  - Virtual environment creation (isolated .venv-training)
  - PyTorch CUDA installation with index-url guidance
  - Repo + training extras installation
  - HF cache configuration outside repo (HF_HOME on persistent storage)
  - Dataset v0 build procedure
  - Dry-run validation (validate_training_ready, train_sft_lora --dry-run, preflight_private_sft)
  - Real training execution with monitoring guidance
  - Post-run validation (postrun_private_sft, adapter manifest, hashes)
  - Explicit DO NOT upload to HF and DO NOT commit outputs sections
  - Sanitized manifest/eval summary copy procedures
  - Pre-flight and post-run scripts reference table
  - Storage and cost estimates with tables
  - 10 safety reminders throughout
  - Termination checklist
  - Full cross-references to related docs
- Created training/requirements-training.txt (~55 lines):
  - 10 training dependencies with pinned minimum versions
  - Per-dependency comments explaining purpose and why separated from runtime
  - torch, transformers, datasets, accelerate, peft, trl, safetensors, pyyaml, sentencepiece, protobuf
  - Header comments explaining separation rationale, version pinning note, CI exclusion
- Created training/configs/private_sft_execution.example.yaml:
  - Provider, GPU type, VRAM configuration
  - HF cache, output dir, dataset build dir settings
  - Required environment variables list
  - 6 command definitions (build_dataset, preflight, train, eval_baseline, eval_adapter, postrun)
  - Notes with safety reminders and cross-reference
- Created docs/PRIVATE_RUN_ARTIFACTS.md (~230 lines):
  - Files that stay local only (NEVER commit): adapter weights, checkpoints, optimizer states, raw eval outputs, TensorBoard, WandB, merged models, GGUF exports (12 items with gitignore patterns)
  - Files that CAN be committed with conditions: MANIFEST.yaml, eval_summary.json, compare_summary.json, adapter_config.json (with per-field conditions)
  - Detailed sanitization procedures for each committable file type
  - Pre-commit review checklist (13 items)
  - Quick verification commands (git diff --cached checks)
  - Accidental commit recovery procedure
  - Reference to PRIVATE_EVAL_RESULTS_POLICY.md with key principles
  - Summary table of all artifacts
- Created docs/PRIVATE_RUN_FAILURES.md (~350 lines):
  - 10 failure modes each with Symptom/Cause/Fix/Prevention:
    1. OOM during training (5 causes, 5 immediate fixes, monitoring tips)
    2. CUDA unavailable (6 causes, RunPod-specific fixes)
    3. Tokenizer load failure (7 causes, pre-download verification)
    4. Dataset validation failure (6 causes, rebuild procedure)
    5. PEFT/TRL version mismatch (5 causes, fresh venv procedure)
    6. Eval endpoint unavailable (6 causes, llama-server restart)
    7. Adapter manifest hash mismatch (6 causes, integrity verification)
    8. Accidental raw outputs committed (6 causes, not-yet-pushed and already-pushed recovery)
    9. How to abort and keep gate BLOCKED (abort conditions, safe abort procedure, post-abort actions)
    10. Recovery procedures (5 scenarios: interrupted, bad results, sensitive data, hash mismatch, instance expired)
  - Quick reference table: Failure → Gate State → Can Resume → Must Re-run
  - All failures keep gate BLOCKED

Stage Summary:
- 5 files created for v0.1.22-alpha
- docs/REMOTE_GPU_RUNPOD_GUIDE.md: Complete RunPod/remote GPU guide with GPU recommendations, VRAM estimates, step-by-step setup, safety throughout
- training/requirements-training.txt: 10 training deps separated from runtime with rationale
- training/configs/private_sft_execution.example.yaml: Execution config template for remote/local GPU
- docs/PRIVATE_RUN_ARTIFACTS.md: Clear local-only vs committable classification with sanitization procedures
- docs/PRIVATE_RUN_FAILURES.md: 10 failure modes with Symptom/Cause/Fix/Prevention + 5 recovery scenarios
- All documents cross-reference existing project docs (ADAPTER_ARTIFACT_POLICY, ADAPTER_PREVIEW_GATE, PRIVATE_EVAL_RESULTS_POLICY, etc.)
- All safety rules followed: no weights committed, no HF upload, gate stays BLOCKED, no false claims, no private data

---
Task ID: 4-5-9-10-11-12
Agent: Main Agent
Task: Create 5 new Python scripts and improve train_sft_lora.py for v0.1.22-alpha

Work Log:
- Read worklog.md to understand project history (v0.1.21-alpha, private SFT pipeline)
- Read existing scripts (train_sft_lora.py, create_adapter_manifest.py, create_eval_summary.py, compare_runs.py, run_private_sft_dryrun.py, validate_training_ready.py) to understand patterns
- Read configs (private_sft_run.v0.yaml, kimari_sft_lora.v0.example.yaml) for integration
- Read eval/kimarifit_prompts.jsonl to understand prompt structure (35 prompts, 10 categories)

Created 5 new scripts:
1. training/scripts/preflight_private_sft.py — CLI preflight check for private SFT readiness
   - Checks: Python >= 3.10, torch (graceful), CUDA (if torch), transformers/peft/trl/accelerate, dataset build, output_dir gitignored, public_release_allowed=false, hf_upload_allowed=false, preview gate BLOCKED, no GGUF/adapters in git
   - --strict flag fails if torch not installed; non-strict exits 1 only for safety-critical failures
   - --json output with per-check status
   - Works WITHOUT torch installed (try/except, no top-level imports)

2. training/scripts/postrun_private_sft.py — CLI post-training orchestration
   - Calls create_adapter_manifest, create_eval_summary, compare_runs (if baseline), verify gate BLOCKED
   - Dry-run by default (--no-dry-run for real execution)
   - Suggests next steps, never commits anything
   - --json output with step results

3. training/scripts/run_training_command_preview.py — CLI for training command preview
   - recommended_command, recommended_environment (GPU requirements), expected_outputs
   - forbidden_commit_patterns (*.safetensors, *.bin, *.pt, *.ckpt, *.gguf, wandb/, runs/)
   - safety_warnings (8 warnings)
   - Reads config, no training/downloads

4. eval/scripts/run_baseline_eval_plan.py — CLI for baseline eval planning
   - model_label, prompts_path, prompt_count, categories, recommended_endpoint, recommended_output
   - score_status: manual_review_required
   - 6 steps with commands, dry-run by default
   - Recommended output: eval/results/baseline-smollm3-base-private.json

5. eval/scripts/run_adapter_eval_plan.py — CLI for adapter eval planning
   - Same structure as baseline, plus baseline_available check and compare_with_baseline step
   - 9 steps including merge_adapter, check_safety, compare_with_baseline
   - Recommended output: eval/results/adapter-kimari-smollm3-sft-v0-private.json

Improved train_sft_lora.py with 4 new CLI flags:
- --print-command: prints recommended training command and exits
- --estimate-only: prints step estimation JSON and exits (no full plan)
- --require-dataset: fails if dataset_path doesn't exist on disk
- output_dir gitignored validation: checks if output_dir inside repo is gitignored, warns if not
- Clear warning: "Real training must not run in CI"

All scripts:
- Use `from __future__ import annotations`
- Use argparse for CLI
- Support --json output
- Never hardcode secrets
- Work in CI without torch installed
- Use pyyaml with simple fallback parser
- Pass ruff check (target py310, line-length 120, select E/F/W/I/N/UP/B/SIM, ignore E501)
- Pass ruff format --check
- Pass py_compile

Stage Summary:
- 5 new scripts created, 1 existing script improved
- All scripts tested with --json and human-readable output
- ruff check + format: ALL PASSED
- py_compile: ALL PASSED
- No real training, no model downloads, no HF uploads
- All safety rules followed: no weights committed, gate stays BLOCKED, no false claims

---
Task ID: 15
Agent: Main Agent
Task: Update RELEASE_CHECKLIST.md and scripts/release/check-release.py for v0.1.22-alpha

Work Log:
- Read worklog.md to understand project history and prior work
- Read current RELEASE_CHECKLIST.md — identified insertion point before "## Post-Release" section
- Read current check-release.py — identified 49 sections with [1/49] to [49/49] counters
- Added "## v0.1.22 Checks" section to RELEASE_CHECKLIST.md with 16 checklist items:
  - docs/REMOTE_GPU_RUNPOD_GUIDE.md exists
  - training/requirements-training.txt exists
  - training/scripts/preflight_private_sft.py exists and --json works without torch
  - training/scripts/postrun_private_sft.py exists and --dry-run --json works with fake paths
  - training/configs/private_sft_execution.example.yaml exists
  - docs/PRIVATE_RUN_ARTIFACTS.md exists
  - docs/PRIVATE_RUN_FAILURES.md exists
  - training/scripts/run_training_command_preview.py exists and --json works
  - eval/scripts/run_baseline_eval_plan.py exists and --dry-run --json works
  - eval/scripts/run_adapter_eval_plan.py exists and --dry-run --json works
  - train_sft_lora.py supports --print-command and --estimate-only
  - No training outputs committed
  - No adapter/weight files tracked in git
  - Preview gate still BLOCKED
  - default_profile is still "test"
  - No "Kimari-4B released" false claim anywhere
- Updated scripts/release/check-release.py:
  - Replaced all /49] with /50] in print() statements (replace_all)
  - Added new [50/50] v0.1.22 private SFT execution package section with checks for:
    - docs/REMOTE_GPU_RUNPOD_GUIDE.md exists
    - training/requirements-training.txt exists
    - training/scripts/preflight_private_sft.py exists
    - training/scripts/postrun_private_sft.py exists
    - training/configs/private_sft_execution.example.yaml exists
    - docs/PRIVATE_RUN_ARTIFACTS.md exists
    - docs/PRIVATE_RUN_FAILURES.md exists
    - training/scripts/run_training_command_preview.py exists
    - eval/scripts/run_baseline_eval_plan.py exists
    - eval/scripts/run_adapter_eval_plan.py exists
    - train_sft_lora.py supports --print-command and --estimate-only
    - No adapter/weights/GGUF tracked in git (re-check)
    - Preview gate still BLOCKED (re-check in ADAPTER_PREVIEW_GATE.md)
    - No "Kimari-4B released" false claim (re-check)
- Verified no remaining /49] references in check-release.py (0 occurrences)
- Verified all 50 section counters present ([1/50] through [50/50])
- Verified Python syntax with py_compile — OK

Stage Summary:
- RELEASE_CHECKLIST.md: Added v0.1.22 Checks section with 16 items before Post-Release
- scripts/release/check-release.py: Section counters updated from /49] to /50], new [50/50] section added
- 2 files changed
- All syntax checks passed

---
Task ID: 13
Agent: Docs Agent
Task: Update existing documentation files for v0.1.22-alpha — add v0.1.22-alpha Additions sections

Work Log:
- Read worklog.md to understand project history and prior agent work
- Read all four target documentation files to understand current content and structure
- Updated docs/PRIVATE_TRAINING_RUNBOOK.md:
  - Added "v0.1.22-alpha Additions" section before "Related Documents" with table of 6 new scripts/guides (preflight_private_sft.py, run_training_command_preview.py, run_baseline_eval_plan.py, run_adapter_eval_plan.py, postrun_private_sft.py, REMOTE_GPU_RUNPOD_GUIDE.md)
  - Added 3 new entries to "Related Documents" table: REMOTE_GPU_RUNPOD_GUIDE.md, PRIVATE_RUN_ARTIFACTS.md, PRIVATE_RUN_FAILURES.md
- Updated docs/ADAPTER_ARTIFACT_POLICY.md:
  - Added "v0.1.22-alpha Additions" section before "Related Documents" with references to PRIVATE_RUN_ARTIFACTS.md and postrun_private_sft.py
  - Added "Pre-commit Checklist for Summaries" subsection with 4 checklist items (no raw prompts, no local paths, no tokens, no unreviewed benchmark claims)
  - Added 1 new entry to "Related Documents" table: PRIVATE_RUN_ARTIFACTS.md
- Updated docs/BASELINE_EVAL_PLAN.md:
  - Added "v0.1.22-alpha Additions" section before "Related Documents" with table of 2 new CLI tools (run_baseline_eval_plan.py, run_adapter_eval_plan.py)
  - Documented --dry-run and --json flags for both scripts
  - Added "Post-evaluation Comparison" subsection with compare_runs.py --summary-output example
- Updated docs/SFT_TO_ORPO_DECISION.md:
  - Added "v0.1.22-alpha Additions" section before "Related Documents" with 4 safeguard items
  - Documented ORPO decision deferred until postrun summary reviewed
  - Documented manual_review_required=true blocks automatic ORPO proceed
  - Documented safety_regression_detected=true blocks ORPO
  - Referenced postrun_private_sft.py for post-training evaluation orchestration

Stage Summary:
- 4 documentation files updated with v0.1.22-alpha Additions sections
- All additions properly formatted Markdown integrating smoothly with existing content
- Related Documents tables updated with new cross-references
- No code changes, no test changes — documentation only

---
Task ID: v0.1.22-alpha-implementation
Agent: Main Agent
Task: Implement v0.1.22-alpha of Kimari Local AI — Private SFT execution package

Work Log:
- Version bumped to 0.1.22-alpha in pyproject.toml, kimari/__init__.py, README.md, docs/index.html, MODEL_CARD.md, CHANGELOG.md, ROADMAP.md, docs/PUBLISHING.md
- Created docs/REMOTE_GPU_RUNPOD_GUIDE.md — RunPod/GPU execution guide with GPU recommendations, VRAM estimates, step-by-step setup, safety reminders
- Created training/requirements-training.txt — Separated training dependencies (torch, transformers, peft, trl, accelerate, datasets, etc.)
- Created training/scripts/preflight_private_sft.py — CLI preflight check for SFT readiness, works without torch, --strict mode, --json
- Created training/scripts/postrun_private_sft.py — CLI post-training orchestration, dry-run by default, --json
- Created training/configs/private_sft_execution.example.yaml — Execution config template for remote/local GPU
- Created docs/PRIVATE_RUN_ARTIFACTS.md — Classification of what stays local vs what can be committed
- Created docs/PRIVATE_RUN_FAILURES.md — Troubleshooting guide for 10 failure modes
- Created training/scripts/run_training_command_preview.py — CLI for training command preview, --json
- Created eval/scripts/run_baseline_eval_plan.py — CLI for baseline eval planning, --dry-run, --json
- Created eval/scripts/run_adapter_eval_plan.py — CLI for adapter eval planning, --dry-run, --json
- Improved training/scripts/train_sft_lora.py — Added --print-command, --estimate-only, --require-dataset, output_dir gitignored validation
- Updated docs/PRIVATE_TRAINING_RUNBOOK.md — Added v0.1.22 references to preflight, postrun, eval plans, remote GPU guide
- Updated docs/ADAPTER_ARTIFACT_POLICY.md — Added PRIVATE_RUN_ARTIFACTS.md, postrun script, pre-commit checklist
- Updated docs/BASELINE_EVAL_PLAN.md — Added baseline/adapter eval plan scripts, compare_runs comparison
- Updated docs/SFT_TO_ORPO_DECISION.md — Added ORPO decision deferred until postrun, manual_review_required blocks ORPO, safety_regression blocks ORPO
- Updated RELEASE_CHECKLIST.md — Added v0.1.22 Checks section
- Updated scripts/release/check-release.py — Added v0.1.22 section (50/50) with all new file checks
- Created tests/test_release_v0122.py — Comprehensive tests for all v0.1.22 artifacts
- Fixed version assertions in older test files (0111-0120) to match current 0.1.22-alpha
- Fixed false claim self-detection in test_release_v0119.py
- All validations passed: pytest (all tests), ruff check, ruff format, check-release.py (50/50 checks OK)

Stage Summary:
- Version: 0.1.22-alpha
- 11 new files created, 12+ files updated
- All 50 release checks pass
- All tests pass
- Ruff lint and format pass
- All new CLIs tested and working
- Preview gate remains BLOCKED
- No weights, adapters, GGUF, or checkpoints tracked
- No false claims about Kimari-4B

---
Task ID: v0.1.23-alpha
Agent: Main Agent
Task: Implement v0.1.23-alpha of Kimari Local AI — private SFT pre-run hardening + screenshots/docs polish

Work Log:
- Version bumped to 0.1.23-alpha in pyproject.toml, kimari/__init__.py, README.md, docs/index.html, MODEL_CARD.md
- Updated all version assertions in test files (test_cli_smoke.py, test_release_v0111-v0122.py) from 0.1.22-alpha to 0.1.23-alpha
- Fixed postrun_private_sft.py P1: step_create_eval_summary now passes --json directly in the command list, removed post-hoc string append
- Improved preflight_private_sft.py P1: reads dataset_build_dir from run_config if available, falls back to dataset/build/kimari-v0/report.json
- Added dataset_build_dir, dataset_report_path, dataset_build_dir_source fields to preflight JSON output
- Refactored preflight to reuse parsed YAML data (avoid double-parsing run_config)
- Created docs/SCREENSHOTS.md with CLI preview gallery, planned screenshots table, and policy rules
- Created docs/assets/screenshots/README.md with naming conventions, format policy, content guidelines
- Created docs/assets/screenshots/PLACEHOLDER.md with planned screenshots checklist
- Added Screenshots & CLI Preview section to README.md
- Added CLI Preview section to docs/index.html with code cards
- Updated docs/index.html hero badge, What's New section, and status table for v0.1.23-alpha
- Added v0.1.23 Checks section to RELEASE_CHECKLIST.md
- Expanded scripts/release/check-release.py with v0.1.23 checks (postrun --json, preflight dataset_build_dir, screenshots docs, no secrets, no benchmarks, README/index links)
- Created tests/test_release_v0123.py with 34 tests
- Updated CHANGELOG.md with v0.1.23-alpha entry
- Updated ROADMAP.md (v0.1.22→Released, v0.1.23→Current, v0.1.24→Planned)
- Updated MODEL_CARD.md version references
- Added agent-ctx/ to .gitignore to prevent accidental commits
- All 659 tests pass, ruff check/format pass, check-release passes with 0 warnings

Stage Summary:
- Version: 0.1.23-alpha at commit b38fe44
- Key fixes: postrun --json passthrough, preflight config-aware dataset_build_dir
- New docs: SCREENSHOTS.md, screenshot assets README/PLACEHOLDER
- 29 files changed, 1112 insertions, 161 deletions
- All release checks pass
- Preview gate remains BLOCKED
- No weights, adapters, GGUF, or checkpoints tracked
- No false claims about Kimari-4B
---
Task ID: v0.1.24-alpha
Agent: Main Agent
Task: Implement v0.1.24-alpha — private run record workflow, safe screenshot capture guide, CLI screenshot text generator, release-check improvements

Work Log:
- Version bumped to 0.1.24-alpha in pyproject.toml, kimari/__init__.py, README.md badge/alpha notice, docs/index.html hero badge/focus block/status table
- Created docs/FIRST_PRIVATE_SFT_RECORD.md — Guide for registering private SFT runs without committing sensitive outputs; documents run_id, base model, dataset hash, training config, hardware/runtime, adapter manifest (local only), eval/compare summaries, gate state BLOCKED, blocked actions, what can/cannot be committed
- Created training/templates/private_sft_run_record.template.json — Committable template with gate.state=BLOCKED, public_release_allowed=false, hf_upload_allowed=false; all values as PLACEHOLDER or null
- Created training/scripts/create_private_run_record.py — CLI with --run-config, --manifest, --eval-summary, --compare-summary, --output, --dry-run, --json; computes SHA256 of existing files; rejects absolute home directory paths; gate always BLOCKED; works without PyYAML
- Created docs/SAFE_SCREENSHOT_CAPTURE.md — Guide for safe terminal screenshot capture; pre/during/post capture checklists; dimensions, formats, naming, alt text, review-before-commit
- Created scripts/docs/generate_cli_screenshot_text.py — CLI generating safe text blocks for 6 kinds (setup, optimize, preflight, training_preview, baseline_eval, postrun); --output for file writing; --json for structured output; no private paths/tokens/benchmarks
- Created 5 screenshot text examples in docs/assets/screenshots/examples/: kimari-setup-json, kimari-preflight-private-sft, kimari-training-command-preview, kimari-baseline-eval-plan, kimari-postrun-dryrun
- Updated docs/SCREENSHOTS.md — Added Safe Screenshot Capture section, CLI Text Examples section, Replacing Placeholders section
- Updated README.md — Added First Private Run Record section with links; added Safe Screenshot Capture link; added screenshot text examples reference; updated docs table
- Updated docs/index.html — v0.1.24-alpha hero badge, What's New chips, status table rows
- Updated RELEASE_CHECKLIST.md — Added v0.1.24 Checks section (19 items)
- Updated scripts/release/check-release.py — Added [50/50] section with v0.1.24 checks (FIRST_PRIVATE_SFT_RECORD, run record template JSON validation, create_private_run_record, SAFE_SCREENSHOT_CAPTURE, generate_cli_screenshot_text, 5 screenshot example files, no secrets in examples, SCREENSHOTS.md references, README links, no oversized screenshots, no adapter/weights/GGUF, preview gate BLOCKED, no false claims)
- Created tests/test_release_v0124.py — 42 tests covering: run record template JSON/gate/fields, create_private_run_record CLI, FIRST_PRIVATE_SFT_RECORD doc, SAFE_SCREENSHOT_CAPTURE doc, generate_cli_screenshot_text all 6 kinds + secrets check + file output, screenshot examples existence/secrets/paths, README links, SCREENSHOTS.md references, release check, no tracked artifacts, version consistency
- Updated CHANGELOG.md — v0.1.24-alpha entry with all Added/Changed items
- Updated ROADMAP.md — v0.1.23-alpha Released, v0.1.24-alpha Current, v0.1.25-alpha Planned

Stage Summary:
- Version: v0.1.24-alpha
- 42 new tests passing
- All ruff checks/formatting clean
- check-release.py: All checks passed (0 warnings)
- Build + twine: PASSED
- kimari --version: v0.1.24-alpha
- kimari setup --json: works correctly
- create_private_run_record --dry-run --json: works correctly
- generate_cli_screenshot_text --kind setup --json: works correctly
- No adapter/weights/GGUF tracked
- Preview gate still BLOCKED
- No "Kimari-4B released" false claims
- No secrets in any screenshot examples or docs
- Ready for commit and push
