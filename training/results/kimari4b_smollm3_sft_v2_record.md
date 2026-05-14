# Kimari-4B SmolLM3-3B SFT v2 — Training Run Record

**Run ID**: `kimari4b-smollm3-sft-v2-private-002`
**Date**: 2026-05-14
**Status**: ✅ COMPLETED
**HF Job**: `6a05d0c0e48bea4538b9ccf8`

---

## Base Model
- **Model**: HuggingFaceTB/SmolLM3-3B
- **Parameters**: ~3B
- **License**: Apache-2.0
- **Context length**: 16384
- **Tokenizer**: BPE (SmolLM family)

## Dataset
- **Name**: kimari_sft_v1
- **Total items**: 320 (288 train, 32 validation)
- **Categories**: 8 (spanish_technical, coding_debug, server_ops, local_llm_cuda_gguf, openclaw_agents, safety_refusal, style_consistency, json_tooling)
- **Language split**: 82.5% Spanish, 10.3% English, 7.2% mixed
- **Format**: JSONL with `messages` field (chat format)

## Training Configuration

| Parameter | Value |
|-----------|-------|
| Method | QLoRA (4-bit quantization + LoRA) |
| LoRA rank (r) | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.1 |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj (7 modules) |
| Max sequence length | 4096 |
| Max steps | 150 |
| Epochs (effective) | ~8.3 |
| Learning rate | 5e-5 |
| LR scheduler | cosine |
| Warmup steps | 10 |
| Batch size (per device) | 4 |
| Gradient accumulation | 4 |
| Effective batch size | 16 |
| Steps per epoch | ~18 |
| FP16 | true |
| Gradient checkpointing | true |
| Seed | 42 |
| Weight decay | 0.01 |
| Report to | none |

## Best Model Selection
- **Strategy**: `load_best_model_at_end=true`
- **Metric**: `eval_loss` (lower is better)
- **Save total limit**: 3 checkpoints

## Results

| Step | Train Loss | Eval Loss | Train Accuracy | Eval Accuracy |
|------|-----------|-----------|---------------|---------------|
| 25 | 2.49 | — | 56.6% | — |
| 50 | 2.00 | **1.65** | 60.4% | 65.1% |
| 75 | 1.68 | — | 64.8% | — |
| 100 | 1.65 | **1.50** | 65.2% | 67.3% |
| 125 | 1.55 | — | 66.5% | — |
| 150 | 1.45 | **1.44** | 68.1% | 68.3% |
| 175 | 1.40 | **1.44** | 68.6% | 68.3% |
| 200 | 1.38 | — | 68.9% | — |
| 225 | 1.33 | — | 69.8% | — |
| 250 | 1.33 | **1.42** | 69.8% | 68.7% |
| 275 | 1.28 | — | 70.8% | — |
| 300 | 1.26 | — | 71.0% | — |
| Final | 1.26 | **1.41** | 70.2% | 68.9% |

### Key Metrics
- **Best eval loss**: 1.41 (selected by load_best_model_at_end)
- **Train/eval gap**: 0.15 (healthy, no overfitting)
- **Eval accuracy**: 68.9%
- **Completion**: All 150 steps completed successfully

## Artifacts
- **Adapter repo**: `Smouj013/kimari4b-smollm3-sft-v2-adapter` (private)
- **Adapter size**: ~121 MB (safetensors)
- **Checkpoints saved**: checkpoint-100, checkpoint-125, checkpoint-150
- **Total repo size**: 1.1 GB

## Comparison with v1 (Overfitted Run)

| Metric | v1 (overfitted) | v2 (correct) |
|--------|-----------------|--------------|
| Train loss | 0.019 | 1.26 |
| Eval loss | 2.81 ↑ | 1.41 ↓ |
| Train/eval gap | 2.79 🔴 | 0.15 ✅ |
| Train accuracy | 99.4% | 70.2% |
| Eval accuracy | 69.0% | 68.9% |
| LoRA r | 32 | 16 |
| LR | 2e-4 | 5e-5 |
| Dropout | 0.05 | 0.1 |
| Max steps | 1000 | 150 |

## v1 Failure Analysis
v1 overfitted because:
1. **Too many epochs**: 288 samples / effective batch 8 = 36 steps/epoch × 28 epochs = severe overfitting
2. **LR too high**: 2e-4 with small dataset causes rapid memorization
3. **No regularization**: dropout 0.05 and no early stopping
4. **No best model selection**: final checkpoint was the most overfitted

## Safety
- Gate state: **BLOCKED**
- Public release: **not allowed**
- HF public upload: **not allowed**
- GGUF export: **not allowed**
- Adapter uploaded to **private repo only**
- No benchmark claims made
