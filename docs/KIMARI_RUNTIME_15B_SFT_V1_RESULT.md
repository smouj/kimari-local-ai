# Kimari Runtime 1.5B SFT v1 — Result

## Objective

Run the first SFT v1 real short run for Kimari Runtime on `Qwen/Qwen2.5-1.5B-Instruct` (Apache-2.0).

## Base model

- Model: `Qwen/Qwen2.5-1.5B-Instruct`
- License: Apache-2.0

## Dataset

Kimari SFT v1 seed dataset: 320 examples total.

- Train: 288 examples (SHA256: `28823e22b9889603fd86e30d41176616432d21dd5598ec272c774ee67cf862e8`)
- Validation: 32 examples (SHA256: `8bf32e50e9c2143607c79663a121c8fbfbb5236ddcd6ea1c2973afe8ff1ddd55`)

## Config

- Method: QLoRA
- LoRA rank: `r=16`
- LoRA alpha: `32`
- LoRA dropout: `0.05`
- Max steps: `10` (micro-run)
- Learning rate: `5e-5`
- Gradient accumulation: `8`
- FP16: true
- Max seq length: `2048`
- Seed: `42`

## Run status

Status: **COMPLETED** — Micro-run SFT v1 training completed successfully.

| Field | Value |
| --- | --- |
| job_id | `6a0501dae48bea4538b9c17a` |
| status | COMPLETED |
| GPU | a10g-small (A10G) |
| Docker image | pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel |
| steps completed | 10 |
| loss initial (train) | 2.753 |
| loss final (train) | 2.753 |
| loss final (eval) | 2.652 |
| train runtime | 11.69 seconds |
| train samples/sec | 6.842 |
| eval runtime | 1.255 seconds |

## Training metrics

```
Step  Loss (train)  Loss (eval)
 10   2.753         2.652
```

Eval accuracy: 52.08% (mean_token_accuracy)

## Safety checks

| Check | Value |
| --- | --- |
| training_performed | true (micro-run, 10 steps) |
| adapter_generated | true |
| adapter_committed | false |
| adapter_persisted_private | **IN PROGRESS** (re-running with --persist-adapter to Smouj013/kimari-runtime-15b-sft-v1-adapter) |
| adapter_committed_public | false |
| hf_public_upload_performed | false |
| gguf_generated | false |
| raw_logs_committed | false |
| public_benchmark_allowed | false |
| gate_state | BLOCKED |

> **⚠️ This was a micro-run (10 steps). The adapter was generated but not persisted in the first run (Job `6a0501dae48bea4538b9c17a`). v0.1.67-alpha re-runs the micro-run with `--persist-adapter` to save the adapter to `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private repo). No public weights, GGUF, or benchmarks were produced. Gate remains BLOCKED.**
>
> **Key safety assertions:** adapter_committed_public: false, hf_public_upload_performed: false, gguf_generated: false, public_benchmark_allowed: false, gate_state: BLOCKED.

## Next step

- v0.1.67-alpha: Re-run SFT v1 micro-run with --persist-adapter → persist adapter to private HF repo
- v0.1.68-alpha: Evaluate SFT v1 adapter vs base with KimariEval subset10
- Full 100-step run deferred until evaluation confirms improvement