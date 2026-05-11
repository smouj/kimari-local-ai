# Showcase Plan

> How to present Kimari honestly and attractively — without fake benchmarks, without claiming Kimari-4B is published, and without selling vaporware.

---

## Principles

1. **Honest first** — Never claim features that don't exist yet
2. **Visual appeal** — Show, don't just tell
3. **Real commands** — Only show commands that actually work
4. **No fake numbers** — Never invent benchmark scores or performance claims
5. **Kimari-4B status: not released** — Always clear about this

---

## README Visual Plan

### Sections to Add (small, not overwhelming)

1. **Performance & Benchmarking** — Link to `kimari benchmark --dry-run` and `kimari tune --dry-run`. Explain that dry-run generates plans, not measurements.
2. **Security / HF Token Safety** — Link to `docs/HF_TOKEN_SAFETY.md` and mention the secret scanner.
3. **Showcase / Screenshots** — Link to `docs/SCREENSHOTS.md` and mention safe screenshot capture.

### Quick Start Visual

Already exists but could be enhanced with:
- Visual command table (not just code blocks)
- "Why Kimari?" section (3-5 bullets, honest)
- Hardware-first message ("GTX 1060/1080 first")

### Command Table

| Command | What It Does |
|---------|-------------|
| `kimari doctor` | System diagnostics |
| `kimari setup --write` | Detect and configure your environment |
| `kimari benchmark --dry-run` | Generate a benchmark plan (no execution) |
| `kimari tune --dry-run` | Get recommended settings (estimates) |
| `kimari optimize` | Analyze profile and recommend settings |
| `kimari start` | Start inference server |
| `kimari chat` | Chat with your model |

---

## GitHub Pages Visual Plan

### New Cards/Sections

1. **Benchmark Dry-Run** — Show `kimari benchmark --dry-run --json` output
2. **Tune Dry-Run** — Show `kimari tune --dry-run --json` output
3. **Secret Scanner** — Show `scan_for_secrets.py --json` output
4. **Screenshots** — Link to safe CLI preview
5. **Kimari-4B Status** — "Still not released" (honest, not misleading)

### CLI Visual Section

Show the flow: `setup → optimize → start → chat`

### Hardware Table

Already exists but ensure it's accurate and links to profiles.

### Kimari-4B Roadmap

Honest section:
- Base model accepted for private SFT (SmolLM3-3B)
- No weights released
- No benchmarks claimed
- Preview gate: BLOCKED

---

## Hugging Face Placeholder (docs-only)

If created, the HF placeholder should be:

```
smouj/kimari-4b
Status: no weights released
No GGUF
No benchmarks  
No adapter
```

This positions the brand honestly without misleading users.

**Do NOT create this until v0.1.26+ when there's something more to show.**

---

## Reddit/GitHub Launch Checklist

When Kimari is ready for a broader launch (v0.2+):

- [ ] Real measured benchmarks available
- [ ] At least 3 safe screenshots
- [ ] README is polished and honest
- [ ] GitHub Pages is up-to-date
- [ ] No fake claims anywhere
- [ ] Quick start works end-to-end
- [ ] `kimari doctor` passes on clean install
- [ ] Community docs are complete
- [ ] LICENSE, CODE_OF_CONDUCT, CONTRIBUTING are current

---

## What We Do NOT Do

- ❌ Fake benchmark numbers
- ❌ "Kimari-4B published" claims
- ❌ Screenshots with real tokens/secrets
- ❌ Comparisons with other tools using invented data
- ❌ Screenshots of non-existent commands
- ❌ Performance claims without measurement

---

## See Also

- [Performance Tuning Plan](PERFORMANCE_TUNING_PLAN.md) — How to measure and tune performance
- [Screenshots & CLI Preview](SCREENSHOTS.md) — Safe CLI output examples
- [Safe Screenshot Capture](SAFE_SCREENSHOT_CAPTURE.md) — Guide for safe screenshots
- [HF Token Safety](HF_TOKEN_SAFETY.md) — Secure token handling
