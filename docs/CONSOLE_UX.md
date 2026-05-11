# Console UX — Output Style Guide

> **Document Type:** Design specification
> **Applies to:** Kimari Local AI v0.1.27-alpha
> **Source module:** `kimari/utils/colors.py`, `kimari/cli/main.py`

---

## Overview

This document defines the console output style for Kimari CLI. The goal is clean, aligned, Unicode-simple output that works reliably across terminals — including Windows Command Prompt, PowerShell, and minimal terminal emulators.

**Design principles:**

1. **No `rich` dependency** — all formatting uses `kimari/utils/colors.py` (ANSI codes)
2. **Unicode simple** — avoid emoji or symbols that break Windows terminals
3. **Aligned columns** — consistent spacing for tabular output
4. **Stable JSON** — `--json` flag produces machine-readable, schema-stable output
5. **Human-friendly by default** — render functions produce readable output without `--json`

---

## Color Usage

Colors are defined in `kimari/utils/colors.py`:

| Helper | Prefix | Color | Use Case |
|--------|--------|-------|----------|
| `ok(msg)` | `[OK]` | Green | Successful checks, healthy state |
| `warn(msg)` | `[WARN]` | Yellow | Suboptimal state, non-blocking issues |
| `fail(msg)` | `[FAIL]` | Red | Critical failures, must-fix issues |
| `info(msg)` | `[INFO]` | Cyan | Informational messages, neutral state |

### Color constants

```python
class Color:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"
    WHITE  = "\033[97m"
```

### When to use colors

- **Headers**: `Color.BOLD + Color.CYAN` for section titles
- **Status labels**: Use the helper functions (`ok()`, `warn()`, `fail()`, `info()`)
- **De-emphasized text**: `Color.DIM` for hints, suggestions, and "did you know" messages
- **Values**: `Color.BOLD` for important values within a line

### When NOT to use colors

- **Inside JSON output** — `--json` output must be plain text, no ANSI codes
- **Piped output** — `supports_color()` returns `False` when stdout is not a TTY
- **Log files** — plain text only

---

## Version Header

Key commands display a version header at the top of their output:

```
Kimari CLI v0.1.27-alpha

  Status:      READY
  Profile:     test
  ...
```

The version header uses `Color.BOLD + Color.CYAN` and is followed by a blank line.

Commands that include a version header:
- `kimari status`
- `kimari doctor`
- `kimari doctor --deep`
- `kimari gateway --plan`
- `kimari update check`
- `kimari setup`
- `kimari optimize`
- `kimari perf`

---

## JSON vs. Human Output

Every command that produces output supports two modes:

### Human-readable (default)

```bash
kimari status
```

Output uses render functions with aligned columns, color, and contextual formatting:

```
Kimari CLI v0.1.27-alpha

  Status:      READY
  Profile:     test
  Model:       tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
  Host:        127.0.0.1
  Port:        11435
  PID:         12345
  Uptime:      5m 32s
  Gateway:     planned
```

### Machine-readable (`--json`)

```bash
kimari status --json
```

Output is valid JSON with a stable schema. No ANSI codes, no alignment, no version header:

```json
{
  "status": "READY",
  "profile": "test",
  "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
  "host": "127.0.0.1",
  "port": 11435,
  "pid": 12345,
  "uptime_s": 332,
  "kimari_version": "0.1.27-alpha",
  "gateway": "planned"
}
```

### JSON rules

1. **Stable keys** — key names do not change between versions; new keys are additive
2. **No ANSI in JSON** — all color codes are stripped
3. **No null surprises** — missing values use `null` explicitly, not empty strings
4. **Indent=2** — `json.dumps(data, indent=2)` for consistent formatting
5. **Version included** — `kimari_version` key is always present in JSON output

---

## PASS/WARN/FAIL Table Format

The `kimari doctor --deep` command uses a tabular format for check results:

```
Kimari CLI v0.1.27-alpha — Deep Doctor

  #   Check              Status   Detail
  ──  ─────────────────  ───────  ──────────────────────────────
  1   Python             PASS     3.12.1
  2   Paths              PASS     All directories exist
  3   Config             WARN     host 0.0.0.0 on non-docker profile
  4   Models Dir         PASS     2 GGUF files found
  5   llama-server       PASS     /usr/local/bin/llama-server
  6   Default Profile    PASS     test
  7   Secret Scanner     PASS     Found
  8   Benchmark Prompts  PASS     7 valid prompts
  9   Preview Gate       PASS     BLOCKED
  10  Kimari Version     PASS     0.1.27-alpha
  11  CUDA/NVIDIA        WARN     No GPU detected
  12  Packaged Defaults  PASS     All defaults found
  13  Gateway Module     PASS     Module exists
  14  Integration Docs   PASS     All docs found

Summary: 12 PASS, 2 WARN, 0 FAIL
```

