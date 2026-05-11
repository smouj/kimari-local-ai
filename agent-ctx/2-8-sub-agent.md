# Task 2-8: Adapter Manifest, Eval Summary, Training Docs

## Summary

Created 8 files for v0.1.21-alpha adapter manifest and eval summary infrastructure:

### Files Created

1. **training/templates/adapter_manifest.template.yaml** — Full template with all 22 required fields. preview_gate_state=BLOCKED, public_release_allowed=false, hf_upload_allowed=false, state_history with initial BLOCKED entry.

2. **training/scripts/create_adapter_manifest.py** — CLI script with --run-config, --adapter-dir, --output, --dry-run, --json. Reads template, merges run config and SFT config. Scans adapter dir for allowed files. Rejects suspicious files (.safetensors, .bin, .pt, .pth, .ckpt, .gguf). Enforces BLOCKED state and false release flags. Works without PyYAML.

3. **docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md** — 12-section checklist covering GPU, license, dataset, baseline eval, run config, output dir safety, WandB, HF, training command, post-run manifest, post-run eval, preview gate.

4. **docs/SFT_TO_ORPO_DECISION.md** — Decision framework: safety regression → no ORPO, coding improvement → consider ORPO, overfitting → expand dataset, baseline surpasses → review. Includes ORPO prerequisites, DPO vs ORPO selection, flowchart. DPO/ORPO never runs in CI.

5. **docs/PRIVATE_EVAL_RESULTS_POLICY.md** — What CAN be committed (anonymous summaries, category counts, hashes, score status). What CANNOT (private prompts, local paths, tokens, sensitive outputs, benchmark claims without review).

6. **eval/templates/eval_summary.template.json** — Committable eval summary template. No raw prompts. score_status="manual_review_required".

7. **eval/scripts/create_eval_summary.py** — CLI with --input, --output, --json. Strips prompt/response fields. Produces safe summary. Does NOT invent scores.

8. **tests/fixtures/private_eval_raw.json** — Synthetic fixture with 5 results containing fake sensitive data for testing sanitization.

### Validation

- All Python scripts compile (py_compile)
- create_adapter_manifest.py: dry-run YAML/JSON output verified, adapter dir scanning verified (suspicious files rejected, allowed files included), BLOCKED state enforced
- create_eval_summary.py: prompt/response stripping verified, category counts verified, manual_review_required flagged correctly
- Both scripts tested with tmp_path (tempfile.TemporaryDirectory)
