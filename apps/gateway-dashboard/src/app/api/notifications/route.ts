import { NextResponse } from 'next/server'

interface Notification {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  read: boolean
  createdAt: string
  source: string
}

const notifications: Notification[] = [
  {
    id: '1',
    type: 'info',
    title: 'Server Started',
    message: "llama-server started with profile 'rtx-3060-q4'",
    read: false,
    createdAt: '2025-01-15T10:00:00Z',
    source: 'server',
  },
  {
    id: '2',
    type: 'warning',
    title: 'High VRAM Usage',
    message: 'VRAM usage at 92%. Consider reducing context size.',
    read: false,
    createdAt: '2025-01-15T09:45:00Z',
    source: 'monitor',
  },
  {
    id: '3',
    type: 'success',
    title: 'Model Downloaded',
    message: 'Qwen3 4B Instruct Q4_K_M downloaded successfully',
    read: true,
    createdAt: '2025-01-15T09:30:00Z',
    source: 'models',
  },
  {
    id: '4',
    type: 'error',
    title: 'Benchmark Failed',
    message: 'Benchmark failed: GPU out of memory',
    read: false,
    createdAt: '2025-01-15T08:00:00Z',
    source: 'benchmark',
  },
  {
    id: '5',
    type: 'info',
    title: 'Update Available',
    message: 'Kimari v0.2.0 is available. Current: v0.1.73-alpha',
    read: false,
    createdAt: '2025-01-14T12:00:00Z',
    source: 'system',
  },
  {
    id: '6',
    type: 'success',
    title: 'Integration Connected',
    message: 'Open WebUI connected successfully at http://localhost:3001',
    read: true,
    createdAt: '2025-01-14T11:00:00Z',
    source: 'integrations',
  },
  {
    id: '7',
    type: 'warning',
    title: 'Disk Space Low',
    message: 'Only 2.1 GB remaining in models directory',
    read: false,
    createdAt: '2025-01-13T15:00:00Z',
    source: 'system',
  },
]

export async function GET() {
  const unreadCount = notifications.filter((n) => !n.read).length
  return NextResponse.json({ notifications, unreadCount })
}

export async function POST(request: Request) {
  const body = await request.json()
  const { action, notificationId } = body

  if (action === 'markRead' && notificationId) {
    const notification = notifications.find((n) => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  } else if (action === 'markAllRead') {
    notifications.forEach((n) => {
      n.read = true
    })
  }

  const unreadCount = notifications.filter((n) => !n.read).length
  return NextResponse.json({ notifications, unreadCount })
}
