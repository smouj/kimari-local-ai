# Kimari-4B Model Training Plan

**Version:** 0.1.0  
**Status:** Planning — No training has started  
**Last Updated:** 2026  

---

## ⚠️ Important Disclaimers

- **No training has been performed.** This document describes a planned approach only.
- **No base model has been selected definitively.** Candidates are listed for evaluation.
- **No exact dates are promised.** Phases are sequential dependencies, not timelines.
- **No model weights will ever be committed to this repository.**
- **All hyperparameters listed are starting points**, subject to change after experimentation.
- **Training code referenced is experimental** and will live in a separate branch or repository.
- Local GTX 1060/1080 GPUs are for **inference and testing only**, not for full training runs.
- **No training runs occur in CI.** No model downloads occur in CI.

---

## Overview

This document outlines a phased training plan for Kimari-4B, a ~4 billion parameter local AI model designed for coding, system administration, technical Spanish, agent orchestration, and JSON/tool-use on consumer-grade hardware. Each phase builds on the previous one. No phase begins until the prior phase produces a clear, validated result.

The plan follows a conservative, evaluation-driven approach:

1. Select a base model carefully (license, quality, compatibility).
2. Design and curate datasets before writing any training code.
3. Supervised fine-tuning (SFT) with parameter-efficient methods.
4. Preference tuning (DPO or ORPO) only after SFT converges.
5. Rigorous evaluation before any export or release.
6. GGUF quantization for target hardware.
7. Hugging Face release with full documentation.
8. Integration into the Kimari registry and CLI.

---

## Phase 0: Base Model Selection

**Goal:** Evaluate candidate base models and select one for fine-tuning.

### Candidate Evaluation Criteria

| Criterion | What to Check |
|-----------|--------------|
| Parameter count | ~3–4B parameters (fits target VRAM after quantization) |
| License | Must permit derivative works and commercial use (Apache 2.0, MIT, or equivalent) |
| Tokenizer | Single, well-documented tokenizer — no mixing tokenizers from different models |
| Context length | Minimum 8,192 tokens native; 16,384 preferred |
| Architecture | LLaMA-compatible or well-supported by llama.cpp for GGUF export |
| Baseline quality | Run KimariFit eval and coding benchmarks on the unmodified base |
| Community support | Active development, available tooling (TRL, Axolotl, etc.) |
| Multilingual | Baseline Spanish capability preferred (reduces SFT burden) |

### Candidate Models (Not Yet Selected)

| Model | Params | License | Notes |
|-------|--------|---------|-------|
| Qwen2.5-3B | 3B | Apache 2.0 | Strong multilingual, good coding |
| Qwen3-4B | 4B | Apache 2.0 | Larger, strong reasoning |
| SmolLM3-1.7B | 1.7B | Apache 2.0 | Smaller, efficient, good for 6GB GPUs |
| Llama 3.2 3B Instruct | 3B | Llama 3.2 Community | Strong baseline, wide ecosystem |
| Phi-3.5 Mini | 3.8B | MIT | Good reasoning, Microsoft-backed |

> **No model is selected yet.** The table above lists candidates for evaluation only. A final selection requires running baseline evaluations and confirming license compatibility with the intended release strategy.

### Baseline Evaluation (Before Any Fine-Tuning)

Before committing to a base model, run the following on each candidate:

1. **KimariFit eval** — Using `eval/kimari_eval.jsonl` and `eval/run_eval.py`
2. **Coding benchmarks** — HumanEval pass@1, MBPP pass@1
3. **Spanish technical** — Custom Spanish eval set
4. **JSON/tool-use** — Structured output validity rate
5. **Inference speed** — Tokens/second on GTX 1060 and GTX 1080 (GGUF Q4_K_M, Q5_K_M)
6. **Context window** — Verify claimed context length works in practice with llama.cpp

Record all baseline results. The selected base model must show acceptable baseline quality and clear headroom for improvement via fine-tuning.

### License Review

Each candidate must pass a license review before selection:

- [ ] License permits creation of derivative works
- [ ] License permits distribution of fine-tuned weights
- [ ] License does not restrict use cases relevant to Kimari (coding, sysadmin, etc.)
- [ ] License is compatible with GGUF redistribution
- [ ] No ambiguous "research only" clauses that would block public release
- [ ] Document license in `MODEL_LICENSES.md` before proceeding

---

## Phase 1: Dataset Design

**Goal:** Define data formats, sources, quality criteria, and curation pipeline before writing any training code.

