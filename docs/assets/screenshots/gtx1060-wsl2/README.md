# GTX 1060 WSL2 Screenshots

> Screenshot directory for Kimari Local AI running on NVIDIA GeForce GTX 1060 6GB (WSL2 Ubuntu 24.04).

## Naming Convention

Screenshots follow this pattern:

```
<command-or-feature>-<detail>.png
```

Examples:
- `nvidia-smi.png`
- `kimari-doctor-deep.png`
- `local-endpoint-health.png`

Use lowercase, hyphens for spaces, `.png` or `.webp` format.

## Allowed Screenshots

✅ Terminal output showing:
- GPU detection (nvidia-smi)
- Kimari doctor/status output
- llama-server startup with CUDA
- Endpoint health/models/completions responses
- Integration config output
- Benchmark tables (CPU vs CUDA)

## Prohibited Screenshots

❌ Screenshots containing:
- API keys, tokens, or secrets
- Private directory paths (e.g., `/home/username/...`) — redact or use generic paths
- Billing information
- HF token or account details
- Unreviewed benchmark claims
- Any implication that Kimari-4B is released

## Pre-commit Checklist

Before committing any screenshot:

1. [ ] No API keys, tokens, or secrets visible
2. [ ] No private user paths visible (redact with `/home/user/...` if needed)
3. [ ] No billing or subscription info
4. [ ] No claim that Kimari-4B is released
5. [ ] Benchmark numbers are factual and from real runs
6. [ ] Compress image (prefer WebP for large screenshots)

## Note

**All screenshots use the TinyLlama 1.1B Q4_K_M validation model — NOT Kimari-4B.**

Kimari-4B is not yet released. No weights, adapters, or GGUF files are available.

Gate remains **BLOCKED**.