import { NextResponse } from 'next/server'

interface QuickAction {
  id: string
  label: string
  description: string
  icon: string
  category: 'server' | 'diagnostics' | 'maintenance'
  shortcut?: string
  confirmRequired: boolean
  confirmMessage?: string
  estimatedDuration: number // seconds
}

const availableActions: QuickAction[] = [
  {
    id: 'start_server',
    label: 'Start Server',
    description: 'Launch llama.cpp server with the active GPU profile',
    icon: 'Play',
    category: 'server',
    shortcut: 'S',
    confirmRequired: false,
    estimatedDuration: 5,
  },
  {
    id: 'stop_server',
    label: 'Stop Server',
    description: 'Gracefully shutdown the running llama.cpp instance',
    icon: 'Square',
    category: 'server',
    shortcut: 'X',
    confirmRequired: true,
    confirmMessage: 'Are you sure you want to stop the server? Active connections will be terminated.',
    estimatedDuration: 3,
  },
  {
    id: 'restart_service',
    label: 'Restart Service',
    description: 'Stop and restart the server with the same configuration',
    icon: 'RotateCcw',
    category: 'server',
    confirmRequired: true,
    confirmMessage: 'Restart will briefly disconnect all clients.',
    estimatedDuration: 8,
  },
  {
    id: 'run_benchmark',
    label: 'Run Benchmark',
    description: 'Test model inference speed and token throughput',
    icon: 'Zap',
    category: 'diagnostics',
    shortcut: 'B',
    confirmRequired: false,
    estimatedDuration: 30,
  },
  {
    id: 'run_doctor',
    label: 'Run Diagnostics',
    description: 'Full system health check and compatibility scan',
    icon: 'Stethoscope',
    category: 'diagnostics',
    shortcut: 'D',
    confirmRequired: false,
    estimatedDuration: 15,
  },
  {
    id: 'clear_logs',
    label: 'Clear Logs',
    description: 'Remove all gateway log entries from the database',
    icon: 'Trash2',
    category: 'maintenance',
    confirmRequired: true,
    confirmMessage: 'This will permanently delete all log entries. This action cannot be undone.',
    estimatedDuration: 2,
  },
  {
    id: 'download_model',
    label: 'Download Model',
    description: 'Browse and download a new AI model to the gateway',
    icon: 'Download',
    category: 'maintenance',
    confirmRequired: false,
    estimatedDuration: 60,
  },
]

export async function GET() {
  const categories = [
    { id: 'server', label: 'Server', description: 'Server lifecycle controls' },
    { id: 'diagnostics', label: 'Diagnostics', description: 'Testing and health checks' },
    { id: 'maintenance', label: 'Maintenance', description: 'Cleanup and management' },
  ]

  return NextResponse.json({
    actions: availableActions,
    categories,
  })
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { actionId } = body

    if (!actionId) {
      return NextResponse.json({ error: 'actionId is required' }, { status: 400 })
    }

    const action = availableActions.find((a) => a.id === actionId)
    if (!action) {
      return NextResponse.json({ error: `Unknown action: ${actionId}` }, { status: 404 })
    }

    // Simulate action execution
    const success = Math.random() > 0.05 // 95% success rate

    if (!success) {
      return NextResponse.json({
        success: false,
        actionId,
        message: `Failed to execute ${action.label}. Please try again.`,
        timestamp: new Date().toISOString(),
      })
    }

    // Simulate different outcomes based on action type
    const results: Record<string, { message: string; details?: string }> = {
      start_server: {
        message: 'Server started successfully',
        details: 'llama.cpp running on port 8080 with profile RTX 4090',
      },
      stop_server: {
        message: 'Server stopped gracefully',
        details: '0 active connections were terminated',
      },
      restart_service: {
        message: 'Service restarted successfully',
        details: 'Downtime: 3.2s',
      },
      run_benchmark: {
        message: 'Benchmark completed',
        details: 'Prompt: 42.3 tok/s | Generation: 28.7 tok/s | TTFT: 128ms',
      },
      run_doctor: {
        message: 'Diagnostics complete',
        details: '12/14 checks passed, 2 warnings found',
      },
      clear_logs: {
        message: 'Logs cleared',
        details: 'Removed 847 log entries',
      },
      download_model: {
        message: 'Model download started',
        details: 'Downloading kimari-4b-q4km.gguf (2.4 GB)',
      },
    }

    const result = results[actionId] || { message: `${action.label} completed` }

    return NextResponse.json({
      success: true,
      actionId,
      message: result.message,
      details: result.details,
      timestamp: new Date().toISOString(),
    })
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 })
  }
}