### SFT Dataset Format

Supervised fine-tuning data uses the chat/completions format:

```json
{
  "messages": [
    {"role": "system", "content": "You are Kimari, a local AI assistant..."},
    {"role": "user", "content": "How do I debug a Docker container that won't start?"},
    {"role": "assistant", "content": "Here's a systematic approach..."}
  ],
  "tags": ["docker", "debugging", "sysadmin"],
  "quality_score": 4,
  "source": "curated",
  "language": "en"
}
```

Multi-turn conversations are supported:

```json
{
  "messages": [
    {"role": "system", "content": "You are Kimari..."},
    {"role": "user", "content": "Tengo un error MODULE_NOT_FOUND en Node.js."},
    {"role": "assistant", "content": "Este error indica que Node.js no puede encontrar un módulo..."},
    {"role": "user", "content": "Ya intenté npm install, sigue igual."},
    {"role": "assistant", "content": "Si ya ejecutaste npm install, verifica lo siguiente..."}
  ],
  "tags": ["nodejs", "debugging", "spanish"],
  "language": "es"
}
```

### Preference Dataset Format (for DPO/ORPO in Phase 3)

```json
{
  "prompt": "Write a Python function to parse a CSV file with error handling.",
  "chosen": "def parse_csv(filepath: str) -> list[dict]:\n    import csv\n    try:\n        with open(filepath, newline='') as f:\n            return list(csv.DictReader(f))\n    except FileNotFoundError:\n        raise FileNotFoundError(f'CSV file not found: {filepath}')\n    except csv.Error as e:\n        raise ValueError(f'CSV parsing error: {e}')",
  "rejected": "def parse_csv(filepath):\n    import csv\n    with open(filepath) as f:\n        return list(csv.DictReader(f))"
}
```

The `chosen` response demonstrates better error handling, type annotations, and clearer error messages. The `rejected` response works for the happy path but lacks robustness.

### Data Sources

| Category | Sources | Format | License Consideration |
|----------|---------|--------|-----------------------|
| **Coding** | CodeAlpaca, Evol-Instruct, GitHub (permissive repos) | Instruction-response | Apache 2.0, MIT |
| **System Administration** | StackExchange (Server Fault, Super User, Ask Ubuntu) | Q&A pairs | CC-BY-SA |
| **Technical Spanish** | Custom collection, translated docs, Spanish tech blogs | Instruction-response | MIT, CC-BY |
| **Agent/Tool-Use** | Custom agent prompts, tool-calling examples | Multi-turn with JSON | Original |
| **JSON/Structured Output** | Custom examples, API schema responses | Instruction with JSON output | Original |
| **General Instruction** | Alpaca, Open-Orca (filtered subset) | Instruction-response | Apache 2.0, MIT |

### Quality Criteria

Every training example must pass these checks:

1. **Technical accuracy** — Code must be correct and runnable. Technical claims must be verifiable.
2. **No hallucination** — If a factual claim cannot be verified, the example is excluded.
3. **Safe commands** — Destructive commands must include warnings. Non-destructive alternatives preferred.
4. **Proper formatting** — JSON outputs must be valid. Code must be syntactically correct.
5. **Spanish quality** — Proper technical Spanish with correct loanword usage (no Spanglish).
6. **No PII** — All personally identifiable information removed.
7. **No copyrighted material** — Only original or compatibly-licensed content.
8. **Minimum length** — 50 tokens per example (filters trivial Q&A).
9. **Maximum length** — 4,096 tokens per example (fits training context window).
10. **Deduplication** — Exact and fuzzy deduplication across the entire dataset.

### Dataset Pipeline (Planned)

```
raw/ → cleaned/ → instructions/ → train/ + eval/
                     ↑
              Quality filtering (min score 0.7)
              Deduplication (exact + fuzzy)
              PII removal
              Length filtering (50–4096 tokens)
```

Train/eval split: 90% / 10%, stratified by category and language.

> **The pipeline tools (`collect_data.py`, `clean_data.py`, `filter_quality.py`, `split_data.py`) are planned but not yet implemented.** See `dataset/README.md` and `docs/00-08_dataset_tuning.md` for the intended structure.

---

## Phase 2: Supervised Fine-Tuning (SFT)

**Goal:** Fine-tune the selected base model on curated instruction-response data using LoRA or QLoRA.

**Prerequisite:** Phase 0 complete (base model selected), Phase 1 complete (SFT dataset curated and split).

### Method: LoRA / QLoRA

