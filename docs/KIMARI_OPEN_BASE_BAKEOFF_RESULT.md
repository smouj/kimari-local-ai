# Kimari Open Base Bakeoff Result

> **Version**: v0.1.58-alpha  
> **Status**: Pending — No evaluation executed yet  
> **Gate**: BLOCKED — No public benchmark claims  
> **Last updated**: 2026-05-13

## Overview

This document records the results of the open-license base model bakeoff for Kimari. The bakeoff compares permissive-license base models to select the best foundation for each Kimari model line.

## Candidates

| ID | Model | License | Size | Role | GGUF | GTX 1060 | GTX 1080 |
|----|-------|---------|------|------|------|-----------|----------|
| qwen25-15b | Qwen/Qwen2.5-1.5B-Instruct | Apache 2.0 | 1.5B | Runtime | ✅ | ✅ | ✅ |
| smollm2-17b | HuggingFaceTB/SmolLM2-1.7B-Instruct | Apache 2.0 | 1.7B | Runtime alt | ✅ | ✅ | ✅ |
| smollm3-3b | HuggingFaceTB/SmolLM3-3B | Apache 2.0 | 3B | Core | ✅ | ✅ | ✅ |
| qwen3-4b | Qwen/Qwen3-4B-Instruct-2507 | Apache 2.0 | 4B | 4B candidate | ✅ | Probable | ✅ |

## Blocked (Not Evaluated)

| Model | License | Reason |
|-------|---------|--------|
| Qwen/Qwen2.5-3B-Instruct | qwen-research | Research-only license |
| google/gemma-3-4b-it | Gemma | Custom restrictive license |
| Meta Llama 3.x | Meta Llama | Custom restrictive license |
| Any NC model | Various | Non-commercial |

## Evaluation Phases

| Phase | Prompts | Candidates | Status |
|-------|---------|-------------|--------|
| Smoke | 5 | All 4 | ⏳ Pending |
| Subset10 | 10 | All 4 | ⏳ Pending |
| Subset30 | 30 | Top 2 | ⏳ Pending |

## Evaluation Categories (KimariEval Private v1)

| Category | Count | Focus |
|----------|-------|-------|
| spanish_technical | 14 | Spanish technical Q&A |
| coding_debug | 14 | Code debugging |
| server_ops | 15 | Linux/sysadmin tasks |
| local_llm_gguf | 15 | Local AI/GGUF/CUDA/VRAM |
| openclaw_agents | 14 | Agent/OpenClaw workflows |
| refusal_safety | 15 | Safety/refusal behavior |
| style_consistency | 15 | Kimari style consistency |

## Metrics

| Metric | Method | Status |
|--------|--------|--------|
| Completion rate | Automatic | ⏳ Pending |
| Error rate | Automatic | ⏳ Pending |
| VRAM usage | llama-server benchmark | ⏳ Pending |
| Tokens/s (prompt) | llama-server benchmark | ⏳ Pending |
| Tokens/s (generation) | llama-server benchmark | ⏳ Pending |
| GGUF Q4_K_M size | File size | ⏳ Pending |
| Quality | Manual review | ⏳ Pending |

## GGUF Feasibility (Estimated)

| Model | Q4_K_M Size | GTX 1060 6GB | GTX 1080 8GB | License |
|-------|-------------|--------------|--------------|---------|
| Qwen2.5-1.5B | ~1.0 GB | ✅ Yes | ✅ Yes | Apache 2.0 |
| SmolLM2-1.7B | ~1.2 GB | ✅ Yes | ✅ Yes | Apache 2.0 |
| SmolLM3-3B | ~2.0 GB | ✅ Yes | ✅ Yes | Apache 2.0 |
| Qwen3-4B | ~2.5 GB | ⚠️ Probable | ✅ Yes | Apache 2.0 |

## Results

**No results yet.** The bakeoff has not been executed. This section will be updated when evaluation data is available.

## Decision

**No decision yet.** The following will be populated after evaluation:

| Line | Recommended Base | Reason |
|------|-----------------|--------|
| Runtime 1.5B | ⏳ Pending | — |
| Core 3B | ⏳ Pending | — |
| 4B Candidate | ⏳ Pending | — |

## Safety Constraints

- **No training** — bakeoff only evaluates base models
- **No HF Jobs** — evaluation uses local or HF Jobs endpoints only
- **No public weights/adapters/GGUF** — results are private
- **No public benchmark claims** — manual review required
- **Only permissive-license bases** — Apache 2.0, MIT, BSD
- **Gate BLOCKED** — no release decisions until review

---

_Do not cite this document as a public benchmark. Results are pending manual review._