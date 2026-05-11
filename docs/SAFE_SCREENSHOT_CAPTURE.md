# Safe Screenshot Capture

Guidelines for capturing terminal and UI screenshots that are safe to commit to the Kimari Local AI repository.

---

## 1. Purpose

Screenshots are powerful documentation — they show the project in action. But they also carry risk. A single screenshot can accidentally leak secrets, expose private file paths, or make benchmark claims that haven't been reviewed.

Every screenshot committed to this repo must be **free of secrets, honest in its claims, and reviewed before it lands in git history**. Once a PNG is in the commit log, it's there forever — even if you delete the file in a later commit.

**Why this matters:**

- **No secrets leakage.** API keys, tokens, and passwords visible in a screenshot are compromised the moment the repo is pushed.
- **No false claims.** Showing unreviewed benchmark scores or implying a model is published when it isn't misleads users and damages credibility.
- **No private data.** Real usernames, personal paths, and private file contents have no place in public documentation.

---

## 2. Before Capture

Run through this checklist **before** you take the screenshot:

- [ ] **Clean terminal.** Clear history and previous command output. Run `clear` so only the command you intend to show and its output are visible.
- [ ] **No private user paths.** Replace `/home/username/` with `/home/user/`. Replace any real directory names that identify a person.
- [ ] **No tokens, API keys, or secrets visible.** Check environment variables, config file contents, and any printed output. Redact or use placeholder values (e.g., `sk-...`, `your-api-key-here`).
- [ ] **No raw eval outputs.** Evaluation results must not appear in screenshots unless they have gone through the review process described in [`PRIVATE_EVAL_RESULTS_POLICY.md`](./PRIVATE_EVAL_RESULTS_POLICY.md).
- [ ] **No real unreviewed benchmarks.** Benchmark numbers shown in a screenshot are treated as published claims. Do not include them until they have been reviewed.
- [ ] **Don't show Kimari-4B as published.** Kimari-4B has not been released. Do not capture screenshots that present it as an available or downloadable model.

---

## 3. During Capture

Follow these guidelines while taking the screenshot:

- **Use a clean terminal theme.** Dark background preferred. Avoid themes with distracting visual elements, custom prompts containing personal info, or unreadable color combinations.
- **Font size readable.** 14pt or larger. Smaller fonts are illegible in compressed images and inaccessible to readers with visual impairments.
- **Window size consistent.** Use a standard terminal size:
  - `80x24` for focused, single-command shots
  - `120x36` for wider output (tables, multi-column layouts)
- **Don't capture prompts that could contain private data.** If your shell prompt includes your username, hostname, or other identifying information, reset it to a generic value before capturing (e.g., `user@kimari:~$`).
- **Frame the shot tightly.** Only include the relevant terminal content. Crop out window chrome, desktop backgrounds, and unrelated applications.

---

## 4. After Capture

Review the screenshot carefully before it leaves your machine:

- [ ] **Check for any visible secrets.** Scan for API keys, tokens, passwords, connection strings, or authentication headers. Zoom in — small text can still be readable.
- [ ] **Check for any private paths.** Look for `/home/realname/`, personal directory names, or full paths that reveal system structure.
- [ ] **Check for any benchmark claims that haven't been reviewed.** Any number that looks like a score, metric, or ranking must go through review first.
- [ ] **Check that Kimari-4B is not implied as released.** The screenshot must not suggest that Kimari-4B is available for download or public use.
- [ ] **Optimize image size.** Compress PNG files (use `oxipng` or `optipng`). Consider WebP for further size reduction. Large screenshots bloat the repository.

---

## 5. Recommended Dimensions

| Resolution   | Use Case                               |
|--------------|----------------------------------------|
| 1280 × 720  | Standard documentation, README files   |
| 1920 × 1080 | Detailed output, full terminal sessions |

Scale your terminal window to match one of these resolutions before capturing.

---

## 6. Allowed Formats

| Format | Characteristics                  | When to Use                        |
|--------|----------------------------------|------------------------------------|
| PNG    | Lossless, widely supported       | Default choice for all screenshots |
| WebP   | Compressed, smaller file size    | When file size is a concern        |

Do **not** use JPEG — lossy compression introduces artifacts that make terminal text illegible.

---

## 7. Naming Convention

Screenshots must follow this pattern:

```
kimari-<command>.png
```

Examples:

- `kimari-setup-json.png` — output of `kimari setup --json`
- `kimari-optimize-json.png` — output of `kimari optimize --profile test --json`
- `kimari-start-dryrun.png` — output of `kimari start --dry-run`
- `kimari-api-dryrun.png` — output of `kimari api --dry-run`
- `kimari-preflight-json.png` — output of `python training/scripts/preflight_private_sft.py --json`
- `kimari-postrun-dryrun.png` — output of `python training/scripts/postrun_private_sft.py --dry-run --json`

Use lowercase, hyphen-separated words. The command segment should match the CLI command being demonstrated.

---

## 8. Alt Text

Every screenshot committed to the repo must have descriptive alt text when referenced in Markdown:

```markdown
![Output of the kimari setup command showing JSON configuration](./assets/screenshots/kimari-setup-json.png)
```

Alt text should describe **what the screenshot shows**, not just name the file. A screen reader user should understand the content without seeing the image.

---

## 9. Review Before Commit

**Never commit a screenshot you haven't manually reviewed.**

Before running `git add` on any image file:

1. Open the image at full resolution.
2. Re-run the After Capture checklist (Section 4).
3. Verify the filename matches the naming convention.
4. Verify alt text is prepared for the corresponding Markdown reference.
5. If anything fails, re-capture or edit — do not commit and "fix later."

Once an image is in git history, even deleted in a future commit, the data persists. Treat every screenshot commit as irreversible.

---

## Rules Summary

| Rule | Details |
|------|---------|
| No secrets/tokens | API keys, passwords, auth headers — never visible |
| No raw eval outputs | Evaluation results must be reviewed before appearing in screenshots |
| No unreviewed benchmark claims | Any score or metric is a claim; review first |
| Kimari-4B not released | Do not present Kimari-4B as published or available |
| No fake UI | Only capture real, working interfaces — no mockups presented as real |
| No HF tokens | See [HF Token Safety](HF_TOKEN_SAFETY.md) for token handling guidelines |
