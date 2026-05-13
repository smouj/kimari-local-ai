# Kimari Open-License Policy

> **Version**: v0.1.57-alpha  
> **Status**: Active policy  
> **Last updated**: 2026-05-13

## 1. Purpose

This document defines the licensing policy for all official Kimari models, datasets, and adapters. The goal is to ensure that every publicly released Kimari artifact is built on a foundation with a **free and permissive license**, making Kimari safe to use, modify, and redistribute.

## 2. Core Principle

```
No official Kimari model shall depend on a base with a restrictive,
research-only, non-commercial, or ambiguous license.
```

## 3. Accepted Licenses

| License | Status | Notes |
|---------|--------|-------|
| Apache 2.0 | ✅ Ideal | Preferred for all official models |
| MIT | ✅ Ideal | Fully permissive |
| BSD (2/3-clause) | ✅ Ideal | Fully permissive |
| CC-BY 4.0 | ✅ Acceptable | Attribution required |
| CC-BY-SA 4.0 | ⚠️ Caution | Share-alike required; review compatibility |
| MPL 2.0 | ⚠️ Caution | Weak copyleft; review case by case |
| Other permissive | ⚠️ Review | Must be reviewed before use |

## 4. Blocked Licenses

| License Type | Decision | Rationale |
|---|---|---|
| Non-Commercial (CC-BY-NC, etc.) | ❌ Blocked | Cannot be used commercially |
| Research-Only | ❌ Blocked | Cannot be redistributed freely |
| Unknown / Unspecified | ❌ Blocked | Legal risk too high |
| Custom Restrictive | ❌ Blocked | Must be reviewed; default is blocked |
| Meta Llama License | ⚠️ Review Only | Not Apache/MIT/BSD compatible; private research only |
| Gemma License | ⚠️ Review Only | Not standard permissive; private research only |
| Qwen Research License | ⚠️ Review Only | Not for official public Kimari models |

## 5. Model Base Policy

### 5.1 Official Kimari Models

All official Kimari models must use a base model from the **Accepted** list above. The base model's license must:

1. Allow commercial use
2. Allow modification and redistribution
3. Allow derivative works
4. Have no field-of-use restrictions
5. Be compatible with Apache 2.0 or MIT

### 5.2 Current Approved Base Models

| Model | Size | License | Role |
|-------|------|---------|------|
| `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | Apache 2.0 | Kimari Runtime 1.5B |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | 1.7B | Apache 2.0 | Runtime alternative |
| `HuggingFaceTB/SmolLM3-3B` | 3B | Apache 2.0 | Kimari Core 3B |
| `Qwen/Qwen3-4B-Instruct-2507` | 4B | Apache 2.0 | Kimari-4B candidate |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 1.1B | Apache 2.0 | Smoke/test model |

### 5.3 Quarantined Models (Private Research Only)

| Model | License | Reason |
|-------|---------|--------|
| `Qwen/Qwen2.5-3B-Instruct` | qwen-research | Not for public release |
| `google/gemma-3-4b-it` | Gemma license | Not standard permissive |
| Meta Llama 3.x | Meta license | Not Apache/MIT/BSD |
| Any NC model | Various | Non-commercial |

## 6. Dataset Policy

### 6.1 Accepted Data Sources

| Source | Allowed | Condition |
|--------|---------|-----------|
| Synthetic data (self-generated) | ✅ | Must be reviewed for quality |
| Kimari project docs | ✅ | MIT licensed |
| Hand-written examples | ✅ | No PII |
| Own code | ✅ | License-compatible |
| Apache/MIT/BSD datasets | ✅ | License must be documented |
| StackExchange data | ⚠️ | CC BY-SA; attribution required, careful review |

### 6.2 Blocked Data Sources

| Source | Blocked | Reason |
|--------|---------|--------|
| Real user logs | ❌ | PII and consent issues |
| Private chats | ❌ | Privacy violations |
| Data without clear license | ❌ | Legal risk |
| Outputs from closed models | ⚠️ | Terms may restrict derivative use |

### 6.3 Dataset Manifest Requirement

Every training dataset must have a manifest documenting:

1. Source of each example
2. License of each source
3. Whether examples are synthetic or curated
4. PII review status
5. Total count per category

## 7. Adapter Policy

- Adapters trained on permissive-base models inherit the base license for the combined work
- Adapter license compatibility must be documented before public release
- Private adapters (not released) may use quarantined bases for research
- Public adapter release requires license inheritance documentation

## 8. GGUF Policy

- GGUF exports must include license metadata in the model card
- Base model license must be permissive (from Accepted list)
- GGUF quantization must not introduce additional restrictions
- No GGUF release without license review

## 9. License Inheritance

When Kimari trains an adapter on a permissive base:

```
Base model: Apache 2.0
+ Kimari adapter: MIT
= Combined work: Apache 2.0 (base) + MIT (adapter)
```

The model card must clearly state:
- Base model name and license
- Adapter license
- Combined work license
- Any attribution requirements

## 10. Release Gate Requirements

Before any model reaches `PUBLIC_PREVIEW_ALLOWED`:

1. ✅ Base model license verified as permissive (Apache/MIT/BSD)
2. ✅ Dataset manifest documented with per-license sources
3. ✅ Adapter license inheritance documented
4. ✅ GGUF license metadata included
5. ✅ No safety regression from base model
6. ✅ No data from blocked sources
7. ✅ No outputs from closed-model terms-restricted sources
8. ✅ Human review of all eval results
9. ✅ Explicit written approval from project owner

## 11. Enforcement

- This policy is enforced by `scripts/release/check-release.py`
- This policy is verified by `tests/test_release_v0157.py`
- This policy is documented in `RELEASE_CHECKLIST.md`
- Gate remains BLOCKED until all license requirements are met

---

_This policy ensures Kimari remains genuinely open, redistributable, and legally safe._