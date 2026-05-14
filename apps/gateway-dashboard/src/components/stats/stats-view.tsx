'use client'

import { useStats, useServerStatus, useSystemResources } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { useKimariStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import {
  Activity,
  Thermometer,
  Zap,
  Fan,
  Clock,
  Gauge,
  Server,
  Timer,
  Hash,
  HardDrive,
  MemoryStick,
  Radio,
  ArrowRight,
  RefreshCw,
  Cpu,
  Wifi,
  Play,
  History,
  Monitor,
} from 'lucide-react'
import { useEffect, useState, useRef } from 'react'

function formatUptime(seconds: number): string {
  if (!seconds) return '0s'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}h ${m}m ${s}s`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

function formatMB(mb: number): string {
  if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`
  return `${mb} MB`
}

// Animated number component that smoothly transitions
function AnimatedNumber({ value, decimals = 0, suffix = '' }: { value: number; decimals?: number; suffix?: string }) {
  const [display, setDisplay] = useState(value)
  const prevRef = useRef(value)

  useEffect(() => {
    const prev = prevRef.current
    prevRef.current = value
    const diff = value - prev
    const steps = 12
    let step = 0

    const interval = setInterval(() => {
      step++
      const progress = step / steps
      const eased = 1 - Math.pow(1 - progress, 3) // easeOutCubic
      const current = prev + diff * eased
      setDisplay(current)
      if (step >= steps) clearInterval(interval)
    }, 25)

    return () => clearInterval(interval)
  }, [value])

  return (
    <span className="tabular-nums">
      {display.toFixed(decimals)}{suffix}
    </span>
  )
}

