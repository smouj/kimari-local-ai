# Kimari Brand Assets Plan

> Version: v0.1.55-alpha  
> Scope: visual polish plan only; no generated asset is required for this release.

## Assets to create

| Asset | Size | Purpose |
|---|---:|---|
| Hugging Face org banner | 1600×400 | Kimari AI org profile header |
| Avatar | 512×512 | GitHub/HF/social avatar |
| Flow diagram | 1200×800 or SVG | Explain Kimari local runtime flow |
| Screenshots | 16:9 PNG/WebP | README, docs site, HF Space |

## Visual direction

- Dark technical background.
- Purple/teal accent palette matching the docs site.
- Clear “local-first AI” message.
- Avoid fake enterprise polish or exaggerated claims.

## Recommended screenshots

- `kimari doctor --deep` passing locally.
- `kimari start --profile test` running the local endpoint.
- Open WebUI / OpenClaw / Continue config examples.
- Kimari Fit Lab Space UI.

## Anti-secret checklist

Before publishing screenshots:

- hide usernames, home paths, tokens, hostnames, and private repo names where not needed;
- do not show HF tokens or billing/plan data;
- do not show raw private eval outputs;
- do not imply Kimari-4B weights are available;
- run `scripts/security/scan_for_secrets.py` on any text artifacts.
