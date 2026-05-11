# Screenshot Assets

This directory contains screenshot assets for Kimari Local AI documentation.

## Naming Convention

Screenshots follow this naming pattern:

```
kimari-<command-or-feature>.<format>
```

Examples:
- `kimari-setup-json.png`
- `kimari-preflight-private-sft.png`
- `kimari-training-command-preview.png`
- `kimari-baseline-eval-plan.png`
- `kimari-postrun-dryrun.png`
- `kimari-optimize-json.png`
- `kimari-github-pages.png`

## Allowed Formats

- **PNG** — Preferred for terminal screenshots (lossless).
- **WebP** — Preferred for large images (better compression).

Other formats (JPG, GIF, SVG) are not accepted for screenshots.

## Recommended Dimensions

- **Width:** 800–1200px
- **Height:** As needed (avoid excessively tall screenshots)
- **DPI:** 144 (retina) or 72 (standard)
- **Max file size:** 500 KB per image (optimize before committing)

## Content Guidelines

### MUST NOT Include

- API keys, tokens, or authentication credentials
- Local file paths containing user names (e.g., `/home/username/`)
- Real training outputs (loss curves, adapter weights, raw eval results)
- Benchmark results that have not been reviewed
- Any content implying Kimari-4B is released or available

### MUST Include

- Descriptive alt text in the referencing Markdown
- Clear terminal output showing the command and its result
- A clean, minimal terminal environment (no extra prompts or decorations)

## Placeholder Policy

Until real screenshots are captured from a GPU environment, this directory contains:

- `PLACEHOLDER.md` — Checklist of screenshots to capture

**Do not create fake UI screenshots.** If no real capture is available, use code blocks in documentation instead.

## Optimization

Before committing any screenshot:

1. Optimize with `pngquant` or `optipng` for PNG files
2. Convert to WebP if file size exceeds 200 KB
3. Verify no secrets or private paths are visible
4. Add alt text in the referencing document

## Review Checklist

Before committing a screenshot:

- [ ] No API keys, tokens, or credentials visible
- [ ] No real user names or private paths visible
- [ ] No real training outputs or loss curves shown
- [ ] No unreviewed benchmark claims
- [ ] Does not imply Kimari-4B is released
- [ ] Image is optimized (under 500 KB)
- [ ] Alt text is provided in the referencing document
- [ ] File name follows the naming convention
