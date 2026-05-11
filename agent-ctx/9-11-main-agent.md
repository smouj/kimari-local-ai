# Task 9-11 — Main Agent Work Record

## Task Summary
Improve compare_runs.py with verdict/summary-output, update 4 docs with cross-references for v0.1.21-alpha.

## Files Modified
1. `eval/scripts/compare_runs.py` — Added --summary-output CLI arg, verdict logic (5 levels), safety_regression_detected check, _build_summary_output(), _compute_category_deltas(), _determine_verdict()
2. `docs/PRIVATE_TRAINING_RUNBOOK.md` — Step 5c: create_adapter_manifest.py; Step 7d: create_eval_summary.py; Step 8: SFT_TO_ORPO_DECISION.md ref; Related docs: 4 new entries
3. `docs/ADAPTER_ARTIFACT_POLICY.md` — Manifest CAN be committed note; template-based creation via create_adapter_manifest.py; template path reference
4. `docs/ADAPTER_PREVIEW_GATE.md` — safety_regression_detected field; no auto-transition after manifest; Template References section
5. `docs/BASELINE_EVAL_PLAN.md` — create_eval_summary.py usage; compare_runs.py --summary-output; eval summary template; PRIVATE_EVAL_RESULTS_POLICY.md ref

## Key Decisions
- Verdict logic checks safety_regression_detected BEFORE score comparison (safety first)
- _compute_category_deltas enables "mixed" verdict when some categories improve and others regress
- Summary output format matches eval_summary.template.json fields exactly
- All doc updates are minimal, targeted additions preserving existing style
- No invented scores, no real training, no weights committed

## Validation
- py_compile on compare_runs.py: PASS
- Work record appended to worklog.md
