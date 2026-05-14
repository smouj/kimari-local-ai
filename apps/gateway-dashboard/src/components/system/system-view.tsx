'use client'

import { useSystemResources } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { Cpu, MemoryStick, HardDrive, Wifi, Thermometer, Monitor, Zap, ArrowDown, ArrowUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { Area, AreaChart, ResponsiveContainer } from 'recharts'

function getColor(percent: number) {
  if (percent < 50) return 'oklch(0.7 0.17 230)'
  if (percent < 80) return 'oklch(0.75 0.15 85)'
  return 'oklch(0.65 0.2 25)'
}

function getColorClass(percent: number) {
  if (percent < 50) return 'text-emerald-500'
  if (percent < 80) return 'text-amber-500'
  return 'text-red-500'
}

function getProgressClass(percent: number) {
  if (percent < 50) return '[&>div]:bg-emerald-500'
  if (percent < 80) return '[&>div]:bg-amber-500'
  return '[&>div]:bg-red-500'
}

// Overview Card for the top row
function OverviewCard({
  title,
  icon,
  value,
  subValue,
  percent,
  delay = 0,
}: {
  title: string
  icon: React.ReactNode
  value: string
  subValue?: string
  percent?: number
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <Card className="glass-card depth-shadow card-shine bg-card/80">
        <CardContent className="p-5">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary/25 to-primary/5 flex items-center justify-center shadow-sm shadow-primary/10">
                {icon}
              </div>
              <div>
                <div className="text-xs font-medium text-muted-foreground">{title}</div>
                <div className="text-xl font-bold tabular-nums">{value}</div>
              </div>
            </div>
            {percent !== undefined && (
              <Badge
                variant="outline"
                className={cn(
                  'text-xs font-mono',
                  percent < 50 ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400' :
                  percent < 80 ? 'border-amber-500/40 text-amber-600 dark:text-amber-400' :
                  'border-red-500/40 text-red-600 dark:text-red-400'
                )}
              >
                {percent}%
              </Badge>
            )}
          </div>
          {subValue && (
            <div className="text-xs text-muted-foreground font-medium">{subValue}</div>
          )}
          {percent !== undefined && (
            <Progress value={percent} className={cn('h-1.5 mt-2', getProgressClass(percent))} />
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

// CPU Core utilization bars
function CpuCoreBars({ cores }: { cores: { core: number; usage: number; frequency: number }[] }) {
  return (
    <Card className="glass-card depth-shadow bg-card/80">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          CPU Core Utilization
          <Badge variant="outline" className="text-[10px] font-mono border-border/50 text-muted-foreground ml-auto">
            {cores.length} cores
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2.5">
        {cores.map((core) => (
          <div key={core.core} className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-muted-foreground w-8 shrink-0">
              C{core.core}
            </span>
            <div className="flex-1 relative">
              <div className="h-5 rounded-full bg-muted/40 overflow-hidden">
                <motion.div
                  className={cn('h-full rounded-full', core.usage < 50 ? 'bg-emerald-500/70' : core.usage < 80 ? 'bg-amber-500/70' : 'bg-red-500/70')}
                  initial={{ width: 0 }}
                  animate={{ width: `${core.usage}%` }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                />
              </div>
              <span className={cn('absolute right-2 top-1/2 -translate-y-1/2 text-[10px] font-mono font-bold', getColorClass(core.usage))}>
                {core.usage}%
              </span>
            </div>
            <span className="text-[10px] font-mono text-muted-foreground w-14 text-right shrink-0">
              {core.frequency.toFixed(1)} GHz
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

// Memory Donut Chart (SVG)
function MemoryDonut({ used, cached, free, swapUsed, swapTotal }: {
  used: number
  cached: number
  free: number
  swapUsed: number
  swapTotal: number
}) {
  const total = used + cached + free
  const usedPct = (used / total) * 100
  const cachedPct = (cached / total) * 100
  const freePct = (free / total) * 100

  const radius = 60
  const circumference = 2 * Math.PI * radius

  const usedOffset = 0
  const cachedOffset = usedPct
  const freeOffset = usedPct + cachedPct

  const segments = [
    { pct: usedPct, offset: usedOffset, color: 'oklch(0.55 0.17 230)', label: 'Used', value: used, unit: 'GB' },
    { pct: cachedPct, offset: cachedOffset, color: 'oklch(0.65 0.12 250)', label: 'Cached', value: cached, unit: 'GB' },
    { pct: freePct, offset: freeOffset, color: 'oklch(0.7 0.06 230)', label: 'Free', value: free, unit: 'GB' },
  ]

  return (
    <Card className="glass-card depth-shadow bg-card/80">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <MemoryStick className="h-4 w-4 text-primary" />
          Memory Breakdown
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col sm:flex-row items-center gap-6">
          {/* SVG Donut */}
          <div className="relative shrink-0">
            <svg width="140" height="140" viewBox="0 0 140 140" className="-rotate-90">
              {segments.map((seg) => (
                <circle
                  key={seg.label}
                  cx="70"
                  cy="70"
                  r={radius}
                  fill="none"
                  stroke={seg.color}
                  strokeWidth="14"
                  strokeDasharray={`${(seg.pct / 100) * circumference} ${circumference}`}
                  strokeDashoffset={`${-(seg.offset / 100) * circumference}`}
                  strokeLinecap="butt"
                />
              ))}
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center rotate-0">
              <span className="text-lg font-bold tabular-nums">{used.toFixed(1)}</span>
              <span className="text-[10px] text-muted-foreground">/ {total} GB</span>
            </div>
          </div>

          {/* Legend */}
          <div className="space-y-3 flex-1 w-full">
            {segments.map((seg) => (
              <div key={seg.label} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-sm" style={{ backgroundColor: seg.color }} />
                  <span className="text-sm text-foreground/80">{seg.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-mono font-medium">{seg.value.toFixed(1)} {seg.unit}</span>
                  <span className="text-[10px] text-muted-foreground font-mono">({seg.pct.toFixed(0)}%)</span>
                </div>
              </div>
            ))}
            <div className="pt-2 mt-2 border-t border-border/50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-sm bg-amber-500/60" />
                  <span className="text-sm text-foreground/80">Swap</span>
                </div>
                <span className="text-sm font-mono font-medium">{swapUsed.toFixed(1)} / {swapTotal} GB</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// GPU VRAM Gauge with sparkline
function VramGauge({ vramUsed, vramTotal, vramPercent, history, temperature, hotspot, powerDraw }: {
  vramUsed: number
  vramTotal: number
  vramPercent: number
  history: { tick: number; value: number }[]
  temperature: number
  hotspot: number
  powerDraw: number
}) {
  const size = 140
  const strokeWidth = 12
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (vramPercent / 100) * circumference
  const color = getColor(vramPercent)

  return (
    <Card className="glass-card depth-shadow bg-card/80">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Monitor className="h-4 w-4 text-primary" />
          GPU VRAM
          <Badge variant="outline" className="text-[10px] font-mono border-border/50 text-muted-foreground ml-auto">
            Live
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col sm:flex-row items-center gap-6">
          {/* Gauge */}
          <div className="relative shrink-0">
            <svg width={size} height={size} className="-rotate-90">
              <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="currentColor" strokeWidth={strokeWidth} className="text-muted/30" />
              <motion.circle
                cx={size / 2} cy={size / 2} r={radius} fill="none"
                stroke={color} strokeWidth={strokeWidth} strokeLinecap="round"
                strokeDasharray={circumference}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset: offset }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center rotate-0">
              <span className={cn('text-2xl font-bold tabular-nums', getColorClass(vramPercent))}>{vramPercent}%</span>
              <span className="text-[10px] text-muted-foreground">{vramUsed} / {vramTotal} GB</span>
            </div>
          </div>

          {/* Sparkline + details */}
          <div className="flex-1 w-full space-y-4">
            {/* VRAM Sparkline */}
            <div className="h-16">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={history} margin={{ top: 2, right: 2, left: 2, bottom: 0 }}>
                  <defs>
                    <linearGradient id="vramGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="oklch(0.65 0.17 230)"
                    strokeWidth={1.5}
                    fill="url(#vramGradient)"
                    animationDuration={500}
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div>
                <div className="text-muted-foreground">Core</div>
                <div className="font-mono font-medium">{temperature}°C</div>
              </div>
              <div>
                <div className="text-muted-foreground">Hotspot</div>
                <div className={cn('font-mono font-medium', hotspot > 85 ? 'text-red-500' : hotspot > 70 ? 'text-amber-500' : 'text-foreground')}>
                  {hotspot}°C
                </div>
              </div>
              <div>
                <div className="text-muted-foreground">Power</div>
                <div className="font-mono font-medium">{powerDraw}W</div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Disk I/O chart
function DiskIOChart({ readMbps, writeMbps, used, total, percent }: {
  readMbps: number
  writeMbps: number
  used: number
  total: number
  percent: number
}) {
  return (
    <Card className="glass-card depth-shadow bg-card/80">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <HardDrive className="h-4 w-4 text-primary" />
          Disk I/O
          <Badge variant="outline" className="text-[10px] font-mono border-border/50 text-muted-foreground ml-auto">
            {used} / {total} GB
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={percent} className={cn('h-2', getProgressClass(percent))} />
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
            <div className="h-8 w-8 rounded-lg bg-emerald-500/15 flex items-center justify-center">
              <ArrowDown className="h-4 w-4 text-emerald-500" />
            </div>
            <div>
              <div className="text-[10px] text-muted-foreground font-medium">Read</div>
              <div className="text-sm font-mono font-bold">{readMbps.toFixed(1)} <span className="text-[10px] font-normal text-muted-foreground">MB/s</span></div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
            <div className="h-8 w-8 rounded-lg bg-primary/15 flex items-center justify-center">
              <ArrowUp className="h-4 w-4 text-primary" />
            </div>
            <div>
              <div className="text-[10px] text-muted-foreground font-medium">Write</div>
              <div className="text-sm font-mono font-bold">{writeMbps.toFixed(1)} <span className="text-[10px] font-normal text-muted-foreground">MB/s</span></div>
            </div>
          </div>
        </div>
        {/* Simple throughput bar visualization */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-muted-foreground w-10 shrink-0">Read</span>
            <div className="flex-1 h-3 rounded-full bg-muted/40 overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-emerald-500/70"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(100, (readMbps / 300) * 100)}%` }}
                transition={{ duration: 0.6 }}
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-muted-foreground w-10 shrink-0">Write</span>
            <div className="flex-1 h-3 rounded-full bg-muted/40 overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-primary/70"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(100, (writeMbps / 200) * 100)}%` }}
                transition={{ duration: 0.6 }}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Network throughput chart
function NetworkChart({ inMbps, outMbps, connections, latency }: {
  inMbps: number
  outMbps: number
  connections: number
  latency: number
}) {
  return (
    <Card className="glass-card depth-shadow bg-card/80">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Wifi className="h-4 w-4 text-primary" />
          Network
          <Badge variant="outline" className="text-[10px] font-mono border-border/50 text-muted-foreground ml-auto">
            {connections} connections
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
            <div className="h-8 w-8 rounded-lg bg-emerald-500/15 flex items-center justify-center">
              <ArrowDown className="h-4 w-4 text-emerald-500" />
            </div>
            <div>
              <div className="text-[10px] text-muted-foreground font-medium">Download</div>
              <div className="text-sm font-mono font-bold">{inMbps.toFixed(1)} <span className="text-[10px] font-normal text-muted-foreground">Mbps</span></div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
            <div className="h-8 w-8 rounded-lg bg-primary/15 flex items-center justify-center">
              <ArrowUp className="h-4 w-4 text-primary" />
            </div>
            <div>
              <div className="text-[10px] text-muted-foreground font-medium">Upload</div>
              <div className="text-sm font-mono font-bold">{outMbps.toFixed(1)} <span className="text-[10px] font-normal text-muted-foreground">Mbps</span></div>
            </div>
          </div>
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-muted-foreground w-14 shrink-0">In</span>
            <div className="flex-1 h-3 rounded-full bg-muted/40 overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-emerald-500/70"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(100, (inMbps / 120) * 100)}%` }}
                transition={{ duration: 0.6 }}
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-muted-foreground w-14 shrink-0">Out</span>
            <div className="flex-1 h-3 rounded-full bg-muted/40 overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-primary/70"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(100, (outMbps / 60) * 100)}%` }}
                transition={{ duration: 0.6 }}
              />
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between text-xs pt-2 border-t border-border/50">
          <span className="text-muted-foreground">Latency</span>
          <span className="font-mono font-medium">{latency} ms</span>
        </div>
      </CardContent>
    </Card>
  )
}

// Temperature gauges
function TemperatureGauges({ cpuPackage, gpuHotspot, gpuCore }: {
  cpuPackage: number
  gpuHotspot: number
  gpuCore: number
}) {
  const readings = [
    { label: 'CPU Package', value: cpuPackage, icon: <Cpu className="h-4 w-4" /> },
    { label: 'GPU Core', value: gpuCore, icon: <Monitor className="h-4 w-4" /> },
    { label: 'GPU Hotspot', value: gpuHotspot, icon: <Zap className="h-4 w-4" /> },
  ]

  return (
    <Card className="glass-card depth-shadow bg-card/80">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Thermometer className="h-4 w-4 text-primary" />
          Temperatures
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {readings.map((r) => {
          const isWarning = r.value > 75
          const isCritical = r.value > 85
          const tempColor = isCritical ? 'oklch(0.65 0.2 25)' : isWarning ? 'oklch(0.75 0.15 85)' : 'oklch(0.7 0.17 230)'
          const tempClass = isCritical ? 'text-red-500' : isWarning ? 'text-amber-500' : 'text-emerald-500'

          return (
            <div key={r.label} className="space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={cn('shrink-0', tempClass)}>{r.icon}</span>
                  <span className="text-sm font-medium text-foreground/80">{r.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  {isCritical && <Badge className="text-[9px] h-4 px-1 bg-red-500/15 text-red-500 border-red-500/30">CRITICAL</Badge>}
                  {isWarning && !isCritical && <Badge className="text-[9px] h-4 px-1 bg-amber-500/15 text-amber-500 border-amber-500/30">WARNING</Badge>}
                  <span className={cn('text-sm font-mono font-bold', tempClass)}>{r.value}°C</span>
                </div>
              </div>
              <div className="h-2 rounded-full bg-muted/40 overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: tempColor }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(100, (r.value / 100) * 100)}%` }}
                  transition={{ duration: 0.6 }}
                />
              </div>
              <div className="flex justify-between text-[9px] text-muted-foreground font-mono">
                <span>0°C</span>
                <span className={isWarning || isCritical ? 'text-amber-500 font-bold' : ''}>75°C</span>
                <span className={isCritical ? 'text-red-500 font-bold' : ''}>100°C</span>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

export function SystemView() {
  const { data, isLoading } = useSystemResources()

  if (isLoading) {
    return (
      <div className="p-4 sm:p-6 space-y-6">
        <div className="flex items-center gap-2">
          <Monitor className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold">System Resources</h1>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[120px] w-full rounded-xl shimmer" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[280px] w-full rounded-xl shimmer" />
          ))}
        </div>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Monitor className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold">System Resources</h1>
          <div className="flex items-center gap-1.5 ml-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-[10px] text-muted-foreground font-medium">Live</span>
          </div>
        </div>
        <span className="text-[10px] text-foreground/50 font-mono">Auto-refresh: 3s</span>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <OverviewCard
          title="CPU"
          icon={<Cpu className="h-4 w-4 text-primary" />}
          value={`${data.cpu.usage}%`}
          subValue={`${data.cpu.frequency} · ${data.cpu.temperature}°C`}
          percent={data.cpu.usage}
          delay={0}
        />
        <OverviewCard
          title="RAM"
          icon={<MemoryStick className="h-4 w-4 text-primary" />}
          value={`${data.memory.used.toFixed(1)} GB`}
          subValue={`of ${data.memory.total} GB · Swap ${data.memory.swapUsed.toFixed(1)} GB`}
          percent={data.memory.percent}
          delay={0.05}
        />
        <OverviewCard
          title="VRAM"
          icon={<Monitor className="h-4 w-4 text-primary" />}
          value={`${data.gpu.vramUsed.toFixed(1)} GB`}
          subValue={`of ${data.gpu.vramTotal} GB · ${data.gpu.powerDraw}W`}
          percent={data.gpu.vramPercent}
          delay={0.1}
        />
        <OverviewCard
          title="Temp"
          icon={<Thermometer className="h-4 w-4 text-primary" />}
          value={`${data.temperatures.cpuPackage}°C`}
          subValue={`GPU: ${data.temperatures.gpuCore}°C · Hotspot: ${data.temperatures.gpuHotspot}°C`}
          percent={Math.round((data.temperatures.cpuPackage / 100) * 100)}
          delay={0.15}
        />
      </div>

      {/* CPU Cores + Memory Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CpuCoreBars cores={data.cpu.cores} />
        <MemoryDonut
          used={data.memory.used}
          cached={data.memory.cached}
          free={data.memory.free}
          swapUsed={data.memory.swapUsed}
          swapTotal={data.memory.swapTotal}
        />
      </div>

      {/* GPU VRAM + Temperature */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <VramGauge
          vramUsed={data.gpu.vramUsed}
          vramTotal={data.gpu.vramTotal}
          vramPercent={data.gpu.vramPercent}
          history={data.gpu.vramHistory}
          temperature={data.gpu.temperature}
          hotspot={data.gpu.hotspot}
          powerDraw={data.gpu.powerDraw}
        />
        <TemperatureGauges
          cpuPackage={data.temperatures.cpuPackage}
          gpuHotspot={data.temperatures.gpuHotspot}
          gpuCore={data.temperatures.gpuCore}
        />
      </div>

      {/* Disk I/O + Network */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DiskIOChart
          readMbps={data.disk.readMbps}
          writeMbps={data.disk.writeMbps}
          used={data.disk.used}
          total={data.disk.total}
          percent={data.disk.percent}
        />
        <NetworkChart
          inMbps={data.network.inMbps}
          outMbps={data.network.outMbps}
          connections={data.network.connections}
          latency={data.network.latency}
        />
      </div>
    </div>
  )
}