Full fine-tuning of a 3–4B model is not planned. Instead, parameter-efficient fine-tuning:

- **LoRA** (Low-Rank Adaptation) — Adds trainable low-rank matrices to attention layers. Original weights frozen.
- **QLoRA** (Quantized LoRA) — Further reduces memory by quantizing the base model to 4-bit (NF4) while training LoRA adapters in BF16.

QLoRA is the recommended starting approach given memory constraints. If quality is unsatisfactory, LoRA with a higher-rank adapter can be attempted on a larger GPU.

### Starting Hyperparameters (Not Final)

These are initial values for experimentation. All are subject to change based on validation loss and evaluation results.

```yaml
# SFT Configuration — STARTING POINT ONLY
base_model: <selected-base-model>    # Determined in Phase 0
method: qlora                         # or lora if GPU memory allows
lora_rank: 16                         # Starting value; try 32 if underfitting
lora_alpha: 32                        # Common: 2x rank
lora_dropout: 0.05
target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  # Optionally: gate_proj, up_proj, down_proj (increases memory)

# Training
epochs: 3
batch_size: 4                         # Per-GPU micro-batch size
gradient_accumulation_steps: 8        # Effective batch = 32
learning_rate: 2.0e-4
lr_scheduler: cosine
warmup_ratio: 0.1
max_seq_length: 4096
weight_decay: 0.01

# Precision
bf16: true                            # If GPU supports BF16
fp16: false                           # Fallback if no BF16

# QLoRA-specific (if using QLoRA)
quantization: nf4                     # 4-bit NormalFloat
compute_dtype: bfloat16               # Or float16
double_quant: true                    # Nested quantization for memory savings
```

### Target Modules Considerations

| Target Modules | Trainable Params (~3B model) | Memory Impact | Quality Trade-off |
|---------------|------------------------------|---------------|-------------------|
| q_proj, k_proj, v_proj, o_proj | ~20M | Moderate | Good starting point |
| + gate_proj, up_proj, down_proj | ~50M | Higher | Better capacity, may overfit on small data |

### Validation Strategy

- **Eval every 500 steps** on the held-out eval set
- **Save checkpoint every 1000 steps** 
- **Early stopping** if eval loss does not improve for 3 consecutive evaluations
- **Manual inspection** of generated samples at each checkpoint (not just loss curves)
- **Run KimariFit eval** on the best checkpoint before proceeding to Phase 3

### Tooling (Planned)

| Tool | Purpose | Status |
|------|---------|--------|
| TRL `SFTTrainer` | SFT training loop | To be evaluated |
| Axolotl | Training orchestration | To be evaluated |
| Weights & Biases | Experiment tracking | Optional |
| `kimari bench` | Inference benchmarking post-SFT | Available |

### What SFT Does Not Do

- SFT alone does not align the model to human preferences (that is Phase 3)
- SFT does not guarantee safe outputs (that requires evaluation in Phase 4)
- SFT does not produce the final model — preference tuning and evaluation follow

---

## Phase 3: Preference Tuning (DPO or ORPO)

**Goal:** Align the SFT model to produce higher-quality, preferred outputs.

**Prerequisite:** Phase 2 complete (SFT model with acceptable eval results).

### Why Preference Tuning After SFT

SFT teaches the model to follow instructions. Preference tuning teaches it to choose better responses when multiple valid responses exist. Running preference tuning on a base model without SFT typically produces poor results — the model needs a reasonable instruction-following foundation first.

### Option A: Direct Preference Optimization (DPO)

**How it works:** DPO uses pairs of `chosen` (preferred) and `rejected` (dispreferred) responses to the same prompt. It optimizes the model to increase the likelihood of chosen responses and decrease the likelihood of rejected ones, using a reference model (the SFT checkpoint) as an anchor.

**Pros:**
- Well-supported by TRL (`DPOTrainer`) — mature, widely-used implementation
- Clear theoretical foundation with documented hyperparameter interpretation
- Large community experience and debugging resources available
- Straightforward to implement: same infrastructure as SFT with different data format

**Cons:**
- Requires keeping the reference model in memory alongside the training model
- Approximately doubles peak GPU memory usage compared to SFT alone
- For QLoRA + DPO: base model (4-bit) + LoRA adapter + reference LoRA adapter ≈ may exceed 24GB on larger models
- Preference data must be curated carefully — bad pairs can degrade quality

**Starting Hyperparameters (DPO):**

