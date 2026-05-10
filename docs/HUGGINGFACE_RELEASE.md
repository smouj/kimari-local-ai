# Hugging Face Release Guide — Kimari-4B

> **Purpose:** This document defines the process for releasing Kimari-4B model weights to Hugging Face.
> **Status:** Planning — No release has been made. No model has been trained. No Hugging Face repository exists.
> **Target Repository:** `smouj/kimari-4b` (planned, **not created yet**)

---

## Hard Blocks — Do Not Upload Until ALL Are Resolved

The following conditions **must** be met before any upload to Hugging Face:

| # | Block | Why | How to Resolve |
|---|-------|-----|----------------|
| 1 | **Base model license reviewed** | Cannot distribute derivative weights without confirming the base model permits it | Complete full license review of selected base model; document findings in `MODEL_LICENSES.md` |
| 2 | **License compatibility confirmed for all planned formats** | Some licenses restrict GGUF distribution, commercial use, or require specific attribution | Verify the base model license permits distribution of fine-tuned weights in safetensors and GGUF formats |
| 3 | **Evaluation results exist** | No release without measurable quality data | Run the full evaluation suite (`eval/run_eval.py` and `eval/kimarifit_prompts.jsonl`); record results |
| 4 | **Model card states actual status** | The HF model card must honestly describe what the model is, its capabilities, and its limitations | Update `MODEL_CARD.md` with real benchmark results, training details, and known issues |

> **If any block is not resolved, the release must not proceed.** There are no exceptions.

---

## Files Expected on Hugging Face

When the repository `smouj/kimari-4b` is eventually created, it should contain the following files:

| File | Required | Description |
|------|----------|-------------|
| `README.md` | **Yes** | Hugging Face model card (see template below) |
| `LICENSE` | **Yes** | License file — determined by base model license (Apache 2.0, Meta Community License, etc.) |
| `MODEL_LICENSES.md` | **Yes** | Reference to the full license layers document from the Kimari project |
| Adapter or merged model (safetensors) | **If allowed** | Fine-tuned weights in safetensors format; only if base model license permits redistribution of derivative weights |
| Tokenizer files | **Yes** | `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `vocab.json` (or equivalent for the tokenizer type) |
| GGUF quantizations | **If allowed** | `kimari-4b-q4_k_m.gguf`, `kimari-4b-q5_k_m.gguf`; only if base model license permits GGUF redistribution |
| `config.json` | **Yes** | Model architecture configuration |
| `generation_config.json` | **Yes** | Default generation parameters |
| Eval results | **When available** | Evaluation output from `eval/run_eval.py`; can be a separate file or referenced in the model card |
| SHA-256 hashes | **When available** | Hashes for all distributable files; stored in a `hashes.sha256` file |
| `model.safetensors.index.json` | **If sharded** | Index file if the model is split into multiple shards |

### Files That Must NOT Be Uploaded

| Prohibited | Reason |
|------------|--------|
| Training data or datasets | License restrictions; privacy concerns |
| Training checkpoints | Unnecessary for inference; may contain sensitive data |
| Raw training logs | Not useful for end users; may contain private information |
| HF API keys or tokens | Security risk — never commit secrets |
| GGUF files larger than LFS limits | Use Git LFS or separate quant repositories |
| Base model weights (unmodified) | Redundant; link to the original base model repository instead |

---

## Release Process Checklist

### Phase 1: Pre-Release Preparation

- [ ] **Base model selected** — Document in `MODEL_CARD.md` and `MODEL_LICENSES.md`
- [ ] **License review completed** — Full text reviewed, compatibility confirmed for all formats
- [ ] **Fine-tuning completed** — Training run finished, best checkpoint selected
- [ ] **Evaluation suite run** — Full eval with `eval/run_eval.py` and `kimarifit_prompts.jsonl`
- [ ] **Evaluation results recorded** — Real numbers, not placeholders or targets
- [ ] **GGUF quantization produced** — Q4_K_M and Q5_K_M at minimum
- [ ] **GGUF quantization validated** — Test inference with llama.cpp on target GPUs
- [ ] **SHA-256 hashes computed** — For all distributable files
- [ ] **Model card updated** — Real benchmarks, training details, known limitations
- [ ] **MODEL_LICENSES.md updated** — Confirmed license for weights

### Phase 2: Pre-Upload Validation

Before creating the Hugging Face repository, verify:

- [ ] **No false claims**: Model card does not claim unverified benchmarks, capabilities, or comparisons
- [ ] **License is correct**: LICENSE file matches the base model's requirements
- [ ] **Attribution is present**: Base model is credited as required by its license
- [ ] **No secrets in files**: No API keys, tokens, or private data in any file to be uploaded
- [ ] **No GGUF committed to Git**: GGUF files are uploaded via Git LFS, not committed directly
- [ ] **Tokenizer files are complete**: All required tokenizer files are present and match the model
- [ ] **safetensors files are valid**: Verified with `safetensors` library (no corruption)
- [ ] **GGUF files are valid**: Verified with llama.cpp (can load and generate text)
- [ ] **Hashes match**: SHA-256 hashes in `hashes.sha256` match the actual files
- [ ] **Model card template is filled**: All sections of the HF model card template are completed with real data
- [ ] **Kimari-4B is not claimed as released elsewhere**: No contradicting status claims in other project files

### Phase 3: Upload

- [ ] **Create Hugging Face repository** `smouj/kimari-4b`
- [ ] **Set repository visibility** (public or gated, as appropriate)
- [ ] **Enable Git LFS** for large files (safetensors, GGUF)
- [ ] **Upload files in this order**:
  1. `README.md` (model card)
  2. `LICENSE`
  3. `MODEL_LICENSES.md`
  4. `config.json`, `generation_config.json`
  5. Tokenizer files
  6. `hashes.sha256`
  7. Model weights (safetensors, via LFS)
  8. GGUF quantizations (via LFS)
  9. Eval results (if included as a separate file)
- [ ] **Set model tags** on Hugging Face (e.g., `text-generation`, `pytorch`, `safetensors`, `gguf`, `english`, `spanish`, `code`)

### Phase 4: Post-Upload Verification

After upload, verify the following on the Hugging Face repository page:

- [ ] **Model card renders correctly** — All markdown, tables, and code blocks display properly
- [ ] **Files are all present** — Check the "Files and versions" tab
- [ ] **LFS files are downloadable** — Test downloading a GGUF file
- [ ] **Inference API works** (if supported by the model type) — Test a simple prompt
- [ ] **License is visible** — License tab shows the correct license
- [ ] **No broken links** — All cross-references in the model card work
- [ ] **Tags are correct** — Model appears in relevant Hugging Face search results
- [ ] **SHA-256 hashes match** — Download files and verify against `hashes.sha256`
- [ ] **Model loads locally** — Download GGUF, run with llama.cpp, confirm inference works
- [ ] **Update project references** — Update `MODEL_CARD.md`, `README.md`, `models/README.md`, and `kimari/defaults/kimari.models.json` with the HF repository URL

---

## README Template for Hugging Face Model Card

Below is the template for the Hugging Face model card (`README.md` in the HF repository). Sections marked with `[FILL]` must be completed with real data before upload. Sections marked with `[AUTO]` will be filled automatically or derived from existing project docs.

```markdown
---
language:
  - en
  - es
