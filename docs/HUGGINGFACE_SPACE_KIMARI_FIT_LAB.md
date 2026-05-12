# Hugging Face Space: kimari-fit-lab

> **Deployed and running** at https://huggingface.co/spaces/kimari-ai/kimari-fit-lab

## Deployment Status

| Field | Value |
|-------|-------|
| **Space ID** | `kimari-ai/kimari-fit-lab` |
| **URL** | https://huggingface.co/spaces/kimari-ai/kimari-fit-lab |
| **SDK** | Gradio 5.34.2 |
| **Status** | RUNNING |
| **Visibility** | Public |
| **Deployed** | 2026-05-12 |
| **Hardware** | CPU basic (free tier) |

## What the Space Does

1. GPU compatibility lookup — select your GPU, see which models fit
2. Model compatibility table — VRAM requirements per model size
3. Recommended `kimari` CLI commands
4. Kimari-4B status panel — clearly states "not released yet"

## What the Space Does NOT Do

❌ Does not run any model
❌ Does not download any model
❌ Does not use any API keys
❌ Does not claim Kimari-4B is released
❌ Does not reveal billing/plan information

## Files

| File | Purpose |
|------|---------|
| `app.py` | Gradio application (GPU/model compatibility lookup) |
| `README.md` | Space card with metadata |
| `requirements.txt` | `gradio>=5.34.2` |

## How to Update

1. Edit files locally in `huggingface/kimari-fit-lab/`
2. Push to `https://huggingface.co/spaces/kimari-ai/kimari-fit-lab`
3. Wait for Space to rebuild

```bash
cd huggingface/kimari-fit-lab
git add -A
git commit -m "Update description"
git push
```

## Safety

- **No tokens** in any file
- **No API keys** in any file
- **No model downloads** — the app is purely static
- **No claims** that Kimari-4B is released
- Gate remains **BLOCKED**