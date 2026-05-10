# Kimari Dataset Policy & Reference

This directory defines the dataset structure, schemas, quality standards, and contribution process for training and fine-tuning Kimari models. **No real datasets are included yet** — only empty placeholder directories with `.gitkeep` files.

---

## Directory Structure

```
dataset/
├── README.md              # This file — dataset policy and reference
├── schema/                # JSON Schema definitions for dataset formats
│   ├── sft.schema.json    # Supervised Fine-Tuning schema
│   └── preference.schema.json  # Preference (chosen/rejected) schema
├── raw/                   # Raw, unprocessed data (.gitkeep only)
├── cleaned/               # Cleaned and validated data (.gitkeep only)
├── sft/                   # Supervised Fine-Tuning data (.gitkeep only)
├── preference/            # Preference tuning data (.gitkeep only)
├── code/                  # Code-specific examples (.gitkeep only)
├── eval/                  # Evaluation-only data — never used for training
└── scripts/               # Validation and transformation scripts
```

> **Note**: All data subdirectories are currently empty except for `.gitkeep` files. No datasets are shipped with this repository.

---

## Allowed Dataset Types

The following dataset categories are accepted for Kimari training:

| Category | Description | Example Tags |
|----------|-------------|--------------|
| **Supervised Fine-Tuning (SFT)** | Single-turn and multi-turn instruction-response pairs | `coding`, `sysadmin`, `spanish` |
| **Preference** | Chosen/rejected response pairs for DPO/ORPO tuning | `agent`, `json`, `safety` |
| **Code Solutions** | Programming problems with correct solutions | `python`, `typescript`, `bash` |
| **Server Debugging** | Real-world error diagnosis and resolution | `linux`, `nginx`, `systemd` |
| **Agent Prompts** | Multi-step reasoning and tool-use examples | `agent`, `tool-use`, `reasoning` |
| **Spanish Technical** | Technical responses in proper Spanish | `spanish`, `networking`, `devops` |
| **System Administration** | Linux/Windows automation and configuration | `sysadmin`, `docker`, `ssh` |
| **JSON/Structured Output** | Formatted output generation (JSON, YAML, TOML) | `json`, `yaml`, `structured` |
| **Documentation** | Technical writing and explanation examples | `docs`, `tutorial`, `explanation` |
| **Evaluation** | Held-out data for benchmarking — **never for training** | `eval`, `kimarifit`, `benchmark` |

---

## Forbidden Data

The following types of data are **strictly prohibited** in this repository:

| Forbidden Type | Reason |
|---------------|--------|
| **Private user data** | PII, personal conversations, user logs without explicit consent |
| **Scraped secrets** | API keys, passwords, tokens, connection strings from any source |
| **Copyrighted dumps without permission** | Stack Overflow dumps, GitHub code without license, published books |
| **Credentials** | Database passwords, SSH keys, OAuth tokens, certificate keys |
| **Malware payloads** | Exploit code intended for harm, ransomware samples, attack toolkits |
| **Unlicensed content** | Any content where the license is unknown or non-permissive |
| **Synthetic data from closed models** | Output from GPT-4, Claude, etc. unless the model's ToS explicitly allows it |

### Enforcement

- Every dataset entry **must** include a `source` and `license` field.
- Entries with missing or `"unknown"` source/license will be rejected during validation.
- Automated validation scripts will scan for potential secrets (API key patterns, credential formats).
- Any contribution containing forbidden data will be immediately removed and the contributor notified.

---

## JSONL Schemas

All training data must conform to one of the two schemas defined in `dataset/schema/`. Data is stored in **JSONL format** (one JSON object per line).

### SFT (Supervised Fine-Tuning) Format

Used for instruction-following and multi-turn conversation training.

```json
{
  "messages": [
    {"role": "system", "content": "Eres Kimari, asistente técnico local..."},
    {"role": "user", "content": "Tengo un error MODULE_NOT_FOUND en Node.js."},
    {"role": "assistant", "content": "Este error indica que Node.js no puede encontrar un módulo..."}
  ],
  "source": "community-debugging",
  "license": "CC-BY-4.0",
  "tags": ["coding", "spanish", "sysadmin"]
}
```

