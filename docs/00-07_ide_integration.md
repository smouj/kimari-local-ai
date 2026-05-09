# Kimari IDE Integration

## Document: 00-07 IDE Integration (Continue.dev)
**Version:** 0.1.0
**Status:** Draft
**Last Updated:** 2025

---

## Overview

Kimari integrates seamlessly with [Continue](https://continue.dev), an open-source AI code assistant for VS Code and JetBrains IDEs. This allows you to use your local Kimari model as the coding assistant directly within your editor.

## What is Continue?

Continue is an open-source alternative to GitHub Copilot that runs entirely local. Key features:
- Inline code completion
- Chat sidebar for coding questions
- File-aware context (reads your open files)
- Multiple model support
- Custom prompts and commands
- Works with VS Code and JetBrains

## Quick Setup

### 1. Install Continue

**VS Code:**
```
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Continue"
4. Install "Continue - Codestral, Claude, and more"
```

**JetBrains (IntelliJ, PyCharm, WebStorm):**
```
1. Open Settings → Plugins
2. Search for "Continue"
3. Install and restart IDE
```

### 2. Configure for Kimari

Copy or create the Continue configuration file:

**VS Code:** `~/.continue/config.yaml`
**JetBrains:** `~/.continue/config.yaml`

Use the provided config:
```bash
cp ide/continue/config.yaml ~/.continue/config.yaml
```

### 3. Start Kimari

```bash
# Start the Kimari server
make start-1060
# or
make start-1080
```

### 4. Use Continue in Your IDE

- **Chat:** Open the Continue sidebar (Ctrl+L) and ask coding questions
- **Autocomplete:** Start typing and accept inline suggestions (Tab)
- **Commands:** Use `/edit`, `/comment`, `/test` commands

## Configuration Details

The provided `ide/continue/config.yaml`:

```yaml
models:
  - name: Kimari-4B
    provider: ollama  # Uses OpenAI-compatible API
    model: Kimari-4B-Q4_K_M
    apiBase: http://127.0.0.1:11435/v1
    options:
      temperature: 0.3
      numCtx: 8192
      maxTokens: 2048

tabAutocompleteModel:
  name: Kimari-4B-Auto
  provider: ollama
  model: Kimari-4B-Q4_K_M
  apiBase: http://127.0.0.1:11435/v1
  options:
    temperature: 0.1
    maxTokens: 256

context:
  providers:
    - name: code
    - name: docs
    - name: file
    - name: url

slashCommands:
  - name: edit
    description: "Edit selected code"
  - name: comment
    description: "Comment the selected code"
  - name: test
    description: "Generate tests for selected code"
  - name: explain
    description: "Explain the selected code"
```

### Key Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `apiBase` | `http://127.0.0.1:11435/v1` | Kimari server endpoint |
| `temperature` (chat) | 0.3 | Low for precise coding assistance |
| `temperature` (autocomplete) | 0.1 | Very low for deterministic completions |
| `numCtx` | 8192 | Match your profile's context size |
| `maxTokens` | 2048 | Reasonable limit for code responses |

## Use Cases

### 1. Code Generation

**Prompt in Continue sidebar:**
```
Write a Python async function that fetches data from multiple URLs concurrently
using aiohttp. Include error handling and timeout support.
```

**Expected output:**
- Clean, working Python code
- Type hints
- Error handling
- Docstring

### 2. Code Explanation

Select code → Right-click → Continue → Explain

```
Explain what this function does and identify any potential bugs:
```

### 3. Bug Fixing

Select buggy code → Ask Continue:
```
This function has a bug where it returns None when the list is empty.
Fix it to raise a ValueError instead.
```

### 4. Code Review

Paste code into Continue sidebar:
```
Review this code for:
1. Security vulnerabilities
2. Performance issues
3. Python best practices
4. Type safety
```

### 5. Test Generation

Select a function → Use `/test` command:
```
Generate pytest tests for this function with edge cases.
```

### 6. Refactoring

```
Refactor this function to use dataclasses instead of a dictionary.
Keep the same interface.
```

## Performance Tips

### For Autocomplete

Autocomplete needs fast responses (< 500ms). Optimize for speed:

```yaml
tabAutocompleteModel:
  options:
    temperature: 0.1      # Deterministic
    maxTokens: 256        # Short completions
    numCtx: 2048          # Small context window
```

### For Chat

Chat can be slower but should produce higher quality:

```yaml
models:
  options:
    temperature: 0.3      # Some creativity
    maxTokens: 2048       # Longer responses
    numCtx: 8192          # Larger context
```

### For Large Projects

When working with large codebases, Continue sends file content as context. This can fill your context window quickly. Tips:

1. Use `.continueignore` to exclude files
2. Keep autocomplete context small
3. Close files you're not actively working on
4. Use `/file` to selectively include files

## Troubleshooting

### "Model not found" Error

Continue sends the model name as specified in config. Make sure:
1. Kimari server is running (`make status`)
2. The model name matches what's loaded in llama-server
3. The `apiBase` URL is correct

### Slow Responses

1. Use the `turbo` profile for faster inference
2. Reduce `maxTokens` for autocomplete
3. Use the GTX 1080 profile if available
4. Close unused browser tabs (free VRAM)

### Context Window Full

1. Use `/clear` to reset conversation
2. Close unused files
3. Add files to `.continueignore`

### Connection Refused

1. Start Kimari: `make start-1060`
2. Check port: `curl http://127.0.0.1:11435/health`
3. Verify Continue config: `cat ~/.continue/config.yaml`

## Alternative: Custom IDE Plugin

For deeper integration, a custom Kimari VS Code extension could be built:

**Planned features:**
- Kimari server management (start/stop/restart)
- GPU profile switching from the editor
- KimariFit score display
- Real-time token/speed metrics
- Project-aware context injection
- Custom slash commands

This is planned for a future release.

---

*See [Continue documentation](https://continue.dev/docs) for more configuration options.*
