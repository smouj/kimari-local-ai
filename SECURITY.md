# Security Policy

## Local-First Design

Kimari is a **local-first** project. By default, it does **not** send any data to the cloud. All inference, prompt processing, and response generation happen entirely on your machine. The only network connections Kimari makes are:

- **Model downloads** over HTTPS from HuggingFace (only when you run `kimari pull`)
- **The local API server** bound to `127.0.0.1:11435` by default

There is no telemetry, no analytics, no phone-home, and no remote logging.

---

## Risks of Opening Ports (`0.0.0.0`)

By default, Kimari's API server binds to `127.0.0.1` (localhost only), meaning only applications on your own machine can reach it.

Some configurations — such as the `docker` profile or the `--host 0.0.0.0` override — bind the server to all network interfaces. **This exposes the API to every device on your local network, and potentially the public internet.**

### Why this is dangerous

| Risk | Description |
|------|-------------|
| **Unauthenticated access** | Kimari does not implement API key authentication or user accounts. Anyone who can reach the port can send prompts and read responses. |
| **Prompt injection from the network** | Other machines on the same network can submit arbitrary prompts to your model, potentially extracting information from the conversation context. |
| **Resource abuse** | Remote users can saturate your GPU, consume VRAM, and degrade or crash the server. |
| **Lateral movement** | On compromised or shared networks, an open Kimari instance can be used as a stepping stone by attackers. |
| **Data exposure** | If you are working with sensitive prompts or data in the conversation context, other users on the network could read them. |

### How to mitigate

- **Do not bind to `0.0.0.0` on public or untrusted networks.**
- If you must expose Kimari on a LAN (e.g., for Open WebUI via Docker), use firewall rules to restrict access to trusted IPs only.
- Place a reverse proxy (nginx, Caddy) in front with HTTPS and authentication.
- Never expose Kimari directly to the public internet without proper access controls.

```bash
# Restrict access to a single trusted IP (example)
sudo ufw allow from 192.168.1.50 to any port 11435
sudo ufw deny 11435/tcp
```

---

## Risks of Downloading Models from Third Parties

Kimari downloads GGUF model files from HuggingFace repositories. While HuggingFace is a well-known platform, you should be aware of the following risks:

| Risk | Description |
|------|-------------|
| **Supply chain compromise** | A model repository could be compromised and serve a different (malicious) file than expected. |
| **Mislabelled models** | A file may claim to be one model but actually be another — potentially one trained to produce harmful or misleading outputs. |
| **No authenticity guarantee** | Anyone can publish a model on HuggingFace. The platform does not cryptographically verify that a model behaves as described. |
| **Model backdoors** | A model could be trained to produce specific outputs when triggered by certain prompts (backdoor attacks). |
| **License violations** | A third-party upload may redistribute model weights in violation of the original license. |

### Recommendations

- Prefer models from **official organizations** (e.g., `Qwen`, `HuggingFaceTB`, `meta-llama`).
- Use well-known quantizers (e.g., `TheBloke`, `Bartowski`) when you need pre-quantized GGUF files.
- Always verify model hashes (see below).
- Treat model outputs with the same skepticism you would apply to any unverified information source.

---

## Model Hash Verification

Verifying the SHA-256 hash of a downloaded model file ensures it matches the expected file and has not been tampered with.

### Step-by-step

1. **Find the expected hash.** Check the model's HuggingFace repository page or the model card for a published SHA-256 checksum. If the publisher provides an integrity file, download it.

2. **Compute the hash of your downloaded file:**

   ```bash
   # Linux / macOS
   sha256sum models/qwen3-4b-q4_k_m.gguf

   # Windows (PowerShell)
   Get-FileHash models\qwen3-4b-q4_k_m.gguf -Algorithm SHA256
   ```

3. **Compare the hashes.** The output must match the published checksum exactly. If it does not match, **do not use the file** — delete it and re-download.

4. **Automated verification (optional).** If a checksum is listed in `config/kimari.models.json` under the `sha256` field, `kimari pull` will verify it automatically after download. Note that not all models have pre-populated hashes; for those that do not, manual verification is recommended.

