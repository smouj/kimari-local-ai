import { createServer } from 'http'
import { Server } from 'socket.io'

const httpServer = createServer()
const io = new Server(httpServer, {
  path: '/',
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
  pingTimeout: 60000,
  pingInterval: 25000,
})

// --- Log generation types and data ---

type LogLevel = 'info' | 'warn' | 'error' | 'debug'
type LogSource = 'gateway' | 'server' | 'system' | 'benchmark'

interface LogEntry {
  id: string
  level: LogLevel
  source: LogSource
  message: string
  metadata: string | null
  createdAt: string
}

const generateId = (): string =>
  Math.random().toString(36).substring(2, 11) + Date.now().toString(36)

// Level distribution: info 70%, warn 20%, error 8%, debug 2%
function randomLevel(): LogLevel {
  const r = Math.random()
  if (r < 0.02) return 'debug'
  if (r < 0.10) return 'error'
  if (r < 0.30) return 'warn'
  return 'info'
}

// Source distribution: gateway 40%, server 35%, system 15%, benchmark 10%
function randomSource(): LogSource {
  const r = Math.random()
  if (r < 0.10) return 'benchmark'
  if (r < 0.25) return 'system'
  if (r < 0.60) return 'server'
  return 'gateway'
}

// Realistic Kimari gateway messages organized by (level, source)
const messageTemplates: Record<string, string[]> = {
  // Gateway messages
  'info+gateway': [
    'Request processed: {tokens} tokens generated in {time}s',
    'Context window expanded to {ctx} tokens',
    'Cache hit ratio: {cache}%',
    'Profile switch requested: {profile}',
    'API request forwarded to llama.cpp backend',
    'Session resumed: 3 active conversations',
    'Gateway middleware chain completed in {latency}ms',
    'Request routed to model: {model}',
    'Streaming response started for session {session}',
    'Gateway health check: all systems nominal',
  ],
  'warn+gateway': [
    'Warning: GPU temperature approaching threshold ({temp}°C)',
    'Warning: Context length nearing limit ({used}/{max} tokens)',
    'Warning: Cache eviction rate increasing: {rate}%',
    'Warning: Request queue depth at {depth}',
    'Warning: Memory pressure detected, consider reducing context',
  ],
  'error+gateway': [
    'Error: Request timeout after 30s',
    'Error: Failed to connect to llama.cpp backend',
    'Error: Model inference failed — retrying...',
    'Error: Gateway middleware exception: rate limit exceeded',
  ],
  'debug+gateway': [
    'Debug: Token probability distribution logged',
    'Debug: Gateway routing table refreshed',
  ],

  // Server messages
  'info+server': [
    'Model loaded: {model}',
    'VRAM usage: {vram}GB / {vramTotal}GB ({vramPct}%)',
    'Server metrics: {rps} req/s, {latency}ms avg latency',
    'llama.cpp backend: {threads} threads active',
    'Batch processing: {batch} requests in {batchTime}ms',
    'KV cache utilization: {kvUsed}/{kvTotal} cells',
    'Model warmup complete: ready for inference',
    'Token generation speed: {tokPerSec} tok/s',
  ],
  'warn+server': [
    'Warning: VRAM usage above 85% — consider smaller context',
    'Warning: Inference latency spike detected ({latency}ms)',
    'Warning: Model swap may be required for requested context length',
  ],
  'error+server': [
    'Error: Out of memory — reduce context size or batch count',
    'Error: Model file corrupted, re-download required',
    'Error: Server process crashed — attempting restart',
  ],
  'debug+server': [
    'Debug: llama.cpp internal state dump captured',
  ],

  // System messages
  'info+system': [
    'Integration heartbeat: {integration} connected',
    'System resource check: CPU {cpu}%, RAM {ram}%, GPU {gpu}%',
    'Configuration updated: {config} applied',
    'Scheduled maintenance window starting in 2 hours',
    'Auto-save checkpoint created at {checkpoint}',
    'Background task completed: model quantization scan',
  ],
  'warn+system': [
    'Warning: Disk space below 10% on /data partition',
    'Warning: High swap usage detected ({swap}MB)',
    'Warning: System clock drift detected: {drift}ms',
  ],
  'error+system': [
    'Error: Disk I/O error on model storage volume',
    'Error: NVIDIA driver communication lost',
  ],
  'debug+system': [
    'Debug: System call trace captured for profiling',
  ],

  // Benchmark messages
  'info+benchmark': [
    'Benchmark started: {model} with pp={pp}, tg={tg}, pl={pl}',
    'Benchmark result: TTFT={ttft}ms, tok/s={tokPerSec}',
    'Benchmark phase complete: prompt processing in {ppTime}ms',
    'Benchmark score: {score} tokens/second (Q4_K_M)',
    'Benchmark complete: {model} scored {grade}',
  ],
  'warn+benchmark': [
    'Warning: Benchmark results may be unreliable due to thermal throttling',
    'Warning: Benchmark interrupted — system under load',
  ],
  'error+benchmark': [
    'Error: Benchmark failed — model not found',
    'Error: Benchmark crashed during generation phase',
  ],
  'debug+benchmark': [
    'Debug: Benchmark timing calibration: overhead={overhead}μs',
  ],
}

