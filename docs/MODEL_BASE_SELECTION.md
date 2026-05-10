# Model Base Selection — Kimari-4B

> **Status:** All candidates are under review. No final selection has been made.
> This document is a decision-support comparison, not a commitment.

## Purpose

This document compares candidate base models for the proposed **Kimari-4B** fine-tuned
model. Kimari-4B is intended to be a consumer-GPU-friendly assistant model (targeting
GTX 1060 6 GB / GTX 1080 8 GB) that can be redistributed as quantized GGUF weights.

The primary selection criteria are:

1. **License clarity** — Can we legally redistribute derivative (fine-tuned) weights?
2. **Hardware compatibility** — Does the model fit in VRAM after Q4_K_M quantization?
3. **Capability baseline** — Is the base model strong enough in the domains we care
   about (coding, structured output, instruction-following)?
4. **Fine-tuning risk** — How well-understood is the architecture for LoRA/QLoRA
   fine-tuning?

---

## Comparison Table

| Candidate | Params | License | Context Length | Strengths | Risks | GTX 1060/1080 Compatibility | Fine-Tuning Risk | Release Suitability | Status |
|---|---|---|---|---|---|---|---|---|---|
| **HuggingFaceTB/SmolLM3-3B** | 3B | Apache 2.0 | Long context support | Open license; Apache 2.0 permits derivative redistribution; well-documented training pipeline; good fit for local inference | Less capable in coding tasks compared to Qwen; smaller community fine-tuning ecosystem | **Good** — 3B at Q4_K_M ≈ 2 GB, fits easily on both GTX 1060 and GTX 1080 | **Low** — Well-understood transformer architecture; Apache 2.0 means no license complications for derivative works | **High** — Apache 2.0 allows derivative redistribution without special attribution beyond the license terms | Under Review |
| **Qwen/Qwen2.5-3B-Instruct** | 3.09B (36 layers, GQA) | qwen-research | 32K | Strong coding, math, JSON, and multilingual performance; popular architecture with extensive community fine-tuning knowledge; GQA for efficient inference | License must be reviewed for derivative weights redistribution; "qwen-research" is not a standard open-source license — terms are specific to Qwen and may restrict commercial derivative release | **Good** — 3.09B at Q4_K_M ≈ 2 GB, fits easily on both GTX 1060 and GTX 1080 | **Low-Medium** — Popular architecture with well-documented fine-tuning recipes, but GQA adds slight complexity | **Medium** — License review required before any derivative weights can be redistributed; terms must be verified for commercial and non-commercial derivative distribution | Under Review |
| **meta-llama/Llama-3.2-3B-Instruct** | 3B | Meta Community License (custom, not standard open-source) | 128K (with RoPE scaling) | Strong general performance; Meta ecosystem and broad community support; very long context window with RoPE scaling | Custom license with attribution/naming requirements for derivatives; redistribution constraints (must review Meta's acceptable use policy and derivative model naming rules); not OSI-approved open-source | **Good** — 3B at Q4_K_M ≈ 2 GB, fits easily on both GTX 1060 and GTX 1080 | **Low** — Well-known architecture with extensive fine-tuning documentation and tooling | **Low-Medium** — License constraints for redistribution; Meta requires specific attribution and may restrict derivative model naming; commercial use has monthly active user caps | Under Review |
| **Microsoft Phi-3.5-mini** *(optional)* | ~3.8B | To be verified | 128K | Strong reasoning for size; Microsoft ecosystem | License/availability must be verified before consideration; Microsoft's model licenses have varied (some permissive, some with restrictions) | **To be evaluated** — If ~3.8B, Q4_K_M ≈ 2.5 GB, likely fits but needs verification on GTX 1060 6 GB | **To be evaluated** — Architecture specifics and fine-tuning community support need assessment | **To be evaluated** — Cannot assess until license is confirmed | To be evaluated |

---

## Detailed Analysis

### 1. SmolLM3-3B — Safest Legal Choice

**Why it leads for a first preview release:**

- **Apache 2.0** is the most permissive and well-understood open-source license in this
  comparison. It explicitly grants rights to create and distribute derivative works,
  including fine-tuned model weights, with minimal requirements (license copy, copyright
  notice, state changes).
- The HuggingFace team's training documentation is thorough and transparent, which
  reduces risk of hidden training data contamination concerns.
- At 3B parameters, Q4_K_M quantization produces a ~2 GB GGUF file — well within
  the GTX 1060 6 GB VRAM budget with room for context.

**Honest assessment of weaknesses:**

- Benchmark data and community reports indicate SmolLM3 is less capable than Qwen2.5
  in coding, mathematical reasoning, and structured output generation.
- The fine-tuning community around SmolLM3 is smaller, meaning fewer reference recipes
  and LoRA configurations to draw from.
- For Kimari's target use case (coding assistant, JSON/structured output, local
  inference), SmolLM3 may require more extensive fine-tuning to reach acceptable
  capability levels.