### Quick sanity checks

Even without a published hash, you can detect obvious tampering:

```bash
# Check that the file size is plausible
ls -la models/qwen3-4b-q4_k_m.gguf

# Inspect GGUF metadata
python -c "
from gguf import GGUFReader
reader = GGUFReader('models/qwen3-4b-q4_k_m.gguf')
for field in reader.fields.values():
    print(field)
"
```

---

## Reporting Vulnerabilities

If you discover a security vulnerability in Kimari, please report it responsibly:

- **Email:** [smouj013@users.noreply.github.com](mailto:smouj013@users.noreply.github.com)
- **Do NOT** open a public GitHub issue for security vulnerabilities.

Please include the following in your report:

1. A description of the vulnerability
2. Steps to reproduce
3. The affected version
4. Any potential impact

We will acknowledge receipt within 48 hours and work toward a fix. We ask that you allow reasonable time for remediation before public disclosure.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest alpha (v0.1.x) | ✅ Yes |
| Any older alpha | ❌ No |
| Pre-release / development builds | ❌ No |

Only the **latest alpha release** receives security updates. We strongly recommend always running the most recent version.

---

## Optional API Authentication (Future)

Kimari currently has **no API authentication** for the local llama-server endpoint (`http://127.0.0.1:11435/v1`). This is acceptable for local-only use where the server binds to `127.0.0.1` (localhost), since only applications on your own machine can reach it.

However, **this is not acceptable for network-exposed setups**. If you bind Kimari to `0.0.0.0` or expose it on a LAN/WAN, anyone who can reach the port has full, unauthenticated access to the API (see [Risks of Opening Ports](#risks-of-opening-ports-0000) above).

### Planned: `kimari api` command (v0.2)

A future `kimari api` command (planned for v0.2) will add optional **Bearer token authentication** to the llama-server endpoint. This will allow you to require an API key for all requests, making it safe to expose the server on a trusted network.

The plan is documented in [`docs/WEB_UI_PLAN.md`](docs/WEB_UI_PLAN.md).

### Workaround: Reverse proxy

Until built-in authentication is available, users who need to expose the API on a network should place a **reverse proxy** (nginx, Caddy, etc.) in front of Kimari. The reverse proxy can handle:

- **TLS/HTTPS** — Encrypt traffic between clients and the server.
- **Authentication** — HTTP Basic Auth, Bearer tokens, or OAuth2 via the proxy.
- **Access control** — IP allowlists, rate limiting, etc.

Example nginx configuration:

```nginx
server {
    listen 443 ssl;
    server_name kimari.example.com;

    ssl_certificate     /etc/nginx/ssl/kimari.crt;
    ssl_certificate_key /etc/nginx/ssl/kimari.key;

    location /v1/ {
        # Require HTTP Basic Auth
        auth_basic "Kimari API";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_pass http://127.0.0.1:11435;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

> **Important:** Even with a reverse proxy, keep Kimari bound to `127.0.0.1` and let the proxy handle external connections.

---

## Security Best Practices

When using Kimari, follow these practices to minimize risk:

1. **Keep Kimari and llama.cpp up to date.** Security patches are included in new releases.
2. **Bind to localhost only** (`127.0.0.1`) unless you have a specific reason to do otherwise and understand the risks.
3. **Use a firewall** if you must expose the API on a LAN. Restrict access to trusted hosts only.
4. **Verify model hashes** after downloading. Do not run unverified model files.
5. **Download models only from trusted sources** — official HuggingFace organizations or well-known quantizers.
6. **Do not run Kimari as root or Administrator.** It is designed to work as an unprivileged user.
7. **Review model outputs** before acting on them. Models can hallucinate or generate insecure code.
8. **Do not submit sensitive or classified data** to any model unless you fully understand and accept the local storage implications.
9. **Secure your local machine.** Disk encryption, OS updates, and strong authentication protect your model files and conversation data.
10. **Inspect configuration changes.** Before applying third-party profile overrides or config modifications, review them for unexpected host or port bindings.
