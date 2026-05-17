# Low-VRAM Agent Validation — v0.1.85-alpha

> **Last updated:** 2026-05-17
> **Status:** Partial — download and hash verification complete. GPU inference not yet tested.

---

## Honest Status

| Item | Status |
|------|--------|
| Model download (Qwen3-4B Q4_K_M) | ✅ Verified — 2,497,280,256 bytes |
| Model download (SmolLM3 Q4_K_M) | ✅ Verified — 1,915,305,312 bytes |
| SHA256 hash (Qwen3-4B) | ✅ Computed from real file |
| SHA256 hash (SmolLM3) | ✅ Computed from real file |
| GPU inference (GTX 1060) | ❌ Not tested — no GPU in validation environment |
| GPU inference (GTX 1080) | ❌ Not tested — no GPU available |
| `/health` endpoint | ❌ Not tested — requires llama-server + GPU |
| `/v1/chat/completions` | ❌ Not tested — requires llama-server + GPU |
| VRAM measurement | ❌ Not tested — requires GPU |
| tokens/s measurement | ❌ Not tested — requires GPU |
| Stability test | ❌ Not tested — requires GPU |

**This document is a partial validation.** Model downloads and hashes are verified. GPU inference requires real hardware and is pending.

---

## Model Download Verification

### Qwen3-4B Q4_K_M

| Field | Value |
|-------|-------|
| Source repo | `Qwen/Qwen3-4B-GGUF` |
| URL | `https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf` |
| File size | 2,497,280,256 bytes (2.33 GB) |
| SHA256 | `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` |
| Download command | `kimari pull recommended` |
| Download result | ✅ Success |

### SmolLM3-3B Q4_K_M

| Field | Value |
|-------|-------|
| Source repo | `ggml-org/SmolLM3-3B-GGUF` |
| URL | `https://huggingface.co/ggml-org/SmolLM3-3B-GGUF/resolve/main/SmolLM3-Q4_K_M.gguf` |
| File size | 1,915,305,312 bytes (1.78 GB) |
| SHA256 | `8334b850b7bd46238c16b0c550df2138f0889bf433809008cc17a8b05761863e` |
| Download command | `kimari pull smollm3-3b-q4` |
| Download result | ✅ Success |

---

## Environment (Download Verification Only)

| Field | Value |
|-------|-------|
| OS | Linux (sandbox, no GPU) |
| Python | 3.12 |
| Kimari | v0.1.84-alpha |
| NVIDIA GPU | None available |
| CUDA | None available |
| llama-server | Not installed |

---

## GPU Inference Tests — PENDING

The following tests require real GTX 1060/1080 hardware. They have NOT been executed yet.

### GTX 1060 — agent-qwen1060

```bash
kimari start --profile agent-qwen1060 --daemon
kimari status --json
curl http://127.0.0.1:11435/health
curl http://127.0.0.1:11435/v1/models
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3-4B-Q4_K_M.gguf",
    "messages": [
      {"role": "system", "content": "Answer briefly and technically."},
      {"role": "user", "content": "Explain what Kimari does in one paragraph."}
    ],
    "max_tokens": 128,
    "temperature": 0.2
  }'
```

| Metric | Result |
|--------|--------|
| Server start | ⬜ Pending |
| `/health` | ⬜ Pending |
| `/v1/models` | ⬜ Pending |
| Chat completion | ⬜ Pending |
| VRAM used | ⬜ Pending |
| tokens/s prompt | ⬜ Pending |
| tokens/s generation | ⬜ Pending |
| Stability (5 min) | ⬜ Pending |
| OOM / errors | ⬜ Pending |

### GTX 1060 — agent-smollm1060

```bash
kimari stop || true
kimari start --profile agent-smollm1060 --daemon
```

| Metric | Result |
|--------|--------|
| Server start | ⬜ Pending |
| `/health` | ⬜ Pending |
| `/v1/models` | ⬜ Pending |
| Chat completion | ⬜ Pending |
| VRAM used | ⬜ Pending |
| tokens/s prompt | ⬜ Pending |
| tokens/s generation | ⬜ Pending |
| Stability (5 min) | ⬜ Pending |
| OOM / errors | ⬜ Pending |

### GTX 1080 — agent-qwen1080

```bash
kimari stop || true
kimari start --profile agent-qwen1080 --daemon
```

| Metric | Result |
|--------|--------|
| Server start | ⬜ Pending |
| `/health` | ⬜ Pending |
| `/v1/models` | ⬜ Pending |
| Chat completion | ⬜ Pending |
| VRAM used | ⬜ Pending |
| tokens/s prompt | ⬜ Pending |
| tokens/s generation | ⬜ Pending |
| Stability (5 min) | ⬜ Pending |
| OOM / errors | ⬜ Pending |

---

## How to Complete This Validation

Run on a machine with a real GTX 1060 or GTX 1080:

1. Install Kimari: `pip install -e .`
2. Download models: `kimari pull recommended && kimari pull smollm3-3b-q4`
3. Verify hashes: `kimari models hash --json <path>` and compare with values above
4. Start each profile and run the curl commands
5. Record VRAM with `nvidia-smi` while the server is running
6. Fill in the pending rows above
7. Commit the updated document

---

## Conclusion (Partial)

Model downloads are verified and working. SHA256 hashes are computed from real downloaded files and can be pinned to the registry.

GPU inference validation requires real hardware and remains **pending**. No performance claims should be made until these tests are completed on actual GTX 1060/1080 hardware.
