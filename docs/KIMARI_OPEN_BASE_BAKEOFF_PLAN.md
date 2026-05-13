# Kimari Open Base Bakeoff Plan

> **Version**: v0.1.57-alpha  
> **Status**: Planned (not started)  
> **Last updated**: 2026-05-13  
> **Gate**: BLOCKED — no training, no HF Jobs, no adapters

## 1. Objective

Compare permissive-license base models to select the best foundation for each Kimari model line before committing to training.

## 2. Base Models (Permissive Only)

| Model | Size | License | Target Role |
|-------|------|---------|-------------|
| `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | Apache 2.0 | Kimari Runtime 1.5B |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | 1.7B | Apache 2.0 | Runtime alternative |
| `HuggingFaceTB/SmolLM3-3B` | 3B | Apache 2.0 | Kimari Core 3B |
| `Qwen/Qwen3-4B-Instruct-2507` | 4B | Apache 2.0 | Kimari-4B candidate |

### Excluded (Non-Permissive License)

| Model | Reason |
|-------|--------|
| `Qwen/Qwen2.5-3B-Instruct` | qwen-research license |
| `google/gemma-3-4b-it` | Gemma custom license |
| Meta Llama 3.x | Meta custom license |

## 3. Evaluation Methodology

### 3.1 KimariEval Categories

Each base model will be evaluated on KimariEval Private v1 (104 cases, 7 categories):

| Category | Count | Focus |
|----------|-------|-------|
| spanish_technical | 14 | Spanish technical Q&A |
| coding_debug | 14 | Code debugging |
| server_ops | 15 | Linux/sysadmin tasks |
| local_llm_gguf | 15 | Local AI/GGUF/CUDA/VRAM |
| openclaw_agents | 14 | Agent/OpenClaw workflows |
| refusal_safety | 15 | Safety/refusal behavior |
| style_consistency | 15 | Kimari style consistency |

### 3.2 Additional Metrics

| Metric | Method | Notes |
|--------|--------|-------|
| VRAM usage | llama-server benchmark | GTX 1060 6GB + GTX 1080 8GB |
| Prompt tokens/s | llama-server benchmark | CUDA vs CPU |
| Generation tokens/s | llama-server benchmark | CUDA vs CPU |
| GGUF Q4_K_M feasibility | llama.cpp quantization | Must fit in target VRAM |
| Context length | llama-server test | 2048/4096/8192 tokens |
| JSON/tool following | KimariEval subset | Structured output quality |
| Multi-language | KimariEval subset | Spanish + English |

### 3.3 Cost Estimation

| Model | Est. Training Cost (QLoRA) | Est. Eval Cost | Total Est. |
|-------|---------------------------|----------------|------------|
| Qwen2.5-1.5B | ~$0.50-1.00 (A10G, 500 steps) | ~$0.10 | ~$1.10 |
| SmolLM2-1.7B | ~$0.50-1.00 (A10G, 500 steps) | ~$0.10 | ~$1.10 |
| SmolLM3-3B | ~$1.00-2.00 (A10G, 500 steps) | ~$0.15 | ~$2.15 |
| Qwen3-4B | ~$1.50-3.00 (A10G, 500 steps) | ~$0.20 | ~$3.20 |

## 4. Bakeoff Procedure

### Phase 1: Baseline Evaluation (No Training)

1. Download each base model in GGUF Q4_K_M format
2. Run KimariEval subset10 on each base model (unmodified)
3. Measure VRAM, tokens/s, and context length
4. Document results in `reports/evals/open_base_bakeoff_v1/`

### Phase 2: Micro SFT Probe (500 steps, per model)

1. Train QLoRA adapter on each base model with Kimari SFT v1 dataset
2. Evaluate adapter vs baseline on KimariEval subset10
3. Compare quality, safety, and style metrics
4. Document results alongside baseline

### Phase 3: Decision

1. Compare all models on all metrics
2. Select best candidate per role (Runtime, Core, 4B)
3. Document decision in `KIMARI_BASE_MODEL_DECISION.md`
4. Proceed to full SFT only for selected candidates

## 5. Output Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Bakeoff plan | `docs/KIMARI_OPEN_BASE_BAKEOFF_PLAN.md` | ✅ This document |
| Baseline results | `reports/evals/open_base_bakeoff_v1/` | 📋 Planned |
| Decision record | `docs/KIMARI_BASE_MODEL_DECISION.md` | 📋 Planned |

## 6. Safety Constraints

- **No training until bakeoff baselines are evaluated**
- **No HF Jobs until explicit approval**
- **No adapters published publicly**
- **No benchmark claims until review**
- **All results stored locally, not committed raw**
- **Gate: BLOCKED**

---

_This bakeoff ensures Kimari selects the best permissive-license foundation before investing in training._