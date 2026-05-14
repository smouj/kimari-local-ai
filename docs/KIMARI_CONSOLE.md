# Kimari Console

`kimari console` is the CLI home screen for Kimari.

```bash
kimari console
```

It shows:

- Kimari version
- GPU name and VRAM when detected
- CUDA status
- Test model availability
- Local API status
- Gateway dashboard status
- Gate: **BLOCKED**
- Kimari-4B: **not released**

## Non-interactive status

```bash
kimari console --json
kimari console --no-interactive
```

## Menu

```text
[1] Run doctor
[2] Setup/write config
[3] Download test model
[4] Start local API
[5] Stop local API
[6] Gateway setup
[7] Gateway start/open
[8] Generate integrations
[9] Exit
```

Destructive or external-impacting actions require confirmation. No models are downloaded unless you choose the download action.
