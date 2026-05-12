# Hugging Face Space: kimari-fit-lab

> A Gradio GPU compatibility checker for Kimari Local AI.

## Purpose

`kimari-fit-lab` is a static Gradio Space that helps users determine if their GPU is compatible with Kimari Local AI. It does **not** run any model, download any model, or call any API.

## What It Demonstrates

✅ Which GPUs are compatible with Kimari's profiles
✅ VRAM requirements for different model sizes
✅ Recommended `kimari` CLI commands
✅ That Kimari-4B is not yet released

## What It Does NOT Demonstrate

❌ Running any model (no model execution)
❌ Downloading any model (no model downloads)
❌ Using any API keys
❌ Any benchmark claims about Kimari-4B
❌ That Kimari-4B weights exist (they don't)

## Deployment

1. Create a new Space on Hugging Face: `kimari-ai/kimari-fit-lab`
2. Set SDK to `gradio`
3. Upload the contents of `huggingface/kimari-fit-lab/`
4. The Space will build automatically

```bash
# Manual deployment via huggingface_hub
cd huggingface/kimari-fit-lab
huggingface-cli upload kimari-ai/kimari-fit-lab . --repo-type space
```

## Updating

1. Edit `app.py` locally
2. Test with `python app.py`
3. Upload to HF Spaces

## Safety

- **No tokens** in any file
- **No API keys** in any file
- **No model downloads** — the app is purely static
- **No claims** that Kimari-4B is released
- Gate remains **BLOCKED**