```yaml
# DPO Configuration — STARTING POINT ONLY
method: dpo
beta: 0.1                             # KL penalty; lower = more deviation from reference
learning_rate: 5.0e-5                 # Lower than SFT
epochs: 1                             # Preference tuning converges fast; overfitting risk is real
batch_size: 2                         # Smaller due to reference model memory
gradient_accumulation_steps: 16       # Effective batch = 32
max_seq_length: 4096
reference_model: <sft-checkpoint>     # Frozen reference
```

### Option B: Odds Ratio Preference Optimization (ORPO)

**How it works:** ORPO combines the SFT objective with an odds-ratio-based preference objective in a single training step. It does not require a separate reference model — the preference signal is computed from the log-odds ratio between chosen and rejected responses within the same forward pass.

**Pros:**
- No reference model needed — significantly reduces peak memory
- Simpler training setup (single model, single training loop)
- Combines SFT-like and preference objectives, potentially recovering SFT quality while adding alignment
- May enable preference tuning on 24GB GPUs where DPO would OOM

**Cons:**
- Less widely adopted than DPO — fewer community resources and debugging guides
- Must validate with actual tooling (TRL `ORPOTrainer` exists but is less battle-tested)
- Theoretical properties are less well-understood in practice
- The combined objective may interact unexpectedly with certain dataset compositions
- "May reduce memory" is a hypothesis — actual memory savings depend on implementation details and must be measured

**Starting Hyperparameters (ORPO):**

```yaml
# ORPO Configuration — STARTING POINT ONLY
method: orpo
lambda: 0.25                          # Weight for the odds-ratio preference loss
learning_rate: 5.0e-5
epochs: 1
batch_size: 4                         # Larger than DPO since no reference model
gradient_accumulation_steps: 8        # Effective batch = 32
max_seq_length: 4096
```

### DPO vs. ORPO Decision Framework

| Factor | DPO | ORPO |
|--------|-----|------|
| Memory requirement | Higher (reference model) | Lower (no reference) |
| Tooling maturity | High (TRL stable) | Moderate (TRL available, less community data) |
| Training simplicity | Moderate | Simpler |
| Risk of regression | Lower (well-understood) | Higher (less community experience) |
| 24GB GPU feasibility | Tight, may OOM on 4B model | More likely to fit |

**Recommendation:** Start with DPO if GPU memory allows (40GB+ GPU). Fall back to ORPO if memory is constrained (24GB GPU). Either way, validate the first preference tuning run carefully before committing to the approach.

> **Neither method is selected yet.** The choice depends on Phase 2 results, available GPU memory, and validation of ORPO tooling with the chosen base model.

### Preference Data Requirements

- Minimum ~1,000 high-quality preference pairs for a meaningful signal
- Pairs should cover all target domains (coding, sysadmin, Spanish, JSON/tool-use)
- `chosen` responses must be clearly better than `rejected` — ambiguous pairs hurt training
- Sources: human annotation, model-generated with manual review, or existing open preference datasets filtered for Kimari domains

---

## Phase 4: Evaluation

**Goal:** Comprehensively evaluate the fine-tuned model before export and release.

**Prerequisite:** Phase 3 complete (preference-tuned model available).

### Evaluation Categories

| Category | Test | Metric | Target (vs. base model) |
|----------|------|--------|------------------------|
| **KimariFit** | `eval/kimari_eval.jsonl` | Score | Improvement over base |
| **Coding** | HumanEval | pass@1 | Competitive with same-class models |
| **Coding** | MBPP | pass@1 | Competitive with same-class models |
| **System Administration** | Custom sysadmin eval | Accuracy | Correct troubleshooting steps |
| **Technical Spanish** | Custom Spanish eval | Accuracy + fluency | Proper terminology, no Spanglish |
| **JSON/Tool-Use** | Structured output eval | Validity rate | >95% valid JSON when requested |
| **Agent** | Multi-step reasoning eval | Step completion | Correct sequential reasoning |
| **Safety** | Harmful prompt eval | Refusal rate | Refuses clearly harmful requests |
| **Hallucination** | Factual QA on known topics | Accuracy | Higher than base model |

### Evaluation Process

1. **Automated eval** — Run `eval/run_eval.py` on the fine-tuned GGUF model
2. **Benchmark suite** — HumanEval, MBPP, MMLU (5-shot) using standard harnesses
3. **Manual spot-check** — 50+ examples across all domains, rated by the developer
4. **Comparison against base model** — Every metric must be compared to the Phase 0 baseline
5. **Comparison against reference models** — Compare with Qwen2.5-3B, Llama 3.2 3B at same quantization
6. **Regression testing** — Verify no catastrophic forgetting on general tasks
7. **Safety review** — Test with adversarial prompts; document any failures

