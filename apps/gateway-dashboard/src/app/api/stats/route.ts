import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

function randomVariation(base: number, range: number): number {
  return Math.round((base + (Math.random() - 0.5) * 2 * range) * 100) / 100
}

export async function GET() {
  try {
    // Check if server is running
    const serverState = await db.serverState.findFirst()
    const isRunning = serverState?.status === 'running'

    if (!isRunning) {
      return NextResponse.json({
        serverRunning: false,
        stats: null,
      })
    }

    const uptime = serverState.uptime ?? 0
    const profile = serverState.profile ?? 'test'

    // Generate realistic mock stats with slight random variations
    const stats = {
      tokensPerSec: {
        prompt: randomVariation(85 + uptime * 0.001, 5),
        generation: randomVariation(32 + uptime * 0.0005, 3),
      },
      vramUsage: {
        used: Math.round(randomVariation(4.2 + uptime * 0.00005, 0.15) * 1024), // MB
        total: 8192, // MB (8 GB)
        percent: Math.round(randomVariation(52 + uptime * 0.001, 2) * 10) / 10,
      },
      gpuStats: {
        temperature: Math.round(randomVariation(62 + uptime * 0.0003, 3)),
        powerDraw: Math.round(randomVariation(145 + uptime * 0.001, 8)),
        fanSpeed: Math.round(randomVariation(55 + uptime * 0.0002, 5)),
        clockSpeed: Math.round(randomVariation(2100 + uptime * 0.01, 30)),
      },
      requestStats: {
        active: Math.max(0, Math.round(randomVariation(2, 1.5))),
        total: Math.round(1247 + uptime * 0.8 + Math.random() * 10),
        avgLatency: Math.round(randomVariation(142, 18)),
        queueDepth: Math.max(0, Math.round(randomVariation(1, 0.8))),
      },
      memoryStats: {
        modelSize: Math.round(randomVariation(3840, 10)), // MB
        contextSize: Math.round(randomVariation(512, 15)), // MB
        overhead: Math.round(randomVariation(280, 10)), // MB
        total: Math.round(randomVariation(4632, 20)), // MB
      },
      serverInfo: {
        uptime,
        lastRequest: new Date(Date.now() - Math.random() * 5000).toISOString(),
        model: serverState.model ?? 'kimari-4b-q4_k_m.gguf',
        profile,
      },
    }

    return NextResponse.json({
      serverRunning: true,
      stats,
    })
  } catch (error) {
    console.error('Failed to fetch stats:', error)
    return NextResponse.json(
      { error: 'Failed to fetch server stats' },
      { status: 500 }
    )
  }
}