function fillTemplate(template: string): string {
  return template
    .replace('{tokens}', String(Math.floor(Math.random() * 300) + 50))
    .replace('{time}', (Math.random() * 5 + 0.5).toFixed(1))
    .replace('{ctx}', String([2048, 4096, 8192, 16384, 32768][Math.floor(Math.random() * 5)]))
    .replace('{cache}', (Math.random() * 20 + 75).toFixed(1))
    .replace('{profile}', ['rtx-3060-q4', 'rtx-3080-q5', 'rtx-4090-fp16', 'rtx-3070-q4'][Math.floor(Math.random() * 4)])
    .replace('{model}', ['Qwen3 4B Instruct Q4_K_M', 'Qwen3 8B Instruct Q5_K_M', 'Llama 3.1 8B Q4_K_M', 'Mistral 7B Q4_K_M', 'Qwen3 14B Q3_K_M'][Math.floor(Math.random() * 5)])
    .replace('{latency}', String(Math.floor(Math.random() * 200) + 10))
    .replace('{session}', String(Math.floor(Math.random() * 9000) + 1000))
    .replace('{temp}', String(Math.floor(Math.random() * 15) + 72))
    .replace('{used}', String(Math.floor(Math.random() * 30000) + 2000))
    .replace('{max}', String([4096, 8192, 32768][Math.floor(Math.random() * 3)]))
    .replace('{rate}', (Math.random() * 30 + 5).toFixed(1))
    .replace('{depth}', String(Math.floor(Math.random() * 20) + 1))
    .replace('{vram}', (Math.random() * 4 + 2).toFixed(1))
    .replace('{vramTotal}', String([8, 12, 16, 24][Math.floor(Math.random() * 4)]))
    .replace('{vramPct}', (Math.random() * 40 + 30).toFixed(1))
    .replace('{rps}', (Math.random() * 5 + 0.5).toFixed(1))
    .replace('{threads}', String(Math.floor(Math.random() * 12) + 4))
    .replace('{batch}', String(Math.floor(Math.random() * 8) + 1))
    .replace('{batchTime}', String(Math.floor(Math.random() * 500) + 50))
    .replace('{kvUsed}', String(Math.floor(Math.random() * 3000) + 500))
    .replace('{kvTotal}', String([4096, 8192, 16384][Math.floor(Math.random() * 3)]))
    .replace('{tokPerSec}', (Math.random() * 30 + 5).toFixed(1))
    .replace('{integration}', ['Open WebUI', 'Lobe Chat', 'SillyTavern', 'Continue.dev'][Math.floor(Math.random() * 4)])
    .replace('{cpu}', String(Math.floor(Math.random() * 60) + 10))
    .replace('{ram}', String(Math.floor(Math.random() * 50) + 30))
    .replace('{gpu}', String(Math.floor(Math.random() * 70) + 15))
    .replace('{config}', ['max_context', 'default_profile', 'thread_count', 'temperature'][Math.floor(Math.random() * 4)])
    .replace('{checkpoint}', new Date().toISOString())
    .replace('{swap}', String(Math.floor(Math.random() * 2000) + 100))
    .replace('{drift}', String(Math.floor(Math.random() * 500) + 10))
    .replace('{pp}', String([512, 1024, 2048][Math.floor(Math.random() * 3)]))
    .replace('{tg}', String([128, 256, 512][Math.floor(Math.random() * 3)]))
    .replace('{pl}', String([1, 2, 4][Math.floor(Math.random() * 3)]))
    .replace('{ttft}', String(Math.floor(Math.random() * 300) + 20))
    .replace('{ppTime}', String(Math.floor(Math.random() * 1000) + 100))
    .replace('{score}', (Math.random() * 40 + 10).toFixed(1))
    .replace('{grade}', ['A+', 'A', 'B+', 'B', 'C'][Math.floor(Math.random() * 5)])
    .replace('{overhead}', String(Math.floor(Math.random() * 100) + 5))
}

