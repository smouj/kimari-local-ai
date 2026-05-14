'use client'

import { useSystemResources } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Cpu, HardDrive, MemoryStick, Wifi } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

function getColor(percent: number) {
  if (percent < 50) return { stroke: 'oklch(0.7 0.17 230)', text: 'text-emerald-500', bg: 'text-emerald-500/20' }
  if (percent < 80) return { stroke: 'oklch(0.75 0.15 85)', text: 'text-amber-500', bg: 'text-amber-500/20' }
  return { stroke: 'oklch(0.65 0.2 25)', text: 'text-red-500', bg: 'text-red-500/20' }
}

function CircularGauge({ percent, size = 80, strokeWidth = 6 }: { percent: number; size?: number; strokeWidth?: number }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (percent / 100) * circumference
  const color = getColor(percent)

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Background ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-muted/30"
        />
        {/* Progress ring */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color.stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={cn('text-lg font-bold tabular-nums', color.text)}>
          {Math.round(percent)}%
        </span>
      </div>
    </div>
  )
}

function ResourceCard({
  title,
  icon,
  percent,
  children,
  delay = 0,
}: {
  title: string
  icon: React.ReactNode
  percent: number
  children: React.ReactNode
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <Card className="glass-card depth-shadow card-shine bg-card/80 h-full">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            {icon}
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center gap-3">
          <CircularGauge percent={percent} />
          <div className="w-full space-y-1.5 text-xs text-foreground/70">
            {children}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function StatRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between">
      <span>{label}</span>
      <span className="font-mono font-medium text-foreground/90">{value}</span>
    </div>
  )
}

export function SystemResourcesWidget() {
  const { data, isLoading } = useSystemResources()

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          <h2 className="text-base font-semibold">System Resources</h2>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[200px] w-full rounded-xl shimmer" />
          ))}
        </div>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Cpu className="h-4 w-4 text-primary" />
        <h2 className="text-base font-semibold">System Resources</h2>
        <span className="text-[10px] text-foreground/50 font-mono ml-auto">Auto-refresh: 3s</span>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <ResourceCard title="CPU" icon={<Cpu className="h-4 w-4 text-primary" />} percent={data.cpu.usage} delay={0}>
          <StatRow label="Cores" value={data.cpu.coreCount} />
          <StatRow label="Temperature" value={`${data.cpu.temperature}°C`} />
          <StatRow label="Frequency" value={data.cpu.frequency} />
        </ResourceCard>

        <ResourceCard title="Memory" icon={<MemoryStick className="h-4 w-4 text-primary" />} percent={data.memory.percent} delay={0.05}>
          <StatRow label="Used / Total" value={`${data.memory.used} / ${data.memory.total} GB`} />
          <StatRow label="Swap" value={`${data.memory.swapUsed} / ${data.memory.swapTotal} GB`} />
        </ResourceCard>

        <ResourceCard title="Disk" icon={<HardDrive className="h-4 w-4 text-primary" />} percent={data.disk.percent} delay={0.1}>
          <StatRow label="Used / Total" value={`${data.disk.used} / ${data.disk.total} GB`} />
          <StatRow label="Read" value={`${data.disk.readMbps} MB/s`} />
          <StatRow label="Write" value={`${data.disk.writeMbps} MB/s`} />
        </ResourceCard>

        <ResourceCard title="Network" icon={<Wifi className="h-4 w-4 text-primary" />} percent={0} delay={0.15}>
          <StatRow label="Download" value={`${data.network.inMbps} Mbps`} />
          <StatRow label="Upload" value={`${data.network.outMbps} Mbps`} />
          <StatRow label="Connections" value={data.network.connections} />
          <StatRow label="Latency" value={`${data.network.latency} ms`} />
        </ResourceCard>
      </div>
    </div>
  )
}