license: [FILL: e.g., apache-2.0, llama3.2, or other — match base model license]
library_name: transformers
tags:
  - text-generation
  - code
  - gguf
  - llama-cpp
  - local-ai
  - quantization
base_model: [FILL: e.g., HuggingFaceTB/SmolLM3-3B]
pipeline_tag: text-generation
---

# Kimari-4B

A fine-tuned local LLM for coding, system administration, and agent assistance — designed to run on consumer GPUs (GTX 1060 6GB and better).

## Model Details

| Field | Value |
|-------|-------|
| **Model Name** | Kimari-4B |
| **Base Model** | [FILL: base model name and link] |
| **Model Type** | Causal Language Model (Transformer) |
| **Parameters** | [FILL: actual parameter count] |
| **Context Length** | [FILL: maximum context length] |
| **Languages** | English, Technical Spanish |
| **Intended Runtime** | llama.cpp / llama-server via GGUF quantization |
| **Developer** | Smouj |
| **License** | [FILL: license name — determined by base model] |

## Intended Uses

- **Local coding assistant** — Code generation, debugging, and explanation
- **System administration** — Linux/Windows troubleshooting, automation scripts
- **Agent orchestration** — Multi-step reasoning for semi-autonomous tasks
- **Bilingual assistance** — English and technical Spanish support

## Out-of-Scope Uses

- Medical, legal, or financial advice
- Safety-critical systems
- Surveillance or privacy violation
- Generation of harmful content
- Replacing human expertise in critical decisions

## Hardware Targets

