# Run Agents Now — Public GGUF Models

> **Last updated:** 2026-05-17
> **Audience:** Anyone who wants to run local AI agents today using Kimari's runtime with publicly available models.

---

## Honest Status

| Item | Status |
|------|--------|
| **Kimari-4B** | **NOT published.** No public weights, no adapters, no GGUF. Do not reference it as available. |
| **Qwen3-4B Q4_K_M** | **Recommended** for real local agent workflows today. Best quality-to-VRAM ratio. |
| **SmolLM3-3B Q4_K_M** | **Recommended** for lowest VRAM pressure. Good fallback on 6 GB cards. |
| **TinyLlama** | **Runtime validation only.** Not suitable for real agent use. Only for confirming the stack boots. |
| **Gate** | **BLOCKED.** No adapter or fine-tune will be published until gate criteria are met. |

If you are here looking for Kimari-4B weights — they do not exist publicly yet.
Use the public community models below to get real work done today.

---

## Installation

```bash
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
kimari doctor --deep
kimari setup --write --yes
```

`kimari doctor --deep` will verify your GPU, CUDA runtime, and Python environment.
`kimari setup --write --yes` writes the default config and accepts recommended settings.

---

## Model Download

```bash
# List all available models
kimari pull --list

# Pull the recommended set (Qwen3-4B + SmolLM3-3B quantized)
kimari pull recommended

# Pull SmolLM3-3B Q4 specifically
kimari pull smollm3-3b-q4

# Verify what you have
kimari models --downloaded
```

Models are stored locally in `~/.kimari/models/` by default.

---

## GTX 1060 Startup (6 GB VRAM — Qwen3-4B)

```bash
kimari start --profile agent-qwen1060 --daemon
kimari status --json
```

The `agent-qwen1060` profile is tuned for 6 GB VRAM:
- Q4_K_M quantization
- 4K context window
- Single parallel slot (`parallel=1`)
- Offload all layers to GPU

---

## GTX 1080 Startup (8 GB VRAM — Qwen3-4B)

```bash
kimari start --profile agent-qwen1080 --daemon
kimari status --json
```

The `agent-qwen1080` profile takes advantage of the extra VRAM:
- Q4_K_M quantization
- 8K context window
- Single parallel slot (`parallel=1`)
- Full GPU offload

---

## Safer GTX 1060 (SmolLM3-3B — Lowest VRAM Pressure)

If Qwen3-4B is too tight on your 6 GB card, use SmolLM3-3B:

```bash
kimari start --profile agent-smollm1060 --daemon
kimari status --json
```

This profile uses the smaller SmolLM3-3B model:
- Q4_K_M quantization
- 4K context window
- Single parallel slot (`parallel=1`)
- Maximum headroom for system overhead

---

## Endpoint Validation

After starting any profile, verify the server is responding:

```bash
# Health check
curl http://127.0.0.1:11435/health

# List available models
curl http://127.0.0.1:11435/v1/models

# Test a chat completion
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-4b-q4_k_m.gguf",
    "messages": [
      {"role": "system", "content": "Responde breve."},
      {"role": "user", "content": "Di OK y una frase sobre Kimari."}
    ],
    "max_tokens": 64
  }'
```

For SmolLM3-3B, replace the model field with `smollm3-3b-q4_k_m.gguf`.

---

## Integrations

Generate configuration snippets for popular clients:

```bash
# OpenWebUI
kimari integrations generate --target openwebui --json

# OpenClaw
kimari integrations generate --target openclaw --json

# Hermes
kimari integrations generate --target hermes --json

# Continue (VS Code / JetBrains)
kimari integrations generate --target continue --json
```

Each command outputs a ready-to-paste JSON configuration pointing at your local Kimari endpoint (`http://127.0.0.1:11435`).

---

## Recommendations

### Performance

| Setting | GTX 1060 (6 GB) | GTX 1080 (8 GB) |
|---------|------------------|------------------|
| `parallel` | **1** | **1** |
| Context | **4K** | **8K** |
| Temperature | **0.2–0.4** | **0.2–0.4** |

### General Guidance

- **`parallel=1` for low VRAM** — running more than one concurrent request will OOM on 6–8 GB cards.
- **Temperature 0.2–0.4 for agents** — lower temperature yields more deterministic, reliable tool-use and reasoning chains.
- **4K context on GTX 1060, 8K on GTX 1080** — exceeding these limits risks VRAM overflow.
- **External RAG instead of giant context** — use a retrieval system (vector DB, keyword search) to inject relevant context rather than stuffing everything into the prompt. This keeps context small and quality high.
- **Tools executed by the app, not relying on native tool calling initially** — implement tool execution in your application layer. Do not depend on the model's native function/tool calling until you have validated it end-to-end with your chosen model.
- **Qwen3-4B Q4_K_M for best quality** — this is the recommended model for agent workflows where output quality matters most.
- **SmolLM3-3B for lowest VRAM pressure** — use this when you need maximum VRAM headroom or are running other GPU processes alongside Kimari.

---

## Model Hash Verification

Hash verification ensures model integrity after download.

### Important Notes

- **Hashes are `null` in the registry until models are downloaded and verified.** A null hash does not mean something is wrong — it means the model has not yet been checked.
- **Do NOT invent or guess hashes.** Only use hashes computed by the tool or provided by the upstream model publisher.

### Commands

```bash
# Compute the hash for a downloaded model file
kimari models hash --json <path>

# Pin a verified hash to the model registry
kimari models pin-hash <model-id> --write --yes
```

After pinning, `kimari models --downloaded` will show the hash alongside the model entry.

---

## What This Is NOT

This guide is **not**:

- **A Kimari-4B release.** Kimari-4B is not published. No weights, adapters, or GGUF files exist publicly.
- **A benchmark claim.** No performance numbers are implied or guaranteed. Run your own evaluations.
- **Production-ready.** This is a local development setup using community models. Use at your own risk.
- **Official Kimari models.** The models referenced here (Qwen3-4B, SmolLM3-3B) are public community models published by their respective creators. They are not Kimari models.

These are practical instructions for running real local agent workflows today with publicly available models, while Kimari's own models complete their development and release process.
