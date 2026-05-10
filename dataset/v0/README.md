# Dataset v0 — Small Synthetic Dataset for First Private SFT Run

> **Version:** v0.1.19-alpha  
> **Date:** 2026-05-21  
> **Status:** Active — dataset files for first private SFT run

---

## Objective

Dataset v0 provides a **small, own, and legal** synthetic dataset for the first private supervised fine-tuning (SFT) run of Kimari-4B on SmolLM3-3B. The dataset is intentionally minimal — its purpose is to validate the training pipeline end-to-end, not to produce a production-quality model.

**Key principles:**

- **Small** — Enough data to train an adapter and evaluate it, but not a full-scale training corpus
- **Own** — All data is created by the Kimari project; no third-party datasets are included
- **Legal** — All data is synthetic and MIT-compatible; no copyrighted content, no private data, no secrets

---

## Allowed Sources

Only the following data source is permitted in dataset v0:

| Source | Description | License |
|--------|-------------|---------|
| **kimari-v0-synthetic** | Synthetic data created by the Kimari project for pipeline validation | MIT-compatible synthetic |

**No other sources are allowed in v0.** Community contributions, scraped data, and third-party datasets belong in later dataset versions after proper review.

### Source and License Fields

Every record in dataset v0 **must** include the following mandatory fields:

| Field | Required Value |
|-------|----------------|
| `source` | `"kimari-v0-synthetic"` |
| `license` | `"MIT-compatible synthetic"` |

Records with missing, `"unknown"`, or mismatched `source`/`license` fields will be rejected by the validation scripts.

---

## Data Formats

### SFT Format

Used for supervised fine-tuning with instruction-response pairs.

```json
{
  "messages": [
    {"role": "system", "content": "You are Kimari, a local technical assistant..."},
    {"role": "user", "content": "How do I check disk usage on Linux?"},
    {"role": "assistant", "content": "Use the `df -h` command to check disk usage..."}
  ],
  "source": "kimari-v0-synthetic",
  "license": "MIT-compatible synthetic",
  "tags": ["sysadmin", "linux"]
}
```

**Field reference:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | array | **Yes** | Ordered list of conversation turns (system, user, assistant) |
| `messages[].role` | string | **Yes** | One of: `system`, `user`, `assistant` |
| `messages[].content` | string | **Yes** | Turn content (minimum 1 character) |
| `source` | string | **Yes** | Must be `"kimari-v0-synthetic"` |
| `license` | string | **Yes** | Must be `"MIT-compatible synthetic"` |
| `tags` | array of strings | No | Categorization tags (e.g., `coding`, `sysadmin`, `spanish`) |

**Rules:**

- At least one `user` and one `assistant` message are required
- The `system` message is optional but recommended
- Validated by `dataset/schema/sft.schema.json`

---

### Preference Format

Used for DPO/ORPO preference tuning with chosen/rejected response pairs.

```json
{
  "prompt": "Explain how to configure nginx as a reverse proxy.",
  "chosen": "To configure nginx as a reverse proxy, create a configuration file in /etc/nginx/sites-available/ with the proxy_pass directive...",
  "rejected": "nginx is a web server. Install it with apt install nginx.",
  "source": "kimari-v0-synthetic",
  "license": "MIT-compatible synthetic",
  "tags": ["sysadmin", "networking"]
}
```

**Field reference:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | **Yes** | The input prompt or question (minimum 1 character) |
| `chosen` | string | **Yes** | The preferred/higher-quality response (minimum 1 character) |
| `rejected` | string | **Yes** | The less-preferred/lower-quality response (minimum 1 character) |
| `source` | string | **Yes** | Must be `"kimari-v0-synthetic"` |
| `license` | string | **Yes** | Must be `"MIT-compatible synthetic"` |
| `tags` | array of strings | No | Categorization tags |

**Rules:**

- `chosen` and `rejected` must be meaningfully different
- `chosen` should be demonstrably better (more accurate, helpful, safer)
- Validated by `dataset/schema/preference.schema.json`

---

### Eval Holdout Format

Used for held-out evaluation data. This data is **never** used for training — it is reserved for benchmarking only.

```json
{
  "id": "eval-sysadmin-001",
  "category": "sysadmin",
  "prompt": "How do I restart a systemd service that has failed?",
  "expected_traits": ["mentions systemctl restart", "mentions systemctl status for diagnostics", "mentions journalctl for logs"],
  "forbidden_traits": ["suggests rebooting as first step", "suggests kill -9 without warning"]
}
```

