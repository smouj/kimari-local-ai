import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  const timeRange = request.nextUrl.searchParams.get('range') || '24h'

  try {
    // Real benchmark history from DB
    const benchmarks = await db.benchmarkResult.findMany({
      orderBy: { createdAt: 'desc' },
      take: timeRange === '30d' ? 30 : timeRange === '7d' ? 7 : 10,
    })

    const gpuMetrics = benchmarks.map((b) => ({
      timestamp: b.createdAt,
      model: b.model,
      profile: b.profile,
      promptTokPerSec: b.promptTokPerSec,
      genTokPerSec: b.genTokPerSec,
      ttft: b.ttft,
      vramUsedMb: b.vramUsedMb,
      status: b.status,
    }))

    // Real request history from logs (count by hour)
    const logs = await db.gatewayLog.findMany({ orderBy: { createdAt: 'desc' }, take: 100 })
    const requestHistory = aggregateLogsByTime(logs, timeRange)

    // Real model usage from benchmarks
    const modelUsage = benchmarks.reduce((acc, b) => {
      const key = b.model
      if (!acc[key]) acc[key] = { model: key, runs: 0, avgPrompt: 0, avgGen: 0 }
      acc[key].runs++
      acc[key].avgPrompt += b.promptTokPerSec || 0
      acc[key].avgGen += b.genTokPerSec || 0
      return acc
    }, {} as Record<string, { model: string; runs: number; avgPrompt: number; avgGen: number }>)

    // Finalize averages
    const modelUsageArray = Object.values(modelUsage).map(m => ({
      ...m,
      avgPrompt: m.runs > 0 ? Math.round(m.avgPrompt / m.runs * 10) / 10 : 0,
      avgGen: m.runs > 0 ? Math.round(m.avgGen / m.runs * 10) / 10 : 0,
    }))

    return NextResponse.json({
      timeRange,
      gpuMetrics,
      requestHistory,
      modelUsage: modelUsageArray,
      summary: {
        totalBenchmarks: benchmarks.length,
        totalLogEntries: logs.length,
        latestBenchmark: benchmarks[0]?.createdAt || null,
      },
    })
  } catch (error) {
    console.error('Failed to get analytics:', error)
    return NextResponse.json({
      timeRange,
      gpuMetrics: [],
      requestHistory: [],
      modelUsage: [],
      summary: { totalBenchmarks: 0, totalLogEntries: 0, latestBenchmark: null },
    })
  }
}

function aggregateLogsByTime(logs: { level: string; createdAt: string }[], _timeRange: string) {
  // Group logs by hour
  const byHour: Record<string, { hour: string; total: number; errors: number }> = {}

  for (const log of logs) {
    const date = new Date(log.createdAt)
    const hourKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:00`

    if (!byHour[hourKey]) {
      byHour[hourKey] = { hour: hourKey, total: 0, errors: 0 }
    }
    byHour[hourKey].total++
    if (log.level === 'error') byHour[hourKey].errors++
  }

  return Object.values(byHour).sort((a, b) => a.hour.localeCompare(b.hour))
}
