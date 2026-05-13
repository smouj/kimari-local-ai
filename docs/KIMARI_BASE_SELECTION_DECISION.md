# Kimari Base Selection Decision

> **Version**: v0.1.58-alpha  
> **Status**: Pending — No evaluation executed yet  
> **Gate**: BLOCKED — No release decisions until bakeoff complete  
> **Last updated**: 2026-05-13

## Decision Criteria

The base model for each Kimari line will be selected based on:

1. **License compatibility** — Must be Apache 2.0, MIT, BSD, or equivalent permissive
2. **Quality** — Performance on KimariEval categories (manual review, not auto-scored)
3. **VRAM feasibility** — Must run on consumer hardware (GTX 1060/1080)
4. **GGUF availability** — Must have quantized GGUF versions
5. **Cost** — Training and evaluation cost must be reasonable
6. **Safety** — No regression in refusal/safety behavior from base model
7. **JSON/tool following** — Structured output quality for agent workflows

## Candidates

| Line | Candidate | License | Size | GGUF Q4 | GTX 1060 | GTX 1080 |
|------|-----------|---------|------|---------|----------|----------|
| Runtime | Qwen/Qwen2.5-1.5B-Instruct | Apache 2.0 | 1.5B | ✅ | ✅ | ✅ |
| Runtime alt | HuggingFaceTB/SmolLM2-1.7B-Instruct | Apache 2.0 | 1.7B | ✅ | ✅ | ✅ |
| Core | HuggingFaceTB/SmolLM3-3B | Apache 2.0 | 3B | ✅ | ✅ | ✅ |
| 4B candidate | Qwen/Qwen3-4B-Instruct-2507 | Apache 2.0 | 4B | ✅ | ⚠️ | ✅ |

## Current Recommendation (Pre-Bakeoff)

Based on available information (NOT yet confirmed by evaluation):

| Line | Tentative Recommendation | Rationale |
|------|--------------------------|-----------|
| Runtime 1.5B | Qwen/Qwen2.5-1.5B-Instruct | Already tested in micro-SFT, Apache 2.0, good multilingual support |
| Core 3B | HuggingFaceTB/SmolLM3-3B | Fully open, 3B fits well in GTX 1060/1080, Apache 2.0 |
| 4B candidate | Qwen/Qwen3-4B-Instruct-2507 | Strong code/tools, Apache 2.0, but needs GGUF/VRAM validation |

**These are TENTATIVE. The bakeoff will confirm or change them.**

## Decision Process

1. **Bakeoff Phase 1 (Smoke)**: 5 prompts per model, all 4 candidates
2. **Bakeoff Phase 2 (Subset10)**: 10 prompts per model, all 4 candidates
3. **Bakeoff Phase 3 (Subset30)**: 30 prompts, top 2 candidates
4. **Manual Review**: Human review of all outputs for quality, safety, style
5. **GGUF Validation**: Confirm quantized versions work on target hardware
6. **Final Decision**: Document in this file with rationale

## Blocked Models

The following models are NOT considered for official Kimari releases:

| Model | License | Reason |
|-------|---------|--------|
| Qwen/Qwen2.5-3B-Instruct | qwen-research | Research-only, not permissive |
| google/gemma-3-4b-it | Gemma | Custom license, not standard permissive |
| Meta Llama 3.x | Meta Llama | Custom restrictive license |
| Any NC model | Various | Non-commercial |

## Safety

- **No final decision** until bakeoff data is available
- **No model release** until gate review
- **Only permissive-license bases** are considered
- **Gate BLOCKED** until all criteria are met

---

_This decision document will be updated when bakeoff results are available._