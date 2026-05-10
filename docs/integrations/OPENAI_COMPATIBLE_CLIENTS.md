# OpenAI-Compatible Client Integration

Kimari exposes a standard OpenAI-compatible API that works with any client supporting the OpenAI Chat Completions format.

## Endpoint

```
http://127.0.0.1:11435/v1
```

## Quick Verification

### List Models

```bash
curl http://127.0.0.1:11435/v1/models
```

### Chat Completion

```bash
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimari",
    "messages": [{"role": "user", "content": "Hello, Kimari!"}],
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

## Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:11435/v1",
    api_key="kimari-local"
)

response = client.chat.completions.create(
    model="kimari",
    messages=[{"role": "user", "content": "Hello, Kimari!"}],
    temperature=0.7,
    max_tokens=512
)

print(response.choices[0].message.content)
```

## Node.js

```javascript
const response = await fetch("http://127.0.0.1:11435/v1/chat/completions", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "kimari",
    messages: [{ role: "user", content: "Hello, Kimari!" }],
    temperature: 0.7,
    max_tokens: 512
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

## Open WebUI

Open WebUI connects automatically when Kimari is started with the Docker profile:

```bash
kimari start --profile docker --daemon
```

Then configure Open WebUI to point to `http://host.docker.internal:11435/v1` or the appropriate Docker network address.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Connection refused | Server not running | Run `kimari start` |
| Model not found | No GGUF in models/ | Run `kimari pull test` |
| llama-server missing | Not built or not in PATH | Run `bash scripts/linux/build-llamacpp-cuda.sh` or set `LLAMA_SERVER` |
| 404 on endpoint | Wrong URL path | Use `/v1/chat/completions`, not `/chat/completions` |
| Timeout | Local inference is slow | Increase timeout; try `kimari optimize` for faster settings |
| Slow response | Large model or context | Use `kimari optimize` to find better settings for your GPU |

## Security Notes

- **Never expose on 0.0.0.0** unless you understand the risks. Use `127.0.0.1` for local-only access.
- **No authentication** by default. If you need auth, use an nginx reverse proxy with basic auth.
- **API key is a placeholder**. Kimari does not validate API keys.
