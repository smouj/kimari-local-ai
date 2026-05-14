'use client'

import { useSystemResources } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Cpu, HardDrive, MemoryStick, Wifi } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

// Color coding based on percentage
function getGaugeColor(percent: number): { stroke: string; text: string; bg: string } {
  if (percent >= 80) {
    return {
      stroke: 'oklch(0.63 0.22 25)',
      text: 'text-red-600 dark:text-red-400',
      bg: 'bg-red-500/10',
    }
  }
  if (percent >= 50) {
    return {
      stroke: 'oklch(0.75 0.15 85)',
      text: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-500/10',
    }
  }
  return {
    stroke: 'oklch(0.72 0.17 230)',
    text: 'text-emerald-600 dark:text-emerald-400',
    bg: 'bg-emerald-500/10',
  }
}

// Animated circular SVG gauge
function CircularGauge({
  percent,
  label,
  icon,
  detail,
  size = 90,
}: {
  percent: number
  label: string
  icon: React.ReactNode
  detail?: string
  size?: number
}) {
  const colors = getGaugeColor(percent)
  const strokeWidth = size * 0.09
  const radius = (size - strokeWidth) / 2
  const center = size / 2
  const circumference = 2 * Math.PI * radius
  const arcLength = circumference * 0.75 // 270 degrees
  const gapLength = circumference * 0.25
  const rotation = 135
  const pct = Math.min(percent, 100) / 100

  const [animatedPercent, setAnimatedPercent] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedPercent(percent), 50)
    return () => clearTimeout(timer)
  }, [percent])

  const currentPct = Math.min(animatedPercent, 100) / 100

  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="relative">
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="transform -rotate-90"
        >
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-muted/20"
            strokeDasharray={`${arcLength} ${gapLength}`}
            strokeLinecap="round"
            transform={`rotate(${rotation}, ${center}, ${center})`}
          />
          {/* Value arc */}
          <motion.circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${gapLength}`}
            strokeLinecap="round"
            transform={`rotate(${rotation}, ${center}, ${center})`}
            initial={{ strokeDashoffset: arcLength }}
            animate={{ strokeDashoffset: arcLength - arcLength * currentPct }}
            transition={{ duration: 1, ease: 'easeOut' }}
            style={{
              filter: `drop-shadow(0 0 4px ${colors.stroke})`,
            }}
          />
        </svg>
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={cn('mb-0.5', colors.bg, 'rounded-lg p-1')}>
            {icon}
          </div>
          <motion.span
            className={cn('text-sm font-bold tabular-nums', colors.text)}
            key={Math.round(percent)}
            initial={{ opacity: 0.5, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            {Math.round(percent)}%
          </motion.span>
        </div>
      </div>
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      {detail && (
        <span className="text-[10px] text-muted-foreground/70 tabular-nums">{detail}</span>
      )}
    </div>
  )
}

function SystemResourcesLoading() {
  return (
    <Card className="glass-card depth-shadow card-shine">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          System Resources
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-around py-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex flex-col items-center gap-2">
              <Skeleton className="h-[90px] w-[90px] rounded-full shimmer" />
              <Skeleton className="h-3 w-12 shimmer" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export function SystemResources() {
  const { data, isLoading } = useSystemResources()

  if (isLoading || !data) {
    return <SystemResourcesLoading />
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
    >
      <Card className="glass-card depth-shadow card-shine">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Cpu className="h-4 w-4 text-primary" />
            System Resources
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-around py-2">
            <CircularGauge
              percent={data.cpu.usage}
              label="CPU"
              icon={<Cpu className="h-3.5 w-3.5 text-primary" />}
              detail={data.cpu.frequency}
            />
            <CircularGauge
              percent={data.memory.percent}
              label="Memory"
              icon={<MemoryStick className="h-3.5 w-3.5 text-primary" />}
              detail={`${data.memory.used} / ${data.memory.total} GB`}
            />
            <CircularGauge
              percent={data.disk.percent}
              label="Disk"
              icon={<HardDrive className="h-3.5 w-3.5 text-primary" />}
              detail={`${data.disk.used} GB`}
            />
            <CircularGauge
              percent={Math.min(
                (data.network.connections / 50) * 100,
                100
              )}
              label="Network"
              icon={<Wifi className="h-3.5 w-3.5 text-primary" />}
              detail={`${data.network.inMbps} Mbps`}
            />
          </div>
          {/* Detail row */}
          <div className="grid grid-cols-4 gap-2 mt-3 pt-3 border-t border-border/50">
            <div className="text-center">
              <div className="text-[10px] text-muted-foreground">Cores</div>
              <div className="text-xs font-mono font-medium">{data.cpu.coreCount}</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-muted-foreground">Temp</div>
              <div className="text-xs font-mono font-medium">{data.cpu.temperature}°C</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-muted-foreground">R/W</div>
              <div className="text-xs font-mono font-medium truncate">{data.disk.readMbps}/{data.disk.writeMbps}</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-muted-foreground">Latency</div>
              <div className="text-xs font-mono font-medium">{data.network.latency} ms</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