### Go/No-Go Criteria

Before proceeding to Phase 5 (GGUF export):

- [ ] KimariFit score improves over base model
- [ ] No regression >10% on any single evaluation category
- [ ] JSON validity rate >90% when JSON is requested
- [ ] Spanish eval shows improvement without English degradation
- [ ] Safety eval shows no new failure modes vs. base model
- [ ] Manual spot-check confirms qualitative improvement

If any criterion fails, return to the relevant phase (SFT hyperparameters, dataset quality, or preference tuning configuration) and iterate.

---

## Phase 5: GGUF Export and Quantization

**Goal:** Convert the fine-tuned model to GGUF format and create quantized variants for target hardware.

**Prerequisite:** Phase 4 complete (model passes evaluation criteria).

### Export Process

```bash
# Step 1: Merge LoRA/QLoRA adapters into base model
# (Exact command depends on tooling used in Phase 2)
python merge_lora.py --base <base-model> --adapter <sft-adapter> --output <merged-model>

# Step 2: Convert merged HF model to GGUF F16
python convert_hf_to_gguf.py <merged-model> --outfile Kimari-4B-F16.gguf

# Step 3: Quantize to target formats
./llama-quantize Kimari-4B-F16.gguf Kimari-4B-Q4_K_M.gguf Q4_K_M
./llama-quantize Kimari-4B-F16.gguf Kimari-4B-Q5_K_M.gguf Q5_K_M
./llama-quantize Kimari-4B-F16.gguf Kimari-4B-IQ4_XS.gguf IQ4_XS
```

### Target Quantization Levels

| Quantization | Est. Size (4B) | Target GPU | Context Window |
|-------------|---------------|------------|----------------|
| Q4_K_M | ~3.1 GiB | GTX 1060 (6 GB) | 8,192 |
| Q5_K_M | ~3.8 GiB | GTX 1080 (8 GB) | 16,384 |
| IQ4_XS | ~2.8 GiB | GTX 1060 (6 GB, longer context) | 16,384 |

### Post-Quantization Validation

After quantization, re-run evaluation on each variant:

1. **Tokens/second** — Must meet targets in `MODEL_CARD.md` (>15 t/s on GTX 1060 Q4_K_M)
2. **Quality degradation** — Compare quantized model eval vs. F16 model eval; degradation should be <5%
3. **Context window** — Verify the claimed context length works without OOM on target hardware
4. **KimariFit** — Re-run on quantized models; scores should be within 5% of F16

---

## Phase 6: Hugging Face Release

**Goal:** Publish the model on Hugging Face with full documentation.

**Prerequisite:** Phase 5 complete (GGUF files validated on target hardware).

### Release Checklist

- [ ] Model card written (update `MODEL_CARD.md` with actual benchmarks)
- [ ] License clearly stated (must be compatible with base model license)
- [ ] Training data documentation (sources, cleaning steps, filtering criteria)
- [ ] All evaluation results published (base vs. fine-tuned, per quantization level)
- [ ] GGUF files uploaded to Hugging Face
- [ ] F16 GGUF uploaded for community quantization
- [ ] SHA256 hashes computed and published for all released files
- [ ] README on Hugging Face links back to Kimari Local AI repository
- [ ] Known limitations documented honestly
- [ ] No unverified claims in any release documentation

### Hugging Face Repository Structure

```
kimari-4b/
├── README.md                    # Full model card
├── LICENSE                      # Model license
├── MODEL_CARD.md                # Detailed model card
├── training-data.md             # Training data documentation
├── eval-results/                # Evaluation results
│   ├── baseline.json            # Base model results
│   ├── sft.json                 # Post-SFT results
│   ├── preference.json          # Post-preference-tuning results
│   └── quantized.json           # Quantized model results
├── gguf/
│   ├── Kimari-4B-F16.gguf
│   ├── Kimari-4B-Q4_K_M.gguf
│   ├── Kimari-4B-Q5_K_M.gguf
│   └── Kimari-4B-IQ4_XS.gguf
└── hashes.sha256                # SHA256 checksums
```

---

## Phase 7: Kimari Registry Integration

**Goal:** Add the released model to the Kimari model registry and update CLI profiles.

**Prerequisite:** Phase 6 complete (model publicly available on Hugging Face).

### Registry Updates

