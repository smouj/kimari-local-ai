# Model Licensing

This document explains the licensing of models used with Kimari.

## Overview

Kimari itself is released under the **MIT License**. However, language model weights carry their own licenses that you must comply with independently.

## License Layers

### 1. Kimari Software — MIT License

All code in this repository (CLI, scripts, configurations, documentation) is licensed under the MIT License. You are free to use, modify, and distribute the software.

```
Copyright (c) 2025 Smouj
```

### 2. Kimari Fine-Tuning Modifications — MIT License

Any fine-tuned models, LoRA adapters, or training recipes produced by the Kimari project are released under the MIT License, unless built on a base model with more restrictive terms.

### 3. Base Model Weights — Base Model License

Base model weights (e.g., LLaMA, Mistral, Qwen, or other foundation models) are **not** included in this repository. Each base model has its own license, which may include:

- **Llama 3/3.1/3.2 Community License** — Permits commercial and non-commercial use with restrictions on large-scale distribution
- **Apache 2.0** — Permissive, permits commercial use
- **Gemma Terms of Use** — Permits use with attribution requirements
- **Other** — Review the specific model card for details

## Your Responsibilities

As a user of Kimari, you are responsible for:

1. **Downloading models legally** — Obtain model weights from authorized sources
2. **Complying with base model licenses** — Read and follow the license of any model you use
3. **Not redistributing restricted weights** — Some licenses prohibit redistribution
4. **Commercial use compliance** — Check if the base model license permits your intended use
5. **Attribution** — Provide required attribution per the base model's terms

## Recommended Model Sources

| Model | License | Source |
|-------|---------|--------|
| Llama 3.2 3B | Llama Community License | [Meta AI](https://llama.meta.com/) |
| Qwen2.5 3B | Apache 2.0 | [Hugging Face](https://huggingface.co/Qwen) |
| Phi-3 Mini | MIT | [Hugging Face](https://huggingface.co/microsoft) |
| Gemma 2 2B | Gemma Terms | [Hugging Face](https://huggingface.co/google) |

## Disclaimer

The Kimari project (created by Smouj) does not host, distribute, or take responsibility for model weights. We provide the software infrastructure to run GGUF-quantized models locally. The end user is solely responsible for ensuring compliance with all applicable model licenses.

## Questions?

If you have questions about model licensing:

1. Read the model card of the specific model you're using
2. Check the license file included with the model weights
3. Consult the model provider's website
4. Seek legal advice if unsure about commercial use

---

*This document is provided for informational purposes only and does not constitute legal advice.*
