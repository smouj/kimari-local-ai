import { NextResponse } from 'next/server'

// Simulated system resources with realistic values that fluctuate
let cpuBase = 23 + Math.random() * 15
let memBase = 55 + Math.random() * 10
let diskBase = 42 + Math.random() * 8
let vramBase = 30 + Math.random() * 20
let gpuTempBase = 45 + Math.random() * 10
let gpuPowerBase = 120 + Math.random() * 40
let uptimeSeconds = Math.floor(3600 + Math.random() * 7200)

function jitter(base: number, range: number, min = 0, max = 100) {
  const val = base + (Math.random() - 0.5) * range
  return Math.min(max, Math.max(min, val))
}

export async function GET() {
  cpuBase = jitter(cpuBase, 6, 5, 95)
  memBase = jitter(memBase, 3, 20, 95)
  diskBase = jitter(diskBase, 1, 20, 90)
  vramBase = jitter(vramBase, 4, 5, 95)
  gpuTempBase = jitter(gpuTempBase, 3, 30, 95)
  gpuPowerBase = jitter(gpuPowerBase, 15, 50, 350)
  uptimeSeconds += 5

  const cpuUsage = Math.round(cpuBase)
  const cpuCores = 8
  const cpuTemp = Math.round(42 + cpuUsage * 0.45 + Math.random() * 3)
  const cpuFreq = (2.4 + cpuUsage * 0.015 + Math.random() * 0.2).toFixed(1)

  const memTotal = 32
  const memPercent = Math.round(memBase)
  const memUsed = +(memTotal * memPercent / 100).toFixed(1)
  const swapTotal = 8
  const swapUsed = +(Math.random() * 1.5).toFixed(1)

  const diskTotal = 512
  const diskPercent = Math.round(diskBase)
  const diskUsed = +(diskTotal * diskPercent / 100).toFixed(1)
  const readSpeed = (120 + Math.random() * 80).toFixed(0)
  const writeSpeed = (80 + Math.random() * 60).toFixed(0)

  const downloadSpeed = (5 + Math.random() * 45).toFixed(1)
  const uploadSpeed = (2 + Math.random() * 12).toFixed(1)
  const connections = Math.round(12 + Math.random() * 40)
  const latency = (1 + Math.random() * 4).toFixed(1)

  // GPU / VRAM data
  const vramTotalGB = 12
  const vramPercent = Math.round(vramBase)
  const vramUsedGB = +(vramTotalGB * vramPercent / 100).toFixed(1)
  const gpuTemp = Math.round(gpuTempBase)
  const gpuPowerDraw = Math.round(gpuPowerBase)

  return NextResponse.json({
    cpu: {
      usage: cpuUsage,
      cores: cpuCores,
      temperature: cpuTemp,
      frequency: `${cpuFreq} GHz`,
    },
    memory: {
      used: memUsed,
      total: memTotal,
      percent: memPercent,
      swapUsed: swapUsed,
      swapTotal: swapTotal,
    },
    disk: {
      used: diskUsed,
      total: diskTotal,
      percent: diskPercent,
      readSpeed: `${readSpeed} MB/s`,
      writeSpeed: `${writeSpeed} MB/s`,
    },
    network: {
      downloadSpeed: `${downloadSpeed} MB/s`,
      uploadSpeed: `${uploadSpeed} MB/s`,
      connections,
      latency: `${latency} ms`,
    },
    gpu: {
      vramUsed: vramUsedGB,
      vramTotal: vramTotalGB,
      vramPercent: vramPercent,
      temperature: gpuTemp,
      powerDraw: gpuPowerDraw,
    },
    uptime: uptimeSeconds,
  })
}
