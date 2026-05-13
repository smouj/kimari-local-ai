# Environment Status — Kimari Local AI

> Last verified: 2026-05-13

| Environment | Status | Evidence | Next Action |
|------------|--------|----------|-------------|
| GitHub repo (`smouj/kimari-local-ai`) | ✅ Current | `main` at `v0.1.56-alpha`, CI passing 13/13 | — |
| GitHub Actions | ✅ Passing | Run 25789178707: all jobs success | Monitor next push |
| GitHub Pages (`smouj.github.io/kimari-local-ai`) | ✅ Current | `docs/index.html` at `v0.1.56-alpha`, no stale version references | Force redeploy if stale |
| HF org card (`kimari-ai`) | ✅ Current | Docs say `v0.1.56-alpha`, gate BLOCKED | Sync on next push |
| HF Space (`kimari-ai/kimari-fit-lab`) | ✅ Running | HTTP 200, version `v0.1.56-alpha` | — |
| HF Collection | ✅ Listed | 5 reference/community models, no official Kimari model | Verify manually |
| HF profile (`Smouj013`) | ⚠️ Unverified | Not manually verified | Add bio + links |
| Local WSL2 GTX 1060 | ✅ Validated | CUDA 12.0, llama-server CUDA, 228/73 tok/s | — |
| HF Jobs | ✅ Access | Smouj013, a10g-small verified | — |
| Private adapter repo (`Smouj013/kimari4b-micro-sft-adapter-v0`) | ✅ Persisted | Job `6a03a25e72518a06598ffae0` | — |
| KimariEval Private v1 | ✅ Ready | 104 cases, 7 categories | Run subset30 when ready |
| Gate | 🔒 BLOCKED | No public weights, no GGUF, no benchmark claims | — |