# Model Card: Kimari-4B

> **Status: Planned / Not Released**
> Weights are not available in this repository. Kimari-4B is the target model under development.
> Until release, Kimari can run compatible GGUF base models for testing.
> See `models/README.md` for recommended test models.

## Model Details

- **Model Name:** Kimari-4B
- **Model Type:** Causal Language Model (Transformer)
- **Base Architecture:** LLaMA-based
- **Parameter Count:** ~4 billion
- **Context Length:** Up to 16,384 tokens (profile-dependent)
- **Quantization:** GGUF (Q4_K_M, Q5_K_M, IQ4_XS)
- **License:** See [MODEL_LICENSES.md](MODEL_LICENSES.md)
- **Developer:** Smouj ([@smouj013](https://x.com/smouj013))

## Training Information

### Base Model

Kimari-4B is built on a base language model (not yet selected — candidates include LLaMA-based, Qwen, SmolLM3, and other 3–4B parameter architectures). The base model provides general language understanding and generation capabilities. A final selection will be made before fine-tuning begins.

### Fine-Tuning (Planned)

| Aspect | Status | Details |
|--------|--------|---------|
| Instruction tuning | Planned | Multi-turn conversation data |
| Coding skills | Planned | Python, TypeScript, shell scripting |
| Technical Spanish | Planned | IT infrastructure, DevOps |
| Agent capabilities | Planned | Multi-step reasoning, tool use |
| System administration | Planned | Linux/Windows admin tasks |

### Training Data (Planned)

The fine-tuning dataset includes:
- Instruction-response pairs from open-source datasets
- Technical documentation and tutorials
- Code examples with explanations
- Multi-language technical content (English + Spanish)
- Conversational data for assistant-style responses

## Intended Use

### Primary Use Cases

1. **Local coding assistant** — Code generation, debugging, code review
2. **System administration** — Linux/Windows troubleshooting, automation
3. **Technical documentation** — Explaining concepts, writing docs
4. **Agent orchestration** — Multi-step reasoning for autonomous tasks
5. **Bilingual assistance** — English and technical Spanish support

### Target Users

- Developers working locally without internet access
- System administrators needing quick troubleshooting
- Teams with data privacy requirements (on-premise AI)
- Students and learners in technical fields
- Users with consumer-grade GPUs

### Target Hardware

| GPU | VRAM | Recommended Quantization | Context |
|-----|------|------------------------|---------|
| GTX 1060 | 6 GB | Q4_K_M | 8,192 |
| GTX 1080 | 8 GB | Q5_K_M | 16,384 |
| RTX 2060 | 6 GB | Q4_K_M | 8,192 |
| RTX 3060 | 12 GB | Q5_K_M | 32,768 |

## Limitations

1. **No real-time knowledge** — The model does not have access to the internet or current events
2. **Hallucination risk** — May generate plausible but incorrect information
3. **Context window** — Limited by available VRAM; long documents may be truncated
4. **Quantization artifacts** — Lower quantization levels may degrade output quality
5. **No multimodal** — Text-only; does not process images or audio
6. **Language coverage** — Optimized for English and technical Spanish; other languages not tested
7. **Reasoning depth** — Complex multi-step reasoning may be inconsistent

## Ethical Considerations

### Safety Measures

- Model outputs should not be used for critical decisions without human review
- No PII is collected or transmitted — all processing is local
- Model weights are not included in this repository

### Known Risks

- **Misinformation** — Model may generate factually incorrect content
- **Bias** — Training data may contain biases that propagate to outputs
- **Security** — Model may generate code with vulnerabilities; always review

### Responsible Use

Users are responsible for:
- Reviewing all model outputs before use
- Not using the model for harmful purposes
- Complying with applicable laws and regulations
- Ensuring base model license compliance

## Performance

### Benchmark Targets

| Metric | Target (Q4_K_M) | Target (Q5_K_M) |
|--------|----------------|-----------------|
| Tokens/second (GTX 1060) | > 15 t/s | N/A |
| Tokens/second (GTX 1080) | > 20 t/s | > 15 t/s |
| Time to first token | < 2s | < 3s |
| MMLU (5-shot) | TBD | TBD |
| HumanEval (pass@1) | TBD | TBD |

*Actual benchmarks will be published after model training.*

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | TBD | Initial release — base model with GGUF conversion |
| 0.2.0 | Planned | Instruction-tuned variant |
| 0.3.0 | Planned | Coding-specialized variant |
| 1.0.0 | Planned | Full fine-tuned release |

---

*This model card will be updated as development progresses.*
