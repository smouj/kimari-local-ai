# Kimari SFT v1 Training Plan

> **Version**: v0.1.59-alpha  
> **Last updated**: 2026-05-13  
> **Status**: Dataset seed created — Training deferred to v0.1.60-alpha  
> **Gate**: BLOCKED — no training until bakeoff complete and license review

## 1. Overview

This document defines the SFT v1 training plan for all three Kimari model lines, using only permissive-license base models.

## 2. Model Lines

### 2.1 Kimari Runtime 1.5B

| Field | Value |
|-------|-------|
| **Base model** | `Qwen/Qwen2.5-1.5B-Instruct` |
| **Base license** | Apache 2.0 |
| **Method** | QLoRA |
| **Parameters** | ~1.5B |
| **Target hardware** | GTX 1060 6GB (Q4_K_M GGUF) |
| **Role** | Lightweight local runtime |

### 2.2 Kimari Core 3B

| Field | Value |
|-------|-------|
| **Base model** | `HuggingFaceTB/SmolLM3-3B` |
| **Base license** | Apache 2.0 |
| **Method** | QLoRA |
| **Parameters** | ~3B |
| **Target hardware** | GTX 1080 8GB (Q4_K_M GGUF) |
| **Role** | Primary model for balanced quality/VRAM |

### 2.3 Kimari-4B Candidate

| Field | Value |
|-------|-------|
| **Base model** | `Qwen/Qwen3-4B-Instruct-2507` |
| **Base license** | Apache 2.0 |
| **Method** | QLoRA |
| **Parameters** | ~4B |
| **Target hardware** | GTX 1080 8GB (Q4_K_M GGUF, may require Q3) |
| **Role** | Brand model; only if eval justifies |

**Condition**: Kimari-4B proceeds ONLY if it passes KimariEval, license review, cost review, GGUF feasibility, and GTX 1060/1080 validation.

## 3. Training Configuration

### 3.1 QLoRA Config (All Lines)

```yaml
method: qlora
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
max_seq_length: 2048
learning_rate: 5.0e-5
epochs: 1
max_steps: 500
batch_size: 1
gradient_accumulation_steps: 8
push_to_hub: false
report_to: none
gate_state: BLOCKED
```

### 3.2 Safety Flags (ALL Training Runs)

```yaml
push_to_hub: false          # Never push to HF
report_to: none             # No WandB/TB upload
public_release_allowed: false
hf_upload_allowed: false
gguf_export_allowed: false
local_only: true
```

### 3.3 Dataset

- **Dataset**: `kimari_sft_v1` (see `KIMARI_SFT_V1_DATASET_LICENSE_PLAN.md`)
- **Size target**: 1,400–1,700 examples
- **All sources must have permissive-compatible licenses**
- **Manifest required before training**

## 4. Training Sequence

### Phase 1: Bakeoff Baselines (v0.1.57)

1. Evaluate each base model unmodified on KimariEval subset10
2. Measure VRAM, tokens/s, context length
3. Document results
4. **No training in this phase**

### Phase 2: SFT v1 Runtime 1.5B (v0.1.59)

1. Train QLoRA adapter on Qwen2.5-1.5B-Instruct
2. Evaluate adapter vs baseline on KimariEval
3. Private adapter only; no public release
4. **Gate: BLOCKED until eval complete**

### Phase 3: SFT v1 Core 3B (v0.1.61)

1. Train QLoRA adapter on SmolLM3-3B (only if bakeoff justifies)
2. Evaluate adapter vs baseline on KimariEval
3. Private adapter only; no public release
4. **Gate: BLOCKED until eval complete**

### Phase 4: SFT v1 4B Experimental (v0.1.62)

1. Train QLoRA adapter on Qwen3-4B-Instruct-2507
2. Validate whether Kimari-4B deserves to exist as a product line
3. Private adapter only; no public release
4. **Gate: BLOCKED until eval complete**

## 5. Private Adapter Policy

- All adapters are private until gate review
- No adapter files (`.safetensors`) committed to git
- No GGUF files committed to git
- Adapter manifests document base model, license, and method
- Private repos on Hugging Face only (Smouj013/*)
- No public benchmark claims until review

## 6. GGUF Export Plan (v0.1.63)

Only after SFT v1 evaluation shows improvement:

| Quantization | Purpose | Target Hardware |
|---|---|---|
| Q4_K_M | Primary | GTX 1060 6GB / GTX 1080 8GB |
| Q5_K_M | Balanced | GTX 1080 8GB |
| Q8_0 | Reference | GTX 1080 8GB |

## 7. GTX 1060/1080 Validation (v0.1.64)

Before any public release:

- Measure VRAM usage per quantization
- Measure tokens/s (prompt + generation)
- Measure context window stability
- Test on real hardware (not simulation)
- Document any errors or crashes

## 8. Public Preview Decision (v0.1.65)

Only if ALL conditions pass:

1. ✅ Base model license permissive (Apache/MIT/BSD)
2. ✅ Dataset manifest clean (all sources documented)
3. ✅ Eval shows improvement over baseline (+10% utility or clear manual review)
4. ✅ No safety regression
5. ✅ GGUF validated on GTX 1060/1080
6. ✅ Model card honest and complete
7. ✅ License inheritance documented
8. ✅ Explicit written approval from project owner

---

_All training is gate-blocked. No training, HF Jobs, or adapter publication until bakeoff is complete and explicitly approved._