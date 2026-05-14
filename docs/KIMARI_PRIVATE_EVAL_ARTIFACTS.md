# Kimari Private Eval Artifacts — v0.1.76-alpha

Gate: **BLOCKED**  
Public benchmark: **not allowed**  
Public weights/GGUF: **not allowed**

## Purpose

Private scoring needs raw model outputs for manual review, but those outputs must never be committed to the public repo.

`v0.1.76-alpha` hardens this rule: subset30 scoring is not considered review-ready unless `raw_outputs_private.json` is generated, uploaded to private storage, and validated by hash/size.

## Private artifact

Private-only file:

- `raw_outputs_private.json`

It may contain full prompts, reference answers, and generated model outputs. For that reason it belongs only in private storage, not in Git.

## Public metadata only

The public repo may record only sanitized metadata:

- private artifact path
- SHA256
- size in bytes
- uploaded true/false
- manual review availability
- aggregate scoring metrics
- gate state

No raw prompt or response bodies are allowed.

## Validation

Use:

```bash
python eval/scripts/validate_private_eval_artifacts.py \
  --repo-id Smouj013/jobs-artifacts \
  --artifact-path kimari-evals/v0176/subset30/raw_outputs_private.json \
  --expected-sha256 <sha256> \
  --json
```

Validation must confirm:

- artifact exists
- filename is `raw_outputs_private.json`
- size is greater than zero
- SHA256 matches when provided
- `raw_outputs_private.json` is not tracked in the public repo
- `manual_review_available=true`

## Safety rules

- No token CLI args.
- Use environment/HF auth only.
- No billing or plan details in docs/logs.
- No public benchmark claims.
- No public weights or GGUF.
- Gate remains BLOCKED until later manual review and larger evals.

## v0.1.76 result

- scoring job: `6a0590cce48bea4538b9c7b9`
- private artifact: `hf://buckets/Smouj013/jobs-artifacts/kimari-evals/v0176/subset30/raw_outputs_private.json`
- SHA256: `0c88803e796ed4adaa0fe55a683659ef45fd40386fb79fae88c7fe1bbc801e37`
- size: `90282` bytes
- validation: passed
- manual review available: true
- gate: BLOCKED
