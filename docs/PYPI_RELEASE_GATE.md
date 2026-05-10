# PyPI Release Gate — v0.1.16-alpha

> **Purpose:** This document is the gate checklist for publishing `kimari-local-ai` to the real PyPI index.
> No release to PyPI real may proceed unless every item below is **APPROVED**.

---

## Checklist

Each item must be verified by a maintainer before the release proceeds.

### 1. TestPyPI Upload OK

- [ ] Package builds cleanly: `python -m build`
- [ ] Upload to TestPyPI succeeds: `twine upload --repository testpypi dist/*`
- [ ] TestPyPI page shows correct version `0.1.16-alpha`
- [ ] TestPyPI page shows correct metadata (description, classifiers, Python versions)

### 2. Clean Venv Install OK

- [ ] Create a fresh virtual environment: `python -m venv /tmp/kimari-test && source /tmp/kimari-test/bin/activate`
- [ ] Install from TestPyPI: `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai==0.1.16a0`
- [ ] Import succeeds: `python -c "import kimari; print(kimari.__version__)"`
- [ ] CLI entry point works: `kimari --version`

### 3. Wheel-Install Smoke OK

- [ ] Install from local `.whl` file succeeds in a clean venv
- [ ] `kimari --version` outputs `0.1.16-alpha`
- [ ] `kimari setup --json` returns valid JSON without errors
- [ ] `kimari start --dry-run` completes without errors
- [ ] `kimari doctor` runs and reports results (warnings are OK, errors are not)

### 4. Docs Current

- [ ] `CHANGELOG.md` has an entry for `0.1.16-alpha`
- [ ] `README.md` reflects current installation instructions
- [ ] `docs/` directory is up to date with current endpoints and CLI commands
- [ ] `RELEASE_CHECKLIST.md` has been reviewed for this version
- [ ] Version in `pyproject.toml` matches the version being released

### 5. Security Reviewed

- [ ] No secrets, tokens, or API keys in the source tree or distribution
- [ ] `kimari/security/tokens.py` does not write tokens to world-readable locations
- [ ] No hardcoded credentials in any file
- [ ] `.gitignore` excludes common secret file patterns
- [ ] No known vulnerabilities in dependencies (`pip audit` clean or issues documented)

### 6. No False Claims

- [ ] No claims that FastAPI support is stable (it remains experimental)
- [ ] No claims that the Responses API is supported
- [ ] No claims that `Kimari-4B` model is published on any model hub
- [ ] No claims that `llama-server` is bundled (it must be installed separately)
- [ ] Version classifiers in `pyproject.toml` reflect alpha status (`Development Status :: 3 - Alpha`)

### 7. No Secrets in Package

- [ ] `MANIFEST.in` does not include secret files
- [ ] Built wheel/tarball does not contain `.env`, `*.key`, `*.pem`, or token files
- [ ] `kimari token show` output is not captured in any log or test fixture

### 8. No GGUF Models in Package

- [ ] No `.gguf` files are included in the source distribution or wheel
- [ ] `.gitignore` excludes `*.gguf` from the repository
- [ ] `MANIFEST.in` does not include `models/` directory
- [ ] `pyproject.toml` package data does not include `.gguf` files

### 9. Code of Conduct Contact Reviewed

- [ ] `CODE_OF_CONDUCT.md` has a current, reachable contact email
- [ ] The contact email is not a personal email that could become invalid
- [ ] The contact is an active maintainer or a shared alias

---

## Result

After completing all checklist items, record the result:

| Status | Meaning |
|---|---|
| **APPROVED** | All items pass. Release to PyPI real may proceed. |
| **BLOCKED** | One or more items fail. Release is blocked until fixed. |
| **PENDING** | Checklist not yet completed for this version. |

---

## Current Status: **PENDING**

TestPyPI has not yet been validated with `v0.1.16-alpha`. The checklist above must be completed before any release to the real PyPI index.

**Do NOT publish to PyPI real yet.**

---

## Process

1. A maintainer creates a release branch: `release/0.1.16-alpha`
2. All checklist items are verified and checked off.
3. The result is recorded as **APPROVED**, **BLOCKED**, or **PENDING**.
4. Only when the result is **APPROVED** may `twine upload` be run against the real PyPI index.
5. If **BLOCKED**, the blocking issues must be resolved and the checklist re-verified.

### Who Can Approve

Only maintainers listed in `MAINTAINERS.md` may set the result to **APPROVED**.

### Audit Trail

Record the following when approving:

```
Version: 0.1.16-alpha
Date: YYYY-MM-DD
Approver: <maintainer name>
TestPyPI URL: https://test.pypi.org/project/kimari-local-ai/0.1.16a0/
Result: APPROVED | BLOCKED | PENDING
Notes: <any relevant notes>
```

---

*This document is part of Kimari Local AI v0.1.16-alpha. It must be updated for each release.*