Update `config/kimari.models.json` and `kimari/defaults/kimari.models.json`:

```json
{
  "id": "kimari-4b",
  "name": "Kimari-4B",
  "family": "kimari",
  "status": "released",
  "params": "4B",
  "quantizations": ["Q4_K_M", "Q5_K_M", "IQ4_XS"],
  "sha256": {
    "Q4_K_M": "<computed-hash>",
    "Q5_K_M": "<computed-hash>",
    "IQ4_XS": "<computed-hash>"
  },
  "expected_vram_gb": {
    "Q4_K_M": 3.1,
    "Q5_K_M": 3.8,
    "IQ4_XS": 2.8
  },
  "download_url": "https://huggingface.co/<org>/kimari-4b/resolve/main/",
  "license": "<determined-in-phase-0>"
}
```

### Profile Updates

Update GPU profiles in `config/kimari.profiles.json` to point to Kimari-4B:

| Profile | Model | Quantization |
|---------|-------|-------------|
| `gtx1060` | Kimari-4B | Q4_K_M |
| `gtx1080` | Kimari-4B | Q5_K_M |
| `turbo` | Kimari-4B | IQ4_XS |
| `test` | (unchanged) | (unchanged) |

### CLI Integration

- `kimari pull gtx1060` → downloads Kimari-4B Q4_K_M
- `kimari pull gtx1080` → downloads Kimari-4B Q5_K_M
- `kimari pull kimari-4b` → downloads default quantization
- `kimari models --downloaded` → shows Kimari-4B if downloaded
- `kimari models verify kimari-4b` → verifies SHA256 hash
- Default profile remains `test` until user explicitly switches

---

## Hardware

### Local Hardware (Inference and Testing Only)

| GPU | VRAM | Use Case | Not For |
|-----|------|----------|---------|
| GTX 1060 | 6 GB | Inference (Q4_K_M), eval, smoke testing | Training |
| GTX 1080 | 8 GB | Inference (Q5_K_M), eval, smoke testing | Training |

> **GTX 1060/1080 are not suitable for training a 3–4B model**, even with QLoRA. A 4-bit quantized 4B model + LoRA adapters + optimizer states + gradients exceeds 8 GB VRAM. These GPUs are reserved for running inference, evaluating quantized models, and testing the end-user experience.

### Recommended Training Hardware (Rented)

| GPU | VRAM | Feasibility | Estimated Cost |
|-----|------|-------------|---------------|
| RTX 4090 | 24 GB | QLoRA on 3B model; tight for 4B | ~$0.50–1.00/hr |
| L40S | 48 GB | LoRA on 4B model; comfortable for QLoRA | ~$1.00–2.00/hr |
| A100 40GB | 40 GB | LoRA on 3–4B model | ~$1.50–3.00/hr |
| A100 80GB | 80 GB | Full fine-tuning possible (not planned) | ~$3.00–5.00/hr |

### Memory Budget Estimates (QLoRA, 4B model)

| Component | Memory (approximate) |
|-----------|---------------------|
| Base model (NF4 quantized) | ~2.5 GB |
| LoRA adapters (rank 16) | ~50 MB |
| Optimizer states (8-bit AdamW) | ~200 MB |
| Gradients | ~200 MB |
| Activations (batch=4, seq=4096) | ~4–8 GB |
| **Total (QLoRA, 4B)** | **~7–11 GB** |

| Component | Memory (approximate) |
|-----------|---------------------|
| Base model (BF16) | ~8 GB |
| LoRA adapters (rank 16) | ~50 MB |
| Optimizer states (8-bit AdamW) | ~400 MB |
| Gradients | ~400 MB |
| Activations (batch=4, seq=4096) | ~4–8 GB |
| **Total (LoRA, 4B)** | **~13–17 GB** |

> These are rough estimates. Actual memory usage depends on the specific model architecture, sequence length, batch size, and framework implementation. **Measure before committing to a specific GPU rental.**

### QLoRA on 24GB GPU (3B Model)

A 3B parameter model with QLoRA (NF4 quantization, rank 16) should fit on a 24 GB GPU with room for:
- Batch size 4, gradient accumulation 8
- Max sequence length 4096
- 8-bit optimizer

This is the minimum viable training setup. For 4B models, 24 GB is tight and may require reducing batch size or sequence length.

### Training Is Not Done From Scratch

This plan does **not** propose training a model from random initialization. All approaches build on an existing pre-trained base model via parameter-efficient fine-tuning (LoRA/QLoRA). Full pre-training of a 4B model would require significantly more compute (multi-GPU, weeks of training, orders of magnitude more data) and is not within the scope of this project.

