# Kimari Web, PWA & Desktop

## Document: 00-06 Web PWA & Desktop Application
**Version:** 0.1.0
**Status:** Planning
**Last Updated:** 2025

---

## Overview

Kimari currently provides a CLI and API interface. This document outlines the planned Progressive Web App (PWA) and Desktop application for a more accessible user experience.

## Current Solution: Open WebUI

For immediate web access, Kimari integrates with [Open WebUI](https://github.com/open-webui/open-webui), an open-source web interface for LLMs.

### Setup

```bash
# Start Kimari server
make start-1060

# Launch Open WebUI with Docker
docker compose -f docker/docker-compose.open-webui.yml up -d
```

Open WebUI provides:
- Chat interface with conversation history
- Model selection
- Temperature and parameter controls
- Document upload for RAG
- User authentication
- Multi-model support

### Configuration

Open WebUI connects to Kimari's OpenAI-compatible API:

```
API Base URL: http://127.0.0.1:11435/v1
API Key: (not required for local use)
```

---

## Planned: Kimari PWA

### Concept

A lightweight Progressive Web App that provides a focused, Kimari-optimized chat experience without the overhead of Docker or a full web framework.

### Features

1. **Chat Interface** — Clean, responsive chat UI
2. **Profile Switcher** — Switch between GPU profiles
3. **Real-time Streaming** — Token-by-token response display
4. **Conversation History** — Local storage-based history
5. **Settings Panel** — Temperature, top-p, max tokens
6. **Model Info** — Show loaded model, context remaining
7. **Benchmark UI** — Run and display benchmarks visually
8. **KimariFit Display** — Show hardware fit score
9. **Offline Support** — Service worker for full offline use
10. **Installable** — "Add to Home Screen" on any device

### Technical Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Frontend | Vanilla JS / Lit | Minimal bundle, no build step |
| Styling | Tailwind CSS | Rapid prototyping, utility-first |
| Icons | Lucide Icons | Clean, consistent icon set |
| Storage | IndexedDB | Conversation history, settings |
| Service Worker | Workbox | Offline caching, updates |
| API | Fetch API | Native, no dependencies |
| Streaming | SSE (EventSource) | Real-time token streaming |

### File Structure (Planned)

```
web/
├── index.html
├── manifest.json
├── sw.js                    # Service worker
├── css/
│   └── styles.css           # Tailwind output
├── js/
│   ├── app.js               # Main application
│   ├── api.js               # Kimari API client
│   ├── chat.js              # Chat UI logic
│   ├── settings.js          # Settings management
│   └── storage.js           # IndexedDB wrapper
└── assets/
    ├── icon-192.png
    ├── icon-512.png
    └── favicon.svg
```

### API Integration

The PWA communicates with Kimari's OpenAI-compatible API:

```javascript
// Chat completion
const response = await fetch('http://127.0.0.1:11435/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'Kimari-4B-Q4_K_M',
    messages: conversationHistory,
    stream: true,
    max_tokens: 1024,
    temperature: 0.7,
  }),
});

// Stream tokens
const reader = response.body.getReader();
const decoder = new TextDecoder();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value);
  // Parse SSE data and display tokens
}
```

### Responsive Design

- **Mobile** (< 640px): Single column, full-screen chat
- **Tablet** (640–1024px): Chat + sidebar toggle
- **Desktop** (> 1024px): Chat + sidebar + settings panel

### PWA Manifest

```json
{
  "name": "Kimari Local AI",
  "short_name": "Kimari",
  "description": "Local AI for Consumer GPUs",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#3b82f6",
  "icons": [
    { "src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

---

## Planned: Kimari Desktop (Tauri)

### Concept

A native desktop application built with Tauri for deeper OS integration, better performance, and native features.

### Why Tauri?

| Factor | Tauri | Electron |
|--------|-------|----------|
| Bundle size | ~5 MB | ~150 MB |
| Memory usage | ~50 MB | ~200 MB |
| Native feel | Yes (webview) | No (Chromium) |
| Auto-updates | Built-in | Requires extra tooling |
| System tray | Built-in | Requires library |
| File system | Full access (Rust) | Limited (Node) |
| Kimari integration | Direct (Rust bindings) | HTTP API only |

### Features Beyond PWA

1. **System Tray** — Minimize to tray, background running
2. **Auto-start** — Start Kimari server on system boot
3. **Global Hotkey** — Activate Kimari from any app
4. **File Operations** — Drag-and-drop file analysis
5. **Clipboard Integration** — Quick text processing
6. **Native Notifications** — OS notification for long tasks
7. **GPU Monitor** — Real-time VRAM/CPU usage overlay
8. **Model Manager** — Download and manage GGUF files
9. **Auto-updates** — Update Kimari desktop seamlessly
10. **Deep CLI Integration** — Run CLI commands from the UI

### Architecture

```
┌─────────────────────────────────────────┐
│          Tauri Application              │
│  ┌───────────────────────────────────┐  │
│  │        Frontend (WebView)         │  │
│  │  HTML + CSS + TypeScript          │  │
│  │  (Same UI as PWA, enhanced)       │  │
│  └───────────────┬───────────────────┘  │
│                  │ Tauri Commands       │
│  ┌───────────────┴───────────────────┐  │
│  │        Backend (Rust)             │  │
│  │  ┌──────────┐  ┌──────────────┐  │  │
│  │  │ Server   │  │   Model      │  │  │
│  │  │ Manager  │  │   Manager    │  │  │
│  │  └──────────┘  └──────────────┘  │  │
│  │  ┌──────────┐  ┌──────────────┐  │  │
│  │  │ System   │  │   Config     │  │  │
│  │  │ Tray     │  │   Manager    │  │  │
│  │  └──────────┘  └──────────────┘  │  │
│  └───────────────────────────────────┘  │
│         ▲                              │
│         │ llama.cpp (C FFI)            │
└─────────┼──────────────────────────────┘
          │
          ▼
    NVIDIA GPU
```

### Roadmap

| Phase | Deliverable | Timeline |
|-------|-------------|----------|
| v0.1 | Open WebUI integration | Current |
| v0.2 | Basic PWA (chat + settings) | Q3 2025 |
| v0.3 | PWA with offline support | Q4 2025 |
| v0.5 | Tauri desktop alpha | Q1 2026 |
| v1.0 | Tauri desktop stable + PWA | Q2 2026 |

---

## Design Mockups

### Chat Interface (Planned)

```
┌──────────────────────────────────────────────┐
│  Kimari                    [gtx1060] [⚙️]    │
├──────────────────────────────────────────────┤
│                                              │
│  User:  Write a Python function to sort a    │
│          list of dictionaries by a key       │
│                                              │
│  Kimari: Here's a function that sorts a list │
│  of dictionaries by a specified key:         │
│                                              │
│  ```python                                   │
│  def sort_dicts(items, key):                 │
│      return sorted(items, key=lambda x: x[key])│
│  ```                                         │
│                                              │
│  [copy] [retry]                              │
│                                              │
├──────────────────────────────────────────────┤
│  [Type your message...          ] [Send ➤]   │
│                                              │
│  KimariFit: 97  |  Context: 6,234/8,192     │
└──────────────────────────────────────────────┘
```

---

*This document will be updated as development progresses.*
