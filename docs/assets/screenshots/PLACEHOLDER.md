# Screenshot Placeholders

This file tracks screenshots planned for future capture from a real GPU environment.

## Status

**No screenshots captured yet.** All CLI outputs shown in documentation use code blocks, not images.

## Planned Screenshots

| # | File | Command | Status | Notes |
|---|------|---------|--------|-------|
| 1 | `kimari-setup-json.png` | `kimari setup --json` | ⬜ Not captured | Environment detection output |
| 2 | `kimari-preflight-private-sft.png` | `preflight_private_sft.py --json` | ⬜ Not captured | Preflight check results |
| 3 | `kimari-training-command-preview.png` | `run_training_command_preview.py --json` | ⬜ Not captured | Training command preview |
| 4 | `kimari-baseline-eval-plan.png` | `run_baseline_eval_plan.py --dry-run --json` | ⬜ Not captured | Baseline eval planning |
| 5 | `kimari-postrun-dryrun.png` | `postrun_private_sft.py --dry-run --json` | ⬜ Not captured | Post-training orchestration |
| 6 | `kimari-optimize-json.png` | `kimari optimize --profile test --json` | ⬜ Not captured | Performance optimization |
| 7 | `kimari-github-pages.png` | GitHub Pages landing | ⬜ Not captured | Landing page overview |

## Capture Guidelines

When capturing screenshots:

1. Use a clean terminal with default settings
2. Ensure no secrets, tokens, or private paths are visible
3. Do not show real training outputs or loss curves
4. Do not show benchmark results that haven't been reviewed
5. Do not imply Kimari-4B is released or available
6. Optimize image size before committing
7. Add alt text in the referencing Markdown document

## Rules

- **Do not invent UI.** If a feature doesn't exist yet, don't create a mock screenshot.
- **Do not fake data.** All outputs must come from actual CLI execution.
- **Do not show secrets.** Redact or use test fixtures before capturing.
