# CPU Inference Validation — v0.1.86-alpha

> **Last updated:** 2026-05-17
> **Validation type:** CPU inference (no GPU available in test environment)
> **GPU inference:** NOT TESTED — requires real GTX 1060/1080 hardware

---

## Honest Status

| Item | Status |
|------|--------|
| Model download (Qwen3-4B Q4_K_M) | ✅ Verified |
| Model download (SmolLM3 Q4_K_M) | ✅ Verified |
| SHA256 hash verification | ✅ Verified (pinned in v0.1.85-alpha) |
| llama-server startup (Qwen3-4B) | ✅ Verified (CPU) |
| llama-server startup (SmolLM3) | ✅ Verified (CPU) |
| `/health` endpoint | ✅ Both models respond `{"status":"ok"}` |
| `/v1/models` endpoint | ✅ Both models listed with correct metadata |
| `/v1/chat/completions` endpoint | ✅ Both models generate coherent responses |
| Coherent output | ✅ Both models produce readable text |
| GPU inference (GTX 1060) | ❌ Not tested — no GPU in environment |
| GPU inference (GTX 1080) | ❌ Not tested — no GPU available |
| VRAM measurement | ❌ Not tested — requires GPU |
| GPU tokens/s measurement | ❌ Not tested — requires GPU |
| Stability test (5+ min) | ❌ Not tested — server shuts down after idle timeout |

**Important:** CPU tokens/s measurements below are NOT representative of GPU performance. GPU performance on GTX 1060/1080 must be measured separately before any GPU performance claim is made.

---

## Test Environment

| Field | Value |
|-------|-------|
| CPU | Intel Xeon (4 cores) |
| RAM | 8.1 GiB total, 6.9 GiB available |
| GPU | None |
| CUDA | None |
| OS | Linux (sandbox) |
| llama-server version | 1 (build a6d6183) |
| llama.cpp compiler | GNU 14.2.0, Linux x86_64 |
| Build type | CPU-only (no CUDA support) |

---

## Qwen3-4B Q4_K_M — CPU Inference

### Server Configuration

```bash
llama-server \
  -m ~/.local/share/kimari/models/Qwen3-4B-Q4_K_M.gguf \
  --host 127.0.0.1 --port 11435 \
  -c 2048 -b 64 -ub 32 -t 4 \
  -ngl 0 --parallel 1 \
  --no-warmup --no-cache-idle-slots --timeout 600
```

Note: `-ngl 0` means all layers on CPU (no GPU offload). The `agent-qwen1060` profile uses `-ngl all` with GPU offload.

### Model Metadata

| Field | Value |
|-------|-------|
| Source | `Qwen/Qwen3-4B-GGUF` |
| File size | 2,497,280,256 bytes (2.33 GB) |
| Parameters | 4,022,468,096 |
| Quantization | Q4_K_M |
| Context (test) | 2048 |
| Host memory projected | 612 MiB |
| SHA256 | `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` |

### Endpoint Results

| Endpoint | Result |
|----------|--------|
| `/health` | ✅ `{"status":"ok"}` |
| `/v1/models` | ✅ Model listed with correct params and size |
| `/v1/chat/completions` | ✅ 128 tokens generated coherently |

### CPU Performance

| Metric | Test 1 | Test 2 |
|--------|--------|--------|
| Prompt tokens/s | 56.38 | 61.83 |
| Generation tokens/s | 9.98 | 10.74 |
| Prompt ms/token | 16.17 | 17.73 |
| Generation ms/token | 100.16 | 93.09 |

**Note:** Qwen3-4B uses thinking/reasoning mode by default. The `reasoning_content` field is populated before `content`.

### Sample Output

```
Prompt: "Explain what Kimari does in one paragraph."
Reasoning: "Okay, the user is asking me to explain what Kimari does in one paragraph. First, I need to figure out what Kimari refers to..."
```

---

## SmolLM3 Q4_K_M — CPU Inference

### Server Configuration

