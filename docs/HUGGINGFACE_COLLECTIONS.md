# Hugging Face Collections

> Version: v0.1.55-alpha
> Status: reference/community models only — no official Kimari model release

Kimari currently maintains a reference collection under the user namespace because the existing collection was created before org-level collection ownership was finalized:

https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66

## Purpose

The collection lists community/reference GGUF models that are useful for testing Kimari Local AI workflows. These models help users validate install, profile selection, llama.cpp CUDA, and local OpenAI-compatible endpoint integrations.

## Not official Kimari models

Every item must be described as:

> Reference/community GGUF model for Kimari testing. Not an official Kimari model.

The collection does **not** contain:

- Kimari-4B public weights
- official Kimari-4B GGUF files
- public Kimari adapters
- benchmark claims

Gate: **BLOCKED**.

## Inclusion criteria

A model can be included if:

- it has a clear license on Hugging Face;
- it provides GGUF files suitable for llama.cpp;
- it is small enough to be useful on consumer GPUs;
- it has a practical Kimari profile recommendation;
- it is clearly labelled as reference/community, not official Kimari.

## Recommended reference items

| Model | Purpose | Suggested Kimari profile | VRAM guidance | Note |
|---|---|---|---:|---|
| TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF | Smoke test | `test` | 2 GB | Reference/community GGUF model for Kimari testing. Not an official Kimari model. |
| bartowski/Qwen2.5-1.5B-Instruct-GGUF | Small chat/coding test | `test` / `gtx1060` | 3 GB | Reference/community GGUF model for Kimari testing. Not an official Kimari model. |
| bartowski/SmolLM2-1.7B-Instruct-GGUF | Small instruction test | `test` / `gtx1060` | 3 GB | Reference/community GGUF model for Kimari testing. Not an official Kimari model. |
| bartowski/Llama-3.2-1B-Instruct-GGUF | Small Meta-family test | `test` / `gtx1060` | 3 GB | Reference/community GGUF model for Kimari testing. Not an official Kimari model. |
| bartowski/Qwen2.5-3B-Instruct-GGUF | GTX 1060/1080 practical test | `gtx1060` / `gtx1080` | 5 GB | Reference/community GGUF model for Kimari testing. Not an official Kimari model. |

## Maintenance checklist

Before adding or updating collection items:

- confirm the model page is public;
- confirm license information exists;
- use neutral wording;
- do not claim official Kimari performance;
- do not imply Kimari-4B is released;
- do not add private adapters, weights, or raw eval outputs.
