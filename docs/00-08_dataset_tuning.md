# Kimari Dataset & Fine-Tuning

## Document: 00-08 Dataset Preparation & Tuning Roadmap
**Version:** 0.1.0
**Status:** Planning
**Last Updated:** 2025

---

## Overview

This document describes the dataset strategy for fine-tuning Kimari models. It covers dataset sources, preparation pipeline, training methodology, and evaluation framework.

## Dataset Philosophy

Kimari is designed to excel at specific technical domains on consumer hardware. Rather than training a general-purpose model, we focus on:

1. **Coding** — Python, TypeScript, shell scripting
2. **System Administration** — Linux, Windows, Docker, networking
3. **Technical Spanish** — IT infrastructure, DevOps
4. **Agent Capabilities** — Multi-step reasoning, tool use
5. **Product & Strategy** — Technical product thinking

## Dataset Structure

```
dataset/
├── raw/              # Downloaded or collected data (pre-cleaning)
├── cleaned/          # Cleaned and deduplicated data
├── instructions/     # Instruction-response pairs for fine-tuning
├── conversations/    # Multi-turn conversations
├── code/             # Code-specific training data
├── eval/             # Evaluation and holdout sets
└── README.md         # This file
```

## Data Sources

### Public Datasets (Planned)

| Dataset | Type | Size | License | Purpose |
|---------|------|------|---------|---------|
| Alpaca | Instructions | 52K | Apache 2.0 | General instruction following |
| Open-Orca | Conversations | 4.2M | MIT | Multi-turn chat |
| CodeAlpaca | Code instructions | 20K | Apache 2.0 | Code generation |
| Evol-Instruct | Complex instructions | 52K | Apache 2.0 | Reasoning |
| ShareGPT | Conversations | 90K | CC-BY-NC | Conversation style |
| StackExchange | Q&A | 10M+ | CC-BY-SA | Technical Q&A |
| Python Q&A | Code Q&A | 200K+ | Various | Python troubleshooting |
| Spanish Tech | Custom | TBD | MIT | Technical Spanish |

### Domain-Specific Data

#### Coding Data

```
Source: GitHub repositories (permissive license only)
- Python projects with type hints
- TypeScript projects with strict mode
- Shell scripts with error handling
- Code with tests and documentation
```

#### System Administration Data

```
Source: StackExchange (Server Fault, Super User, Ask Ubuntu)
- Linux troubleshooting
- Docker and Kubernetes
- Networking and DNS
- Windows Server administration
```

#### Technical Spanish Data

```
Source: Custom collection
- Translated technical documentation
- Spanish-language tech blogs
- Localized error messages
- IT exam preparation materials
```

## Data Preparation Pipeline

### Step 1: Collection

```bash
# Download public datasets
python tools/collect_data.py \
  --sources alpaca,codealpaca,openorca \
  --output dataset/raw/

# Scrape Spanish tech content
python tools/collect_spanish.py \
  --output dataset/raw/spanish/
```

### Step 2: Cleaning

```bash
# Clean and deduplicate
python tools/clean_data.py \
  --input dataset/raw/ \
  --output dataset/cleaned/ \
  --min-length 50 \
  --max-length 4096 \
  --deduplicate \
  --remove-pii
```

Cleaning rules:
- Remove duplicates (exact and fuzzy)
- Filter by length (50–4096 tokens)
- Remove PII (emails, phone numbers, IPs)
- Fix encoding issues
- Normalize whitespace
- Remove low-quality entries (gibberish, spam)

### Step 3: Format Conversion

Convert to the training format (JSONL):

```json
{
  "instruction": "Write a Python function...",
  "input": "",
  "output": "def binary_search(arr, target):..."
}
```

Or for chat format:
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "Write a Python function..."},
    {"role": "assistant", "content": "def binary_search(...)"}
  ]
}
```

### Step 4: Quality Filtering

```bash
# Score and filter by quality
python tools/filter_quality.py \
  --input dataset/cleaned/ \
  --output dataset/instructions/ \
  --min-quality 0.7
