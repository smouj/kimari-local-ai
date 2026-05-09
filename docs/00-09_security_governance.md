# Kimari Security & Governance

## Document: 00-09 Security & Governance
**Version:** 0.1.0
**Status:** Draft
**Last Updated:** 2025

---

## Overview

Kimari is designed with security and privacy as core principles. This document outlines the security model, data governance policies, and responsible AI guidelines.

## Security Model

### Threat Model

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|------------|
| Network intrusion (remote) | Low | High | Bind to localhost only |
| Data exfiltration | Very Low | Critical | No network calls; zero telemetry |
| Model poisoning | N/A | N/A | Users control their own models |
| Local privilege escalation | Low | Medium | Runs as unprivileged user |
| Malicious model execution | Medium | Medium | Warning system; model verification |
| Supply chain attack | Low | High | Minimal dependencies; vetted libs |

### Design Principles

1. **Local-First** — All data processing happens on the user's machine
2. **Zero Telemetry** — No data is sent to any external server
3. **Minimal Dependencies** — Only `requests` beyond Python stdlib
4. **Least Privilege** — No root/admin required; no special permissions
5. **Transparent** — Open source; all code is auditable
6. **User Control** — Users decide what models to run and what data to provide

### Network Security

#### Default Configuration

- llama-server binds to `127.0.0.1` (localhost only)
- No external network connections
- No API key required (local use)
- Port can be customized via profile

#### Exposing to Network (Not Recommended)

If you must expose Kimari to a local network:

```bash
# Change host in profile (DANGEROUS on public networks)
# config/kimari.profiles.json
{
  "host": "0.0.0.0"  // Binds to all interfaces
}
```

**Recommendations if exposing:**
- Use a firewall to restrict access
- Set up a reverse proxy with HTTPS (nginx/caddy)
- Consider adding API key authentication
- Never expose directly to the public internet

#### Firewall Configuration

```bash
# Allow only localhost access
sudo ufw deny 11435/tcp
sudo ufw allow from 127.0.0.1 to any port 11435

# Or use iptables
sudo iptables -A INPUT -p tcp --dport 11435 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 11435 -j DROP
```

## Data Privacy

### What Kimari Does NOT Collect

- **Zero telemetry** — No usage statistics sent anywhere
- **No conversations logged** — Kimari does not save chat history
- **No system information sent** — `kimari doctor` output stays local
- **No unique identifiers** — No device fingerprinting
- **No analytics** — No tracking pixels or analytics scripts

### What Kimari Stores Locally

| Data | Location | Purpose |
|------|----------|---------|
| Server PID | `server/kimari.pid` | Process management |
| Server log | `server/kimari.log` | Debugging |
| Config | `config/kimari.profiles.json` | Profile settings |

### User-Managed Data

| Data | Location | Managed By |
|------|----------|-----------|
| Model weights | `models/*.gguf` | User |
| Benchmark results | `benchmarks/results/` | User |
| Conversation history | Web UI (browser storage) | User / Browser |

### Data Deletion

To remove all Kimari data:

```bash
# Stop server
make stop  # or kimari stop

# Remove all data
rm -rf server/kimari.pid server/kimari.log
# Models are separate — user manages them
```

## Model Governance

### Model Security

1. **GGUF Verification** — Recommended to verify model file checksums
2. **Source Verification** — Download models only from trusted sources
3. **Model Isolation** — Models run in a sandboxed inference process
4. **No Arbitrary Code** — Models cannot execute system commands

### Model Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| Malicious model | Model trained to produce harmful outputs | Use models from trusted sources |
| Hallucination | Model generates incorrect information | Always verify important outputs |
| Bias | Model reflects biases in training data | Awareness and monitoring |
| PII leakage | Model may memorize training data | Avoid sensitive data in prompts |

### Recommended Model Sources

1. **Hugging Face (Official orgs)** — Meta, Microsoft, Google, Qwen
2. **TheBloke (quantized)** — Well-known quantized model provider
3. **Bartowski (quantized)** — Popular GGUF quantizations
4. **Official Kimari releases** — When available

### Model Verification

```bash
# Check file size (rough sanity check)
ls -la models/Kimari-4B-Q4_K_M.gguf

# Compare with expected hash (if provided)
sha256sum models/Kimari-4B-Q4_K_M.gguf

# Use GGUF tools to inspect model metadata
gguf-dump models/Kimari-4B-Q4_K_M.gguf | head -20
```

## Responsible AI

### Intended Uses

- Software development assistance
- Technical documentation
- System administration support
- Educational purposes
- Research and experimentation

### Prohibited Uses

- Generating malicious code (malware, exploits)
- Harassment or hate speech generation
- Misinformation or disinformation
- Impersonation of individuals
- Illegal activities
- Automated decision-making affecting humans without oversight

### Limitations Disclosure

Users must be aware that:

1. **Models are not infallible** — Outputs should be verified
2. **No real-time information** — Models don't have internet access
3. **Biases exist** — Training data may contain societal biases
4. **Quality varies** — Smaller models are less capable than large ones
5. **Language limitations** — English and Spanish only; quality varies

## Vulnerability Reporting

If you discover a security vulnerability in Kimari:

1. **Do NOT** open a public GitHub issue
2. Email: security@kimari.ai (when available)
3. Include: description, steps to reproduce, affected version
4. Allow reasonable time for response before public disclosure

### Response Process

1. Acknowledge receipt within 48 hours
2. Assess severity and impact
3. Develop and test fix
4. Release security update
5. Credit reporter (with permission)

## Compliance

### GDPR

Kimari processes no personal data externally. All processing is local on the user's machine. No data controller/data processor relationship exists between Kimari AI and users.

### AI Act (EU)

Kimari provides tools for running AI models locally. Users are responsible for:
- Ensuring their use case complies with applicable regulations
- Not deploying Kimari in high-risk AI applications without appropriate safeguards

### Export Controls

Some AI models may be subject to export controls depending on:
- Model size and capability
- User's jurisdiction
- Intended use

Users are responsible for compliance with applicable export control laws.

## Security Checklist

For users deploying Kimari:

- [ ] Running Kimari on a trusted machine
- [ ] Using models from verified sources
- [ ] Keeping llama.cpp updated (for security patches)
- [ ] Not exposing server to public internet
- [ ] Using firewall rules if on shared network
- [ ] Verifying model file integrity
- [ ] Reviewing outputs before acting on them
- [ ] Not using Kimari for safety-critical decisions

---

*Security is an ongoing process. This document will be updated as new threats and mitigations are identified.*
