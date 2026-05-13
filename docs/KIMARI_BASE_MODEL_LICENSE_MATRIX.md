# Kimari Base Model License Matrix

> **Version**: v0.1.57-alpha  
> **Last updated**: 2026-05-13  
> **Policy**: See `KIMARI_OPEN_LICENSE_POLICY.md`

## Allowed Models — Official Kimari Models Only

These models have permissive licenses and are approved as bases for official public Kimari models.

| Model | Parameters | License | License URL | Kimari Role | Status |
|-------|-----------|---------|-------------|-------------|--------|
| `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | Apache 2.0 | https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct | Kimari Runtime 1.5B | ✅ Approved |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | 1.7B | Apache 2.0 | https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct | Runtime alternative | ✅ Approved |
| `HuggingFaceTB/SmolLM3-3B` | 3B | Apache 2.0 | https://huggingface.co/HuggingFaceTB/SmolLM3-3B | Kimari Core 3B | ✅ Approved |
| `Qwen/Qwen3-4B-Instruct-2507` | 4B | Apache 2.0 | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 | Kimari-4B candidate | ✅ Approved |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 1.1B | Apache 2.0 | https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0 | Smoke/test model | ✅ Approved |

### Selection Criteria

Each approved model must satisfy ALL of:

1. **License**: Apache 2.0, MIT, BSD, or equivalent permissive
2. **Weights available**: Publicly downloadable from Hugging Face
3. **Commercial use**: Explicitly allowed by license
4. **Derivative works**: Explicitly allowed by license
5. **Redistribution**: Explicitly allowed by license
6. **No field-of-use restriction**: No restrictions on application domain
7. **GGUF viable**: Can be quantized and run on consumer hardware (GTX 1060/1080)

## Blocked Models — Not for Official Kimari Public Release

These models have restrictive or unclear licenses and MUST NOT be used as bases for official public Kimari models. They may be used for private research only.

| Model | License | Reason | Decision |
|-------|---------|--------|----------|
| `Qwen/Qwen2.5-3B-Instruct` | qwen-research | Research-only license | ❌ Blocked for public Kimari |
| `google/gemma-3-4b-it` | Gemma license | Custom license, not standard permissive | ⚠️ Private research only |
| Meta Llama 3.x | Meta Llama License | Custom restrictive license | ⚠️ Private research only |
| Any CC-BY-NC model | CC-BY-NC | Non-commercial | ❌ Blocked |
| Any research-only model | Various | No commercial/redistribution | ❌ Blocked |
| Any model without clear license | Unknown | Legal risk | ❌ Blocked |

### Why Blocked

- **qwen-research**: Explicitly restricts commercial use and redistribution
- **Gemma**: Custom license with use-case restrictions; not Apache/MIT/BSD
- **Llama**: Custom license with redistribution conditions; not standard permissive
- **CC-BY-NC**: Explicitly prohibits commercial use
- **Unknown**: Cannot verify legal safety

## Quarantine Process

If a model's license status is unclear:

1. Do NOT add to Allowed list
2. Add to Blocked list with reason "Under review"
3. Research the license terms
4. Document findings in this file
5. Only move to Allowed after explicit license verification

## Verification

- `scripts/release/check-release.py` verifies this matrix exists and is current
- `tests/test_release_v0157.py` verifies no blocked model is marked as official public
- This matrix must be updated before any new base model is used in training

---

_No model may be used for an official Kimari public release without being listed in the Allowed table above with all criteria met._