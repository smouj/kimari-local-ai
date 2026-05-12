# Kimari-4B First Private Adapter Run

> First real SFT LoRA adapter for Kimari-4B. Private only. No public release.

## Objective

Prove that the Kimari training pipeline can produce a valid LoRA adapter from a permissive base model. This is a **validation run**, not a production model.

## What Is Being Trained

| Property | Value |
|----------|-------|
| Base model | Qwen/Qwen2.5-3B-Instruct (Apache 2.0) |
| Method | SFT LoRA (r=16, alpha=32) |
| Dataset | kimari-fit-v0 (~200 examples) |
| Target | Spanish technical + GPU/CUDA + coding/sysadmin |

## What Is NOT Being Published

❌ No adapter weights will be uploaded to Hugging Face
❌ No GGUF will be generated or exported
❌ No checkpoints will be committed to git
❌ No raw eval outputs will be committed
❌ No benchmark claims about Kimari-4B
❌ Kimari-4B remains "not released"

## Hardware Recommendation

| Option | Suitability |
|--------|-------------|
| RunPod RTX 4090 / L40S | ✅ Best option now |
| RunPod A100 | ✅ Overkill but works |
| HF Jobs | ⚠️ Only if 403 resolves |
| GTX 1060 6GB | ❌ Too small for 3B LoRA training |
| CPU | ❌ Impractical for 3B model |

## Commands

```bash
# 1. Preflight checks
python training/scripts/preflight_kimari4b_adapter.py \
    --config training/configs/kimari4b_private_adapter_run.v0.yaml

# 2. Dry-run (default)
python training/scripts/run_kimari4b_private_adapter.py \
    --config training/configs/kimari4b_private_adapter_run.v0.yaml \
    --dry-run --json

# 3. Real training (requires explicit consent)
python training/scripts/run_kimari4b_private_adapter.py \
    --config training/configs/kimari4b_private_adapter_run.v0.yaml \
    --allow-train --yes

# 4. Create manifest (after training completes)
python training/scripts/create_kimari4b_adapter_manifest.py \
    --output-dir training/adapters/kimari4b-private-adapter-v0 \
    --config training/configs/kimari4b_private_adapter_run.v0.yaml

# 5. Evaluate (when endpoints are running)
python eval/scripts/evaluate_kimari4b_adapter.py \
    --baseline-endpoint http://localhost:11435/v1 \
    --adapter-endpoint http://localhost:11436/v1
```

## Artifact Policy

| Artifact | Committed | Uploaded | Notes |
|----------|-----------|----------|-------|
| Config YAML | ✅ Yes | ❌ No | Safe — no secrets |
| Runner script | ✅ Yes | ❌ No | Safe — no execution without flags |
| Preflight script | ✅ Yes | ❌ No | Safe — read-only checks |
| Manifest template | ✅ Yes | ❌ No | Safe — no real hashes |
| Adapter `.safetensors` | ❌ No | ❌ No | Gitignored |
| Checkpoints | ❌ No | ❌ No | Gitignored |
| Raw eval outputs | ❌ No | ❌ No | Gitignored |
| Summary (sanitized) | ✅ Yes | ❌ No | Safe — no private paths |
| GGUF files | ❌ No | ❌ No | Not generated yet |

## Eval Policy

- Baseline vs adapter comparison
- Categories: KimariFit, safety, Spanish, coding, JSON
- No public benchmark claims
- See [KIMARI4B_ADAPTER_EVAL_PLAN.md](KIMARI4B_ADAPTER_EVAL_PLAN.md)

## Gate

**BLOCKED** — No automatic transitions. See [KIMARI4B_RELEASE_GATE.md](KIMARI4B_RELEASE_GATE.md)

Even after a successful adapter run, the gate stays BLOCKED until:
1. Eval completes and is reviewed
2. Human explicitly advances gate to PRIVATE_ADAPTER_READY
3. Public release requires PUBLIC_PREVIEW_ALLOWED (human decision only)