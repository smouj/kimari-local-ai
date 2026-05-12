# Kimari-4B Micro SFT Persisted Run — Result

> Second micro SFT run on HF Jobs with private adapter persistence.

## Status: COMPLETED ✅

| Field | Value |
|-------|-------|
| **Job ID** | `6a03a25e72518a06598ffae0` |
| **Status** | COMPLETED |
| **GPU** | NVIDIA A10G, 22.3 GB VRAM |
| **Base model** | Qwen/Qwen2.5-1.5B-Instruct (Apache 2.0) |
| **Docker** | pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel (via uv run) |
| **PyTorch** | 2.11.0+cu130 |
| **transformers** | 5.8.0 |
| **peft** | 0.19.1 |
| **trl** | 1.4.0 |
| **Max steps** | 20 |
| **Steps completed** | 20/20 |
| **Loss** | 5.005 → 4.228 |
| **Trainable params** | 1,089,536 (0.0705%) |
| **Total params** | 1,544,803,840 |
| **Dataset** | 21 examples (3×7, inline) |

## Key Results

| Check | Value |
|-------|-------|
| training_performed | ✅ true |
| adapter_generated | ✅ true |
| adapter_persisted_private | ✅ true |
| adapter_private_repo | `Smouj013/kimari4b-micro-sft-adapter-v0` |
| adapter_hash | `26a8190dab52f816157da467369ae88f` |
| adapter_size | 4,372,840 bytes (4.17 MB) |
| adapter_load_check | ✅ true |
| generation_success | ✅ true |
| adapter_committed_public | ✅ false |
| hf_public_upload_performed | ✅ false |
| gguf_generated | ✅ false |
| gate_state | ✅ BLOCKED |

## Test Generation

Prompt: `User: ¿Qué es Kimari?\nAssistant:`
Response: `Kimari es un juego de rol japonés desarrollado ...`

**Note**: This is a hallucinated response from 3 inline examples. Not meaningful for quality assessment. The load check validates **integrity and compatibility**, not quality.

## Private Repo

- **Repo**: `Smouj013/kimari4b-micro-sft-adapter-v0`
- **Visibility**: Private
- **Files uploaded**: adapter_model.safetensors, adapter_config.json, tokenizer files, checkpoints
- **LFS**: Enabled for *.safetensors

## Difference from v0.1.49

| Aspect | v0.1.49 | v0.1.51 |
|--------|---------|---------|
| Adapter persistence | Ephemeral (/tmp/) | ✅ Private HF repo |
| Upload | None | ✅ Private upload to Smouj013/kimari4b-micro-sft-adapter-v0 |
| Load check | None | ✅ Passed |
| Generation test | None | ✅ Passed |
| Steps | 10 | 20 |
| Stack | PyTorch 2.5.1+cu124 | PyTorch 2.11.0+cu130 (uv) |
| trl | ≥0.12 | 1.4.0 |
| transformers | ≥4.46 | 5.8.0 |
| peft | ≥0.13 | 0.19.1 |

## Estimated Cost

~$0.50 for 20 steps on a10g-small

## Gate

**BLOCKED** — No automatic gate transition.

**Adapter persistence note**: The adapter was uploaded to a private Hugging Face model repository (`Smouj013/kimari4b-micro-sft-adapter-v0`). This is **not** a public release. The adapter is for internal evaluation only.

**No benchmark claims**: The loss values and generation output are not meaningful for quality assessment. This validates the training and persistence pipeline only.

**Dataset hash note**: The inline dataset uses 3 examples repeated 7 times (21 total), not the full 72-example `sft_micro.jsonl`. The dataset SHA256 refers to the full file on disk.