function StatCard({
  title,
  value,
  suffix,
  icon,
  color,
  decimals = 0,
}: {
  title: string
  value: number
  suffix?: string
  icon: React.ReactNode
  color: string
  decimals?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="glass-card depth-shadow card-shine">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-muted-foreground">{title}</span>
            <div className={cn('h-7 w-7 rounded-lg flex items-center justify-center', color)}>
              {icon}
            </div>
          </div>
          <div className="text-2xl font-bold tracking-tight">
            <AnimatedNumber value={value} decimals={decimals} suffix={suffix} />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function GpuMiniCard({
  label,
  value,
  unit,
  icon,
  colorClass,
}: {
  label: string
  value: number
  unit: string
  icon: React.ReactNode
  colorClass: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="glass-card depth-shadow">
        <CardContent className="p-4 text-center">
          <div className={cn('mx-auto mb-2 h-8 w-8 rounded-lg flex items-center justify-center', colorClass)}>
            {icon}
          </div>
          <div className="text-xl font-bold tabular-nums">
            <AnimatedNumber value={value} decimals={0} />
          </div>
          <div className="text-[10px] text-muted-foreground mt-0.5">{unit}</div>
          <div className="text-xs font-medium text-muted-foreground mt-1">{label}</div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function VramGauge({ vramUsage }: { vramUsage: { used: number; total: number; percent: number } }) {
  const usedPercent = vramUsage.percent
  const modelPercent = 47
  const contextPercent = 6
  const overheadPercent = 3.5
  const freePercent = Math.max(0, 100 - modelPercent - contextPercent - overheadPercent)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
    >
      <Card className="glass-card depth-shadow">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <HardDrive className="h-4 w-4 text-primary" />
            VRAM Usage
            <Badge variant="outline" className="ml-auto font-mono text-xs border-primary/30 text-primary">
              <AnimatedNumber value={usedPercent} decimals={1} suffix="%" />
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Main horizontal bar */}
          <div className="h-8 rounded-lg overflow-hidden bg-muted/50 flex">
            <motion.div
              className="h-full bg-gradient-to-r from-primary/80 to-primary/60 flex items-center justify-center"
              initial={{ width: 0 }}
              animate={{ width: `${modelPercent}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            >
              <span className="text-[10px] font-bold text-primary-foreground drop-shadow-sm">Model</span>
            </motion.div>
            <motion.div
              className="h-full bg-gradient-to-r from-cyan-500/80 to-cyan-500/60 flex items-center justify-center"
              initial={{ width: 0 }}
              animate={{ width: `${contextPercent}%` }}
              transition={{ duration: 0.8, ease: 'easeOut', delay: 0.1 }}
            >
              <span className="text-[10px] font-bold text-white drop-shadow-sm">Ctx</span>
            </motion.div>
            <motion.div
              className="h-full bg-gradient-to-r from-amber-500/80 to-amber-500/60 flex items-center justify-center"
              initial={{ width: 0 }}
              animate={{ width: `${overheadPercent}%` }}
              transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
            >
              <span className="text-[10px] font-bold text-white drop-shadow-sm">Ovh</span>
            </motion.div>
            <div className="h-full flex-1 bg-muted/30 flex items-center justify-center">
              <span className="text-[10px] text-muted-foreground">Free</span>
            </div>
          </div>
          {/* Legend */}
          <div className="flex items-center gap-4 mt-3">
            <div className="flex items-center gap-1.5">
              <div className="h-2.5 w-2.5 rounded-sm bg-primary/70" />
              <span className="text-[10px] text-muted-foreground">Model</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="h-2.5 w-2.5 rounded-sm bg-cyan-500/70" />
              <span className="text-[10px] text-muted-foreground">Context</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="h-2.5 w-2.5 rounded-sm bg-amber-500/70" />
              <span className="text-[10px] text-muted-foreground">Overhead</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="h-2.5 w-2.5 rounded-sm bg-muted/50" />
              <span className="text-[10px] text-muted-foreground">Free</span>
            </div>
          </div>
          {/* Detailed numbers */}
          <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Used</span>
              <span className="font-mono font-medium">{formatMB(vramUsage.used)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total</span>
              <span className="font-mono font-medium">{formatMB(vramUsage.total)}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function TokenDisplay({
  label,
  value,
  icon,
  color,
}: {
  label: string
  value: number
  icon: React.ReactNode
  color: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="glass-card depth-shadow card-shine">
        <CardContent className="p-6 text-center">
          <div className={cn('mx-auto mb-3 h-10 w-10 rounded-xl flex items-center justify-center', color)}>
            {icon}
          </div>
          <div className="text-4xl font-bold tracking-tight tabular-nums">
            <AnimatedNumber value={value} decimals={1} />
          </div>
          <div className="text-sm text-muted-foreground mt-1">tok/s</div>
          <div className="text-xs font-medium text-muted-foreground mt-2">{label}</div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function MemoryBar({
  label,
  value,
  total,
  color,
}: {
  label: string
  value: number
  total: number
  color: string
}) {
  const percent = Math.min((value / total) * 100, 100)

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-mono font-medium">{formatMB(value)}</span>
      </div>
      <div className="h-2 rounded-full bg-muted/50 overflow-hidden">
        <motion.div
          className={cn('h-full rounded-full', color)}
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

// Mini circular gauge for offline state (declared outside component to avoid re-creation)
function OfflineMiniGauge({ percent, label, icon, size = 60 }: { percent: number; label: string; icon: React.ReactNode; size?: number }) {
  const strokeWidth = size * 0.1
  const radius = (size - strokeWidth) / 2
  const center = size / 2
  const circumference = 2 * Math.PI * radius
  const arcLength = circumference * 0.75
  const gapLength = circumference * 0.25
  const rotation = 135
  const pct = Math.min(percent, 100) / 100

  const color = percent >= 80 ? 'oklch(0.63 0.22 25)' : percent >= 50 ? 'oklch(0.75 0.15 85)' : 'oklch(0.72 0.17 230)'
  const textColor = percent >= 80 ? 'text-red-600 dark:text-red-400' : percent >= 50 ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="transform -rotate-90">
          <circle
            cx={center} cy={center} r={radius} fill="none" stroke="currentColor"
            strokeWidth={strokeWidth} className="text-muted/20"
            strokeDasharray={`${arcLength} ${gapLength}`} strokeLinecap="round"
            transform={`rotate(${rotation}, ${center}, ${center})`}
          />
          <motion.circle
            cx={center} cy={center} r={radius} fill="none" stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${gapLength}`} strokeLinecap="round"
            transform={`rotate(${rotation}, ${center}, ${center})`}
            initial={{ strokeDashoffset: arcLength }}
            animate={{ strokeDashoffset: arcLength - arcLength * pct }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          {icon}
        </div>
      </div>
      <span className={cn('text-xs font-bold tabular-nums', textColor)}>{Math.round(percent)}%</span>
      <span className="text-[10px] text-muted-foreground">{label}</span>
    </div>
  )
}

function ServerStoppedState() {
  const setActiveView = useKimariStore((s) => s.setActiveView)
  const { data: resources, isLoading: resourcesLoading } = useSystemResources()

  // Mock last session data
  const lastSession = {
    duration: '2h 34m',
    model: 'kimari-4b-q4_k_m.gguf',
    profile: 'RTX 4070 Ti - Q4_K_M',
    promptSpeed: 87.3,
    genSpeed: 31.8,
    totalRequests: 1247,
    avgLatency: 142,
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6 p-6"
    >
      {/* Main offline card */}
      <Card className="glass-card depth-shadow card-shine overflow-hidden relative pulse-border">
        {/* Gradient background accent */}
        <div className="absolute inset-0 pointer-events-none bg-gradient-to-br from-primary/5 via-transparent to-cyan-500/5" />
        <CardContent className="p-8 relative">
          <div className="flex flex-col items-center text-center mb-6">
            <div className="mx-auto mb-4 h-16 w-16 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20 flex items-center justify-center">
              <Radio className="h-8 w-8 text-primary/50" />
            </div>
            <h2 className="text-lg font-semibold mb-2">Server Offline</h2>
            <p className="text-sm text-muted-foreground max-w-md">
              Start the server to see live GPU metrics, token throughput, and request performance in real-time.
            </p>
          </div>

          {/* Call-to-action button */}
          <div className="flex justify-center mb-8">
            <Button
              className="gap-2 btn-press bg-gradient-to-r from-emerald-600/90 to-emerald-500/90 hover:from-emerald-600 hover:to-emerald-500 text-white h-12 px-8 text-base font-semibold shadow-lg shadow-emerald-500/25"
              onClick={() => setActiveView('server')}
            >
              <Play className="h-5 w-5" />
              Start Server to View Live Stats
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Two-column layout: System Info + Last Session */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Info Summary */}
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="glass-card depth-shadow h-full">
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Monitor className="h-4 w-4 text-primary" />
                System Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground/80 flex items-center gap-2">
                    <Cpu className="h-3.5 w-3.5" /> CPU
                  </span>
                  <span className="font-mono font-medium">8 Cores / 16 Threads</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground/80 flex items-center gap-2">
                    <MemoryStick className="h-3.5 w-3.5" /> RAM
                  </span>
                  <span className="font-mono font-medium">32 GB DDR5</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground/80 flex items-center gap-2">
                    <Zap className="h-3.5 w-3.5" /> GPU
                  </span>
                  <span className="font-mono font-medium">NVIDIA RTX 4070 Ti</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground/80 flex items-center gap-2">
                    <HardDrive className="h-3.5 w-3.5" /> VRAM
                  </span>
                  <span className="font-mono font-medium">12 GB GDDR6X</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground/80 flex items-center gap-2">
                    <Wifi className="h-3.5 w-3.5" /> Network
                  </span>
                  <span className="font-mono font-medium">1 Gbps Ethernet</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Last Session Summary */}
        <motion.div
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
        >
          <Card className="glass-card depth-shadow h-full">
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <History className="h-4 w-4 text-primary" />
                Last Session
                <Badge variant="outline" className="ml-auto text-[10px] border-primary/30 text-primary">2h ago</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Duration</span>
                  <span className="font-mono font-medium">{lastSession.duration}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Model</span>
                  <span className="font-mono font-medium text-xs truncate max-w-[180px]">{lastSession.model}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Profile</span>
                  <span className="font-mono font-medium text-xs truncate max-w-[180px]">{lastSession.profile}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Prompt Speed</span>
                  <Badge variant="outline" className="border-emerald-500/30 text-emerald-600 dark:text-emerald-400 font-mono">
                    {lastSession.promptSpeed} tok/s
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Gen Speed</span>
                  <Badge variant="outline" className="border-cyan-500/30 text-cyan-600 dark:text-cyan-400 font-mono">
                    {lastSession.genSpeed} tok/s
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Total Requests</span>
                  <span className="font-mono font-medium">{lastSession.totalRequests.toLocaleString()}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Current System Resources (idle) */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="glass-card depth-shadow">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              System Resources
              <Badge variant="outline" className="ml-auto text-[10px] border-border/50 text-muted-foreground">Idle</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {resourcesLoading ? (
              <div className="flex items-center justify-around py-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="flex flex-col items-center gap-2">
                    <Skeleton className="h-[60px] w-[60px] rounded-full shimmer" />
                    <Skeleton className="h-3 w-10 shimmer" />
                  </div>
                ))}
              </div>
            ) : resources ? (
              <div className="flex items-center justify-around py-2">
                <OfflineMiniGauge
                  percent={resources.cpu.usage}
                  label="CPU"
                  icon={<Cpu className="h-4 w-4 text-primary/60" />}
                />
                <OfflineMiniGauge
                  percent={resources.memory.percent}
                  label="RAM"
                  icon={<MemoryStick className="h-4 w-4 text-primary/60" />}
                />
                <OfflineMiniGauge
                  percent={resources.disk.percent}
                  label="Disk"
                  icon={<HardDrive className="h-4 w-4 text-primary/60" />}
                />
              </div>
            ) : (
              <div className="text-center py-4 text-sm text-muted-foreground">
                Unable to load system resources
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center gap-3">
        <Skeleton className="h-8 w-40 shimmer" />
        <Skeleton className="h-5 w-16 shimmer" />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-[88px] w-full rounded-xl shimmer" />
        ))}
      </div>
      <Skeleton className="h-[160px] w-full rounded-xl shimmer" />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-[120px] w-full rounded-xl shimmer" />
        ))}
      </div>
    </div>
  )
}

