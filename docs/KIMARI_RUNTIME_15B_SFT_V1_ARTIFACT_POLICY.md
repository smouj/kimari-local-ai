# Kimari Runtime 1.5B SFT v1 Artifact Policy

## Adapter

Adapters are private only. If a future approved run creates adapter weights, they must be saved locally under ignored training artifact paths and must never be committed to the public repository.

## Public Repositories

No public repository may be created for adapter weights during the BLOCKED gate.

## GGUF

No GGUF generation is allowed until evaluation passes, manual review is complete, and the gate is explicitly transitioned.

## Manifest

Run manifests must be sanitized before sharing or committing. They must not contain tokens, secrets, PII, private prompts, raw infrastructure logs, or local credential paths.

## Raw Training Logs

Raw training logs must not be committed. Only sanitized summaries may be tracked.

## Gate

Current gate: BLOCKED.

## Public Release

Public release is allowed only after:

1. Evaluation passes.
2. Manual review is completed.
3. Artifact manifest is sanitized.
4. A human explicitly approves the gate transition.
5. The release gate no longer says BLOCKED.
