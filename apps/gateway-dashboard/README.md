# Kimari Gateway Dashboard

Real-time dashboard for managing and monitoring a local Kimari AI gateway — GPU profiles, models, benchmarks, system resources, and integrations.

## Quick Start

```bash
cd apps/gateway-dashboard

# One-command setup (install + DB + build)
npm run setup

# Start the dashboard
npm start
```

Open **http://localhost:3105** in your browser.

## Manual Setup

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

## Development

```bash
npm run dev        # Hot-reload dev server on port 3105
npm run lint       # ESLint check
npm run build      # Production build
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

- **Node.js** 18+ and npm
- **Ollama** (optional, for chat — runs on port 11434)
- **llama-server** from llama.cpp (optional, for direct inference — port 11435)
- **NVIDIA GPU** with CUDA (for GPU-accelerated inference)

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

- This is an isolated Next.js sub-app. The Kimari Python CLI lives in the repository root.
- Database is SQLite (`prisma/dev.db`) — created automatically on `npm run db:setup`.
- Do not commit `.env`, `.next/`, `node_modules/`, or DB files.
- Model gate is **BLOCKED** until public release — no weights, GGUF, or benchmark claims.
