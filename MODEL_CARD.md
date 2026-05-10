# Model Card: Kimari-4B

> **Version:** v0.1.19-alpha (project framework)
> **Last Updated:** 2026-05-21
> **Developer:** Smouj ([@smouj013](https://x.com/smouj013))

---

## Status

**Planned / Training Design**

Kimari-4B has **not been trained yet**. No model weights exist, no training run has been started, and no benchmarks have been measured. This model card describes the **design targets and planned architecture** for a future fine-tuned local LLM. All specifications below are aspirational and subject to change during development.

> **Important:** Until Kimari-4B is released, the Kimari framework can run compatible GGUF base models for testing. See `models/README.md` for recommended test models.

---

## Weights Availability

**No weights have been released.** Kimari-4B model weights do not exist in any form — no safetensors, no GGUF, no Hugging Face repository, no download link. Any claim of available Kimari-4B weights is false.

When weights are eventually produced, they will be announced through official channels and this model card will be updated accordingly.

---

## Model Identity

| Field | Value |
|-------|-------|
| **Model Name** | Kimari-4B |
| **Model Type** | Causal Language Model (Transformer) — fine-tuned for local coding, system administration, and agent assistance |
| **Target Parameter Class** | 3B–4B parameters |
| **Target Context Length** | Up to 16,384 tokens (profile-dependent) |
| **Intended Runtime** | llama.cpp / llama-server via GGUF quantization |
| **Primary Languages** | English, Technical Spanish |

---

## Target Hardware

Kimari-4B is designed to run entirely on consumer-grade GPUs available since 2016. The following table defines the **minimum and recommended hardware targets**:

| GPU | VRAM | Recommended Quantization | Target Context | Notes |
|-----|------|------------------------|----------------|-------|
| NVIDIA GTX 1060 | 6 GB | GGUF Q4_K_M | 8,192 tokens | Minimum viable GPU; safe VRAM budget ~4.9 GB |
| NVIDIA GTX 1080 | 8 GB | GGUF Q5_K_M | 16,384 tokens | Comfortable Q5 fit; safe VRAM budget ~6.8 GB |
| NVIDIA RTX 2060 | 6 GB | GGUF Q4_K_M | 8,192 tokens | Similar to GTX 1060 with newer architecture |
| NVIDIA RTX 3060 | 12 GB | GGUF Q5_K_M | 32,768 tokens | Extended context; room for larger batches |

> These are **design targets**, not guaranteed performance levels. Actual performance will depend on the final base model, quantization behavior, and training outcome.

---

## Planned Formats

| Format | Status | Notes |
|--------|--------|-------|
| safetensors (full base or adapter) | Planned | Availability depends on selected base model and license |
| GGUF Q4_K_M | Planned | Primary distribution format for 6 GB VRAM targets |
| GGUF Q5_K_M | Planned | Higher quality for 8 GB+ VRAM targets |
| GGUF IQ4_XS | Optional | May be produced if quality degradation is acceptable for maximum compression |

> Format availability is contingent on the selected base model's license terms. Some licenses may restrict distribution of derivative weights or require specific attribution.

---

## Base Model Candidates

The base model has **not been selected yet**. The following candidates are under evaluation. Each has distinct trade-offs in capability, licensing, and community ecosystem:

| Candidate | Parameters | License | Strengths | Concerns |
|-----------|-----------|---------|-----------|----------|
| **SmolLM3-3B** | ~3B | Apache 2.0 | Fully permissive license; allows unrestricted distribution of fine-tuned weights and commercial use; active community | Smaller parameter count may limit reasoning depth; relatively newer model with less community benchmarking |
| **Qwen2.5-3B-Instruct** | ~3B | Requires review | Strong multilingual and coding capabilities; well-benchmarked; instruction-tuned out of the box | License must be reviewed before commitment — may impose restrictions on derivative distribution or commercial use |
| **Llama 3.2 3B** | ~3B | Llama 3.2 Community License | Strong general capability; Meta's training infrastructure; large ecosystem | Custom Meta license with specific use restrictions (e.g., monthly active user thresholds, acceptable use policy); may constrain distribution of fine-tuned weights |

### Selection Criteria

The final base model selection will be based on:

1. **License compatibility** — Must permit distribution of fine-tuned weights in planned formats (GGUF, safetensors)
2. **Capability baseline** — Pre-training quality in coding, reasoning, and multilingual understanding
3. **Community benchmarks** — Available evaluation data (MMLU, HumanEval, etc.) for the base model
4. **Tokenization alignment** — No mixing of models/tokenizers across different architectures
5. **Ecosystem support** — llama.cpp / GGUF conversion maturity for the architecture

> **No base model has been definitively chosen.** The "Selected Base" field below will be updated when a final decision is made.

### Selected Base Model

**HuggingFaceTB/SmolLM3-3B** — Accepted for first private SFT training run. NOT yet accepted for public release. Public release base subject to evaluation results and full license review. See [docs/BASE_MODEL_ACCEPTANCE.md](docs/BASE_MODEL_ACCEPTANCE.md) for details.

---

## License

**TBD** — The license for Kimari-4B weights depends entirely on the selected base model:

- If **SmolLM3-3B** (Apache 2.0) is selected → Kimari-4B weights could be released under Apache 2.0
- If **Qwen2.5-3B-Instruct** is selected → License TBD pending review of Qwen's terms
- If **Llama 3.2 3B** is selected → Llama 3.2 Community License applies, with its specific restrictions on derivative distribution and commercial use

The Kimari **software** (CLI, scripts, configurations) is released under the MIT License regardless of the model license. See [MODEL_LICENSES.md](MODEL_LICENSES.md) for full details on license layers.

> **Do not assume any specific license for Kimari-4B weights until the base model is selected and license compatibility is confirmed.**

---

## Training Status

| Aspect | Status |
|--------|--------|
| Base model selection | **Accepted for private SFT (SmolLM3-3B)** |
| Training data curation | **Not started** |
| Fine-tuning run | **Not started** |
| Evaluation | **Not started** |
| Weight release | **Not started** |

Training has not begun. No GPUs have been allocated, no training scripts have been executed, and no checkpoints exist. The project is currently in the **training design** phase — defining requirements, evaluating base models, and planning data curation.

---

## Pipeline Status (v0.1.19-alpha)

| Aspect | Status |
|--------|--------|
| Current model work | v0.1.19 private SFT candidate accepted |
| Base selection status | SmolLM3-3B accepted for first private SFT candidate |
| Dataset status | v0 synthetic dataset prepared (SFT + preference + holdout) |
| Training status | Not started (configs and validation ready) |
| Evaluation status | KimariFit scoring plan prepared, dimensions defined |
| GGUF export | Plan defined (Q4_K_M, Q5_K_M, IQ4_XS) |
| HF release | Placeholder plan defined, not executed |

---

## Benchmarks

**No benchmarks have been measured.** Kimari-4B does not exist as a trained model, so no benchmark scores are available.

The following table lists **evaluation targets only** — these are aspirational goals for the future model, not achieved results:

### Evaluation Targets (Not Achieved)

| Benchmark | Metric | Q4_K_M Target | Q5_K_M Target | Notes |
|-----------|--------|--------------|--------------|-------|
| Inference Speed (GTX 1060) | tokens/second | > 15 t/s | N/A (6 GB limited) | Target for Q4_K_M on minimum hardware |
| Inference Speed (GTX 1080) | tokens/second | > 20 t/s | > 15 t/s | Q5 fits comfortably on 8 GB |
| Time to First Token (TTFT) | seconds | < 2s | < 3s | Prompt processing latency |
| MMLU (5-shot) | accuracy | TBD | TBD | Target to be set after base model selection |
| HumanEval (pass@1) | accuracy | TBD | TBD | Core coding benchmark target |
| MultiPL-E (Python) | pass@1 | TBD | TBD | Coding capability target |
| SWE-bench (Lite) | resolved % | TBD | TBD | Agent/reasoning capability target |

> **These are targets, not results.** Actual performance may differ significantly. Benchmark targets will be refined after base model selection and initial evaluation of the base model's capabilities.

---

## Intended Uses

### Primary Use Cases

1. **Local coding assistant** — Code generation, debugging, code review, and explanation in Python, TypeScript, shell scripting, and other languages
2. **System administration** — Linux and Windows troubleshooting, automation script generation, log analysis, and infrastructure guidance
3. **Agent orchestration** — Multi-step reasoning for semi-autonomous tasks, tool use planning, and decision chains
4. **Technical documentation** — Writing and explaining technical concepts, generating documentation, and summarizing complex topics
5. **Bilingual assistance** — English and technical Spanish support for IT infrastructure, DevOps, and software engineering

### Target Users

- Developers working locally without internet access (air-gapped environments)
- System administrators needing quick, private troubleshooting assistance
- Teams with data privacy requirements requiring on-premise AI
- Students and learners in technical fields
- Users with consumer-grade GPUs (GTX 1060 or better)

---

## Out-of-Scope Uses

The following uses are **explicitly out of scope** for Kimari-4B:

- **Medical, legal, or financial advice** — The model is not qualified for professional advice in regulated domains
- **Real-time safety-critical systems** — Do not use for medical diagnosis, autonomous vehicle control, or any system where failure could cause harm
- **Surveillance or privacy violation** — Do not use to process personal data without consent or for surveillance purposes
- **Generation of harmful content** — Malware, exploits, harassment, disinformation, or any content intended to cause harm
- **Replacing human expertise in critical decisions** — Model outputs must always be reviewed by a qualified human
- **Large-scale commercial deployment without license review** — Ensure base model license permits your intended use case
- **Multimodal tasks** — Kimari-4B is text-only; it does not process images, audio, or video
- **General-purpose knowledge tasks beyond technical domains** — The model is specialized for coding/sysadmin/agent tasks; general knowledge accuracy is not a design priority

---

## Limitations

1. **No real-time knowledge** — The model has no access to the internet, APIs, or current events. All knowledge is frozen at training time.
2. **Hallucination risk** — Like all LLMs, Kimari-4B may generate plausible but factually incorrect information, especially in domains outside its training focus.
3. **Context window constraints** — Available context length is limited by VRAM. Long documents or conversations may be truncated. On 6 GB GPUs, context is limited to ~8K tokens.
4. **Quantization artifacts** — Lower quantization levels (Q4_K_M, IQ4_XS) may degrade output quality, especially for nuanced reasoning or precise code generation.
5. **No multimodal capability** — Text-only input and output. Cannot process images, diagrams, audio, or other modalities.
6. **Language coverage** — Optimized for English and technical Spanish. Other languages are not tested or supported.
7. **Reasoning depth** — As a 3B–4B parameter model, complex multi-step reasoning may be inconsistent or incorrect. Larger models will generally outperform on difficult reasoning tasks.
8. **Code correctness** — Generated code may contain bugs, security vulnerabilities, or deprecated APIs. Always review and test generated code before use.
9. **Base model limitations inherited** — Whatever limitations the selected base model has (biases, knowledge gaps, safety concerns) will be inherited by Kimari-4B.
10. **No self-correction guarantee** — The model cannot reliably identify its own mistakes. External validation is always required.

---

## Safety Notes

### Harm Reduction

- Model outputs should **never** be used for critical decisions without human review
- Generated code must be reviewed for security vulnerabilities before deployment
- No PII is collected or transmitted — all processing is local by design
- Model weights are not included in this repository

### Known Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| Misinformation | Model may generate factually incorrect content with high confidence | Always verify outputs against authoritative sources |
| Bias | Training data may contain biases that propagate to outputs | Be aware of potential bias; do not use for decisions affecting people |
| Code vulnerabilities | Generated code may contain security flaws | Mandatory human code review before any deployment |
| Over-reliance | Users may trust model outputs without verification | Treat model as a suggestion tool, not an authority |
| Prompt injection | Malicious prompts may manipulate outputs in unexpected ways | Sanitize inputs in production; do not pipe untrusted input directly |

### Responsible Use

Users are responsible for:

- Reviewing all model outputs before use in any context
- Not using the model for harmful, illegal, or unethical purposes
- Complying with applicable laws and regulations in their jurisdiction
- Ensuring base model license compliance for their specific use case
- Implementing appropriate safeguards when deploying in shared environments

---

## Release Checklist

The following items must be completed before Kimari-4B weights can be released:

| # | Item | Status |
|---|------|--------|
| 1 | Base model selected and license reviewed | 🟡 In Progress (SmolLM3-3B accepted for private training) |
| 2 | License compatibility confirmed for all planned formats | ❌ Not started |
| 3 | Training data curated and documented | ❌ Not started |
| 4 | Fine-tuning completed | ❌ Not started |
| 5 | Base model benchmarks measured (pre-fine-tune baseline) | ❌ Not started |
| 6 | Fine-tuned model benchmarks measured | ❌ Not started |
| 7 | GGUF quantization produced and validated (Q4_K_M, Q5_K_M) | ❌ Not started |
| 8 | Optional IQ4_XS quantization evaluated | ❌ Not started |
| 9 | Inference speed tested on all target GPUs | ❌ Not started |
| 10 | Safety evaluation completed | ❌ Not started |
| 11 | Model card updated with actual benchmark results | ❌ Not started |
| 12 | MODEL_LICENSES.md updated with confirmed license | ❌ Not started |
| 13 | Hugging Face repository created (or equivalent distribution) | ❌ Not started |
| 14 | Kimari framework model registry updated | ❌ Not started |
| 15 | Community announcement published | ❌ Not started |

> This checklist will be updated as progress is made. No item has been started as of v0.1.17-alpha.
>
> As of v0.1.19-alpha, SmolLM3-3B has been accepted for first private SFT training. No real training, evaluation, or public release has occurred.

---

## Version History

| Version | Date | Status | Changes |
|---------|------|--------|---------|
| 0.1.19-alpha | 2026-05-21 | Planned | SmolLM3-3B accepted for first private SFT candidate; dataset v0; training readiness validation; KimariFit scoring plan; v0 training configs; HF placeholder plan |
| 0.1.18-alpha | 2026-05-20 | Planned | Pipeline dry-run: base decision record, seed datasets, dataset mix builder, KimariFit dry-run harness, GGUF export plan |
| 0.1.17-alpha | 2026-05-19 | Planned | Complete model card rewrite for v0.1.17-alpha; transparent status, honest evaluation targets, expanded safety and limitation sections |
| — | TBD | Future | Initial training design document based on selected base model |
| — | TBD | Future | First fine-tuning run and benchmark results |
| — | TBD | Future | Weight release (safetensors + GGUF) |

---

*This model card will be updated as development progresses. No information herein should be interpreted as a promise or guarantee of future results.*
