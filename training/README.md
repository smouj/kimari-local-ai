# Training

> **WARNING: Training code is experimental.**
> No training has been performed yet. No model weights exist.
> No base model has been selected. All configurations are starting points, NOT final values.

## Important Rules

- **No training in CI** — Training scripts must never run in CI/CD pipelines.
- **No model weights committed** — The `runs/`, `adapters/`, and `logs/` directories are gitignored.
- **No hardcoding base model** — All configs use `"TBD"` until a base model is selected.
- **No network calls** — Scripts must not download models or datasets. All data must be local.
- **No downloads** — Scripts must not fetch anything from the internet.
- **Fail clearly** — Scripts must fail with a clear error message if dependencies are missing.
- **Tests only use `--dry-run`** — Automated tests must never trigger real training.

## Folder Structure

```
training/
├── README.md              # This file
├── configs/               # Training configuration YAML files
│   ├── kimari_sft_lora.example.yaml
│   └── kimari_orpo.example.yaml
├── scripts/               # Training and data preparation scripts
│   ├── prepare_dataset.py
│   └── train_sft_lora.py
├── runs/                  # Training run outputs (gitignored)
├── adapters/              # LoRA adapter outputs (gitignored)
└── logs/                  # Training logs (gitignored)
```

## Dependencies

Training requires the following Python packages (not installed by default):

```bash
pip install transformers datasets peft trl accelerate torch pyyaml
```

| Package       | Purpose                          |
|---------------|----------------------------------|
| `transformers`| Model loading and tokenization   |
| `datasets`    | Dataset loading and processing   |
| `peft`        | Parameter-efficient fine-tuning  |
| `trl`         | SFTTrainer and training loops    |
| `accelerate`  | Distributed training support     |
| `torch`       | PyTorch backend                  |
| `pyyaml`      | YAML config loading              |

## Usage

### 1. Prepare a Dataset

```bash
# Validate and clean an SFT dataset
python training/scripts/prepare_dataset.py \
    --input ./dataset/raw/sft_raw.jsonl \
    --output ./dataset/cleaned/sft_train.jsonl \
    --schema sft

# Validate and clean a preference dataset
python training/scripts/prepare_dataset.py \
    --input ./dataset/raw/preference_raw.jsonl \
    --output ./dataset/cleaned/preference_train.jsonl \
    --schema preference
```

### 2. Run SFT LoRA Training (Dry Run)

Always validate your config with `--dry-run` first:

```bash
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.example.yaml \
    --dry-run
```

### 3. Run SFT LoRA Training (Real)

```bash
# WARNING: This requires GPU hardware, dependencies, and a selected base model.
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.example.yaml
```

### 4. ORPO Preference Tuning

ORPO runs **after** SFT is complete. Use the SFT adapter as the base:

```bash
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_orpo.example.yaml \
    --dry-run
```

## Safety Notes

- **Never train on data that encourages harmful outputs.**
- Always evaluate safety refusal after preference tuning (ORPO/DPO).
- No model weights should ever be committed to this repository.
- The `runs/`, `adapters/`, and `logs/` directories are excluded from git.
- Training configurations are starting points — adjust based on evaluation results.
- Base model selection is pending. Do not hardcode any model name in scripts.
