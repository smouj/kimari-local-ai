# Kimari Runtime 1.5B SFT v1 — Private Scoring Subset30

Private scoring eval for the 100-step SFT adapter.

## Result

- Job: `6a052b32e48bea4538b9c34f`
- Baseline proxy score: `0.3158`
- Adapter proxy score: `0.3286`
- Delta: `+0.0128`
- Adapter wins: `16`
- Baseline wins: `12`
- Ties: `2`

## Interpretation

The 100-step adapter is measurably better than the base on this private lexical proxy, but **not much better yet**. This supports a guarded 500-step full-run before any GGUF/public release work.

## Safety

- Raw outputs are private HF Jobs artifacts only.
- No raw outputs are committed here.
- This is not a public benchmark.
- Gate remains `BLOCKED`.
