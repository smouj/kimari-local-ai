# Kimari One-Command Install

Kimari is designed so normal users do not need to run npm manually or navigate internal folders.

## Linux / WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.sh | bash
kimari console
```

Optional flags:

```bash
curl -fsSL https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.sh | bash -s -- --with-dashboard --with-test-model --yes
```

- `--with-test-model` downloads the small test model. Models are never downloaded by default.
- `--with-dashboard` runs `kimari gateway setup`.
- `--dry-run` previews actions.
- Default network binds stay on `127.0.0.1`.

## Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.ps1 | iex
```

The installer verifies Python 3.10+ and Git, creates a virtual environment, installs Kimari, writes initial config, and prints next steps.

## Next

```bash
kimari console
kimari doctor --deep
kimari pull test
kimari start
kimari gateway start --open
```

Kimari-4B is not released. Gate remains **BLOCKED**.
