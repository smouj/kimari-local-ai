# Kimari Runtime 1.5B SFT v1 — 500-step Private Scoring Subset30

Private scoring eval for the 500-step SFT adapter.

## Jobs

- Training job: `6a052ce6e48bea4538b9c365`
- Scoring job: `6a052f5ce48bea4538b9c37d`

## Training signal

- Train runtime: `488.7s`
- Train loss: `1.944`
- Eval loss: `2.315 @50` → `1.757 @500`
- Eval token accuracy: `0.5487 @50` → `0.6307 @500`

## Private proxy scoring

| Metric | Baseline | 100-step Adapter | 500-step Adapter |
| --- | ---: | ---: | ---: |
| Proxy score | 0.3158 | 0.3286 | 0.3404 |
| Delta vs baseline | — | +0.0128 | +0.0246 |
| Wins vs baseline | — | 16 vs 12 | 17 vs 12 |

## Interpretation

The 500-step adapter is better than the base and better than the 100-step adapter. The delta vs baseline is nearly 2x the 100-step delta. However, the improvement is still modest and requires manual raw-output review before any public release or GGUF packaging.

## Safety

- Raw outputs are private HF Jobs artifacts only.
- No raw outputs are committed here.
- This is not a public benchmark.
- Gate remains `BLOCKED`.
