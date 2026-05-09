# Privacy Policy

**Last updated:** 2025

---

## Summary

Kimari is a **local-first** AI framework. It does not collect, transmit, or share any personal data. Your prompts, responses, and model files stay on your machine.

---

## Data Collection

**Kimari collects zero data.** Specifically:

| Category | Collected? | Details |
|----------|-----------|---------|
| Telemetry | ❌ No | No usage statistics are sent anywhere. |
| Analytics | ❌ No | No tracking, no pixels, no event logging. |
| Crash reports | ❌ No | No automatic error reporting. |
| Device identifiers | ❌ No | No hardware fingerprinting or unique IDs. |
| IP addresses | ❌ No | No server receives your IP address. |
| Prompts or responses | ❌ No | Conversations are never logged or transmitted by Kimari. |
| System information | ❌ No | Output from `kimari doctor` stays on your machine. |

---

## Network Connections

Kimari makes **only two types of network connections**, both under your direct control:

### 1. Model Downloads (HTTPS to HuggingFace)

When you run `kimari pull`, Kimari downloads GGUF model files from HuggingFace over **HTTPS**. This is the only outbound connection Kimari ever makes.

- The connection is initiated only when you explicitly request a model download.
- HuggingFace can see your IP address and the file you requested as part of normal HTTPS traffic.
- No Kimari-specific identifiers, prompts, or usage data are sent.
- You can inspect the exact URLs in `config/kimari.models.json` before downloading.

### 2. Local API Server

When you run `kimari start`, an OpenAI-compatible API server starts locally:

- **Default binding:** `127.0.0.1:11435` (localhost only — no external access).
- This server handles inference requests from your local applications (CLI, Open WebUI, Continue.dev, etc.).
- No data from this server is forwarded or replicated anywhere.

There are **no other network connections**. Kimari does not phone home, check for updates automatically, or communicate with any cloud service.

---

## Local Data Storage

All data Kimari generates stays on your local machine:

| Data | Location | Purpose |
|------|----------|---------|
| Server PID file | `server/kimari.pid` | Process management |
| Server log | `server/kimari.log` | Debugging (local only) |
| Configuration | `config/kimari.profiles.json`, `config/kimari.models.json` | Profile and model settings |
| Downloaded models | `models/*.gguf` | Inference (user-managed) |

### Log files

Log files (`server/kimari.log`) are written to disk locally and **never transmitted**. They may contain server status messages and error output. They do **not** contain the content of your prompts or model responses. You can delete them at any time:

```bash
rm -f server/kimari.log server/kimari.pid
```

---

## Prompts and Responses

- **Prompts** you send to Kimari and **responses** the model generates are processed entirely in local RAM and VRAM.
- They are **not logged** to disk by Kimari itself.
- They are **not transmitted** to any external server.
- If you use a web interface (e.g., Open WebUI), that interface may store conversation history in its own database or browser storage. See the [Docker / Open WebUI](#docker--open-webui) section below.

---

## Docker / Open WebUI

Kimari optionally integrates with [Open WebUI](https://github.com/open-webui/open-webui) via Docker for a full-featured web chat interface. **Open WebUI is a third-party project with its own privacy policy.**

Key points:

- Open WebUI runs in its own Docker container and stores data in a Docker volume (`open-webui-data`).
- Conversation history, user accounts, and settings are managed by Open WebUI, not by Kimari.
- Open WebUI may have different data handling practices. **Review [Open WebUI's privacy policy](https://github.com/open-webui/open-webui) before use.**
- The Docker container communicates with Kimari's local API over `host.docker.internal`. This traffic stays on your machine.
- Kimari has no access to, and does not control, data stored within the Open WebUI container.

---

## Third-Party Models

When you download models using `kimari pull`, the files come from HuggingFace repositories operated by third parties (e.g., Qwen, TheBloke, HuggingFaceTB). Each model is governed by its own license and terms — see `MODEL_LICENSES.md` for details.

Kimari does not modify model behavior or inject any data collection into model inference. What the model does with your input is determined solely by the model weights you chose to run.

---

## Data Deletion

To remove all Kimari-generated data from your machine:

```bash
# Stop the server
kimari stop

# Remove logs and PID files
rm -f server/kimari.log server/kimari.pid

# Remove downloaded models (optional — these are large files)
rm -rf models/*.gguf

# Remove Docker data (if using Open WebUI)
docker volume rm kimari-local-ai_open-webui-data
```

---

## Changes to This Policy

If Kimari's privacy practices change in the future, this document will be updated accordingly. Any change that introduces new data collection will be clearly disclosed.

---

## Contact

For privacy-related questions, contact: [smouj013@users.noreply.github.com](mailto:smouj013@users.noreply.github.com)
