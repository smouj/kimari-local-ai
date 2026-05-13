# Kimari Flow Diagram

```mermaid
flowchart LR
    User[User] --> CLI[Kimari CLI]
    CLI --> Resolver[GPU profile resolver]
    Resolver --> Llama[llama.cpp CUDA]
    Llama --> Endpoint[Local OpenAI-compatible endpoint]
    Endpoint --> OpenWebUI[Open WebUI]
    Endpoint --> OpenClaw[OpenClaw]
    Endpoint --> Continue[Continue.dev]
```

## Notes

- The endpoint is local by default: `http://127.0.0.1:11435/v1`.
- Kimari runs compatible GGUF models through llama.cpp.
- Kimari-4B is not released yet.
- Gate: **BLOCKED**.
