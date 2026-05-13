# Kimari SFT v1 Dataset License Plan

> **Version**: v0.1.59-alpha  
> **Last updated**: 2026-05-13  
> **Status**: Seed created — 320 examples, 8 categories  
> **Gate**: BLOCKED — no training until bakeoff complete

## 1. Objective

Define the licensing and provenance policy for the Kimari SFT v1 training dataset. Every example must have a clear, permissive-compatible license.

## 2. Dataset Target

| Category | Target Count | Focus |
|----------|-------------|-------|
| Spanish technical | 300 | Technical Q&A in Spanish |
| Coding/debug | 300 | Python, shell, debugging |
| Linux/sysadmin | 250 | Server operations, systemd, Docker |
| Local AI/GGUF/CUDA/VRAM | 250 | LLM deployment, quantization, hardware |
| OpenClaw/agents | 200 | Agent workflows, tool use, MCP |
| Safety/refusal | 150 | Refusal of harmful requests, safe responses |
| JSON/tooling | 150 | Structured output, API calls, tool following |
| Style consistency | 100 | Kimari tone and style examples |
| **Total** | **1,700** | |

Principle: **Better 1,500 examples impecable than 50,000 examples dirty.**

## 3. Data Source Policy

### 3.1 Approved Sources

| Source | License | Allowed | Condition |
|--------|---------|---------|-----------|
| Self-generated synthetic data | MIT (Kimari project) | ✅ | Must be reviewed for quality |
| Kimari project documentation | MIT | ✅ | Direct use |
| Hand-written examples by author | MIT | ✅ | No PII |
| Own code (Kimari repo) | Apache 2.0 | ✅ | License-compatible |
| Datasets under Apache 2.0 | Apache 2.0 | ✅ | Document license per source |
| Datasets under MIT | MIT | ✅ | Document license per source |
| Datasets under BSD | BSD | ✅ | Document license per source |
| StackExchange dumps | CC BY-SA 4.0 | ⚠️ | Attribution required; careful review |

### 3.2 Blocked Sources

| Source | Reason | Decision |
|--------|--------|----------|
| Real user logs | PII and consent | ❌ Never |
| Private chats | Privacy violations | ❌ Never |
| Datasets without clear license | Legal risk | ❌ Never |
| Outputs from closed-model APIs (OpenAI, Anthropic) | Terms may restrict derivative use | ⚠️ Avoid unless terms explicitly allow |
| Non-commercial datasets | License incompatible | ❌ Never |
| Research-only datasets | License incompatible | ❌ Never |

## 4. Dataset Manifest Requirement

Every training dataset must include a manifest (`dataset/kimari_sft_v1/MANIFEST.jsonl`) documenting:

```json
{
  "source": "synthetic_kimari_docs",
  "license": "MIT",
  "category": "spanish_technical",
  "count": 300,
  "reviewed": true,
  "pii_review": true,
  "provenance": "Generated from Kimari project documentation",
  "created_date": "2026-05-13"
}
```

Each manifest entry must include:
1. `source` — origin of examples
2. `license` — explicit license
3. `category` — KimariEval category
4. `count` — number of examples
5. `reviewed` — whether examples have been reviewed
6. `pii_review` — whether PII review has been conducted
7. `provenance` — description of how examples were created
8. `created_date` — when examples were created

## 5. PII Review

All examples must pass PII review before inclusion:
- No real names, emails, addresses, or phone numbers
- No real API keys, tokens, or passwords
- No real server IPs or hostnames
- No real user data or chat logs
- Generic placeholders only (e.g., `example.com`, `user`, `placeholder-key`)

## 6. Quality Criteria

- Each example must have a clear, unambiguous prompt
- Each example must have a correct, helpful response
- Responses should be concise (under 500 tokens preferred)
- No contradictory examples
- No examples that teach harmful behavior
- Style examples must match Kimari tone: technical, direct, no filler

## 7. Output Structure

```
dataset/kimari_sft_v1/
├── MANIFEST.jsonl
├── spanish_technical.jsonl
├── coding_debug.jsonl
├── server_ops.jsonl
├── local_llm_cuda_gguf.jsonl
├── openclaw_agents.jsonl
├── safety_refusal.jsonl
├── json_tooling.jsonl
├── style_consistency.jsonl
└── README.md
```

## 8. Safety Constraints

- No training until bakeoff baselines evaluated
- No public dataset release until gate review
- Raw outputs not committed to git
- Manifest must be complete before training
- Gate: BLOCKED

---

_This plan ensures Kimari's training data is clean, well-documented, and license-compatible._