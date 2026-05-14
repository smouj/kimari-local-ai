import { NextResponse } from 'next/server'
import { execSync } from 'child_process'
import { readFileSync } from 'fs'

export const dynamic = 'force-dynamic'

interface SystemResources {
  cpu: { usage: number; cores: number; model: string }
  memory: { used: number; total: number; percent: number; available: number }
  disk: { used: number; total: number; percent: number }
  gpu: {
    name: string
    vramTotalMb: number
    vramUsedMb: number
    vramPercent: number
    temperature: number | null
    powerDraw: number | null
    driverVersion: string | null
  } | null
  llamaServer: {
    running: boolean
    url: string
    models: string[]
  }
  ollama: {
    running: boolean
    url: string
    models: { id: string; size: string }[]
  }
  uptime: number
}

function safeExec(cmd: string): string {
  try { return execSync(cmd, { timeout: 5000, encoding: 'utf-8' }).trim() } catch { return '' }
}

function parseProcMeminfo(): { total: number; used: number; available: number; percent: number } {
  try {
    const content = readFileSync('/proc/meminfo', 'utf-8')
    const get = (key: string) => {
      const m = content.match(new RegExp(`${key}:\\s+(\\d+)`))
      return m ? parseInt(m[1], 10) / 1024 : 0 // kB → MB → GB (/1024 twice, but we want GB)
    }
    const total = get('MemTotal') / 1024
    const available = get('MemAvailable') / 1024
    const used = total - available
    return { total: Math.round(total * 10) / 10, used: Math.round(used * 10) / 10, available: Math.round(available * 10) / 10, percent: Math.round((used / total) * 100) }
  } catch {
    return { total: 0, used: 0, available: 0, percent: 0 }
  }
}

function parseProcStat(): number {
  try {
    // Read cumulative CPU time
    const lines = readFileSync('/proc/stat', 'utf-8').split('\n')
    const cpuLine = lines[0]
    const vals = cpuLine.split(/\s+/).slice(1).map(Number)
    const idle = vals[3] + vals[4]
    const total = vals.reduce((a, b) => a + b, 0)
    return total > 0 ? Math.round(((total - idle) / total) * 100) : 0
  } catch {
    return 0
  }
}

function getGpuInfo(): SystemResources['gpu'] {
  // Try nvidia-smi first (real hardware)
  const smi = safeExec('nvidia-smi --query-gpu=name,memory.total,memory.used,temperature.gpu,power.draw,driver_version --format=csv,noheader,nounits 2>/dev/null')
  if (smi) {
    const parts = smi.split(',').map(s => s.trim())
    if (parts.length >= 4) {
      return {
        name: parts[0] || 'Unknown GPU',
        vramTotalMb: parseInt(parts[1]) || 0,
        vramUsedMb: parseInt(parts[2]) || 0,
        vramPercent: parseInt(parts[1]) > 0 ? Math.round((parseInt(parts[2]) / parseInt(parts[1])) * 100) : 0,
        temperature: parts[3] && parts[3] !== '[N/A]' ? parseFloat(parts[3]) : null,
        powerDraw: parts[4] && parts[4] !== '[N/A]' ? parseFloat(parts[4]) : null,
        driverVersion: parts[5] || null,
      }
    }
  }

  // Fallback: check via llama-server --version output (shows GPU detection)
  const llamaVer = safeExec('~/.local/bin/llama-server --version 2>&1')
  const gpuMatch = llamaVer.match(/Device 0: (.+?),/)
  const vramMatch = llamaVer.match(/VRAM: (\d+) MiB/)
  if (gpuMatch) {
    return {
      name: gpuMatch[1],
      vramTotalMb: vramMatch ? parseInt(vramMatch[1]) : 0,
      vramUsedMb: 0,
      vramPercent: 0,
      temperature: null,
      powerDraw: null,
      driverVersion: null,
    }
  }

  return null
}

async function checkLlamaServer(): Promise<SystemResources['llamaServer']> {
  const url = 'http://127.0.0.1:11435'
  try {
    const res = await fetch(`${url}/v1/models`, { signal: AbortSignal.timeout(2000) })
    if (res.ok) {
      const data = await res.json()
      return { running: true, url, models: (data.data || []).map((m: { id: string }) => m.id) }
    }
  } catch { /* not running */ }
  return { running: false, url, models: [] }
}

async function checkOllama(): Promise<SystemResources['ollama']> {
  const url = 'http://127.0.0.1:11434'
  try {
    const res = await fetch(`${url}/v1/models`, { signal: AbortSignal.timeout(2000) })
    if (res.ok) {
      const data = await res.json()
      return {
        running: true,
        url,
        models: (data.data || []).map((m: { id: string; created?: number }) => ({ id: m.id, size: '' })),
      }
    }
  } catch { /* not running */ }
  return { running: false, url, models: [] }
}

export async function GET() {
  const cores = parseInt(safeExec('nproc')) || 8
  const cpuModel = safeExec("lscpu | grep 'Model name' | head -1 | sed 's/Model name:\\s*//'") || 'Unknown CPU'
  const cpuUsage = parseProcStat()
  const memory = parseProcMeminfo()

  // Disk
  const diskInfo = safeExec("df -h / | tail -1 | awk '{print $3,$2,$5}'")
  const diskParts = diskInfo.split(/\s+/)
  const diskUsed = parseFloat(diskParts[0]) || 0
  const diskTotal = parseFloat(diskParts[1]) || 0
  const diskPercent = parseInt(diskParts[2]) || 0

  // Uptime
  const uptimeSec = parseInt(safeExec("cat /proc/uptime | cut -d. -f1")) || 0

  // GPU + services (async)
  const [gpu, llamaServer, ollama] = await Promise.all([
    Promise.resolve(getGpuInfo()),
    checkLlamaServer(),
    checkOllama(),
  ])

  return NextResponse.json({
    cpu: { usage: cpuUsage, cores, model: cpuModel },
    memory,
    disk: { used: diskUsed, total: diskTotal, percent: diskPercent },
    gpu,
    llamaServer,
    ollama,
    uptime: uptimeSec,
  })
}
