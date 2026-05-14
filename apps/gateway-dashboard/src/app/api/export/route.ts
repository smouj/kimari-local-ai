import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const type = searchParams.get('type') || 'logs'
  const format = searchParams.get('format') || 'json'

  try {
    let data: Record<string, unknown> = {}
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')

    switch (type) {
      case 'dashboard': {
        const serverState = await db.serverState.findFirst()
        const profiles = await db.gpuProfile.findMany()
        const models = await db.modelEntry.findMany()
        data = {
          exportedAt: new Date().toISOString(),
          server: serverState,
          profiles,
          models,
        }
        break
      }
      case 'logs': {
        const logs = await db.gatewayLog.findMany({ take: 500, orderBy: { createdAt: 'desc' } })
        data = {
          exportedAt: new Date().toISOString(),
          logs,
        }
        if (format === 'csv') {
          const header = 'id,level,source,message,createdAt'
          const rows = logs.map((l: { id: string; level: string; source: string; message: string; createdAt: string }) =>
            `"${l.id}","${l.level}","${l.source}","${l.message.replace(/"/g, '""')}","${l.createdAt}"`
          )
          const csv = [header, ...rows].join('\n')
          return new Response(csv, {
            headers: {
              'Content-Type': 'text/csv',
              'Content-Disposition': `attachment; filename="kimari-logs-${timestamp}.csv"`,
            },
          })
        }
        break
      }
      case 'benchmarks': {
        const benchmarks = await db.benchmarkResult.findMany({ orderBy: { createdAt: 'desc' } })
        data = {
          exportedAt: new Date().toISOString(),
          benchmarks,
        }
        if (format === 'csv') {
          const header = 'id,profile,model,quantization,contextSize,promptTokPerSec,genTokPerSec,ttft,vramUsedMb,status,createdAt'
          const rows = benchmarks.map((b: { id: string; profile: string; model: string; quantization: string; contextSize: number; promptTokPerSec: number | null; genTokPerSec: number | null; ttft: number | null; vramUsedMb: number | null; status: string; createdAt: string }) =>
            `"${b.id}","${b.profile}","${b.model}","${b.quantization}",${b.contextSize},${b.promptTokPerSec ?? ''},${b.genTokPerSec ?? ''},${b.ttft ?? ''},${b.vramUsedMb ?? ''},"${b.status}","${b.createdAt}"`
          )
          const csv = [header, ...rows].join('\n')
          return new Response(csv, {
            headers: {
              'Content-Type': 'text/csv',
              'Content-Disposition': `attachment; filename="kimari-benchmarks-${timestamp}.csv"`,
            },
          })
        }
        break
      }
      case 'analytics': {
        const serverState = await db.serverState.findFirst()
        const logs = await db.gatewayLog.findMany({ take: 100, orderBy: { createdAt: 'desc' } })
        const benchmarks = await db.benchmarkResult.findMany({ take: 50, orderBy: { createdAt: 'desc' } })
        data = {
          exportedAt: new Date().toISOString(),
          server: serverState,
          recentLogs: logs,
          recentBenchmarks: benchmarks,
        }
        break
      }
      default:
        return NextResponse.json({ error: 'Invalid export type' }, { status: 400 })
    }

    if (format === 'csv') {
      // For types without dedicated CSV, flatten to JSON-in-CSV
      const header = 'key,value'
      const rows = Object.entries(data).map(([k, v]) =>
        `"${k}","${JSON.stringify(v).replace(/"/g, '""')}"`
      )
      const csv = [header, ...rows].join('\n')
      return new Response(csv, {
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': `attachment; filename="kimari-${type}-${timestamp}.csv"`,
        },
      })
    }

    return new Response(JSON.stringify(data, null, 2), {
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': `attachment; filename="kimari-${type}-${timestamp}.json"`,
      },
    })
  } catch (error) {
    console.error('Export error:', error)
    return NextResponse.json({ error: 'Export failed' }, { status: 500 })
  }
}
