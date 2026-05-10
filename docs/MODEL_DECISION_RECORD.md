# ADR-001: Select Base Model for Kimari-4B Fine-Tuning

| Field            | Value                                             |
|------------------|---------------------------------------------------|
| ADR Number       | 001                                               |
| Title            | Select Base Model for Kimari-4B Fine-Tuning       |
| Status           | Proposed                                          |
| Decision Date    | TBD                                               |
| Last Updated     | 2026-05-20                                        |

---

## Context

Kimari-4B is a planned 3B–4B parameter fine-tuned model for local coding, system administration, and agent assistance on consumer NVIDIA GPUs (GTX 1060/1080). The model requires SFT (Supervised Fine-Tuning) followed by preference tuning (DPO or ORPO). A base model must be selected from the available open-weight candidates in the ~3B parameter class.

The selection must balance legal safety (license compatibility for derivative distribution), technical capability, and practical deployment constraints. No training has been started. No model weights have been downloaded or evaluated.

---

## Candidate Shortlist

| Candidate                      | Parameters | License                        | Context Length | Key Strength                           |
|--------------------------------|-----------|--------------------------------|---------------|----------------------------------------|
| HuggingFaceTB/SmolLM3-3B       | ~3B       | Apache 2.0                     | 16,384        | Safest legal path; fully permissive    |
| Qwen/Qwen2.5-3B-Instruct       | ~3B       | qwen-research                  | 32,768        | Strong coding & multilingual quality   |
| meta-llama/Llama-3.2-3B-Instruct | ~3B     | Llama 3.2 Community License   | 131,072       | Strong general model; large context    |

---

## Evaluation Criteria

| # | Criterion                      | Weight | Description                                                          |
|---|-------------------------------|--------|----------------------------------------------------------------------|
| 1 | License clarity               | 3      | How clear and permissive is the license for derivative works         |
| 2 | Redistribution compatibility  | 3      | Can fine-tuned weights be redistributed under compatible terms       |
| 3 | Tokenizer stability           | 2      | Is the tokenizer well-established and unlikely to change             |
| 4 | GGUF support                  | 2      | Maturity of GGUF conversion for this architecture                    |
| 5 | Coding ability                | 2      | Baseline coding performance of the base model                        |
| 6 | Spanish technical ability     | 1      | Spanish technical language capability                                |
| 7 | Agent/JSON behavior           | 2      | JSON output and agent-like behavior quality                          |
| 8 | GTX 1060/1080 inference       | 2      | Runs well on GTX 1060/1080 at 4-bit quantization                    |
| 9 | Training cost                 | 1      | Expected GPU hours for SFT + preference tuning                       |

**Total weight: 18 (max weighted score: 18 × 5 = 90)**

---

## Scoring (1–5 per criterion)

| Criterion                      | Weight | SmolLM3-3B | Qwen2.5-3B-Instruct | Llama-3.2-3B-Instruct |
|-------------------------------|--------|-----------|---------------------|----------------------|
| License clarity               | 3      | 5         | 3                   | 2                    |
| Redistribution compatibility  | 3      | 5         | 3                   | 2                    |
| Tokenizer stability           | 2      | 3         | 4                   | 5                    |
| GGUF support                  | 2      | 3         | 4                   | 5                    |
| Coding ability                | 2      | 3         | 5                   | 4                    |
| Spanish technical ability     | 1      | 2         | 4                   | 3                    |
| Agent/JSON behavior           | 2      | 3         | 4                   | 4                    |
| GTX 1060/1080 inference       | 2      | 4         | 4                   | 4                    |
| Training cost                 | 1      | 4         | 4                   | 3                    |

---

## Weighted Scores

| Candidate                    | Weighted Total | Max Possible | Score /90 |
|------------------------------|---------------|-------------|-----------|
| SmolLM3-3B                   | 68            | 90          | ~68/90    |
| Qwen2.5-3B-Instruct          | 66            | 90          | ~66/90    |
| Llama-3.2-3B-Instruct        | 60            | 90          | ~60/90    |

---

## Recommendation

### Primary: SmolLM3-3B (~68/90)

If the Apache 2.0 license is verified to cover derivative distribution of fine-tuned weights, SmolLM3-3B is the recommended first candidate. It offers the lowest legal friction with full permission to redistribute fine-tuned weights in any format (GGUF, safetensors). The main risk is potentially lower baseline capability compared to Qwen2.5 and Llama.

### Capability Candidate: Qwen2.5-3B-Instruct (~66/90)

If the qwen-research license terms allow derivative distribution for the Kimari use case, Qwen2.5-3B-Instruct is the strongest capability candidate. It has excellent coding and multilingual performance. However, the license must be reviewed before commitment.

### Constrained Candidate: Llama-3.2-3B-Instruct (~60/90)

Llama-3.2-3B-Instruct is the strongest general model with the largest context window (131K), but the Llama 3.2 Community License imposes restrictions that may conflict with Kimari's distribution goals (MAU thresholds, acceptable use policy, derivative distribution constraints). It is ranked third due to legal risk.

---

## Decision

**Not final yet.** No base model has been selected. All candidates remain under review. The formal decision is expected in v0.1.19-alpha after license verification and, if hardware permits, baseline evaluation.

---

## Consequences

### If SmolLM3-3B is selected
- **Positive:** Full legal freedom to distribute fine-tuned weights under Apache 2.0; no license review needed; simplest release process.
- **Negative:** May require more training effort to reach target capability; less community benchmarking available; smaller context window (16K).

### If Qwen2.5-3B-Instruct is selected
- **Positive:** Strongest coding and multilingual baseline; best chance of meeting capability targets; instruction-tuned out of the box.
- **Negative:** License review required; may restrict commercial distribution; risk of license change in future versions.

### If Llama-3.2-3B-Instruct is selected
- **Positive:** Strong general capability; largest context window (131K); mature GGUF ecosystem.
- **Negative:** Llama 3.2 Community License restrictions on derivative distribution; MAU thresholds; acceptable use policy; may limit Kimari's distribution channels.

---

## Required Validation Before Final Choice

1. **Verify SmolLM3-3B Apache 2.0 license** covers derivative distribution of fine-tuned weights
2. **Review Qwen2.5-3B-Instruct license terms** for commercial and derivative use
3. **Evaluate Llama 3.2 Community License restrictions** for the Kimari use case (MAU thresholds, acceptable use policy)
4. **Run baseline evaluation** on each candidate if hardware permits (using KimariFit prompts)
5. **Test GGUF conversion** for each candidate architecture
6. **Measure inference speed** on GTX 1060 and GTX 1080 at Q4_K_M and Q5_K_M quantization
7. **Confirm training feasibility** (VRAM requirements for LoRA fine-tuning on available hardware)

---

*This ADR will be updated when a final decision is made. No information herein should be interpreted as a commitment to any specific base model.*
