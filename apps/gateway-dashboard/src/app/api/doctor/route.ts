import { NextResponse } from 'next/server';
import { execSync } from 'child_process';
import { existsSync, readFileSync } from 'fs';

export const dynamic = 'force-dynamic'

interface DiagnosticCheck {
  name: string;
  category: string;
  status: 'PASS' | 'WARN' | 'FAIL';
  message: string;
  details?: string;
}

function safeExec(cmd: string): string {
  try { return execSync(cmd, { timeout: 5000, encoding: 'utf-8' }).trim() } catch { return '' }
}

async function checkUrl(url: string, timeout = 2000): Promise<{ ok: boolean; status?: number; body?: string }> {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(timeout) })
    const body = await res.text()
    return { ok: res.ok, status: res.status, body }
  } catch {
    return { ok: false }
  }
}

export async function GET() {
  const checks: DiagnosticCheck[] = [];

  // ── Python Runtime ──
  const pyVer = safeExec('python3 --version 2>&1')
  const pyPath = safeExec('which python3 2>/dev/null')
  if (pyVer) {
    checks.push({
      name: 'Python Runtime',
      category: 'Runtime',
      status: 'PASS',
      message: `${pyVer} found at ${pyPath || 'unknown'}`,
      details: 'Python 3.11+ recommended for all Kimari features.',
    })
  } else {
    checks.push({
      name: 'Python Runtime',
      category: 'Runtime',
      status: 'FAIL',
      message: 'Python 3 not found in PATH',
      details: 'Kimari CLI requires Python 3.10+.',
    })
  }

  // ── Kimari Version ──
  const kimariInit = '/home/smouj/.openclaw/workspace/kimari-local-ai/kimari/__init__.py'
  if (existsSync(kimariInit)) {
    const content = readFileSync(kimariInit, 'utf-8')
    const match = content.match(/__version__\s*=\s*["']([^"']+)["']/)
    const ver = match ? match[1] : 'unknown'
    checks.push({
      name: 'Kimari Version',
      category: 'Core',
      status: 'PASS',
      message: `Running Kimari ${ver}`,
      details: `Package version from ${kimariInit}`,
    })
  } else {
    checks.push({
      name: 'Kimari Version',
      category: 'Core',
      status: 'WARN',
      message: 'Kimari package not found at expected path',
      details: 'Dashboard may be running standalone without the Kimari CLI.',
    })
  }

  // ── llama-server Binary ──
  const llamaPath = safeExec('which llama-server 2>/dev/null') || '/home/smouj/.local/bin/llama-server'
  if (existsSync(llamaPath)) {
    const verOutput = safeExec(`${llamaPath} --version 2>&1`)
    const verMatch = verOutput.match(/version:\s*(\S+)/)
    const cudaMatch = verOutput.match(/CUDA/)
    const gpuMatch = verOutput.match(/Device 0: (.+?),/)
    checks.push({
      name: 'llama-server Binary',
      category: 'Runtime',
      status: 'PASS',
      message: `Found at ${llamaPath}${verMatch ? ` (v${verMatch[1]})` : ''}${cudaMatch ? ', CUDA enabled' : ''}`,
      details: gpuMatch ? `GPU: ${gpuMatch[1]}` : 'No GPU detected by llama-server',
    })
  } else {
    checks.push({
      name: 'llama-server Binary',
      category: 'Runtime',
      status: 'FAIL',
      message: `Not found at ${llamaPath}`,
      details: 'Required for local LLM inference. Install llama.cpp.',
    })
  }

  // ── GPU Detection ──
  const smi = safeExec('nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null')
  if (smi) {
    const parts = smi.split(',').map(s => s.trim())
    checks.push({
      name: 'GPU (nvidia-smi)',
      category: 'Hardware',
      status: 'PASS',
      message: `${parts[0]} — ${parts[1]} VRAM — driver ${parts[2]}`,
      details: 'GPU available for CUDA inference.',
    })
  } else {
    // Fallback via llama-server
    const llamaVer = safeExec('~/.local/bin/llama-server --version 2>&1')
    const gpuMatch = llamaVer.match(/Device 0: (.+)/)
    if (gpuMatch) {
      checks.push({
        name: 'GPU (llama-server)',
        category: 'Hardware',
        status: 'WARN',
        message: `${gpuMatch[1]} (detected by llama-server, nvidia-smi unavailable)`,
        details: 'nvidia-smi not found. GPU stats (temp, power) may be unavailable.',
      })
    } else {
      checks.push({
        name: 'GPU',
        category: 'Hardware',
        status: 'WARN',
        message: 'No GPU detected via nvidia-smi or llama-server',
        details: 'CPU-only inference will be significantly slower.',
      })
    }
  }

  // ── Model Files ──
  const modelsDir = '/home/smouj/.local/share/kimari/models'
  if (existsSync(modelsDir)) {
    const ggufFiles = safeExec(`find ${modelsDir} -name '*.gguf' -exec ls -lh {} \\;`)
    const count = ggufFiles ? ggufFiles.split('\n').filter(Boolean).length : 0
    checks.push({
      name: 'Model Files',
      category: 'Models',
      status: count > 0 ? 'PASS' : 'WARN',
      message: `${count} GGUF model${count !== 1 ? 's' : ''} in ${modelsDir}`,
      details: ggufFiles || 'No GGUF files found.',
    })
  } else {
    checks.push({
      name: 'Model Files',
      category: 'Models',
      status: 'WARN',
      message: `Models directory not found: ${modelsDir}`,
      details: 'Create the directory and download models.',
    })
  }

  // ── llama-server Status (live check) ──
  const llamaHealth = await checkUrl('http://127.0.0.1:11435/health')
  if (llamaHealth.ok) {
    checks.push({
      name: 'llama-server Status',
      category: 'Services',
      status: 'PASS',
      message: 'llama-server running on port 11435',
      details: `Health response: ${llamaHealth.body?.substring(0, 100)}`,
    })
  } else {
    checks.push({
      name: 'llama-server Status',
      category: 'Services',
      status: 'WARN',
      message: 'llama-server not running on port 11435',
      details: 'Start with: kimari start --profile test',
    })
  }

  // ── Ollama Status ──
  const ollamaHealth = await checkUrl('http://127.0.0.1:11434/api/tags')
  if (ollamaHealth.ok) {
    try {
      const data = JSON.parse(ollamaHealth.body || '{}')
      const modelCount = data.models?.length || 0
      checks.push({
        name: 'Ollama',
        category: 'Services',
        status: 'PASS',
        message: `Ollama running on port 11434 — ${modelCount} model${modelCount !== 1 ? 's' : ''} loaded`,
        details: data.models?.map((m: { name: string }) => m.name).join(', ') || '',
      })
    } catch {
      checks.push({
        name: 'Ollama',
        category: 'Services',
        status: 'PASS',
        message: 'Ollama running on port 11434',
      })
    }
  } else {
    checks.push({
      name: 'Ollama',
      category: 'Services',
      status: 'WARN',
      message: 'Ollama not running on port 11434',
      details: 'Optional — start with: ollama serve',
    })
  }

  // ── System Resources ──
  const memInfo = safeExec("free -h | grep Mem | awk '{print $2, $3, $7}'")
  const diskInfo = safeExec("df -h / | tail -1 | awk '{print $2, $3, $5}'")
  checks.push({
    name: 'System Memory',
    category: 'System',
    status: 'PASS',
    message: `RAM: ${memInfo.replace(/\s+/g, ' ')}`,
    details: 'Total / Used / Available',
  })
  checks.push({
    name: 'Disk Space',
    category: 'System',
    status: 'PASS',
    message: `Disk: ${diskInfo.replace(/\s+/g, ' ')}`,
    details: 'Total / Used / Use%',
  })

  // ── WSL Detection ──
  const procVer = safeExec('cat /proc/version 2>/dev/null')
  if (procVer.includes('microsoft-standard')) {
    checks.push({
      name: 'WSL Environment',
      category: 'System',
      status: 'PASS',
      message: 'Running under WSL2 (Windows Subsystem for Linux)',
      details: procVer.split(' ').slice(0, 3).join(' '),
    })
  }

  return NextResponse.json({ checks, timestamp: new Date().toISOString() });
}