| GPU | VRAM | Recommended Quantization | Target Context |
|-----|------|------------------------|----------------|
| NVIDIA GTX 1060 | 6 GB | GGUF Q4_K_M | 8,192 tokens |
| NVIDIA GTX 1080 | 8 GB | GGUF Q5_K_M | 16,384 tokens |
| NVIDIA RTX 3060 | 12 GB | GGUF Q5_K_M | 32,768 tokens |

## Quantization Variants

| Variant | File | Size | Recommended For |
|---------|------|------|-----------------|
| Q4_K_M | `kimari-4b-q4_k_m.gguf` | [FILL] GB | 6 GB VRAM GPUs |
| Q5_K_M | `kimari-4b-q5_k_m.gguf` | [FILL] GB | 8 GB+ VRAM GPUs |

## Evaluation Results

[FILL: Insert real evaluation results here. This section must contain actual measured results, not targets or estimates. Use the output from eval/run_eval.py and eval/kimarifit_prompts.jsonl.]

| Benchmark | Metric | Q4_K_M | Q5_K_M |
|-----------|--------|--------|--------|
| Inference Speed (GTX 1060) | tokens/s | [FILL] | N/A |
| Inference Speed (GTX 1080) | tokens/s | [FILL] | [FILL] |
| Time to First Token (GTX 1080) | seconds | [FILL] | [FILL] |
| [FILL: additional benchmarks] | | | |

## KimariFit Scores

[FILL: Insert KimariFit scores for target GPU configurations. These are hardware compatibility scores, not quality scores.]

| GPU | Quantization | Context | KimariFit | Rating |
|-----|-------------|---------|-----------|--------|
| GTX 1060 6GB | Q4_K_M | 8192 | [FILL] | [FILL] |
| GTX 1080 8GB | Q5_K_M | 16384 | [FILL] | [FILL] |
| RTX 3060 12GB | Q5_K_M | 32768 | [FILL] | [FILL] |

## Training Details

- **Base model**: [FILL: name and link]
- **Fine-tuning method**: [FILL: e.g., LoRA, QLoRA, full fine-tune]
- **Training hardware**: [FILL: GPU used for training]
- **Training data**: [FILL: description of training data categories; do not redistribute datasets]
- **Training framework**: [FILL: e.g., axolotl, trl, custom]

## Limitations

1. **Hallucination risk** — May generate plausible but incorrect information
2. **Context window constraints** — Limited by VRAM on smaller GPUs
3. **Quantization artifacts** — Lower quantization may degrade output quality
4. **No multimodal capability** — Text-only input and output
5. **Language coverage** — Optimized for English and technical Spanish only
6. **Reasoning depth** — As a 3B–4B model, complex reasoning may be inconsistent
7. **Code correctness** — Generated code may contain bugs or security issues; always review

## Safety

- Model outputs should **never** be used for critical decisions without human review
- Generated code must be reviewed for security vulnerabilities before deployment
- All processing is local by design — no PII is collected or transmitted
- Destructive commands are flagged with warnings

## License

[FILL: License determined by base model. See LICENSE file and MODEL_LICENSES.md for details.]

The Kimari **software** (CLI, scripts, configurations) is released under the MIT License. The license for model weights depends on the base model.

## Hashes

[FILL: SHA-256 hashes for all distributable files. See hashes.sha256 in this repository.]

## Links

- **Project repository**: https://github.com/smouj/kimari-local-ai
- **Documentation**: https://github.com/smouj/kimari-local-ai/tree/main/docs
- **Model card source**: https://github.com/smouj/kimari-local-ai/blob/main/MODEL_CARD.md
- **License details**: See MODEL_LICENSES.md in this repository
- **Report issues**: https://github.com/smouj/kimari-local-ai/issues
```

---

## GGUF Release Considerations

### Git LFS

GGUF files are large (typically 2–6 GB for a 4B model). They **must** be stored via Git LFS, not committed directly to the repository.

```bash
# Install Git LFS (if not already)
git lfs install

# Track GGUF files
git lfs track "*.gguf"
git add .gitattributes