### Formatting rules

- **Column alignment**: Left-aligned with fixed-width columns
- **Status column**: Uses color — PASS (green), WARN (yellow), FAIL (red)
- **Separator line**: Uses `──` (simple Unicode dashes, not heavy box-drawing characters)
- **Number column**: Right-aligned for clean alignment of two-digit numbers
- **Summary line**: `X PASS, Y WARN, Z FAIL` with color per count

---

## Next Steps Section

Commands that require follow-up action display a "Next Steps" section:

```
  Next Steps:
    1. Run:  kimari pull test
    2. Then: kimari start --profile test
    3. Verify: kimari doctor --deep
```

### Formatting rules

- "Next Steps" uses `Color.BOLD` for the header
- Each step is numbered
- Command examples use inline code style (no backticks in terminal output)
- Steps are ordered: first action → verification

---

## Emoji and Symbol Policy

### No excessive emojis

Kimari avoids emojis in terminal output for these reasons:

1. **Windows compatibility** — Windows Command Prompt and older PowerShell do not render many emojis correctly
2. **Terminal width** — Emojis have inconsistent character widths across terminals
3. **Accessibility** — Screen readers may not handle emojis well
4. **Log files** — Emojis add noise to log output

### Allowed symbols

| Symbol | Context | Why |
|--------|---------|-----|
| `──` | Table separators | Simple Unicode, widely supported |
| `...` | Truncation | Universal |
| `>` | Prompts | Universal |
| `-` | Bullet points | Universal |

### Not allowed

| Symbol | Why Not |
|--------|---------|
| ✅ ❌ ⚠️ | May not render on Windows; use `[OK]`, `[FAIL]`, `[WARN]` instead |
| 🔧 ⚡ 🔌 | Emoji; may have inconsistent widths |
| ╔ ╗ ╚ ╝ | Heavy box-drawing; may break in narrow terminals |
| ✓ ✗ | May not render on all terminals |

---

## Alignment and Spacing Conventions

### Key-value pairs

```
  Status:      READY
  Profile:     test
  Model:       tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
  Host:        127.0.0.1
  Port:        11435
```

Rules:
- 2-space indent from the left margin
- Key followed by colon and spaces to align values
- Value column starts at a consistent position (typically column 18)
- Use `f"{key:25s}: {value}"` pattern for alignment

### Lists

```
  Planned Endpoints:
    GET    /health                   — Health check
    GET    /status                   — Server status
    POST   /server/start             — Start llama-server
```

Rules:
- 4-space indent for list items
- Method column: 6 characters, left-aligned
- Path column: 25 characters, left-aligned
- Description after em-dash separator

### Sections

```
Kimari CLI v0.1.27-alpha

  Status:      READY
  ...

  Planned Endpoints:
    GET    /health     — Health check
    ...

  No server is started. Gateway is planned for a future release.
```

Rules:
- Blank line before each section
- Section headers use `Color.BOLD`
- Footer/hint text uses `Color.DIM`
- Blank line after the last section

---

## Implementation Reference

### Render function pattern

```python
def check_status(config: dict, json_output: bool = False):
    # ... compute status_data ...

    if json_output:
        print(json.dumps(status_data, indent=2))
        return

    # Human-readable output
    print(f"\n{Color.BOLD}{Color.CYAN}Kimari CLI v{KIMARI_VERSION}{Color.RESET}\n")
    print(f"  Status:      {status_data['status']}")
    print(f"  Profile:     {status_data.get('profile', 'N/A')}")
    # ...
```

Every render function follows this pattern:
1. Compute the data structure
2. If `--json`, dump and return early
3. Otherwise, render with colors, alignment, and version header

### Adding a new command

When adding a new CLI command:

1. Define the data structure first (the JSON schema)
2. Implement the `--json` path
3. Implement the human-readable render function
4. Always include a version header
5. Always include next steps if the command requires follow-up
6. Test both output modes

---

## Summary

| Aspect | Convention |
|--------|-----------|
| Color library | `kimari/utils/colors.py` (ANSI, no `rich`) |
| Version header | `Color.BOLD + Color.CYAN` in key commands |
| Status labels | `[OK]`, `[WARN]`, `[FAIL]`, `[INFO]` — never emoji |
| JSON mode | `--json` flag, `indent=2`, no ANSI, stable schema |
| Alignment | 2-space indent, consistent value column |
| Emojis | Not used — Windows compatibility |
| Separator | `──` for table lines |
| Hints | `Color.DIM` for de-emphasized text |
| Next steps | Numbered, ordered, with command examples |