### 2. Qwen2.5-3B-Instruct — Strongest Capability Candidate

**Why it's the most technically attractive:**

- Qwen2.5-3B-Instruct consistently outperforms other 3B-class models on coding,
  math, and multilingual benchmarks. It is the strongest raw capability candidate
  in this comparison.
- Grouped Query Attention (GQA) provides efficient inference, which is valuable for
  consumer GPU scenarios.
- 32K context length is sufficient for most local-assistant use cases.
- The Qwen fine-tuning community is large and well-documented.

**Honest assessment of risks:**

- The **qwen-research** license is the critical blocker. It is not a standard
  open-source license (not OSI-approved), and its specific terms regarding derivative
  weight redistribution must be carefully reviewed by someone with legal expertise
  before any Kimari-4B weights based on Qwen2.5 could be released.
- If the license does not permit derivative redistribution (or imposes conditions
  we cannot meet), this candidate becomes unsuitable for Kimari-4B regardless of
  its capabilities.
- There is also a risk that the license terms could change between now and when
  Kimari-4B is ready for release.

### 3. Llama-3.2-3B-Instruct — Requires Careful License Review

**Why it's worth considering:**

- Strong general performance backed by Meta's extensive training infrastructure.
- 128K context with RoPE scaling — the longest context window in this comparison.
- Very well-known architecture with massive community fine-tuning knowledge.

**Honest assessment of risks:**

- The **Meta Community License** is a custom license, not standard open-source. Key
  concerns:
  - Derivative models may require specific naming conventions (e.g., must include
    "Llama" in the name).
  - There may be restrictions on how derivative weights can be distributed.
  - The acceptable use policy prohibits certain use cases.
  - For models with >700 million monthly active users, a separate commercial license
    is required. While Kimari-4B is unlikely to hit this threshold, the clause
    introduces legal complexity.
- Redistribution of fine-tuned weights under this license requires careful compliance
  review. A mistake here could create legal liability.

### 4. Phi-3.5-mini — To Be Evaluated

This candidate is marked as **optional** and **to be evaluated**. It should only be
added to the formal comparison after:

- The specific model variant's license is confirmed and reviewed.
- Availability on HuggingFace (or equivalent) is verified for GGUF conversion.
- VRAM compatibility with GTX 1060 6 GB is tested (3.8B at Q4_K_M may be tight).

**No assessment should be assumed until these checks are complete.**

---

## Recommendation Framework (Not a Final Decision)

Based on the analysis above, the following framework is offered — **not a final
selection**:

| Priority | Scenario | Candidate | Rationale |
|---|---|---|---|
| 1st | First preview release where license certainty is paramount | SmolLM3-3B | Apache 2.0 is the safest legal foundation; no derivative redistribution ambiguity |
| 2nd | Maximum capability where license can be resolved | Qwen2.5-3B-Instruct | Strongest baseline capability, but **only** if qwen-research license permits derivative redistribution |
| 3rd | Long-context requirements with compliance overhead | Llama-3.2-3B-Instruct | 128K context is compelling, but Meta Community License adds significant compliance burden |
| TBD | Pending license verification | Phi-3.5-mini | Cannot be ranked until license is confirmed |

**Important:** This framework reflects trade-offs, not decisions. The actual selection
will depend on:

1. Legal review of the Qwen and Meta licenses for derivative weight redistribution.
2. Empirical fine-tuning results (LoRA/QLoRA) on each candidate with Kimari training
   data.
3. Benchmark evaluation of fine-tuned outputs on Kimari's target tasks.
4. Community feedback during the alpha phase.

---

## Constraints and Honest Risks

- **No candidate is chosen.** All remain under review.
- **License accuracy matters.** The license information above is based on the best
  available public information as of the document creation date. Licenses can change;
  always verify the current license at the model's official source before making
  decisions.
- **GTX 1060 6 GB is a hard constraint.** Any candidate that cannot run at Q4_K_M
  quantization within 6 GB VRAM (with room for context) is disqualified.
- **Fine-tuning may change the picture.** A weaker base model that fine-tunes well
  may outperform a stronger base model that fine-tunes poorly on Kimari's specific
  training data. Empirical testing is required.
- **Redistribution is the core question.** Kimari-4B is intended to be distributed
  as quantized GGUF weights. If a base model's license does not clearly permit
  redistribution of fine-tuned/quantized derivatives, that candidate is unsuitable
  regardless of its other merits.

---

*This document does not constitute legal advice. Consult a qualified attorney for
license compliance decisions.*