**Field reference:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | **Yes** | Unique identifier for the eval entry |
| `category` | string | **Yes** | Category for grouping (e.g., `sysadmin`, `coding`, `agent`) |
| `prompt` | string | **Yes** | The evaluation prompt (minimum 1 character) |
| `expected_traits` | array of strings | **Yes** | Traits that a good response should exhibit |
| `forbidden_traits` | array of strings | **Yes** | Traits that a good response must NOT exhibit |

---

## Train/Eval Split

The train/eval split is handled by `build_dataset_mix.py`:

```bash
python training/scripts/build_dataset_mix.py \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --output-dir dataset/build/kimari-v0 \
    --shuffle \
    --seed 42 \
    --report
```

The script:

1. Loads and validates all SFT, preference, and holdout records
2. Shuffles the training data with a fixed seed (`42`) for reproducibility
3. Writes training-ready files to `dataset/build/kimari-v0/`
4. Keeps the holdout data separate — it is never mixed into training files
5. Generates a `report.json` with statistics

**Output files:**

| File | Contents |
|------|----------|
| `dataset/build/kimari-v0/sft.train.jsonl` | SFT records for training |
| `dataset/build/kimari-v0/preference.train.jsonl` | Preference records for training |
| `dataset/build/kimari-v0/eval_holdout.jsonl` | Held-out evaluation data (not for training) |
| `dataset/build/kimari-v0/report.json` | Build statistics and validation report |

---

## Prohibited Content

The following content is **strictly prohibited** in dataset v0:

| Prohibited | Reason |
|------------|--------|
| **No private data** | No PII, personal conversations, user logs, or any data identifying real individuals |
| **No secrets** | No API keys, passwords, tokens, connection strings, SSH keys, or credentials of any kind |
| **No malware** | No exploit code, ransomware samples, attack toolkits, or harmful payloads |
| **No copyrighted dumps** | No Stack Overflow dumps, GitHub code without license, published books, or any copyrighted content without explicit permission |

### Enforcement

- The `source` and `license` fields are mandatory and validated by `build_dataset_mix.py`
- Records with `"unknown"` source or license are rejected
- The validation pipeline checks for potential secrets (API key patterns, credential formats)
- Any prohibited content found will be immediately removed

---

## Files

Dataset v0 consists of three files:

| File | Format | Purpose | Records |
|------|--------|---------|---------|
| `dataset/v0/sft_v0.jsonl` | SFT JSONL | Supervised fine-tuning instruction-response pairs | Small set for pipeline validation |
| `dataset/v0/preference_v0.jsonl` | Preference JSONL | Chosen/rejected pairs for preference tuning | Small set for pipeline validation |
| `dataset/v0/eval_holdout.jsonl` | Eval holdout JSONL | Held-out evaluation data (never for training) | Small set for evaluation |

All files use JSONL format (one JSON object per line) and conform to the schemas in `dataset/schema/`.

---

## Relationship to Other Dataset Versions

| Version | Status | Description |
|---------|--------|-------------|
| **v0** (this) | Active | Small synthetic dataset for first private SFT run |
| **v1** | Future | Larger dataset with community contributions (requires license review for each source) |

Dataset v0 is a starting point. As the project matures, later versions will incorporate more data from diverse, license-reviewed sources.

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [dataset/README.md](../README.md) | General dataset policy, schemas, quality guidelines |
| [docs/FIRST_PRIVATE_TRAINING_RUN.md](../../docs/FIRST_PRIVATE_TRAINING_RUN.md) | Step-by-step guide that uses this dataset |
| [docs/BASE_MODEL_ACCEPTANCE.md](../../docs/BASE_MODEL_ACCEPTANCE.md) | Acceptance record authorizing the private SFT run |
| [dataset/schema/sft.schema.json](../schema/sft.schema.json) | JSON Schema for SFT format validation |
| [dataset/schema/preference.schema.json](../schema/preference.schema.json) | JSON Schema for preference format validation |

---

*Dataset v0 is small, own, and legal. It contains only synthetic data created by the Kimari project under MIT-compatible terms. No private data, secrets, malware, or copyrighted content is included. The dataset is intended for pipeline validation during the first private SFT run only.*