---

## Methods Summary

### SFT with LoRA/QLoRA

- **When:** Phase 2 (first training phase)
- **What:** Teaches the model to follow instructions in Kimari's target domains
- **How:** Freeze base model weights; train low-rank adapter layers on curated instruction data
- **Starting point:** QLoRA with rank 16, alpha 32, learning rate 2e-4
- **Risk:** Overfitting on small datasets; underfitting if rank is too low

### DPO (Direct Preference Optimization)

- **When:** Phase 3 (after SFT only)
- **What:** Aligns model outputs with human preferences using chosen/rejected pairs
- **How:** Optimizes log-likelihood ratio between chosen and rejected responses, regularized against a frozen reference model
- **Tooling:** Supported by TRL (`DPOTrainer`)
- **Memory:** Requires reference model alongside training model — approximately doubles peak memory vs. SFT
- **Trade-off:** Most mature preference method, but memory-intensive

### ORPO (Odds Ratio Preference Optimization)

- **When:** Phase 3 (alternative to DPO, after SFT only)
- **What:** Combines preference alignment with an SFT-like objective in a single pass
- **How:** Computes preference signal from log-odds ratio between chosen/rejected; no reference model needed
- **Tooling:** Available in TRL (`ORPOTrainer`) but less battle-tested than DPO
- **Memory:** No reference model — peak memory similar to SFT alone
- **Trade-off:** Lower memory and simpler setup, but must validate with actual tooling before relying on it

### Method Selection

| Scenario | Recommended Method |
|----------|--------------------|
| 40GB+ GPU available | DPO (most mature) |
| 24GB GPU, 3B model | ORPO (fits memory) or DPO (tight) |
| Preference data is limited | DPO (more predictable with small data) |
| Memory is the primary constraint | ORPO (no reference model) |
| Maximum safety/conservatism | DPO (most community experience) |

> **No method is selected yet.** The choice will be made based on Phase 2 results, available hardware, and validation of ORPO tooling.

---

## Key Reminders

1. **All hyperparameters are starting points.** Nothing in this document is a final configuration. Every value must be validated experimentally.
2. **No final model selection yet.** The base model will be chosen after Phase 0 evaluation.
3. **Training code is experimental.** Do not rely on untested training scripts. Validate every step.
4. **No weights will be committed to the repository.** Model files are excluded via `.gitignore`. Weights will be distributed via Hugging Face only.
5. **No training in CI.** CI validates code quality, not model training. Training runs are manual, on rented hardware.
6. **No model downloads in CI.** CI does not download GGUF files. The `test` profile uses locally-available models only.
7. **No mixing models or tokenizers.** Fine-tuning uses a single base model with its native tokenizer. No cross-model adapter mixing.
8. **No claiming Kimari-4B is released.** Until Phase 6 is complete, all references to Kimari-4B must state it is planned or under development.
9. **No promising exact dates.** Phases are sequential and dependent on results. Timelines emerge from execution, not planning.
10. **GTX 1060/1080 are for inference/testing only.** Do not attempt training runs on consumer GPUs with 6–8 GB VRAM.

---

## Appendix: Phase Dependency Graph

```
Phase 0: Base Model Selection
    │
    ▼
Phase 1: Dataset Design
    │
    ▼
Phase 2: SFT (LoRA/QLoRA)
    │
    ▼
Phase 3: Preference Tuning (DPO or ORPO)
    │
    ▼
Phase 4: Evaluation
    │
    ├── Pass → Phase 5: GGUF Export
    │               │
    │               ▼
    │           Phase 6: Hugging Face Release
    │               │
    │               ▼
    │           Phase 7: Kimari Registry Integration
    │
    └── Fail → Return to Phase 2 or 3, adjust and retry
```

Each phase produces artifacts that the next phase depends on. No skipping, no parallelizing across phases.

---

*This plan is subject to change based on experimental results, resource availability, and community feedback. It represents the current best understanding of the path to Kimari-4B, not a commitment to specific outcomes.*

---

## v0.1.18-alpha Additions

The following pipeline components were added in v0.1.18-alpha to enable reproducible dry-run training:

### Base Model Decision Record (ADR-001)

