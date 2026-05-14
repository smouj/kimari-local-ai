# Gateway Dashboard CLI

The Gateway Dashboard is managed through the Kimari CLI. Normal users should not need to run npm manually.

## Setup

```bash
kimari gateway setup
```

This checks that `apps/gateway-dashboard` exists, verifies Node/npm are installed, then runs:

```text
npm install
npm run db:setup
npm run build
```

Kimari does **not** install Node/npm globally. If Node is missing, it prints instructions and exits.

## Start

```bash
kimari gateway start --open
```

Default bind is `127.0.0.1:3105`. Non-local bind requires explicit acknowledgement:

```bash
kimari gateway start --host 0.0.0.0 --allow-public-bind
```

## Other commands

```bash
kimari gateway status
kimari gateway logs
kimari gateway stop
kimari gateway restart
kimari gateway reset --yes
```

## Dry-run / JSON

```bash
kimari gateway setup --dry-run --json
kimari gateway start --dry-run --json
```

Kimari-4B is not released. Gate remains **BLOCKED**.