```bash
llama-server \
  -m ~/.local/share/kimari/models/SmolLM3-Q4_K_M.gguf \
  --host 127.0.0.1 --port 11435 \
  -c 2048 -b 64 -ub 32 -t 4 \
  -ngl 0 --parallel 1 \
  --no-warmup --no-cache-idle-slots --timeout 600
```

### Model Metadata

| Field | Value |
|-------|-------|
| Source | `ggml-org/SmolLM3-3B-GGUF` |
| File size | 1,915,305,312 bytes (1.78 GB) |
| Parameters | 3,075,098,624 |
| Quantization | Q4_K_M |
| Context (test) | 2048 |
| Host memory projected | 366 MiB |
| SHA256 | `8334b850b7bd46238c16b0c550df2138f0889bf433809008cc17a8b05761863e` |

### Endpoint Results

| Endpoint | Result |
|----------|--------|
| `/health` | ✅ `{"status":"ok"}` |
| `/v1/models` | ✅ Model listed with correct params and size |
| `/v1/chat/completions` | ✅ 124 tokens generated coherently |

### CPU Performance

| Metric | Test 1 | Test 2 |
|--------|--------|--------|
| Prompt tokens/s | 73.60 | 93.00 |
| Generation tokens/s | 13.73 | 13.55 |
| Prompt ms/token | 13.59 | 10.75 |
| Generation ms/token | 72.81 | 73.79 |

### Sample Output

```
Prompt: "Explain what Kimari does in one paragraph."
Content: "Kimari is a traditional Hawaiian dance characterized by its fluid, flowing movements that mimic the motions of the ocean..."
```

(Note: SmolLM3 hallucinated about "Kimari" since it doesn't have specific knowledge about the project — expected behavior for a general model.)

---

## Key Findings

1. **Both models load and serve correctly** via llama-server with OpenAI-compatible API.
2. **All three critical endpoints work**: `/health`, `/v1/models`, `/v1/chat/completions`.
3. **SmolLM3 is ~30% faster** than Qwen3-4B on CPU generation (13.7 vs 10.7 tokens/s), consistent with its smaller size.
4. **Both models use thinking/reasoning mode** by default, which affects response format.
5. **CPU performance is NOT representative** of GTX 1060/1080 GPU performance. With `-ngl all` on a CUDA GPU, performance must be measured on real GTX 1060/1080 hardware before publishing any GPU speed claim.

---

## What Remains Untested

| Test | Requires |
|------|----------|
| GPU offload (`-ngl all`) | GTX 1060/1080 + CUDA |
| Full context (4K/8K) | GPU with sufficient VRAM |
| VRAM measurement | `nvidia-smi` + GPU |
| GPU tokens/s | GPU + CUDA |
| Stability (5+ min) | Longer server uptime |
| Parallel requests | GPU + multiple clients |
| OOM at context limit | GPU + stress test |

---

## How to Complete GPU Validation

On a machine with GTX 1060 or GTX 1080:

```bash
# Build llama.cpp with CUDA
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=61
cmake --build build --target llama-server -j$(nproc)

# Test Qwen3 on GTX 1060
./build/bin/llama-server \
  -m ~/.local/share/kimari/models/Qwen3-4B-Q4_K_M.gguf \
  --host 127.0.0.1 --port 11435 \
  -c 4096 -b 128 -ub 64 -t 4 \
  -ngl all --parallel 1 \
  --no-warmup

# In another terminal:
nvidia-smi  # Record VRAM usage
curl http://127.0.0.1:11435/health
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen3-4B-Q4_K_M.gguf","messages":[{"role":"user","content":"Explain what Kimari does in one paragraph."}],"max_tokens":128,"temperature":0.3}'
```

Fill in the GPU-specific metrics in this document and update the conclusion.

---

## Conclusion (Partial — CPU Only)

Both Qwen3-4B Q4_K_M and SmolLM3 Q4_K_M work correctly with llama-server. All OpenAI-compatible endpoints function as expected. CPU inference is functional but slow.

GPU inference on GTX 1060/1080 remains the critical untested path. The CPU validation confirms model compatibility and API correctness but provides no GPU performance data.

**No GPU performance claims should be made until real GTX 1060/1080 testing is completed.**
