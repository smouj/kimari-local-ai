# Secret Scanner Policy — Kimari Local AI

> **Document Type:** Policy for the project secret scanner (`scripts/security/scan_for_secrets.py`)
> **Applies To:** All contributors, maintainers, and CI pipelines
> **Scanner Version:** 1.1.0+

---

## Table of Contents

1. [What the Scanner Detects](#1-what-the-scanner-detects)
2. [Safe Placeholders](#2-safe-placeholders)
3. [How to Mark Placeholders](#3-how-to-mark-placeholders)
4. [How to Review Git History](#4-how-to-review-git-history)
5. [What to Do If a Real Token Appears](#5-what-to-do-if-a-real-token-appears)
6. [Running the Scanner](#6-running-the-scanner)

---

## 1. What the Scanner Detects

The scanner (`scripts/security/scan_for_secrets.py`) searches all text files in the repository for patterns that indicate leaked secrets or sensitive data. Each pattern is assigned a severity level:

### Secret Patterns

| Pattern | Description | Severity |
|---------|-------------|----------|
| `hf_[a-zA-Z0-9]{30,}` | Hugging Face tokens (`hf_` followed by 30+ alphanumeric characters) | **Critical** |
| `sk-[a-zA-Z0-9]{20,}` | OpenAI API keys (`sk-` followed by 20+ alphanumeric characters) | **Critical** |
| `api_key\s*=\s*['"][^'"]{8,}['"]` | API key assignments (e.g., `api_key = "abcdefgh"`) | **High** |
| `password\s*=\s*['"][^'"]{4,}['"]` | Password assignments (e.g., `password = "pass"`) | **High** |
| `token\s*=\s*['"][^'"]{8,}['"]` | Token assignments (e.g., `token = "secretvalue"`) | **High** |
| `-----BEGIN (RSA\|EC\|DSA\|OPENSSH )?PRIVATE KEY-----` | Private keys in PEM format | **Critical** |
| `AWS_ACCESS_KEY_ID\s*=\s*['"][A-Z0-9]{16,}['"]` | AWS access key assignments | **Critical** |
| `Authorization:\s*Bearer\s+[a-zA-Z0-9._-]{10,}` | Bearer tokens in HTTP headers | **High** |

### Sensitive Path Patterns

| Pattern | Description | Severity |
|---------|-------------|----------|
| `/home/[a-z][a-z0-9_]*/` | Linux home path with a real username (e.g., `/home/john/`) | **Medium** |
| `/Users/[a-z][a-z0-9_]*/` | macOS home path with a real username (e.g., `/Users/jane/`) | **Medium** |
| `C:\Users\[a-z][a-z0-9_]*\` | Windows user path with a real username (e.g., `C:\Users\bob\`) | **Medium** |

> **Note on sensitive paths:** Generic usernames like `user`, `username`, `admin`, `test`, `example`, `placeholder`, `your_user`, `youruser`, and `name` are considered safe and will not trigger a finding. Only paths containing potentially real usernames are flagged.

### Skipped Files

The scanner automatically skips:

- **Binary and media files:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.ico`, `.woff`, `.woff2`, `.ttf`, `.eot`, `.otf`, `.mp4`, `.mp3`, `.wav`, `.ogg`, `.zip`, `.tar`, `.gz`, `.bz2`, `.xz`, `.7z`, `.rar`
- **Compiled files:** `.pyc`, `.pyo`, `.so`, `.dll`, `.dylib`, `.exe`, `.bin`
- **Model files:** `.safetensors`, `.gguf`, `.pt`, `.pth`, `.ckpt`, `.onnx`
- **Database files:** `.db`, `.sqlite`, `.lock`
- **Directories:** `.git`, `__pycache__`, `node_modules`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.tox`, `dist`, `build`, `.eggs`, `*.egg-info`, `.venv`, `venv`, `env`

---

## 2. Safe Placeholders

The scanner recognizes certain placeholder strings that are safe to use in documentation, examples, and configuration templates. If a line matches a secret pattern but the matched content is exactly one of these placeholders, the finding is suppressed.

### Allowed Placeholder Strings

| Placeholder | Use Case |
|-------------|----------|
| `hf_...` | Generic HF token placeholder (exactly `hf_` followed by only dots) |
| `hf_your_token_here` | Explicit "fill in your token" placeholder |
| `hf_YOUR_TOKEN_HERE` | Uppercase variant of the above |
| `<HF_TOKEN>` | Angle-bracket placeholder for HF tokens |
| `your-api-key` | Generic API key placeholder |
| `your_api_key` | Underscore variant of the above |
| `sk-...` | Generic OpenAI-style key placeholder (exactly `sk-` followed by only dots) |
| `<token>` | Angle-bracket placeholder for any token |
| `<API_KEY>` | Angle-bracket placeholder for API keys |

### Additional Safe Context Strings

The scanner also suppresses findings when the line contains any of these contextual strings:

- `your-api-key`
- `your_api_key`
- `replace_with`
- `<your`
- `example.com`
- `sk-...`
- `hf_...`

### Inline Markers

A line containing any of the following markers is skipped entirely, regardless of what patterns it matches:

| Marker | Language |
|--------|----------|
| `# safe-example` | Python, Shell, YAML |
| `# safe-placeholder` | Python, Shell, YAML |
| `// safe-placeholder` | JavaScript, TypeScript, C, C++ |
| `# placeholder` | Python, Shell, YAML |
| `// placeholder` | JavaScript, TypeScript, C, C++ |
| `# example-only` | Python, Shell, YAML |
| `// example-only` | JavaScript, TypeScript, C, C++ |
| `<!-- safe-example -->` | HTML, Markdown |
| `<!-- placeholder -->` | HTML, Markdown |

---

## 3. How to Mark Placeholders

### In Code and Configuration

Use safe placeholder strings in assignment patterns:

```python
# CORRECT — safe placeholder
api_key = "<API_KEY>"               # safe-example
token = "<token>"                    # safe-example
hf_token = "hf_your_token_here"      # safe-example
openai_key = "sk-..."                # safe-example
```

```yaml
# CORRECT — safe placeholder
api_key: <API_KEY>          # safe-placeholder
password: your-api-key       # safe-placeholder
token: <token>               # safe-placeholder
```

```bash
# CORRECT — safe placeholder
export HF_TOKEN="hf_..."     # safe-example
```

### In Documentation (Markdown)

Use angle-bracket placeholders or explicit "your token" strings:

```markdown
Set your HF token:
export HF_TOKEN="<HF_TOKEN>"

Or configure your API key:
api_key = "<API_KEY>"
```

### In Security Guide Files

Security guide files (listed in `SECURITY_GUIDE_FILES` in the scanner) are **no longer skipped entirely**. They are scanned line by line, and only lines containing safe placeholders or inline markers are allowed. The affected files are:

- `HF_TOKEN_SAFETY.md`
- `SECURITY.md`
- `PRIVACY.md`
- `REVERSE_PROXY_AUTH.md`
- `PRIVATE_EVAL_RESULTS_POLICY.md`

When writing examples in these files, always use safe placeholders:

```markdown
<!-- Before: WRONG — will trigger a finding -->
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"

<!-- After: CORRECT — safe placeholder -->
export HF_TOKEN="hf_..."                      <!-- safe-example -->
```

```python
# WRONG — will trigger a finding
token = "hf_abc123def456ghi789jkl012mno345"

# CORRECT — safe placeholder
token = "hf_your_token_here"   # safe-example
```

### Summary of Marking Rules

1. **Always use safe placeholder strings** from the list in [Section 2](#2-safe-placeholders).
2. **Add an inline marker** on the same line for extra clarity (e.g., `# safe-example`).
3. **Never use realistic-looking dummy values** — `hf_abc123xyz` or `sk-test123456` will still trigger a finding because they match the regex pattern.
4. **Security guide files are scanned**, so use safe placeholders there too — they are not exempt.

---

## 4. How to Review Git History

The scanner only checks the **current file state**. Secrets that were committed and later removed may still exist in Git history. To review history for leaked secrets:

### Manual Steps

```bash
# Search full diff history for HF token patterns
git log -p --all | grep -i "hf_"

# Search for other secret patterns
git log -p --all | grep -i "sk-"
git log -p --all | grep -i "api_key"
git log -p --all | grep -i "BEGIN.*PRIVATE KEY"
```

### Using the Scanner

```bash
# Run the scanner with the history reminder flag
python scripts/security/scan_for_secrets.py --paths . --json --include-history-note
```

The `--include-history-note` flag prints a reminder after the scan:

```
NOTE: This scanner only checks the current file state. Secrets removed in past
commits may still exist in git history. Consider manually reviewing git log or
using tools like git-secrets or trufflehog to scan history.
```

### If You Find a Token in History

If you discover a real token in Git history:

1. **Revoke it immediately** on the platform (see [Section 5](#5-what-to-do-if-a-real-token-appears)).
2. **Rewrite Git history** to remove the token from all commits.
3. **Run the scanner** after cleanup to confirm no traces remain.

---

## 5. What to Do If a Real Token Appears

This is a **security incident**. Act immediately.

### Emergency Steps

1. **Revoke the token immediately** on the platform where it was issued:

   | Platform | Revocation URL |
   |----------|---------------|
   | Hugging Face | [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
   | OpenAI | [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
   | AWS | [https://console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/) |

2. **Do NOT just delete the line.** Removing the token from the current code is not sufficient — it remains in Git history and can be found by anyone who clones or forks the repository.

3. **Rewrite Git history** using one of these methods:

   **Option A: `git filter-repo` (recommended)**

   ```bash
   pip install git-filter-repo

   # Remove a specific string from all history
   git filter-repo --replace-text <(echo 'hf_YOUR_LEAKED_TOKEN==>REDACTED')

   # Or remove an entire file
   git filter-repo --invert-paths --path .env
   ```

   **Option B: BFG Repo-Cleaner**

   ```bash
   echo "hf_YOUR_LEAKED_TOKEN" > banned-strings.txt
   bfg --replace-text banned-strings.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

4. **Run the scanner after cleanup** to confirm no traces remain:

   ```bash
   python scripts/security/scan_for_secrets.py --paths . --json
   ```

5. **Document the incident.** Report it to the project maintainer privately:

   - **Email:** [smouj013@users.noreply.github.com](mailto:smouj013@users.noreply.github.com)
   - **Do NOT** open a public GitHub issue describing the leak.

   Include in your report:
   - When the token was committed
   - Which token type was exposed (read-only, write, fine-grained)
   - When the token was revoked
   - Whether Git history was cleaned
   - What resources the token had access to

### After History Cleaning

- **Force-push** the cleaned history: `git push --force --all`
- **Notify all collaborators** — anyone with a clone or fork must re-clone.
- **Invalidate CI caches** — cached state may contain the old history.
- **Request GitHub cache flush** — contact GitHub Support if needed.

---

## 6. Running the Scanner

### Basic Usage

```bash
# Scan specific paths
python scripts/security/scan_for_secrets.py --paths README.md docs training

# Scan the entire repository
python scripts/security/scan_for_secrets.py --paths . --json

# Scan with git history reminder
python scripts/security/scan_for_secrets.py --paths . --json --include-history-note
```

### Command-Line Options

| Flag | Description |
|------|-------------|
| `--paths <path...>` | One or more files or directories to scan (required) |
| `--json` | Output structured JSON instead of human-readable text |
| `--include-history-note` | Print a reminder to manually check Git history for secrets |

### Output Format

**Human-readable (default):**

```
⚠️  Found 2 potential secret(s):

  🔴 [CRITICAL] src/config.py:42
     Pattern: HF token (hf_...)
     Content: hf_abc123def456ghi789jkl012mno345pqr678

  🟠 [HIGH] src/api.py:15
     Pattern: API key assignment
     Content: api_key = "sk-live-xxxxxxxxxxxx"
```

**JSON (`--json`):**

```json
{
  "scanner": "scan_for_secrets.py",
  "version": "1.1.0",
  "paths_scanned": ["/path/to/repo"],
  "total_findings": 2,
  "critical": 1,
  "high": 1,
  "medium": 0,
  "findings": [
    {
      "file": "src/config.py",
      "line": 42,
      "pattern": "HF token (hf_...)",
      "severity": "critical",
      "content": "hf_abc123def456ghi789jkl012mno345pqr678"
    }
  ]
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | No critical findings |
| `1` | One or more critical findings detected — do not commit |

### Integrating into Your Workflow

**Pre-commit hook:**

```bash
echo 'python scripts/security/scan_for_secrets.py --paths .' >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**CI pipeline:**

The project's CI workflow (`scripts/security/scan_for_secrets.py`) can be integrated into GitHub Actions to fail builds when critical secrets are detected.

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────────┐
│               SECRET SCANNER — QUICK REFERENCE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SCANNER:   python scripts/security/scan_for_secrets.py             │
│  FULL SCAN: python scripts/security/scan_for_secrets.py --paths .  │
│  JSON:      python scripts/security/scan_for_secrets.py --paths .  │
│               --json                                                │
│  HISTORY:   python scripts/security/scan_for_secrets.py --paths .  │
│               --json --include-history-note                         │
│                                                                     │
│  DETECTS:   HF tokens, OpenAI keys, API key/password/token         │
│             assignments, PEM private keys, AWS keys, Bearer         │
│             tokens, sensitive home paths                            │
│                                                                     │
│  SAFE:      hf_..., hf_your_token_here, <HF_TOKEN>,               │
│             your-api-key, sk-..., <token>, <API_KEY>               │
│             + inline markers: # safe-example, // safe-placeholder, │
│               <!-- safe-example -->                                 │
│                                                                     │
│  EMERGENCY: 1. Revoke token immediately                            │
│             2. Rewrite git history (do NOT just delete the line)   │
│             3. Run scanner to confirm cleanup                       │
│             4. Document the incident                                │
│                                                                     │
│  REVOKE:    HF → huggingface.co/settings/tokens                    │
│             OpenAI → platform.openai.com/api-keys                   │
│             AWS → console.aws.amazon.com/iam/                       │
│                                                                     │
│  REPORT:    smouj013@users.noreply.github.com (private, no issues) │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Detailed HF token handling guide; uses safe placeholders scanned by this policy |
| [SECURITY.md](../SECURITY.md) | General project security policy |
| [PRIVACY.md](../PRIVACY.md) | Privacy policy — no tokens or secrets collected |
| [REVERSE_PROXY_AUTH.md](REVERSE_PROXY_AUTH.md) | Reverse proxy authentication guide; contains Bearer token examples |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Release gate — requires secret scan clearance before HF uploads |
| [SAFE_SCREENSHOT_CAPTURE.md](SAFE_SCREENSHOT_CAPTURE.md) | Screenshot safety procedures including token redaction |

---

*This document defines the policy for `scripts/security/scan_for_secrets.py` in the Kimari Local AI project. All contributors must follow these guidelines. If a real secret is detected, treat it as a security incident and follow the emergency steps immediately.*
