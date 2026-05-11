# Hugging Face Token Safety Guide — Kimari Local AI

> **Document Type:** Security guide for HF credential handling  
> **Version:** v0.1.29-alpha  
> **Date:** 2026-05-31  
> **Status:** Active — applies to all contributors and maintainers

---

## Overview

This document defines the rules and best practices for handling Hugging Face (HF) access tokens within the Kimari Local AI project. A leaked HF token can result in unauthorized model uploads, repository tampering, or private data exposure. Because Kimari interacts with Hugging Face for model downloads and (eventually) model publishing, every contributor must understand how to handle HF tokens safely.

**Current project state:**

- The Adapter Preview Gate is **BLOCKED** — no uploads to Hugging Face are permitted under any circumstances (see [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md)).
- **Kimari-4B is NOT published.** No Hugging Face model repository exists. The planned repository `smouj/kimari-4b` has not been created.
- The only HF token usage today is for **downloading** base model weights and GGUF files.

---

## Table of Contents

1. [Never Paste Tokens in Chat, Issues, Commits, Logs, or Screenshots](#1-never-paste-tokens-in-chat-issues-commits-logs-or-screenshots)
2. [Use Environment Variables](#2-use-environment-variables)
3. [Use Tokens of Minimum Privilege](#3-use-tokens-of-minimum-privilege)
4. [Revoke Exposed Tokens Immediately](#4-revoke-exposed-tokens-immediately)
5. [Use `huggingface-cli login` Only in a Secure Local Environment](#5-use-huggingface-cli-login-only-in-a-secure-local-environment)
6. [Don't Save Tokens in the Repository](#6-dont-save-tokens-in-the-repository)
7. [Don't Include Tokens in Screenshots](#7-dont-include-tokens-in-screenshots)
8. [Don't Upload Anything to HF Until the Preview Gate Allows It](#8-dont-upload-anything-to-hf-until-the-preview-gate-allows-it)
9. [HF Jobs Token Usage](#9-hf-jobs-token-usage)
10. [Detecting Committed Tokens](#10-detecting-committed-tokens)
11. [What to Do If a Token Is Accidentally Committed](#11-what-to-do-if-a-token-is-accidentally-committed)

---

## 1. Never Paste Tokens in Chat, Issues, Commits, Logs, or Screenshots

An HF token that appears in any of the following is considered **exposed**, regardless of how quickly it is deleted:

| Medium | Risk |
|--------|------|
| **GitHub Issues / PRs** | Publicly visible; indexed by search engines and bots within seconds |
| **Commit messages** | Immutable in Git history; even `git push --force` cannot guarantee removal from forks or caches |
| **Code comments** | Committed to the repository; visible in blame, diffs, and archives |
| **Chat messages** (Discord, Slack, Zulip, etc.) | May be logged, archived, or visible to people outside the intended audience |
| **Log files** | May be committed, shared, or uploaded to issue trackers; `print(token)` is a common debugging mistake |
| **Screenshots** | Token strings are trivially OCR'd; images are shared and cached unpredictably |
| **Stack Overflow / forums** | Publicly indexed permanently |
| **Email** | Forwarded, archived on mail servers, potentially unencrypted in transit |

**Rule:** If you need to share a token for any reason, you are doing something wrong. Tokens should never be shared. If a collaborator needs access, they should create their own token from their own HF account.

---

## 2. Use Environment Variables

HF tokens must be provided to tools and scripts exclusively through **environment variables** — never hardcoded, never in config files committed to the repository, and never passed as command-line arguments (which are visible in `ps` output and shell history).

### Supported Environment Variables

| Variable | Purpose | Used By |
|----------|---------|---------|
| `HF_TOKEN` | Primary token for Hugging Face Hub API | `huggingface_hub`, `kimari pull`, `transformers` |
| `HUGGING_FACE_HUB_TOKEN` | Alternative variable (same purpose, older convention) | `huggingface_hub` (fallback) |

### How to Set Them

**Linux / macOS (bash or zsh):**

```bash
# Set for the current session only
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"

# Or set persistently in your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell):**

```powershell
# Set for the current session only
$env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"

# Or set persistently as a user environment variable
[System.Environment]::SetEnvironmentVariable("HF_TOKEN", "hf_xxxxxxxxxxxxxxxxxxxxxxxxxx", "User")
```

**Docker / Podman:**

```bash
# Pass the token at runtime (never bake it into the image)
docker run --rm -e HF_TOKEN="$HF_TOKEN" kimari-local-ai:latest
```

**RunPod / Cloud GPU:**

Use the environment variable injection feature provided by the platform. Never paste the token into a notebook cell or script file stored on the remote machine.

### `.env` Files (Local Only)

If you use a `.env` file for local development, it must:

1. Be listed in `.gitignore` (already excluded in this project)
2. Never be committed under any circumstances
3. Have file permissions restricted to the owner (`chmod 600 .env`)

```bash
# .env (NEVER COMMIT THIS FILE)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

```bash
# Verify .env is gitignored
git check-ignore .env  # Should output: .env
```

---

## 3. Use Tokens of Minimum Privilege

Hugging Face allows you to create tokens with different permission levels. **Always use the most restrictive token that satisfies your use case.**

| Token Type | Permissions | When to Use |
|------------|-------------|-------------|
| **Read** | Download public models and datasets | Downloading GGUF files with `kimari pull`; the only token type needed for normal usage |
| **Write** | Upload models, datasets; edit repos | Only during an HF release (see [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md)); must not be used for routine downloads |
| **Fine-grained** | Specific repos, specific actions | Preferred for CI/CD or release automation; scope to exact repositories needed |

### Rules

- **For `kimari pull` (downloading models):** Use a **read-only** token. No write access is needed.
- **For HF release uploads:** Use a **fine-grained write token** scoped to the specific repository (e.g., `smouj/kimari-4b`). Revoke it after the upload is complete.
- **Never use a fine-grained token with org-wide or account-wide write access** when a repo-scoped token would suffice.
- **Never use your personal "all-purpose" token** in scripts or CI pipelines. Create a dedicated token with the minimum scope.

### Current Project Status

Because the Adapter Preview Gate is **BLOCKED**, there is **no valid reason to use a write-capable HF token** in this project today. Any write operation to Hugging Face is unauthorized until the gate transitions to `APPROVED_FOR_PUBLIC_PREVIEW`.

---

## 4. Revoke Exposed Tokens Immediately

If an HF token has been exposed — whether in a chat message, a commit, a log file, a screenshot, or any other medium — treat it as compromised. **There is no safe window.** Bots scan public GitHub repositories for leaked secrets within seconds of a push.

### Steps to Revoke

1. **Go to** [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. **Find the exposed token** in your token list
3. **Click "Delete"** (not "Disable" — delete it entirely)
4. **Create a new token** with the same minimum privileges if needed
5. **Update the environment variable** on all machines and services that used the old token

### After Revocation

- Audit what the compromised token could have accessed. If it had write permissions, check the HF repositories for unauthorized changes.
- Follow the incident response steps in [Section 10](#10-what-to-do-if-a-token-is-accidentally-committed) if the token was committed to Git.

---

## 5. Use `huggingface-cli login` Only in a Secure Local Environment

The `huggingface-cli login` command stores your token in a local credentials file:

| OS | Path |
|----|------|
| Linux | `~/.cache/huggingface/token` |
| macOS | `~/.cache/huggingface/token` |
| Windows | `%USERPROFILE%\.cache\huggingface\token` |

### Rules

- **Only run `huggingface-cli login` on a machine you control** — your personal workstation, not a shared server, CI runner, or cloud instance that others can access.
- **Never run it inside a Docker container** that will be pushed or shared — the token file persists in the image layer.
- **Never run it on a multi-user system** where other users might read `~/.cache/huggingface/token`.
- **Set restrictive permissions** on the token file after login:

  ```bash
  chmod 600 ~/.cache/huggingface/token
  ```

- **Prefer environment variables** over `huggingface-cli login` when possible — environment variables are not stored in a file that could be accidentally committed or included in a Docker image.

### On Cloud GPU Instances (RunPod, Lambda, etc.)

- Do **not** run `huggingface-cli login` on cloud instances.
- Instead, use the `HF_TOKEN` environment variable set through the platform's secret injection.
- If you must log in on a cloud instance, **log out** (`huggingface-cli logout`) and **delete the token file** before terminating the instance.

---

## 6. Don't Save Tokens in the Repository

No form of HF token should ever be committed to the `kimari-local-ai` repository — not in code, not in config files, not in documentation, not in test fixtures, and not in `.env` files.

### What This Means

| Prohibited | Examples |
|------------|----------|
| **Hardcoded tokens** | `HF_TOKEN = "hf_xxx"` in Python, YAML, JSON, or shell scripts |
| **Tokens in config files** | `config/kimari.models.json`, `training/configs/*.yaml`, `.env` (committed) |
| **Tokens in test fixtures** | `tests/fixtures/*.json`, mock data, integration test configs |
| **Tokens in documentation** | Example commands that include a real token string |
| **Tokens in CI/CD configs** | GitHub Actions workflows must use `secrets.HF_TOKEN`, not literal strings |
| **Tokens in Jupyter notebooks** | Notebook cells are committed; `os.environ["HF_TOKEN"]` is fine, literal strings are not |

### What's Allowed

```python
# CORRECT: Read from environment variable
import os
token = os.environ.get("HF_TOKEN")
```

```python
# WRONG: Hardcoded token
token = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"  # NEVER DO THIS
```

### `.gitignore` Coverage

The project `.gitignore` already excludes:

```
.env
.env.*
*.secret
```

If you create any new files that contain secrets, ensure they are covered by `.gitignore` **before** you write to them.

---

## 7. Don't Include Tokens in Screenshots

Screenshots are a frequently overlooked vector for token leaks. A token visible in a terminal, environment variable listing, or config file viewer can be extracted with OCR in seconds.

### Rules for Screenshots

1. **Never take a screenshot** of a terminal that has a token visible — not even a `print()` output, not even in an `env` command listing, not even partially.
2. **Before capturing a screenshot**, close or clear any terminal tabs that display tokens.
3. **Redact tokens** before sharing screenshots — use a solid black bar or mosaic, not a blur (blurs can sometimes be reversed).
4. **Check the full image** before uploading — scroll through it looking for any string starting with `hf_`.
5. **Use the project's safe screenshot process** documented in [SAFE_SCREENSHOT_CAPTURE.md](SAFE_SCREENSHOT_CAPTURE.md).

### Example Mistakes

```bash
# DON'T screenshot this — the token is visible
$ echo $HF_TOKEN
hf_xxxxxxxxxxxxxxxxxxxxxxxxxx

# DON'T screenshot this either — it shows the token
$ env | grep HF
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxx

# If you need to verify the token is set, check its length or first 4 chars only
$ echo "Token set: ${HF_TOKEN:+yes}" && echo "Length: ${#HF_TOKEN}"
Token set: yes
Length: 35
```

---

## 8. Don't Upload Anything to HF Until the Preview Gate Allows It

The Adapter Preview Gate (see [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md)) governs all Hugging Face uploads. The current gate state is:

> **BLOCKED — No HF uploads are permitted.**

This means:

| Action | Allowed? |
|--------|----------|
| Download models from HF | Yes (read-only token) |
| Upload adapter weights to HF | **No** |
| Upload GGUF quantizations to HF | **No** |
| Upload eval results to HF | **No** |
| Create or modify the `smouj/kimari-4b` repository | **No** |
| Upload any file to any HF repository as part of this project | **No** |

### When Will Uploads Be Allowed?

Uploads will only be allowed when the adapter reaches the `APPROVED_FOR_PUBLIC_PREVIEW` state in the preview gate, which requires:

1. License verification
2. Secret/data scan clearance
3. Baseline evaluation comparison
4. KimariFit manual review
5. Safety review with no regression
6. Model card updated with real (not placeholder) data
7. Explicit written maintainer approval

**None of these conditions have been met.** No upload should be attempted.

### No HF Repository Exists

The repository `smouj/kimari-4b` has **not been created** on Hugging Face. There is nothing to upload to. Any attempt to push to this repository will fail (and should fail).

For the private SFT handoff process — where trained adapter artifacts are transferred securely between local machines — see [FIRST_PRIVATE_SFT_HANDOFF.md](FIRST_PRIVATE_SFT_HANDOFF.md). This process does **not** involve Hugging Face.

---

## 9. HF Jobs Token Usage

Hugging Face Jobs requires authentication to submit workloads. The same token safety rules apply with additional considerations:

### Rules for HF Jobs

- **Never pass `--token` in any saved command** — Commands may be committed, logged, or shared
- **Prefer local login** — Use `hf auth login` or `huggingface-cli login` on your local machine
- **Review HF Jobs logs before sharing** — Job logs may contain environment variables or paths that reveal tokens
- **Sanitize job outputs** — Before committing any smoke test summary, run `scan_for_secrets.py`

### HF Jobs Does Not Require Tokens in Commands

The `hf jobs` CLI reads authentication from your local credential store. You never need to pass a token:

```bash
# CORRECT: Use local auth
hf auth login
hf jobs run --flavor a10g-small pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel bash -lc 'nvidia-smi'

# WRONG: Never pass tokens in commands
hf jobs run --token hf_xxx ...  # NEVER DO THIS
```

### When Using Cloud GPU for HF Jobs

- **Do not login on the cloud instance** if possible
- **If you must login, logout before terminating** — `hf auth logout`
- **Delete the token file** — `rm ~/.cache/huggingface/token`

---

## 10. Detecting Committed Tokens

If a token is accidentally committed, early detection is critical. The sooner you discover a leak, the less time an attacker has to exploit it.

### Automated Scanning: `scan_for_secrets.py`

The project provides a dedicated secret scanning script:

```
scripts/security/scan_for_secrets.py
```

**What it scans for:**

- HF token patterns (`hf_` prefix followed by alphanumeric characters)
- Generic secret patterns (API keys, private keys, bearer tokens)
- Common secret file names (`.env`, `*.secret`, `credentials.json`)
- Known dangerous patterns in Python, YAML, JSON, and shell scripts

**How to run it:**

```bash
# Scan the entire repository
python scripts/security/scan_for_secrets.py

# Scan a specific directory or file
python scripts/security/scan_for_secrets.py training/configs/

# Scan staged changes before committing
python scripts/security/scan_for_secrets.py --staged
```

**Integrate into your workflow:**

```bash
# Add as a pre-commit hook (manual)
echo 'python scripts/security/scan_for_secrets.py --staged' >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Other Detection Methods

| Method | How to Use |
|--------|------------|
| **GitHub secret scanning** | Enabled by default on public repos; alerts sent to repo admins and the token owner |
| **`git log` search** | `git log -p -S "hf_" --all` — searches full diff history for the `hf_` prefix |
| **`git diff` check** | `git diff --cached | grep -i "hf_"` — check staged changes before committing |
| **Hugging Face security alerts** | HF may email you if they detect a token in a public GitHub repo |
| **Manual review** | Before committing, review your `git diff` for any strings starting with `hf_` |

### What a Leaked Token Looks Like

HF tokens follow these patterns:

```
hf_xxxxxxxxxxxxxxxxxxxxxxxxxx          # Read token (34 chars after hf_)
hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Write token (38+ chars after hf_)
```

If you see any string starting with `hf_` in your diff, **stop and investigate** before committing.

---

## 11. What to Do If a Token Is Accidentally Committed

This is a security incident. Treat it with urgency.

### Immediate Response (Within Minutes)

1. **Revoke the token** — Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and **delete** the compromised token immediately. Do not just disable it — delete it.

2. **Create a replacement token** — Generate a new token with the same (minimum) privileges and update the environment variable on all machines that used the old token.

3. **Assess the damage** — Check what the token had access to:
   - If it was a **read-only token**: The risk is limited (someone could download gated models under your account).
   - If it was a **write token**: Check all repositories the token could access for unauthorized uploads, modifications, or deletions. Check the HF activity log at `https://huggingface.co/settings/tokens` for recent usage.

### Cleaning Git History

Simply removing the token from the current code and pushing a new commit is **not sufficient**. The token remains in the Git history and can be found by anyone who clones or forks the repository.

#### Option A: `git filter-repo` (Recommended)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove the file or string from all history
git filter-repo --invert-paths --path .env
# Or remove a specific string:
git filter-repo --replace-text <(echo 'hf_YOUR_LEAKED_TOKEN==>REDACTED')
```

#### Option B: BFG Repo-Cleaner

```bash
# Install BFG
# https://rtyley.github.io/bfg-repo-cleaner/

# Remove the token string from all history
echo "hf_YOUR_LEAKED_TOKEN" > banned-strings.txt
bfg --replace-text banned-strings.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

#### After History Cleaning

1. **Force-push** the cleaned history: `git push --force --all`
2. **Notify all collaborators** — anyone with a clone or fork must re-clone; their local history still contains the token.
3. **Invalidate GitHub Actions caches** — cached state may contain the old history.
4. **Request GitHub cache flush** — GitHub Support can flush their server-side caches if contacted.

#### If You Cannot Clean the History

If the repository is public and the token was pushed more than a few minutes ago, assume it has been harvested by automated scanners. Revoking the token is the most important step. History cleaning is a defense-in-depth measure but cannot guarantee complete removal from all caches, forks, and mirrors.

### Incident Reporting

Report the incident to the project maintainer so it can be documented and processes can be improved:

- **Email:** [smouj013@users.noreply.github.com](mailto:smouj013@users.noreply.github.com)
- **Do NOT** open a public GitHub issue describing the leak (that would amplify it)

Include in your report:

1. When the token was committed
2. Which token type was exposed (read-only, write, fine-grained)
3. When the token was revoked
4. Whether Git history was cleaned
5. What repositories the token had access to

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│                HF TOKEN SAFETY — QUICK REFERENCE             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ DO                        ❌ DON'T                       │
│  ───                         ─────                           │
│  Use environment variables    Paste tokens in chat/issues    │
│  Use read-only tokens for     Use write tokens for downloads │
│    downloads                  Hardcode tokens in source      │
│  Revoke exposed tokens       Commit .env files              │
│    immediately                Include tokens in screenshots  │
│  Run scan_for_secrets.py     Upload to HF (gate is BLOCKED) │
│  Use huggingface-cli login   Use huggingface-cli login      │
│    on your own machine only    on shared/cloud machines      │
│  Delete token files on       Assume "just a read token"     │
│    cloud instances before       is harmless                  │
│    termination                                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  GATE STATUS: BLOCKED — NO HF UPLOADS ALLOWED               │
│  KIMARI-4B:   NOT PUBLISHED — NO HF REPO EXISTS             │
│  SCAN SCRIPT: scripts/security/scan_for_secrets.py           │
│  REVOKE AT:   https://huggingface.co/settings/tokens        │
└──────────────────────────────────────────────────────────────┘
```

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Release gate — currently BLOCKED; governs when HF uploads are permitted |
| [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md) | Full HF release process; includes its own "no tokens in repo" rules |
| [HF_PLACEHOLDER_PLAN.md](HF_PLACEHOLDER_PLAN.md) | Placeholder repo rules; no tokens allowed in placeholder files |
| [SAFE_SCREENSHOT_CAPTURE.md](SAFE_SCREENSHOT_CAPTURE.md) | Screenshot safety procedures including token redaction |
| [SECURITY.md](../SECURITY.md) | General project security policy |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can/cannot be committed from training runs (no tokens) |
| [FIRST_PRIVATE_SFT_HANDOFF.md](FIRST_PRIVATE_SFT_HANDOFF.md) | Private SFT handoff process — secure transfer without HF |
| [PRIVACY.md](../PRIVACY.md) | Privacy policy — no tokens or secrets collected |

---

*This document is part of Kimari Local AI. The Adapter Preview Gate is BLOCKED. Kimari-4B is not published. No Hugging Face repository exists. HF tokens must never be committed, shared, or exposed. If a token is compromised, revoke it immediately and follow the incident response steps in this guide.*
