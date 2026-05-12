# Kimari-4B Adapter Persistence Strategy

> How to retrieve and store LoRA adapters from HF Jobs ephemeral storage.

## Problem

HF Jobs run in ephemeral containers. The adapter generated during training is saved to `/tmp/` inside the container and is **lost when the job completes**. We need a strategy to persist the adapter for evaluation.

## Options Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **1. HF Hub private repo** | Native, versioned, easy access | Requires HF upload, token handling, visibility control | ✅ Recommended for v0.1.51+ |
| **2. Private GitHub repo + Git LFS** | Already set up (`smouj/kimari-4b-artifacts`), free, versioned | LFS overhead, large files, manual download | ✅ Backup option |
| **3. Signed artifact download** | Direct, no repo overhead | Requires custom infrastructure, no versioning | ❌ Too complex |
| **4. External object storage (S3/GCS)** | Scalable, fast | Requires cloud account, cost, no versioning | ❌ Overkill |
| **5. No persistence** | Zero risk | Can't evaluate adapter | ❌ Blocks progress |

## Recommended Strategy: HF Hub Private Repo

### Why HF Hub Private Repo

1. **Native integration**: HF Jobs can push to Hub natively
2. **Private by default**: `private=true` on the model repo
3. **Versioned**: Git-based, can track adapter versions
4. **Easy retrieval**: `huggingface_hub` Python API or `hf download`
5. **No public exposure**: Private repos are not visible to anyone

### Implementation Plan (v0.1.51)

```python
# In the training script, after model.save_pretrained():
from huggingface_hub import HfApi

api = HfApi()
repo_id = "Smouj013/kimari4b-micro-sft-adapter-v0"

# Create private repo if not exists
api.create_repo(repo_id=repo_id, private=True, exist_ok=True)

# Upload adapter files
api.upload_folder(
    folder_path="/tmp/kimari4b-micro-sft-adapter",
    repo_id=repo_id,
    commit_message=f"Micro SFT v0 adapter - {run_id}",
)
```

### Safety Constraints

- **`private=True`** always — no public model repos
- **No `push_to_hub` in training config** — the upload happens explicitly, not via Trainer
- **Adapter repo is separate from code repo** — `smouj/kimari-local-ai` (public code) vs `Smouj013/kimari4b-micro-sft-adapter-v0` (private weights)
- **Gate stays BLOCKED** — uploading to private HF repo does NOT advance the gate
- **No GGUF export** — only safetensors format

## Backup Strategy: Private GitHub Repo

The private repo `smouj/kimari-4b-artifacts` is already set up with:

- `adapters/` — for LoRA weights (Git LFS)
- `training/results/` — for sanitized summaries
- `eval/baselines/` + `eval/comparisons/` — for eval results
- `.gitattributes` — LFS for `*.safetensors`
- `.gitignore` — excludes `*.bin`, `*.gguf`, `*.pt`, `*.pth`

### Usage

```bash
# After downloading adapter from HF Hub private repo:
cd ~/.openclaw/workspace/kimari-4b-artifacts
mkdir -p adapters/kimari4b-micro-sft-adapter-v0
cp -r /path/to/adapter/* adapters/kimari4b-micro-sft-adapter-v0/
git lfs track "*.safetensors"
git add . && git commit -m "Add micro SFT v0 adapter"
git push origin main
```

## What NOT to Do

- ❌ Upload adapter to public HF Hub
- ❌ Commit adapter to `smouj/kimari-local-ai` (public repo)
- ❌ Generate GGUF from adapter
- ❌ Share adapter outside of private repos
- ❌ Claim quality improvements without baseline eval