# Add and commit GGUF files (LFS handles the storage)
git add kimari-4b-q4_k_m.gguf
git commit -m "Add Q4_K_M GGUF quantization"
git push
```

### Separate Quant Repository (Optional)

If the number of GGUF variants grows large, consider creating a separate repository (e.g., `smouj/kimari-4b-GGUF`) to keep the main model repository clean. This is a common pattern on Hugging Face.

### Quantization Process

1. Merge LoRA adapter with base model (if applicable)
2. Convert merged model to GGUF using llama.cpp's `convert_hf_to_gguf.py`
3. Quantize with llama.cpp's `llama-quantize`:
   ```bash
   llama-quantize kimari-4b-f16.gguf kimari-4b-q4_k_m.gguf Q4_K_M
   llama-quantize kimari-4b-f16.gguf kimari-4b-q5_k_m.gguf Q5_K_M
   ```
4. Verify each quantization:
   ```bash
   llama-server -m kimari-4b-q4_k_m.gguf --port 11435 -c 8192
   # Test with a few prompts, then Ctrl+C
   ```

### No GGUF Files in the Kimari Git Repository

GGUF files must **never** be committed to the main `kimari-local-ai` Git repository. They are distributed exclusively through Hugging Face. The `.gitignore` already excludes `*.gguf`.

---

## Security and Access

### No HF API Keys in the Repository

- Hugging Face API tokens must **never** be committed to any repository
- Tokens should be stored in environment variables or a credential manager
- CI/CD pipelines should use repository secrets, not hardcoded tokens
- The `check-release.py` script checks for leaked secrets

### Gated Access (If Required)

If the base model license requires a gated access model (e.g., Meta Llama), the Kimari-4B repository should also implement gating:

1. Set up a gating form on Hugging Face
2. Require users to agree to the base model's terms before downloading
3. Include the base model's acceptable use policy in the model card

### No GGUF Files Committed

GGUF files are binary model files that should never be in the Git repository. They belong on Hugging Face, distributed via Git LFS.

---

## What NOT to Do

| Action | Why It's Wrong |
|--------|---------------|
| Upload before license review | Illegal distribution of derivative weights |
| Upload before eval results exist | No quality data = misleading release |
| Upload with placeholder benchmarks | False claims about model capability |
| Upload base model weights unmodified | Redundant; link to original instead |
| Include training data | License and privacy restrictions |
| Include HF API tokens | Security vulnerability |
| Commit GGUF to Git | Binary bloat; LFS required |
| Claim Kimari-4B is "released" before all blocks resolved | Dishonest and potentially illegal |
| Mix tokenizer files from different models | Will produce garbled output |
| Omit the base model attribution | License violation |

---

## Placeholder Repository Rules

Before any model weights are ready for distribution, a placeholder repository may be created on Hugging Face to signal project intent and reserve the repository name.

### Allowed in Placeholder

| File | Purpose |
|------|---------|
| `README.md` | Placeholder model card stating "Coming Soon — No weights available yet" |
| `MODEL_CARD.md` | Reference to Kimari project model card |
| `MODEL_LICENSES.md` | License layers document |
| Summary of `docs/HUGGINGFACE_RELEASE.md` | Release process documentation |

### NOT Allowed in Placeholder

| Prohibited | Reason |
|------------|--------|
| Model weights (safetensors) | No weights exist yet |
| Adapter weights | No adapter trained yet |
| GGUF files | No quantized model yet |
| Benchmark results | No evaluation performed yet — fake benchmarks are forbidden |
| Training data | License and privacy restrictions |
| HF API keys/tokens | Security risk |

### When to Create the Placeholder

- After the base model is formally accepted for private training
- After the license has been reviewed (at least preliminarily)
- No automated upload process — manual creation only
- No token/credential committed to any repository

### Transition from Placeholder to Full Release

When all hard blocks in the "Hard Blocks" section above are resolved, the placeholder can be updated to a full release with actual model weights, evaluation results, and quantized variants.

---

## Relationship to Other Project Documents

| Document | Relationship |
|----------|-------------|
| [MODEL_CARD.md](../MODEL_CARD.md) | Source of truth for model status; must be updated before HF release |
| [MODEL_LICENSES.md](../MODEL_LICENSES.md) | License layers and base model candidate details |
| [docs/MODEL_BASE_SELECTION.md](MODEL_BASE_SELECTION.md) | Base model candidate comparison |
| [docs/MODEL_TRAINING_PLAN.md](MODEL_TRAINING_PLAN.md) | Training phases including Phase 6 (HF Release) |
| [eval/README.md](../eval/README.md) | Evaluation suite that must produce results before release |
| [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md) | Software release checklist (separate from model release) |
| [docs/PYPI_RELEASE_GATE.md](PYPI_RELEASE_GATE.md) | PyPI release gate (software, not model) |
| [docs/MODEL_HASHING.md](MODEL_HASHING.md) | SHA-256 hash procedures for model files |

---

*This document is part of Kimari Local AI. No Hugging Face release has been made. No model has been trained. This guide exists to ensure a responsible, honest, and license-compliant release process when the time comes.*
