# Kimari SFT v1 — License Notes

> **Version**: v0.1.59-alpha  
> **Status**: Seed  
> **Last updated**: 2026-05-13

## Dataset License

The Kimari SFT v1 dataset is released under **Apache License 2.0**.

## Per-Source Licenses

| Source File | Source Type | License | Redistribution | Commercial Use | Attribution |
|-------------|-------------|---------|----------------|----------------|-------------|
| spanish_technical.jsonl | kimari-authored | Apache-2.0 | ✅ Yes | ✅ Yes | Required |
| coding_debug.jsonl | kimari-authored | Apache-2.0 | ✅ Yes | ✅ Yes | Required |
| server_ops.jsonl | kimari-authored | Apache-2.0 | ✅ Yes | ✅ Yes | Required |
| local_llm_cuda_gguf.jsonl | kimari-authored | Apache-2.0 | ✅ Yes | ✅ Yes | Required |
| openclaw_agents.jsonl | kimari-authored | Apache-2.0 | ✅ Yes | ✅ Yes | Required |
| safety_refusal.jsonl | kimari-authored | Apache-2.0 | ✅ Yes | ✅ Yes | Required |
| json_tooling.jsonl | kimari-authored | Apache-2.0 | ✅ Yes | Required |
| style_consistency.jsonl | kimari-authored | Apache-2.0 | ✅ Yes | ✅ Yes | Required |

## Individual Example Licenses

Each example in the dataset includes a `license` field. The following values are permitted:

| License | Description | Redistribution | Commercial |
|---------|-------------|----------------|------------|
| `project-owned` | Original content created for Kimari | ✅ | ✅ |
| `MIT` | MIT licensed content | ✅ | ✅ |
| `Apache-2.0` | Apache 2.0 licensed content | ✅ | ✅ |
| `BSD-3-Clause` | BSD 3-Clause licensed content | ✅ | ✅ |
| `CC-BY-4.0` | Creative Commons Attribution 4.0 | ✅ | ✅ |
| `CC-BY-SA-4.0` | Creative Commons Attribution-ShareAlike 4.0 | ✅ | ✅ (with SA) |

## Blocked Licenses

The following sources and licenses are **NOT** permitted in the Kimari SFT v1 dataset:

| Source Type | Reason |
|-------------|--------|
| `unknown` | Cannot verify redistribution rights |
| `non-commercial` | CC-NC licenses do not permit commercial use |
| `research-only` | Research-only terms restrict redistribution |
| `proprietary` | Proprietary content cannot be redistributed |
| `copied-from-private-chat` | Private conversations lack redistribution consent |
| `raw-logs` | Raw logs may contain PII and lack clear license |
| `closed-model-output` | Outputs from closed-source models may have restrictive ToS |

## Attribution

When using this dataset, please attribute:

```
Kimari SFT v1 Dataset
Copyright 2026 Smouj
Licensed under the Apache License, Version 2.0
https://github.com/smouj/kimari-local-ai
```

## Safety

- **No PII**: No personal information, real names, addresses, or emails
- **No tokens**: No API keys, passwords, or authentication tokens
- **No private logs**: No real server logs or chat histories
- **No false claims**: No claims that Kimari-4B is released
- **Gate**: BLOCKED — No training has been executed