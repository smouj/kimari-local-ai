# Reverse Proxy Authentication

> **⚠️ Important:** `llama-server` does **NOT** apply the Kimari token natively. The token is intended for use with a reverse proxy or the future Kimari API. Without a reverse proxy enforcing it, the token has no effect.

---

## Intended Use

- Use **nginx** or **Caddy** as a reverse proxy in front of `llama-server`.
- Kimari binds to `127.0.0.1` (recommended) — the proxy exposes the service to your network.
- **Never** expose `0.0.0.0` publicly without authentication.

---

## Token Setup

Generate and inspect a Bearer token with the CLI:

```bash
# Generate a new token
kimari token create

# Display the current token
kimari token show
```

The token is stored in the user state directory and persists across restarts.

---

## nginx Example

```nginx
server {
    listen 8080;
    server_name _;

    # Reject anything without the correct Bearer token
    if ($http_authorization != "Bearer <YOUR_TOKEN>") {
        return 401;
    }

    location / {
        proxy_pass http://127.0.0.1:11435;

        # Standard proxy headers
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE / streaming support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }
}
```

> **Note:** Replace `<YOUR_TOKEN>` with the actual token from `kimari token show`.

---

## Caddy Example

```Caddyfile
:8080 {
    # Token-based auth — check the Authorization header
    @authnot header Authorization !Bearer <YOUR_TOKEN>
    respond @authnot 401

    reverse_proxy 127.0.0.1:11435
}
```

Caddy handles TLS automatically when you use a domain name instead of a bare port. For example:

```Caddyfile
ai.example.com {
    @authnot header Authorization !Bearer <YOUR_TOKEN>
    respond @authnot 401

    reverse_proxy 127.0.0.1:11435
}
```

> **Note:** Caddy will provision a certificate via Let's Encrypt automatically. Replace `<YOUR_TOKEN>` with the output of `kimari token show`.

---

## Trusted Local Network

If you are on a fully trusted LAN and certain no untrusted device can reach the service, you may skip authentication. However:

- Still bind to `127.0.0.1` and use a proxy to control access.
- **Never** expose `0.0.0.0` publicly without auth.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| **401 Unauthorized** | Token mismatch between client and proxy config | Run `kimari token show` and update the proxy config / client header |
| **Connection refused** | Kimari is not running | Run `kimari status` and start the service if needed |
| **502 Bad Gateway** | Proxy pointing to wrong port | Default port is `11435` — verify `proxy_pass` / `reverse_proxy` target |
| **CORS errors** | Browser blocking cross-origin requests | Add `Access-Control-Allow-*` headers in the proxy config |

---

*This is an alpha-stage project. The authentication model will evolve — expect changes before a stable release.*
