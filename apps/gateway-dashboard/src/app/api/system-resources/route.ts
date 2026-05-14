import { NextResponse } from 'next/server'

// Persistent state for realistic fluctuation
let cpuBases = Array.from({ length: 8 }, () => 15 + Math.random() * 30)
let memUsedBase = 14 + Math.random() * 4
let memCachedBase = 6 + Math.random() * 3
let memFreeBase = 5 + Math.random() * 3
let swapUsedBase = 0.3 + Math.random() * 1.2
let vramUsedBase = 3.2 + Math.random() * 4
let vramHistory: number[] = Array.from({ length: 60 }, (_, i) =>
  30 + Math.sin(i * 0.15) * 10 + Math.random() * 5
)
let diskReadBase = 85 + Math.random() * 60
let diskWriteBase = 45 + Math.random() * 40
let netInBase = 25 + Math.random() * 30
let netOutBase = 8 + Math.random() * 15
let cpuTempBase = 42 + Math.random() * 12
let gpuHotspotBase = 48 + Math.random() * 15
let uptimeSeconds = Math.floor(3600 + Math.random() * 7200)

function jitter(base: number, range: number, min = 0, max = 1000) {
  const val = base + (Math.random() - 0.5) * range
  return Math.min(max, Math.max(min, val))
}

export async function GET() {
  // Update CPU per-core
  cpuBases = cpuBases.map((b) => jitter(b, 8, 3, 97))
  const cpuCores = cpuBases.map((usage, i) => ({
    core: i,
    usage: Math.round(usage),
    frequency: +(2.4 + usage * 0.018 + Math.random() * 0.3).toFixed(2),
  }))

  // CPU package temp
  cpuTempBase = jitter(cpuTempBase, 3, 35, 95)
  const cpuPackageTemp = Math.round(cpuTempBase)

  // CPU avg
  const cpuAvgUsage = Math.round(cpuBases.reduce((a, b) => a + b, 0) / cpuBases.length)
  const cpuFreq = +(cpuCores.reduce((a, c) => a + c.frequency, 0) / cpuCores.length).toFixed(2)

  // Memory breakdown (total 32 GB)
  const memTotal = 32
  memUsedBase = jitter(memUsedBase, 0.8, 8, 22)
  memCachedBase = jitter(memCachedBase, 0.5, 3, 10)
  memFreeBase = memTotal - memUsedBase - memCachedBase
  swapUsedBase = jitter(swapUsedBase, 0.2, 0.1, 4)
  const swapTotal = 8

  const memUsed = +memUsedBase.toFixed(1)
  const memCached = +memCachedBase.toFixed(1)
  const memFree = +Math.max(0, memFreeBase).toFixed(1)
  const memPercent = Math.round((memUsed / memTotal) * 100)
  const swapPercent = Math.round((swapUsedBase / swapTotal) * 100)

  // GPU VRAM (12 GB total)
  const vramTotal = 12
  vramUsedBase = jitter(vramUsedBase, 0.4, 1, 11)
  const vramUsed = +vramUsedBase.toFixed(1)
  const vramPercent = Math.round((vramUsed / vramTotal) * 100)

  // VRAM history (shift and add new point)
  vramHistory = [...vramHistory.slice(1), vramPercent]
  const vramHistoryPoints = vramHistory.map((v, i) => ({
    tick: i,
    value: v,
  }))

  // GPU temperature & hotspot
  gpuHotspotBase = jitter(gpuHotspotBase, 2, 40, 95)
  const gpuTemp = Math.round(vramPercent * 0.5 + 35 + Math.random() * 3)
  const gpuHotspot = Math.round(gpuHotspotBase)
  const gpuPowerDraw = Math.round(80 + vramPercent * 1.8 + Math.random() * 10)

  // Disk I/O
  diskReadBase = jitter(diskReadBase, 20, 10, 300)
  diskWriteBase = jitter(diskWriteBase, 15, 5, 200)
  const diskReadMbps = +diskReadBase.toFixed(1)
  const diskWriteMbps = +diskWriteBase.toFixed(1)

  const diskTotal = 512
  const diskPercent = 42
  const diskUsed = +(diskTotal * diskPercent / 100).toFixed(1)

  // Network throughput
  netInBase = jitter(netInBase, 12, 2, 120)
  netOutBase = jitter(netOutBase, 6, 1, 60)
  const netInMbps = +netInBase.toFixed(1)
  const netOutMbps = +netOutBase.toFixed(1)
  const connections = Math.round(12 + Math.random() * 40)
  const latency = +(1 + Math.random() * 4).toFixed(1)

  // Temperature readings
  const cpuTemp = cpuPackageTemp
  const gpuTempReading = gpuTemp

  // Uptime
  uptimeSeconds += 3

  return NextResponse.json({
    cpu: {
      usage: cpuAvgUsage,
      cores: cpuCores,
      coreCount: 8,
      temperature: cpuTemp,
      frequency: `${cpuFreq} GHz`,
    },
    memory: {
      used: memUsed,
      cached: memCached,
      free: memFree,
      total: memTotal,
      percent: memPercent,
      swapUsed: +swapUsedBase.toFixed(1),
      swapTotal: swapTotal,
      swapPercent: swapPercent,
    },
    gpu: {
      vramUsed,
      vramTotal,
      vramPercent,
      vramHistory: vramHistoryPoints,
      temperature: gpuTempReading,
      hotspot: gpuHotspot,
      powerDraw: gpuPowerDraw,
    },
    disk: {
      used: diskUsed,
      total: diskTotal,
      percent: diskPercent,
      readMbps: diskReadMbps,
      writeMbps: diskWriteMbps,
    },
    network: {
      inMbps: netInMbps,
      outMbps: netOutMbps,
      connections,
      latency,
    },
    temperatures: {
      cpuPackage: cpuTemp,
      gpuHotspot: gpuHotspot,
      gpuCore: gpuTempReading,
    },
    uptime: uptimeSeconds,
  })
}