export function StatsView() {
  const { data, isLoading, dataUpdatedAt } = useStats()
  const { data: serverStatus } = useServerStatus()
  const lastRefresh = dataUpdatedAt ? new Date(dataUpdatedAt) : new Date()

  if (isLoading) {
    return <LoadingSkeleton />
  }

  const isRunning = serverStatus?.status === 'running' || data?.serverRunning === true
  const stats = data?.stats

  if (!isRunning || !stats) {
    return <ServerStoppedState />
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header with Live badge and auto-refresh indicator */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold">Live Server Stats</h2>
          <Badge className="bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1.5 px-2.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            Live
          </Badge>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <RefreshCw className="h-3 w-3 animate-spin-slow" />
          <span>Auto-refresh: 3s</span>
          <span className="text-border">|</span>
          <span>Updated {lastRefresh.toLocaleTimeString()}</span>
        </div>
      </motion.div>

      {/* 4 Stat Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Requests"
          value={stats.requestStats.active}
          icon={<Activity className="h-4 w-4 text-primary-foreground" />}
          color="bg-gradient-to-br from-primary to-primary/70"
        />
        <StatCard
          title="Avg Latency"
          value={stats.requestStats.avgLatency}
          suffix=" ms"
          decimals={0}
          icon={<Timer className="h-4 w-4 text-cyan-50" />}
          color="bg-gradient-to-br from-cyan-500 to-cyan-500/70"
        />
        <StatCard
          title="Queue Depth"
          value={stats.requestStats.queueDepth}
          icon={<Hash className="h-4 w-4 text-amber-50" />}
          color="bg-gradient-to-br from-amber-500 to-amber-500/70"
        />
        <StatCard
          title="Total Processed"
          value={stats.requestStats.total}
          icon={<Gauge className="h-4 w-4 text-primary-foreground" />}
          color="bg-gradient-to-br from-primary/80 to-primary/50"
        />
      </div>

      {/* VRAM Gauge */}
      <VramGauge vramUsage={stats.vramUsage} />

      {/* GPU Stats Section */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground mb-3 flex items-center gap-2">
          <Thermometer className="h-3.5 w-3.5" />
          GPU Statistics
        </h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <GpuMiniCard
            label="Temperature"
            value={stats.gpuStats.temperature}
            unit="°C"
            icon={<Thermometer className="h-4 w-4 text-red-100" />}
            colorClass="bg-gradient-to-br from-red-500/80 to-red-500/50"
          />
          <GpuMiniCard
            label="Power Draw"
            value={stats.gpuStats.powerDraw}
            unit="W"
            icon={<Zap className="h-4 w-4 text-amber-100" />}
            colorClass="bg-gradient-to-br from-amber-500/80 to-amber-500/50"
          />
          <GpuMiniCard
            label="Fan Speed"
            value={stats.gpuStats.fanSpeed}
            unit="%"
            icon={<Fan className="h-4 w-4 text-cyan-100" />}
            colorClass="bg-gradient-to-br from-cyan-500/80 to-cyan-500/50"
          />
          <GpuMiniCard
            label="Clock Speed"
            value={stats.gpuStats.clockSpeed}
            unit="MHz"
            icon={<Clock className="h-4 w-4 text-primary-foreground" />}
            colorClass="bg-gradient-to-br from-primary/80 to-primary/50"
          />
        </div>
      </div>

      {/* Token Performance Section */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground mb-3 flex items-center gap-2">
          <Zap className="h-3.5 w-3.5" />
          Token Performance
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <TokenDisplay
            label="Prompt Processing"
            value={stats.tokensPerSec.prompt}
            icon={<Zap className="h-5 w-5 text-primary-foreground" />}
            color="bg-gradient-to-br from-primary to-primary/70"
          />
          <TokenDisplay
            label="Text Generation"
            value={stats.tokensPerSec.generation}
            icon={<Activity className="h-5 w-5 text-cyan-50" />}
            color="bg-gradient-to-br from-cyan-500 to-cyan-500/70"
          />
        </div>
      </div>

      {/* Memory Breakdown Section */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="glass-card depth-shadow">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <MemoryStick className="h-4 w-4 text-primary" />
              Memory Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <MemoryBar
              label="Model Size"
              value={stats.memoryStats.modelSize}
              total={stats.vramUsage.total}
              color="bg-gradient-to-r from-primary/80 to-primary/50"
            />
            <MemoryBar
              label="Context Size"
              value={stats.memoryStats.contextSize}
              total={stats.vramUsage.total}
              color="bg-gradient-to-r from-cyan-500/80 to-cyan-500/50"
            />
            <MemoryBar
              label="Overhead"
              value={stats.memoryStats.overhead}
              total={stats.vramUsage.total}
              color="bg-gradient-to-r from-amber-500/80 to-amber-500/50"
            />
            <div className="pt-2 border-t border-border/50 flex items-center justify-between text-xs">
              <span className="font-medium">Total Allocated</span>
              <span className="font-mono font-bold text-primary">
                {formatMB(stats.memoryStats.total)}
              </span>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Server Info Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.3 }}
      >
        <Card className="glass-card depth-shadow">
          <CardContent className="p-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="flex items-center gap-2">
                <Clock className="h-3.5 w-3.5 text-primary" />
                <div>
                  <div className="text-muted-foreground">Uptime</div>
                  <div className="font-mono font-medium">{formatUptime(stats.serverInfo.uptime)}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Server className="h-3.5 w-3.5 text-primary" />
                <div>
                  <div className="text-muted-foreground">Model</div>
                  <div className="font-mono font-medium truncate max-w-[150px]">{stats.serverInfo.model}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Gauge className="h-3.5 w-3.5 text-primary" />
                <div>
                  <div className="text-muted-foreground">Profile</div>
                  <div className="font-mono font-medium">{stats.serverInfo.profile}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Timer className="h-3.5 w-3.5 text-primary" />
                <div>
                  <div className="text-muted-foreground">Last Request</div>
                  <div className="font-mono font-medium">
                    {new Date(stats.serverInfo.lastRequest).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
