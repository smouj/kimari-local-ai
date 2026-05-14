import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const integrations = await db.integration.findMany({
      orderBy: { name: 'asc' },
    })

    // Live-status check each integration
    const enriched = await Promise.all(
      integrations.map(async (integration) => {
        let liveStatus = integration.status
        let liveDetails = ''

        try {
          const res = await fetch(integration.baseUrl, {
            method: 'GET',
            signal: AbortSignal.timeout(3000),
          })
          if (res.ok) {
            liveStatus = 'connected'
            liveDetails = `Responded ${res.status} at ${new Date().toISOString()}`
          } else {
            liveStatus = 'error'
            liveDetails = `HTTP ${res.status}`
          }
        } catch {
          // Could be a POST-only endpoint or not running
          if (integration.status === 'connected') {
            liveStatus = 'disconnected'
          }
          liveDetails = 'Connection refused or timed out'
        }

        return {
          ...integration,
          status: liveStatus,
          liveDetails,
        }
      })
    )

    return NextResponse.json(enriched)
  } catch (error) {
    console.error('Failed to get integrations:', error)
    return NextResponse.json({ error: 'Failed to get integrations' }, { status: 500 })
  }
}
