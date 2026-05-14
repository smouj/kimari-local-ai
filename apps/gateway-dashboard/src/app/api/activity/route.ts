import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    // Real activity from gateway logs
    const logs = await db.gatewayLog.findMany({
      orderBy: { createdAt: 'desc' },
      take: 20,
    })

    const events = logs.map((log, i) => ({
      id: log.id,
      type: mapLevelToType(log.level),
      title: extractTitle(log.message),
      description: log.message,
      icon: mapSourceToIcon(log.source),
      timestamp: log.createdAt,
      status: mapLevelToStatus(log.level),
    }))

    return NextResponse.json(events)
  } catch (error) {
    console.error('Failed to get activity:', error)
    return NextResponse.json({ error: 'Failed to get activity' }, { status: 500 })
  }
}

function mapLevelToType(level: string): string {
  switch (level) {
    case 'error': return 'health_check'
    case 'warn': return 'config_change'
    case 'info': return 'health_check'
    default: return 'health_check'
  }
}

function mapLevelToStatus(level: string): string {
  switch (level) {
    case 'error': return 'error'
    case 'warn': return 'warning'
    default: return 'success'
  }
}

function mapSourceToIcon(source: string): string {
  switch (source) {
    case 'system': return 'Server'
    case 'gateway': return 'Activity'
    case 'integration': return 'Link'
    default: return 'Bell'
  }
}

function extractTitle(message: string): string {
  // Take first ~50 chars, break at first sentence/colon
  const shortened = message.length > 60 ? message.substring(0, 57) + '...' : message
  return shortened
}
