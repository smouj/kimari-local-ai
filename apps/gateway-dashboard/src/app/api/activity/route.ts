import { NextResponse } from 'next/server'

type ActivityType =
  | 'server_start'
  | 'server_stop'
  | 'benchmark'
  | 'model_download'
  | 'config_change'
  | 'integration_connect'
  | 'health_check'

type ActivityStatus = 'success' | 'warning' | 'error' | 'info'

interface ActivityEvent {
  id: string
  type: ActivityType
  title: string
  description: string
  icon: string
  timestamp: string
  status: ActivityStatus
}

function hoursAgo(hours: number): string {
  const now = new Date()
  now.setMinutes(now.getMinutes() - Math.round(hours * 60))
  return now.toISOString()
}

function minutesAgo(minutes: number): string {
  return hoursAgo(minutes / 60)
}

const mockEvents: ActivityEvent[] = [
  {
    id: 'act-001',
    type: 'health_check',
    title: 'Health Check Passed',
    description: 'All systems operational — GPU, memory, and API endpoints verified',
    icon: 'Heart',
    timestamp: minutesAgo(3),
    status: 'success',
  },
  {
    id: 'act-002',
    type: 'benchmark',
    title: 'Benchmark Completed',
    description: 'Kimari-4B Q4_K_M achieved 34.2 tok/s prompt, 24.8 tok/s generation',
    icon: 'BarChart3',
    timestamp: minutesAgo(18),
    status: 'success',
  },
  {
    id: 'act-003',
    type: 'config_change',
    title: 'Context Size Updated',
    description: 'Changed context-size from 2048 to 4096 on RTX 3090 profile',
    icon: 'Settings',
    timestamp: minutesAgo(42),
    status: 'info',
  },
  {
    id: 'act-004',
    type: 'server_start',
    title: 'Server Started',
    description: 'llama.cpp server running on port 8080 with profile RTX 3090 Balanced',
    icon: 'Play',
    timestamp: hoursAgo(1.2),
    status: 'success',
  },
  {
    id: 'act-005',
    type: 'model_download',
    title: 'Model Download Completed',
    description: 'Kimari-4B Q4_K_M (2.4 GB) downloaded and verified successfully',
    icon: 'Download',
    timestamp: hoursAgo(1.8),
    status: 'success',
  },
  {
    id: 'act-006',
    type: 'integration_connect',
    title: 'Continue.dev Connected',
    description: 'Continue.dev integration established — API proxy active on /v1/chat/completions',
    icon: 'Puzzle',
    timestamp: hoursAgo(2.3),
    status: 'success',
  },
  {
    id: 'act-007',
    type: 'health_check',
    title: 'Health Check Warning',
    description: 'VRAM usage at 87% — approaching threshold on RTX 3090',
    icon: 'Heart',
    timestamp: hoursAgo(3.5),
    status: 'warning',
  },
  {
    id: 'act-008',
    type: 'server_stop',
    title: 'Server Stopped',
    description: 'Graceful shutdown completed — all connections closed, model unloaded',
    icon: 'Square',
    timestamp: hoursAgo(5.1),
    status: 'info',
  },
  {
    id: 'act-009',
    type: 'config_change',
    title: 'API Key Rotated',
    description: 'Gateway API key updated — existing sessions will need re-authentication',
    icon: 'Settings',
    timestamp: hoursAgo(7.4),
    status: 'warning',
  },
  {
    id: 'act-010',
    type: 'benchmark',
    title: 'Benchmark Failed',
    description: 'Benchmark on Mistral-7B Q5_K_M timed out after 120s — insufficient VRAM',
    icon: 'BarChart3',
    timestamp: hoursAgo(9.2),
    status: 'error',
  },
  {
    id: 'act-011',
    type: 'server_start',
    title: 'Server Started',
    description: 'llama.cpp server running on port 8080 with profile RTX 3090 Fast',
    icon: 'Play',
    timestamp: hoursAgo(11.5),
    status: 'success',
  },
  {
    id: 'act-012',
    type: 'integration_connect',
    title: 'Open WebUI Connected',
    description: 'Open WebUI integration established — chat interface accessible',
    icon: 'Puzzle',
    timestamp: hoursAgo(14.0),
    status: 'success',
  },
  {
    id: 'act-013',
    type: 'model_download',
    title: 'Model Download Started',
    description: 'Downloading Mistral-7B Q5_K_M (4.8 GB) from Hugging Face...',
    icon: 'Download',
    timestamp: hoursAgo(16.3),
    status: 'info',
  },
  {
    id: 'act-014',
    type: 'health_check',
    title: 'Health Check Passed',
    description: 'Routine check — GPU temperature 62°C, VRAM 45%, API latency 18ms',
    icon: 'Heart',
    timestamp: hoursAgo(19.7),
    status: 'success',
  },
  {
    id: 'act-015',
    type: 'server_stop',
    title: 'Server Crashed',
    description: 'Unexpected server termination — SIGKILL received, possible OOM killer',
    icon: 'Square',
    timestamp: hoursAgo(22.5),
    status: 'error',
  },
]

export async function GET() {
  return NextResponse.json({
    events: mockEvents,
    total: mockEvents.length,
  })
}
