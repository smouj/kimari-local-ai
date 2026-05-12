# Kimari-4B Micro SFT Result

> First real micro SFT training result on Hugging Face Jobs.

## Status: PENDING

This document will be updated after the micro SFT run completes.

## Run Info

| Field | Value |
|-------|-------|
| **Run ID** | kimari4b-hfjobs-micro-sft-v0 |
| **Base model** | Qwen/Qwen2.5-1.5B-Instruct (Apache 2.0) |
| **Dataset** | kimari-fit-v0 (72 examples) |
| **Flavor** | a10g-small ($1.00/hour) |
| **Max steps** | 10 |
| **LoRA config** | r=8, alpha=16 |
| **Estimated cost** | ~$0.35 |

## Results

| Field | Value |
|-------|-------|
| **Job ID** | 6a038c797618f125ee2b7979 (PyTorch 2.4.0 fix) |
| **Status** | RUNNING (submitted 2026-05-12) |
| **GPU detected** | NVIDIA A10G (22.3 GB VRAM, CUDA 12.1) |
| **training_performed** | In progress (expected: true) |
| **adapter_generated** | Pending (expected: true) |
| **adapter_committed** | false (never committed) |
| **hf_upload_performed** | false |
| **gguf_generated** | false |
| **gate_state** | BLOCKED |

## What Was NOT Done

- ❌ No adapter committed to git
- ❌ No adapter uploaded to Hugging Face
- ❌ No GGUF generated
- ❌ No checkpoint download
- ❌ No benchmark claims
- ❌ No public release

## Note on Adapter Persistence

The adapter generated in this run exists only in HF Jobs ephemeral storage.
It is NOT downloaded, committed, or uploaded. This is intentional —
we are validating the training pipeline, not producing a persistent adapter.

A future run (v0.1.50+) will implement adapter retrieval for local evaluation.

## Gate

**BLOCKED** — No automatic gate transition.