**Field Reference:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | array | **Yes** | Ordered list of conversation turns |
| `messages[].role` | string | **Yes** | One of: `system`, `user`, `assistant` |
| `messages[].content` | string | **Yes** | Turn content (minimum 1 character) |
| `source` | string | **Yes** | Origin of this data point |
| `license` | string | **Yes** | License under which this data is shared |
| `tags` | array of strings | No | Categorization tags for filtering |

**Rules:**
- At least one `user` message and one `assistant` message are required.
- The `system` message is optional but recommended.
- Conversation turns must alternate between `user` and `assistant` (after optional `system` prefix).
- Validated by `dataset/schema/sft.schema.json`.

### Preference Format

Used for DPO/ORPO preference tuning with chosen/rejected pairs.

```json
{
  "prompt": "Explica cómo configurar nginx como reverse proxy para un servicio en el puerto 3000.",
  "chosen": "Para configurar nginx como reverse proxy, necesitas crear un archivo de configuración en /etc/nginx/sites-available/...",
  "rejected": "nginx es un servidor web. Puedes instalarlo con apt install nginx.",
  "source": "community-preference",
  "license": "CC-BY-4.0",
  "tags": ["agent", "json"]
}
```

**Field Reference:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | **Yes** | The input prompt or question (minimum 1 character) |
| `chosen` | string | **Yes** | The preferred/higher-quality response (minimum 1 character) |
| `rejected` | string | **Yes** | The less-preferred/lower-quality response (minimum 1 character) |
| `source` | string | **Yes** | Origin of this data point |
| `license` | string | **Yes** | License under which this data is shared |
| `tags` | array of strings | No | Categorization tags for filtering |

**Rules:**
- `chosen` and `rejected` must be meaningfully different — trivially different responses add no training signal.
- The `chosen` response should be demonstrably better (more accurate, more helpful, safer, etc.).
- Validated by `dataset/schema/preference.schema.json`.

---

## Quality Guidelines

All contributed data must meet the following quality standards:

### Accuracy
1. All code examples must be **tested and correct** — no unverified code.
2. Technical responses must be **factually accurate** — no hallucinated commands, APIs, or configurations.
3. Spanish responses must use **proper technical terminology** — avoid machine-translation artifacts.

### Safety
4. Destructive commands (e.g., `rm -rf`, `DROP TABLE`) must be **clearly marked with warnings**.
5. Security-sensitive operations must include **explicit risk disclosures**.
6. No instructions that facilitate unauthorized access or exploitation.

### Consistency
7. System prompts must follow the Kimari persona: "Eres Kimari, asistente técnico local..."
8. Multi-turn conversations must maintain **logical coherence** across turns.
9. Tags must use **lowercase, hyphenated** format (e.g., `sysadmin`, `reverse-proxy`).

### Completeness
10. Every entry must have a **valid `source`** (not `"unknown"`).
11. Every entry must have a **valid `license`** (not `"unknown"`).
12. Preference pairs must have a **clear quality gap** between chosen and rejected.

### Diversity
13. Avoid excessive duplication — near-duplicate entries degrade training quality.
14. Cover a range of difficulty levels (beginner to advanced).
15. Include multilingual content where possible (Spanish and English as primary).

---

## Contributing Data

To contribute training data to the Kimari project:

### Step 1: Prepare Your Data

1. Format your data in JSONL following the appropriate schema (SFT or Preference).
2. Validate against the JSON Schema files in `dataset/schema/`:
   ```bash
   # Example using jsonschema (Python)
   pip install jsonschema
   jsonschema -i your_data.jsonl dataset/schema/sft.schema.json
   ```
3. Ensure every entry has a valid `source` and `license`.
4. Verify no forbidden data is present (no secrets, no PII, no copyrighted content without permission).

### Step 2: Place in Raw Directory

1. Place your raw JSONL file in `dataset/raw/` with a descriptive filename:
   ```
   dataset/raw/2026-03-community-sft-spanish-debugging.jsonl
   ```
2. Filename convention: `{date}-{source}-{type}-{description}.jsonl`

