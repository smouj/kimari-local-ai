# Kimari-4B Release Gate

> Gate states for Kimari-4B model release process.

## States

| State | Description | Can advance to |
|-------|-------------|---------------|
| `BLOCKED` | Initial state. No weights exist. No eval. | `PRIVATE_ADAPTER_READY` |
| `PRIVATE_ADAPTER_READY` | Private adapter trained and validated. Not public. | `EVAL_PENDING` |
| `EVAL_PENDING` | Adapter eval in progress. | `REVIEW_PENDING` |
| `REVIEW_PENDING` | Eval complete. Awaiting human review. | `PUBLIC_PREVIEW_ALLOWED` |
| `PUBLIC_PREVIEW_ALLOWED` | Human approved public preview. Weights can be published. | — (terminal) |

## Transition Rules

1. **No automatic transitions.** Every state advance requires explicit human action.
2. **No script** may change the gate state from `BLOCKED` to any other state automatically.
3. **No CI/CD** pipeline may advance the gate.
4. The gate can only go **forward**, never backward.

## Current State

**BLOCKED** — No adapter trained yet. Pipeline preparation in progress.

## Requirements per State

### BLOCKED → PRIVATE_ADAPTER_READY

- [ ] Private adapter trained successfully
- [ ] Adapter manifest created and reviewed
- [ ] Safety flags verified (no HF upload, no public release)
- [ ] Output directory gitignored
- [ ] Preflight checks pass

### PRIVATE_ADAPTER_READY → EVAL_PENDING

- [ ] Adapter eval plan reviewed
- [ ] Baseline endpoint configured
- [ ] Adapter endpoint configured
- [ ] Eval prompts ready

### EVAL_PENDING → REVIEW_PENDING

- [ ] All eval categories completed
- [ ] No safety regressions
- [ ] Summary generated (sanitized, no raw outputs)
- [ ] Results stored locally

### REVIEW_PENDING → PUBLIC_PREVIEW_ALLOWED

- [ ] Human review of all eval results
- [ ] Safety review complete
- [ ] Legal review (license compatibility)
- [ ] Explicit written approval from project owner
- [ ] GGUF conversion plan reviewed
- [ ] HF upload plan reviewed

## Safety Invariants

These must hold in **every** state:

- `public_release_allowed` = false unless `PUBLIC_PREVIEW_ALLOWED`
- `hf_upload_allowed` = false unless `PUBLIC_PREVIEW_ALLOWED`
- `gguf_export_allowed` = false unless `PUBLIC_PREVIEW_ALLOWED`
- `push_to_hub` = false unless `PUBLIC_PREVIEW_ALLOWED`
- `report_to` = "none" (no WandB/TB upload)
- No adapter files (`.safetensors`) committed to git
- No GGUF files committed to git
- No raw eval outputs committed to git