# Kimari Runtime 1.5B SFT v1 — Subset30 Eval Report

> ✅ Completed. Completion-only baseline vs adapter eval after the 100-step full-run.

| Metric | Baseline | Adapter |
| --- | ---: | ---: |
| Load success | ✅ | ✅ |
| Generation success | ✅ | ✅ |
| Completion rate | 30/30 (1.0) | 30/30 (1.0) |

- **Eval job**: `6a05236ee48bea4538b9c315`
- **Adapter training job**: `6a052235e48bea4538b9c309`
- **Adapter repo**: `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private)
- **Score status**: `not_scored`
- **Gate**: BLOCKED
- **No raw outputs committed**
- **No public benchmark claims**

## Decision

The 100-step adapter passes subset30 completion validation. Next recommended step: scoring/quality eval before a 500-step run or GGUF conversion.
