# Kimari Runtime 1.5B 500-step Manual Review — v0.1.75-alpha

Status: **ready for private manual review**  
Gate: **BLOCKED**  
Public benchmark: **not allowed**  
Public weights/GGUF: **not allowed**

## v0.1.76-alpha artifact persistence fix

v0.1.75-alpha correctly blocked manual review because `raw_outputs_private.json` was missing from the recorded private bucket path. v0.1.76-alpha hardens the scoring pipeline so private raw-output upload is mandatory before manual review can become available. Manual review is still not completed in this release.

## What was attempted

v0.1.75-alpha attempted the real private manual-review execution for scoring job `6a052f5ce48bea4538b9c37d` and training job `6a052ce6e48bea4538b9c365`.

Private storage was prepared outside the public repository:

- `~/kimari-private-review/v0175/`

The HF Job metadata shows the artifact bucket mount:

- bucket: `Smouj013/jobs-artifacts`
- path: `20260514T021138-8c30a6`

The bucket path was inspected, but it only exposed the inline scoring script. The expected `raw_outputs_private.json` file was not present at that path, so the 30-case manual review could not be completed honestly.

## Available sanitized aggregates

- subset size: 30
- base proxy score: 0.3158
- 100-step adapter proxy score: 0.3286
- 500-step adapter proxy score: 0.3404
- 500-step delta vs base: +0.0246
- 500-step adapter proxy wins: 17
- base proxy wins: 12
- ties: 1

These are private proxy-scoring aggregates only. They are **not** a public benchmark and do not prove usable quality wins without raw-output review.

## What is not published

- no full prompts
- no full responses
- no generated text bodies
- no raw output files
- no tokens or secrets
- no public benchmark claim
- no public model weights
- no GGUF artifact

The public repository only contains sanitized aggregate metadata, validator logic, and release checks.

## Manual review status

`ready_for_private_manual_review`

v0.1.76-alpha reran subset30 scoring with mandatory private artifact upload. `raw_outputs_private.json` is now available in private bucket storage and validated by SHA256/size. Manual review is still not completed; no adapter wins are quality-confirmed yet.

## Results aggregated

| Field | Value |
| --- | ---: |
| total reviewed | 0 / 30 |
| adapter proxy wins | 17 |
| base proxy wins | 12 |
| ties | 1 |
| accepted adapter wins | 0 |
| rejected adapter wins | 0 |
| accepted base wins | 0 |
| safety regressions | 0 reviewable |
| factual regressions | 0 reviewable |
| coding regressions | 0 reviewable |
| Spanish quality regressions | 0 reviewable |
| JSON/tooling regressions | 0 reviewable |

## Categories improved

None confirmed. Category-level quality cannot be verified without raw outputs.

## Categories regressed

None confirmed. Regression review cannot be verified without raw outputs.

## Safety status

No raw-output safety review was completed. This is **not** a safety pass.

## Decision

`ready_for_private_manual_review`

The next technical step is v0.1.77-alpha: perform the real 30-item private manual review using the validated private raw artifact. The gate remains BLOCKED.

## Recommended next step

Use the validated private artifact for manual review:

- `hf://buckets/Smouj013/jobs-artifacts/kimari-evals/v0176/subset30/raw_outputs_private.json`
- SHA256: `0c88803e796ed4adaa0fe55a683659ef45fd40386fb79fae88c7fe1bbc801e37`
- size: `90282` bytes

Perform the 30-item manual review outside the public repository and update only the sanitized summary.