A formal Architecture Decision Record has been created at [docs/MODEL_DECISION_RECORD.md](MODEL_DECISION_RECORD.md) documenting:
- Candidate shortlist (SmolLM3-3B, Qwen2.5-3B-Instruct, Llama 3.2 3B)
- Weighted scoring criteria (license clarity, redistribution, tokenizer, GGUF, coding, Spanish, agent/JSON, inference, training cost)
- Current status: Proposed (not yet Accepted)
- `training/scripts/select_base_model.py` — CLI tool for heuristic scoring and ranking

### Seed Datasets

- `dataset/samples/sft_seed.jsonl` — 30 synthetic SFT samples across 10 categories
- `dataset/samples/preference_seed.jsonl` — 20 synthetic preference pairs (chosen/rejected)
- All samples are original, synthetic, MIT-compatible — no private data, no secrets, no copyrighted material

### Dataset Mix Builder

- `training/scripts/build_dataset_mix.py` — Validates SFT and preference datasets against schemas, cleans records, and outputs training-ready JSONL files with a report
- `training/scripts/prepare_dataset.py` — Enhanced with `--dedupe`, `--min-chars`, `--max-chars`, `--require-tags`, and `--report` options

### KimariFit Dry-Run Harness

- `eval/kimarifit.py` — Evaluation harness that validates prompts in dry-run mode or calls an OpenAI-compatible endpoint for live evaluation
- `eval/rubrics/kimarifit_rubric.md` — 9-criteria scoring rubric with 0-5 levels
- Dry-run does not require a running model or network access

### GGUF Export Plan

- `training/scripts/export_gguf_plan.py` — Plans GGUF conversion and quantization commands without requiring llama.cpp tools installed
- Supports Q4_K_M, Q5_K_M, IQ4_XS quantization formats
- Validates that GGUF files are not committed to the repository

### First Training Run Guide

- `docs/FIRST_TRAINING_RUN.md` — Step-by-step guide for the first real training run, from base model selection through HF release

---

## v0.1.19-alpha Additions

The following components were added in v0.1.19-alpha to advance from pipeline dry-run to first private training readiness:

### Private SFT Candidate Accepted

SmolLM3-3B (HuggingFaceTB/SmolLM3-3B) has been formally accepted as the experimental base for the first private SFT training run. This acceptance is documented in:
- [docs/BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) — Formal acceptance record with scope and exclusions
- [docs/MODEL_DECISION_RECORD.md](MODEL_DECISION_RECORD.md) — ADR-001 status updated to "Accepted for first private training run"
- `training/configs/base_candidates.yaml` — SmolLM3-3B marked as `accepted_private_training_candidate`

**Important:** This acceptance is for private training only. Public release of fine-tuned weights remains subject to evaluation results, full license verification, and safety review.

### Dataset v0

An expanded synthetic dataset for first private training:
- `dataset/v0/sft_v0.jsonl` — 80+ synthetic SFT examples across 15 categories
- `dataset/v0/preference_v0.jsonl` — 40+ synthetic preference pairs focused on honesty, safety, and quality
- `dataset/v0/eval_holdout.jsonl` — 20+ evaluation examples with expected/forbidden traits
- `dataset/v0/README.md` — Dataset v0 policy and format documentation

All data is synthetic, MIT-compatible, with no private data, secrets, or copyrighted content.

### Training Readiness Validation

- `training/scripts/validate_training_ready.py` — Validates that all prerequisites for first training are met: base acceptance, dataset validity, minimum counts, forbidden strings check, no GGUF, no false claims

### KimariFit Scoring Plan

- `eval/scoring/kimarifit_dimensions.json` — 9 scoring dimensions with max scores, descriptions, and pass/fail examples
- `eval/kimarifit.py` enhanced with `--score-plan` and `--rubric` flags for scoring plan output
- `eval/scripts/summarize_results.py` — Summarizes evaluation results without requiring a model

### v0 Training Configs

- `training/configs/kimari_sft_lora.v0.example.yaml` — SFT LoRA config based on SmolLM3-3B (starting point only)
- `training/configs/kimari_orpo.v0.example.yaml` — ORPO config for post-SFT preference tuning (experimental)

### First Private Training Run Guide

- [docs/FIRST_PRIVATE_TRAINING_RUN.md](FIRST_PRIVATE_TRAINING_RUN.md) — Step-by-step guide from environment setup through adapter output, with safety reminders throughout

### Hugging Face Placeholder Plan

- [docs/HF_PLACEHOLDER_PLAN.md](HF_PLACEHOLDER_PLAN.md) — Plan for docs-only placeholder repository on Hugging Face (no weights, adapters, GGUF, or fake benchmarks until eval/license pass)