function generateLogEntry(): LogEntry {
  const level = randomLevel()
  const source = randomSource()
  const key = `${level}+${source}`
  const templates = messageTemplates[key] || messageTemplates[`info+gateway`]
  const template = templates[Math.floor(Math.random() * templates.length)]
  const message = fillTemplate(template)

  return {
    id: generateId(),
    level,
    source,
    message,
    metadata: level === 'error' ? JSON.stringify({ retryCount: Math.floor(Math.random() * 3) + 1, backoff: 'exponential' }) : null,
    createdAt: new Date().toISOString(),
  }
}

// --- In-memory log buffer ---
const MAX_BUFFER_SIZE = 50
const logBuffer: LogEntry[] = []

// Seed buffer with initial entries
for (let i = 0; i < 20; i++) {
  const entry = generateLogEntry()
  // Space them out over the past few minutes
  const ago = Math.floor(Math.random() * 300) * 1000 // 0-5 minutes ago
  entry.createdAt = new Date(Date.now() - ago).toISOString()
  logBuffer.push(entry)
}

// Sort by time
logBuffer.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())

// --- Socket.io connection handling ---
io.on('connection', (socket) => {
  console.log(`[LogStream] Client connected: ${socket.id}`)

  // Send initial logs on connection
  socket.emit('logs:initial', logBuffer.slice(-20))

  socket.on('logs:clear', () => {
    logBuffer.length = 0
    io.emit('logs:clear')
    console.log('[LogStream] Logs cleared by admin')
  })

  socket.on('disconnect', () => {
    console.log(`[LogStream] Client disconnected: ${socket.id}`)
  })

  socket.on('error', (error) => {
    console.error(`[LogStream] Socket error (${socket.id}):`, error)
  })
})

// --- Periodic log generation ---
function scheduleNextLog() {
  const delay = Math.floor(Math.random() * 5000) + 3000 // 3-8 seconds
  setTimeout(() => {
    const entry = generateLogEntry()
    logBuffer.push(entry)

    // Keep buffer within max size
    if (logBuffer.length > MAX_BUFFER_SIZE) {
      logBuffer.shift()
    }

    // Emit to all connected clients
    io.emit('logs:new', entry)

    // Schedule next
    scheduleNextLog()
  }, delay)
}

scheduleNextLog()

// --- Start server ---
const PORT = 3003
httpServer.listen(PORT, () => {
  console.log(`[LogStream] Kimari Log Stream service running on port ${PORT}`)
})

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[LogStream] Received SIGTERM, shutting down...')
  httpServer.close(() => {
    console.log('[LogStream] Server closed')
    process.exit(0)
  })
})

process.on('SIGINT', () => {
  console.log('[LogStream] Received SIGINT, shutting down...')
  httpServer.close(() => {
    console.log('[LogStream] Server closed')
    process.exit(0)
  })
})
