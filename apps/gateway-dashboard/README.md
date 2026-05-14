# Kimari Gateway Dashboard

Experimental Next.js dashboard for managing and observing a local Kimari gateway.

## Status

- Scope: dashboard UI only; the Python Kimari CLI/runtime remains in the repository root.
- Integration strategy: isolated sub-app under `apps/gateway-dashboard/` to avoid replacing or breaking the existing Kimari package, docs, CI, benchmarks, or release workflow.
- Theme: blue/gray professional palette using OKLCH hue 230.
- Branding: uses real Kimari logos from `docs/assets/` / `public/`.

## Features

- Dashboard overview, server status, profiles, models, logs, analytics, benchmarks, settings.
- Real Kimari logo in layout/sidebar/setup wizard.
- Keyboard shortcuts help dialog (`?`).
- Mobile responsive sidebar using sheet overlay.
- Logs export to JSON/CSV from currently loaded log entries.
- Blue/gray rebrand replacing the previous teal/green accent system.
- Round 13 polish: standardized blue/sky/amber/emerald badges, larger status chip, profile/model/integration card consistency, doctor view polish, animated metric cards, gradient welcome banner, breathing architecture arrows.
- System resources monitor: four circular SVG gauges for CPU, RAM, VRAM, and GPU temperature with 5s refresh and threshold colors.
- QuickLauncher widget: Start Server, Run Benchmark, System Check, and Download Model action cards.

## Local development

```bash
cd apps/gateway-dashboard
npm install
npm run lint
npm run build
npm run dev
```

The app runs on Next.js and is intentionally isolated from the root Python package. Do not move root Kimari CLI files into this app.

For API routes backed by Prisma during local smoke tests:

```bash
DATABASE_URL='file:./dev.db' npx prisma db push
DATABASE_URL='file:./dev.db' npx prisma db seed
```

## Screenshots

Screenshots for the current blue/gray UI pass are stored in:

```text
docs/assets/screenshots/gateway-dashboard/
```

They are referenced from the root `README.md` so project visitors can preview the dashboard without changing the existing CLI-first documentation structure.

## Safety notes

- Do not commit `.env`, `.next/`, `node_modules/`, or runtime DB dumps.
- Keep this app behind localhost/auth when connected to a real gateway.
- Public benchmark or model-performance claims still require verified KimariEval/benchmark evidence.