```

Quality criteria:
- Instruction clarity
- Response completeness
- Code correctness (if applicable)
- Language consistency
- Technical accuracy

### Step 5: Train/Eval Split

```bash
# Split into training and evaluation sets (90/10)
python tools/split_data.py \
  --input dataset/instructions/ \
  --train dataset/instructions/train.jsonl \
  --eval dataset/eval/eval.jsonl \
  --ratio 0.9
```

## Fine-Tuning Roadmap

### Phase 1: Supervised Fine-Tuning (SFT)

**Goal:** Create Kimari-4B-Instruct

**Method:** LoRA (Low-Rank Adaptation) — memory efficient, works on consumer GPUs

**Parameters:**
- Rank (r): 16
- Alpha: 32
- Dropout: 0.05
- Target modules: q_proj, k_proj, v_proj, o_proj

**Training config:**
```yaml
base_model: path/to/base-model-4b
method: lora
lora_rank: 16
lora_alpha: 32
dataset: dataset/instructions/train.jsonl
eval_dataset: dataset/eval/eval.jsonl
epochs: 3
batch_size: 4
learning_rate: 2e-4
warmup_ratio: 0.1
max_seq_length: 4096
gradient_accumulation: 8
fp16: true
```

**Hardware requirement for training:**
- GPU: 24 GB VRAM (for full fine-tuning) or 8 GB (for LoRA)
- RAM: 16 GB
- Disk: 20 GB

### Phase 2: Domain Specialization

**Coding variant:** Fine-tune with coding-heavy dataset
**Spanish variant:** Fine-tune with Spanish technical data
**Sysadmin variant:** Fine-tune with StackExchange data

### Phase 3: RLHF / DPO (Future)

**Goal:** Improve response quality and alignment

**Method:** Direct Preference Optimization (DPO) — simpler than RLHF

**Data:** Human preference pairs (chosen vs rejected responses)

### Phase 4: Quantization

After fine-tuning, quantize the model using llama.cpp:

```bash
# Convert to GGUF
python convert_hf_to_gguf.py /path/to/kimari-4b-instruct --outfile Kimari-4B-Instruct-F16.gguf

# Quantize
./llama-quantize Kimari-4B-Instruct-F16.gguf Kimari-4B-Instruct-Q4_K_M.gguf Q4_K_M
./llama-quantize Kimari-4B-Instruct-F16.gguf Kimari-4B-Instruct-Q5_K_M.gguf Q5_K_M
```

## Evaluation Framework

### Automatic Evaluation

```bash
cd eval
python run_eval.py --model Kimari-4B-Instruct --dataset kimari_eval.jsonl
```

Metrics:
- Exact match (for code tasks)
- Code execution success rate
- JSON validity rate
- Language detection accuracy
- Response length distribution

### Human Evaluation

Conduct blind evaluations comparing:
- Kimari-4B vs base model
- Kimari-4B vs Qwen2.5-3B (same size)
- Different quantization levels

### Benchmark Suite

| Category | Test | Metric |
|----------|------|--------|
| Coding | HumanEval | pass@1 |
| Coding | MBPP | pass@1 |
| Reasoning | MMLU (5-shot) | accuracy |
| Reasoning | GSM8K | accuracy |
| Spanish | Custom ES eval | accuracy |
| JSON Mode | JSON generation | validity rate |
| Agent | Multi-step tasks | step completion |

## Tools

| Tool | Purpose | Status |
|------|---------|--------|
| `collect_data.py` | Download and aggregate datasets | Planned |
| `clean_data.py` | Clean and deduplicate | Planned |
| `filter_quality.py` | Quality scoring and filtering | Planned |
| `split_data.py` | Train/eval splitting | Planned |
| `run_eval.py` | Evaluation runner | Draft |
| `convert_format.py` | Format conversion | Planned |

## Ethical Guidelines

1. **License compliance** — Only use data with compatible licenses
2. **No PII** — Remove all personally identifiable information
3. **Bias auditing** — Check for and mitigate biases
4. **Toxicity filtering** — Remove harmful content
5. **Transparency** — Document all data sources and transformations

---

*This roadmap is subject to change based on experimental results and resource availability.*
