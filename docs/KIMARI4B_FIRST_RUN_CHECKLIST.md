# Kimari-4B First Private SFT Run Checklist

> **Document Type:** Pre-flight checklist for first private SFT run  
> **Version:** v0.1.32-alpha  
> **Date:** 2026-06-02  
> **Status:** Active — complete every item before training  
> **Gate State:** BLOCKED

---

## Purpose

This checklist must be completed **in full** before starting the first private SFT training run for Kimari-4B. Every item must be verified. If any item fails, **do not start training** until the issue is resolved.

---

## 1. Security

- [ ] **HF token not exposed** — No `hf_` strings in any output file, config, or environment variable that could be committed
- [ ] **No API keys in configs** — Run `python scripts/security/scan_for_secrets.py --paths training eval --json`
- [ ] **No .env files with real secrets** — `.env` is gitignored; no real tokens in any tracked file
- [ ] **HF Jobs login secure** — If using HF Jobs, login via `hf auth login` locally only; no `--token` flags in any command

## 2. License

- [ ] **Base model license reviewed** — SmolLM3-3B uses Apache-2.0; permits derivative works
- [ ] **License documented** — `MODEL_LICENSES.md` includes SmolLM3-3B entry
- [ ] **Base model accepted** — `docs/BASE_MODEL_ACCEPTANCE.md` confirms private training scope
- [ ] **No public release claims** — No document claims Kimari-4B is published or available

## 3. Dataset

- [ ] **Dataset v0 validated** — `python training/scripts/validate_training_ready.py --json` passes
- [ ] **Dataset build exists** — `dataset/build/kimari-v0/report.json` exists with valid counts
- [ ] **No private data** — All dataset entries are synthetic with `source="kimari-v0-synthetic"`
- [ ] **Eval holdout preserved** — `dataset/v0/eval_holdout.jsonl` not mixed into training data

## 4. Baseline Evaluation

- [ ] **Baseline eval plan exists** — `docs/BASELINE_EVAL_PLAN.md` reviewed
- [ ] **Baseline eval command ready** — `python eval/scripts/kimari4b_eval_plan.py --baseline-label smollm3-base --json` generates valid plan
- [ ] **llama-server endpoint accessible** — `http://127.0.0.1:11435/v1` responds with base model loaded
- [ ] **Baseline results saved** — `eval/results/baseline-smollm3-q4km.json` exists (or will be generated before comparison)

## 5. Hardware / Environment

- [ ] **RunPod/local GPU prepared** — GPU with 10+ GB VRAM available; 16+ GB recommended
- [ ] **Training dependencies installed** — `pip install -r training/requirements-training.txt` succeeds
- [ ] **Preflight passes** — `python training/scripts/preflight_private_sft.py --run-config training/configs/kimari4b_private_sft_run.v0.yaml --json` passes
- [ ] **Smoke test before training** — Run HF Jobs smoke test or local GPU smoke test before attempting real training
- [ ] **Budget confirmed** — If using HF Jobs, budget approved and under $10 for smoke tests

## 6. Output Directory

- [ ] **output_dir is gitignored** — `training/adapters/kimari4b-smollm3-sft-v0/` is covered by `.gitignore`
- [ ] **Sufficient disk space** — At least 10 GB free for adapter weights, checkpoints, and logs
- [ ] **No stale artifacts** — Output directory is empty or cleaned from previous attempts

## 7. Adapter Manifest

- [ ] **Manifest template exists** — `training/templates/adapter_manifest.template.yaml` available
- [ ] **Manifest creation command ready** — `create_adapter_manifest.py` with `--dry-run` works
- [ ] **Manifest will have gate BLOCKED** — Template enforces `preview_gate_state: BLOCKED`

## 8. Eval Summary

- [ ] **Eval summary template exists** — `eval/templates/eval_summary.template.json` available
- [ ] **Eval summary creation command ready** — `create_eval_summary.py` works
- [ ] **Eval summary will strip prompts/responses** — No raw prompt or response text in output

## 9. No HF Upload

- [ ] **hf_upload_allowed is false** — Confirmed in `training/configs/kimari4b_private_sft_run.v0.yaml`
- [ ] **No automated HF upload** — No script or CI job will upload to Hugging Face
- [ ] **No HF Jobs token in CLI** — Never pass `--token` to hf commands; use local login only
- [ ] **validate_private_sft_commands.py passes** — `python training/scripts/validate_private_sft_commands.py --command-json /tmp/kimari4b_commands.json --training-script training/scripts/train_sft_lora.py --json`

## 10. Gate BLOCKED

- [ ] **preview_gate_state is BLOCKED** — Confirmed in config
- [ ] **public_release_allowed is false** — Confirmed in config
- [ ] **No automatic gate transition** — Gate will NOT advance as a side effect of training
- [ ] **ADAPTER_PREVIEW_GATE.md reviewed** — State machine and transition requirements understood

## 11. Micro SFT (Optional Pre-Step)

- [ ] **Smoke summary validated** — `python training/scripts/validate_hf_jobs_smoke_summary.py --summary /tmp/hf_jobs_smoke_summary.json --json` passes
- [ ] **Budget confirmed for micro SFT** — Under $10 for 10-step run
- [ ] **Micro SFT config reviewed** — `training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml` reviewed and understood
- [ ] **No token in micro SFT command** — Micro SFT wrapper has no --token argument
- [ ] **Micro SFT config has gate BLOCKED** — preview_gate_state: BLOCKED confirmed
- [ ] **Micro SFT config has allow_hf_upload: false** — No HF upload confirmed

---

## After Training

After the training run completes, verify:

- [ ] Adapter weights exist in output_dir (local only)
- [ ] No GGUF, checkpoints, or raw eval outputs staged in git
- [ ] Run `python scripts/security/scan_for_secrets.py` on any files to be committed
- [ ] Follow `docs/FIRST_PRIVATE_SFT_HANDOFF.md` for sanitized summary handoff
- [ ] Gate remains BLOCKED after all steps

---

## Cross-Reference

| Document | Relationship |
|----------|-------------|
| [KIMARI4B_PRIVATE_SFT_RUN.md](KIMARI4B_PRIVATE_SFT_RUN.md) | Full execution guide for this first run |
| [KIMARI4B_EVAL_CRITERIA.md](KIMARI4B_EVAL_CRITERIA.md) | Evaluation criteria |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine |
| [FIRST_PRIVATE_SFT_HANDOFF.md](FIRST_PRIVATE_SFT_HANDOFF.md) | How to bring sanitized results into the repo |
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | SmolLM3-3B acceptance for private training |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Token safety procedures |

---

*Complete every item before starting the first private SFT run. Gate stays BLOCKED. No public release. No HF upload.*
