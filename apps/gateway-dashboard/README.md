# Kimari Gateway Dashboard

Real-time dashboard for managing and monitoring a local Kimari AI gateway — GPU profiles, models, benchmarks, system resources, and integrations.

## Quick Start (CLI-first)

Install Kimari and manage the dashboard through the CLI:

```bash
curl -fsSL https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.sh | bash
kimari console
kimari gateway setup
kimari gateway start --open
```

Open **http://127.0.0.1:3105** in your browser. The dashboard binds to localhost by default; public bind requires an explicit `--allow-public-bind` flag.

## Development only (npm)

```bash
# 1. Install dependencies
npm install

# 2. Set up the database (SQLite, no external DB needed)
npm run db:setup

# 3. Build for production
npm run build

# 4. Start
npm start
```

## Development commands

```bash
npm run dev        # Hot-reload dev server on port 3105
npm run lint       # ESLint check
npm run build      # Production build
npm start          # Production server bound to 127.0.0.1
```

## What You'll See

- **Dashboard** — Server status, metrics, resource gauges (CPU/RAM/VRAM/GPU Temp), quick launcher
- **Profiles** — GPU profiles optimized for your hardware
- **Models** — Available GGUF models with download status
- **Doctor** — System diagnostic checks (Python, GPU, llama-server, Ollama)
- **Integrations** — Live status of connected services
- **Analytics** — Benchmark history and logs
- **Chat** — Direct chat via Ollama or llama-server backend

## Requirements

- **Node.js** 20.9+ and npm (Next.js 16 requires Node 20.9+)
- **Ollama** (optional, for chat — runs on port 11434)
- **llama-server** from llama.cpp (optional, for direct inference — port 11435)
- **NVIDIA GPU** with CUDA (for GPU-accelerated inference)

## Troubleshooting

### Node.js version too old

If `kimari gateway setup` fails with Node.js errors, ensure you have Node.js 20.9 or newer:

```bash
node --version   # must be >= 20.9.0
```

If your system Node is too old, use [nvm](https://github.com/nvm-sh/nvm) or [fnm](https://github.com/Schniz/fnm) to install a recent version. Kimari's `gateway setup` will attempt to use the system Node automatically.

The dashboard works standalone — it reads real system data and probes services automatically. No gateway needs to be running to explore the UI.

## Project Structure

```
apps/gateway-dashboard/
├── prisma/           # SQLite database schema + seed
├── src/
│   ├── app/          # Next.js App Router (pages + API routes)
│   ├── components/   # React UI components
│   ├── hooks/        # Data fetching hooks (use-api.ts)
│   └── lib/          # Prisma client, Zustand store, utils
├── public/           # Static assets (logos)
└── package.json
```

## Notes

- This is an isolated Next.js sub-app. Normal users should manage it through `kimari gateway ...`.
- Database is SQLite (`prisma/dev.db`) — created automatically on `npm run db:setup`.
- Do not commit `.env`, `.next/`, `node_modules/`, or DB files.
- Kimari-4B is **not released**. Gate is **BLOCKED** until public release — no weights, GGUF, or benchmark claims.
- Local only by default: `127.0.0.1:3105`.
