# Gateway Dashboard

Kimari includes a local Gateway Dashboard for monitoring and managing your local AI environment.

## Quick Start

```bash
kimari gateway setup          # Install dashboard dependencies, setup SQLite, build
kimari gateway start --open   # Start local dashboard at 127.0.0.1:3105
```

## CLI Lifecycle

```bash
kimari gateway setup          # Install deps, setup SQLite, build
kimari gateway start --open   # Start and open in browser
kimari gateway start          # Start without opening browser
kimari gateway status         # Check if dashboard is running
kimari gateway status --json  # JSON status output
kimari gateway logs           # View dashboard logs
kimari gateway logs --lines 50  # View last 50 lines
kimari gateway stop           # Stop dashboard
kimari gateway restart        # Restart dashboard
kimari gateway reset          # Reset dashboard state
kimari gateway open           # Open dashboard in browser
```

## Dashboard Features

The dashboard shows:

- **Overview** — Local runtime status, GPU info, quick actions
- **Server** — Running model, endpoint status, process info
- **Analytics** — Performance metrics and usage statistics
- **Profiles** — GPU profile configuration and selection
- **Integrations** — Open WebUI, Continue.dev, OpenClaw, Hermes config
- **Logs** — Real-time dashboard and server logs
- **Chat** — Experimental chat playground
- **Gate** — Release gate status (currently BLOCKED)

## Architecture

The dashboard is implemented as an isolated Next.js sub-app under [`apps/gateway-dashboard/`](../apps/gateway-dashboard/).

It is managed through the Kimari Python CLI. **Users should not need to run `npm` manually** for normal operation.

The management Gateway API remains planned at `127.0.0.1:11436`. `kimari gateway --plan --json` shows the API design.

## Security Defaults

| Setting | Default |
|---|---|
| Host | `127.0.0.1` |
| Public bind | Disabled |
| Mode | Local preview |
| Gate | `BLOCKED` |
| Tokens in UI | No |
| Public model upload | No |

## Safety Note

Kimari-4B is not released. Gate state remains **BLOCKED**. The dashboard binds to `127.0.0.1` by default and does not publish models, weights, or benchmarks.

## Developer Setup

For contributors working on the dashboard itself:

```bash
cd apps/gateway-dashboard
npm install
npm run dev
```

This is for development only. Normal users should use `kimari gateway setup` and `kimari gateway start`.

## Related Docs

- [Gateway Plan](GATEWAY_PLAN.md) — Full gateway architecture and API plan
- [Gateway Prototype Plan](GATEWAY_PROTOTYPE_PLAN.md) — Phased evolution from dry-run to full local controller
- [Gateway Dashboard CLI](GATEWAY_DASHBOARD_CLI.md) — CLI command details