### Step 3: Clean and Validate

1. Run validation scripts from `dataset/scripts/` (if available).
2. Check for:
   - Schema compliance
   - Duplicate entries
   - Secret/credential leakage
   - License compatibility
   - Minimum quality thresholds

### Step 4: Submit for Review

1. Move validated data to the appropriate subdirectory (`dataset/sft/`, `dataset/preference/`, etc.).
2. Submit a pull request with:
   - Description of the data source and collection method
   - Number of entries
   - License information
   - Any known limitations or biases
3. A maintainer will review the data before merging.

### Pull Request Checklist

- [ ] Data follows the correct JSONL schema (SFT or Preference)
- [ ] All entries have valid `source` and `license` fields
- [ ] No private user data, secrets, or credentials present
- [ ] No copyrighted content without explicit permission
- [ ] No malware payloads or exploit code
- [ ] Code examples are tested and correct
- [ ] Destructive commands are marked with warnings
- [ ] Spanish content uses proper technical terminology
- [ ] No near-duplicate entries
- [ ] Filename follows convention: `{date}-{source}-{type}-{description}.jsonl`
- [ ] Eval data is placed in `dataset/eval/` (never in training directories)

---

## Data Categories

Data is organized by both **format** and **domain**:

### By Format
| Directory | Schema | Purpose |
|-----------|--------|---------|
| `sft/` | `sft.schema.json` | Supervised fine-tuning data |
| `preference/` | `preference.schema.json` | Preference tuning data |
| `eval/` | Either | Evaluation only — **never** for training |

### By Domain (via tags)
| Tag | Description |
|-----|-------------|
| `coding` | Programming problems and solutions |
| `sysadmin` | Linux/Windows system administration |
| `spanish` | Spanish-language technical content |
| `agent` | Multi-step reasoning and tool use |
| `json` | Structured output generation |
| `debugging` | Error diagnosis and troubleshooting |
| `docker` | Container management |
| `networking` | Network configuration and debugging |
| `security` | Security best practices and hardening |
| `devops` | CI/CD, deployment, infrastructure |
| `documentation` | Technical writing |

---

## Validation Process

All dataset contributions go through the following validation pipeline:

### 1. Schema Validation
- Every JSONL line must validate against the appropriate JSON Schema.
- Validation is performed by `dataset/schema/sft.schema.json` or `dataset/schema/preference.schema.json`.

### 2. Content Validation
- **Secret detection**: Automated scanning for API keys, passwords, tokens, and other credential patterns.
- **PII detection**: Check for email addresses, phone numbers, and other personal identifiers that shouldn't be present.
- **License check**: Verify all `license` fields reference known, compatible licenses.

### 3. Quality Validation
- **Code correctness**: Spot-check code examples for correctness.
- **Response quality**: Ensure assistant responses are helpful and accurate.
- **Preference gap**: For preference data, verify `chosen` is meaningfully better than `rejected`.
- **Deduplication**: Remove or flag near-duplicate entries.

### 4. Integration Validation
- **Format consistency**: Ensure all entries in a file use the same schema.
- **Tag normalization**: Verify tags are lowercase and hyphenated.
- **Source attribution**: Confirm `source` field is traceable.

### Validation Commands (Planned)

```bash
# Validate a single file against SFT schema
python -m jsonschema dataset/raw/my-data.jsonl -i dataset/schema/sft.schema.json

# Validate all files in a directory
for f in dataset/raw/*.jsonl; do
  python -m jsonschema "$f" -i dataset/schema/sft.schema.json
done
```

> **Note**: Automated validation scripts in `dataset/scripts/` are planned but not yet implemented.

---

## Important Reminders

- **No real datasets are included** in this repository yet.
- **Eval data must never be used for training** — it is held out for benchmarking only.
- **All data must be original or have compatible licensing.**
- **No network calls** in validation scripts — all processing must be local.
- **Default profile is `test`** — dataset scripts must not change this.
- **No model downloads** in dataset scripts or CI.
- Refer to `docs/MODEL_TRAINING_PLAN.md` for how datasets feed into the training pipeline.
