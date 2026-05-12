# Baseline vs Adapter Evaluation Plan

> How to compare base Qwen2.5-1.5B-Instruct against a Kimari-4B LoRA adapter.

## Objective

Measure whether a LoRA adapter improves the base model on KimariEval Private v1 categories, using the same prompts, temperature, and configuration.

## Models to Evaluate

| Model | Description | Source |
|-------|-------------|--------|
| Qwen2.5-1.5B-Instruct | Base model (no adapter) | Hugging Face |
| Kimari-4B-adapter-v0 | LoRA adapter on Qwen2.5-1.5B | Private HF repo |

## Evaluation Configuration

| Parameter | Value |
|-----------|-------|
| Temperature | 0.1 (low, for reproducibility) |
| Max tokens | 512 |
| Top-p | 0.9 |
| Frequency penalty | 0 |
| Context length | 2048 |
| Random seed | 42 (for reproducibility) |

## Evaluation Process

1. **Run base model** on all 100 KimariEval prompts
2. **Run adapter model** on the same 100 prompts
3. **Save raw outputs** to private repo (not public)
4. **Manual review** of each output against ideal
5. **Score** on 5 dimensions (technical accuracy, utility, safety, consistency, efficiency)
6. **Compare** base vs adapter scores per category and overall

## What to Compare

- Per-category scores (Spanish technical, coding, server ops, etc.)
- Safety refusal rates
- Response length and relevance
- Hallucination rate
- Consistency of style and format

## What NOT to Do

- ❌ Publish raw scores or benchmark comparisons
- ❌ Claim "Kimari-4B is X% better than base"
- ❌ Compare with other published models
- ❌ Use scores in marketing materials
- ❌ Share specific prompt/answer pairs publicly

## Required Before Evaluation

- [ ] Baseline model accessible via local endpoint
- [ ] Adapter model loaded and accessible
- [ ] KimariEval v1 validated (100 items, no errors)
- [ ] Evaluation script tested in dry-run mode
- [ ] Manual review rubric agreed upon

## Timeline

- **v0.1.52**: Create eval infrastructure (this document)
- **v0.1.53**: Run baseline evaluation
- **v0.1.54**: Run adapter evaluation (after persistent adapter)
- **v0.1.55+**: Compare and document findings (internal only)

## Gate

**BLOCKED** — Evaluation results are private. No public claims.