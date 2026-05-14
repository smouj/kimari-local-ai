'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useAnalytics } from '@/hooks/use-api'
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts'
import { motion } from 'framer-motion'
import {
  Activity,
  Clock,
  Zap,
  AlertTriangle,
  Thermometer,
  Cpu,
  TrendingUp,
  BarChart3,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const timeRanges = [
  { value: '24h', label: '24h' },
  { value: '7d', label: '7d' },
  { value: '30d', label: '30d' },
] as const

// Custom Chart Tooltip Component
function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card rounded-lg p-3 shadow-lg border border-border/50 min-w-[160px]">
      <p className="text-xs font-medium text-muted-foreground mb-2">{label}</p>
      {payload.map((entry: any, i: number) => (
        <div key={i} className="flex items-center justify-between gap-4 py-0.5">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-xs text-muted-foreground">{entry.name}</span>
          </div>
          <span className="text-xs font-mono font-medium">{typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value}</span>
        </div>
      ))}
    </div>
  )
}

function formatTimestamp(ts: string, range: string) {
  const d = new Date(ts)
  if (range === '24h') {
    return `${String(d.getHours()).padStart(2, '0')}:00`
  }
  return `${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

// Summary Stat Card Component
function StatCard({
  icon: Icon,
  label,
  value,
  subValue,
  trend,
  color,
  delay = 0,
}: {
  icon: React.ElementType
  label: string
  value: string
  subValue?: string
  trend?: 'up' | 'down' | 'neutral'
  color: string
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
    >
      <Card className="glass-card card-hover-lift depth-shadow card-shine relative overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground">{label}</p>
              <p className="text-2xl font-bold tracking-tight">{value}</p>
              {subValue && (
                <p className="text-xs text-muted-foreground">{subValue}</p>
              )}
            </div>
            <div className={cn('rounded-xl p-2.5', color)}>
              <Icon className="h-5 w-5" />
            </div>
          </div>
          {trend && (
            <div className="mt-3 flex items-center gap-1.5">
              <TrendingUp
                className={cn(
                  'h-3 w-3',
                  trend === 'up' && 'text-emerald-500 rotate-0',
                  trend === 'down' && 'text-red-500 rotate-180',
                  trend === 'neutral' && 'text-muted-foreground rotate-90'
                )}
              />
              <span
                className={cn(
                  'text-[11px] font-medium',
                  trend === 'up' && 'text-emerald-500',
                  trend === 'down' && 'text-red-500',
                  trend === 'neutral' && 'text-muted-foreground'
                )}
              >
                {trend === 'up' ? 'Increasing' : trend === 'down' ? 'Decreasing' : 'Stable'}
              </span>
            </div>
          )}
        </CardContent>
        <div className="absolute bottom-0 left-0 right-0 h-[2px] rounded-b-xl" style={{ background: color.includes('primary') ? 'oklch(0.65 0.17 165 / 40%)' : color.includes('cyan') ? 'oklch(0.6 0.15 200 / 40%)' : color.includes('amber') ? 'oklch(0.7 0.14 75 / 40%)' : 'oklch(0.6 0.18 25 / 40%)' }} />
      </Card>
    </motion.div>
  )
}

// Chart Card Wrapper
function ChartCard({
  title,
  icon: Icon,
  iconColor,
  badge,
  children,
  delay = 0,
}: {
  title: string
  icon: React.ElementType
  iconColor: string
  badge?: React.ReactNode
  children: React.ReactNode
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
    >
      <Card className="glass-card depth-shadow">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Icon className={cn('h-4 w-4', iconColor)} />
              {title}
            </CardTitle>
            {badge}
          </div>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </motion.div>
  )
}

// Loading Skeleton for Charts
function ChartSkeleton() {
  return (
    <div className="h-[280px] w-full flex flex-col gap-3 p-4">
      <div className="flex items-end gap-2 h-full">
        {Array.from({ length: 12 }, (_, i) => (
          <Skeleton
            key={i}
            className="flex-1 bg-muted/30 rounded-t"
            style={{ height: `${30 + Math.random() * 60}%` }}
          />
        ))}
      </div>
    </div>
  )
}

export function AnalyticsView() {
  const [timeRange, setTimeRange] = useState<string>('24h')
  const { data, isLoading, isError } = useAnalytics(timeRange)

  if (isError) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center space-y-3">
            <div className="w-12 h-12 rounded-xl bg-destructive/10 flex items-center justify-center mx-auto">
              <AlertTriangle className="h-6 w-6 text-destructive" />
            </div>
            <p className="text-sm font-medium text-destructive">Failed to load analytics data</p>
            <p className="text-xs text-muted-foreground">Please try again later</p>
          </div>
        </div>
      </div>
    )
  }

  // Check if data exists but all arrays are empty
  const hasEmptyData = data && (
    data.gpuMetrics.dataPoints.length === 0 &&
    data.requestHistory.hourlyData.length === 0 &&
    data.latency.trendData.length === 0 &&
    data.errorRate.dailyData.length === 0
  )

  return (
    <div className="p-6 space-y-6">
      {/* Time Range Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">Performance Analytics</h2>
          <p className="text-sm text-muted-foreground mt-0.5">Historical metrics and request analytics</p>
        </div>
        <div className="flex items-center gap-1 bg-muted/50 rounded-lg p-1">
          {timeRanges.map((range) => (
            <Button
              key={range.value}
              variant={timeRange === range.value ? 'default' : 'ghost'}
              size="sm"
              className={cn(
                'h-8 px-3 text-xs font-medium transition-all btn-press',
                timeRange === range.value
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              )}
              onClick={() => setTimeRange(range.value)}
            >
              {range.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Summary Stats Row */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }, (_, i) => (
            <Card key={i} className="glass-card">
              <CardContent className="p-6 space-y-3">
                <Skeleton className="h-3 w-20 bg-muted/30" />
                <Skeleton className="h-8 w-24 bg-muted/30" />
                <Skeleton className="h-3 w-16 bg-muted/30" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={BarChart3}
            label="Total Requests"
            value={data.requestHistory.total.toLocaleString()}
            subValue={`${data.requestHistory.avgTokensPerRequest} avg tokens/req`}
            trend="up"
            color="bg-primary/15 text-primary"
            delay={0}
          />
          <StatCard
            icon={Clock}
            label="Avg Latency"
            value={`${data.latency.avgTtft}ms`}
            subValue={`TTFT · ${data.latency.avgGenTime}s gen time`}
            trend="down"
            color="bg-cyan-500/15 text-cyan-500"
            delay={0.05}
          />
          <StatCard
            icon={Zap}
            label="Avg Throughput"
            value={`${(data.latency.trendData.reduce((s, d) => s + d.tokensPerSec, 0) / data.latency.trendData.length).toFixed(1)} tok/s`}
            subValue="Token generation speed"
            trend="up"
            color="bg-amber-500/15 text-amber-500"
            delay={0.1}
          />
          <StatCard
            icon={AlertTriangle}
            label="Error Rate"
            value={`${data.errorRate.errorRatePercent}%`}
            subValue={`${data.errorRate.errors} of ${data.errorRate.total} requests`}
            trend={data.errorRate.errorRatePercent > 2 ? 'up' : 'neutral'}
            color="bg-rose-500/15 text-rose-500"
            delay={0.15}
          />
        </div>
      ) : null}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* GPU Metrics - VRAM + Temperature */}
        {isLoading ? (
          <ChartSkeleton />
        ) : data ? (
          <ChartCard
            title="GPU Metrics"
            icon={Cpu}
            iconColor="text-primary"
            badge={
              <>
                <Badge variant="outline" className="text-[10px] h-5 gap-1 border-primary/30 text-primary">
                  <Thermometer className="h-2.5 w-2.5" />
                  Live
                </Badge>
                <Badge variant="outline" className="text-[10px] h-5 border-border/50 text-muted-foreground">
                  Last {timeRange}
                </Badge>
              </>
            }
            delay={0.2}
          >
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.gpuMetrics.dataPoints.map((d) => ({
                  ...d,
                  time: formatTimestamp(d.timestamp, timeRange),
                  vramPercent: Math.round((d.vramUsed / d.vramTotal) * 100),
                }))} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                  <defs>
                    <linearGradient id="vramGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0.35} />
                      <stop offset="50%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0.1} />
                      <stop offset="95%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="oklch(0.65 0.15 45)" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="oklch(0.65 0.15 45)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" vertical={false} />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    yAxisId="vram"
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v) => `${v}%`}
                    domain={[40, 100]}
                    label={{ value: 'VRAM %', angle: -90, position: 'insideLeft', style: { fontSize: 11, fill: 'oklch(0.65 0.04 230)' } }}
                  />
                  <YAxis
                    yAxisId="temp"
                    orientation="right"
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v) => `${v}°C`}
                    domain={[40, 95]}
                    label={{ value: 'Temp °C', angle: 90, position: 'insideRight', style: { fontSize: 11, fill: 'oklch(0.65 0.15 45)' } }}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'oklch(0.65 0.17 165 / 30%)', strokeWidth: 1 }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <ReferenceLine yAxisId="vram" y={80} stroke="oklch(0.6 0.15 25 / 30%)" strokeDasharray="4 4" label={{ value: '80%', position: 'right', style: { fontSize: 10, fill: 'oklch(0.6 0.15 25 / 60%)' } }} />
                  <Area
                    yAxisId="vram"
                    type="monotone"
                    dataKey="vramPercent"
                    name="VRAM %"
                    stroke="oklch(0.65 0.17 230)"
                    fill="url(#vramGrad)"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 2 }}
                    animationDuration={800}
                  />
                  <Area
                    yAxisId="temp"
                    type="monotone"
                    dataKey="gpuTemp"
                    name="GPU Temp °C"
                    stroke="oklch(0.65 0.15 45)"
                    fill="url(#tempGrad)"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 2 }}
                    animationDuration={800}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        ) : null}

        {/* Request Volume */}
        {isLoading ? (
          <ChartSkeleton />
        ) : data ? (
          <ChartCard
            title="Request Volume"
            icon={Activity}
            iconColor="text-cyan-500"
            badge={
              <>
                <Badge variant="outline" className="text-[10px] h-5 gap-1 border-cyan-500/30 text-cyan-600 dark:text-cyan-400">
                  {data.requestHistory.total.toLocaleString()} total
                </Badge>
                <Badge variant="outline" className="text-[10px] h-5 border-border/50 text-muted-foreground">
                  Last {timeRange}
                </Badge>
              </>
            }
            delay={0.25}
          >
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.requestHistory.hourlyData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                  <defs>
                    <linearGradient id="reqGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0.9} />
                      <stop offset="100%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0.4} />
                    </linearGradient>
                    <linearGradient id="errGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="oklch(0.6 0.18 25)" stopOpacity={0.9} />
                      <stop offset="100%" stopColor="oklch(0.6 0.18 25)" stopOpacity={0.4} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" vertical={false} />
                  <XAxis
                    dataKey="hour"
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                    label={{ value: 'Count', angle: -90, position: 'insideLeft', style: { fontSize: 11, fill: 'oklch(0.65 0.04 230)' } }}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'oklch(0.65 0.17 230 / 30%)', strokeWidth: 1 }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar
                    dataKey="requests"
                    name="Requests"
                    fill="url(#reqGrad)"
                    radius={[3, 3, 0, 0]}
                    maxBarSize={32}
                    animationDuration={800}
                  />
                  <Bar
                    dataKey="errors"
                    name="Errors"
                    fill="url(#errGrad)"
                    radius={[3, 3, 0, 0]}
                    maxBarSize={32}
                    animationDuration={800}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        ) : null}

        {/* Latency Trends */}
        {isLoading ? (
          <ChartSkeleton />
        ) : data ? (
          <ChartCard
            title="Latency Trends"
            icon={Clock}
            iconColor="text-amber-500"
            badge={
              <>
                <Badge variant="outline" className="text-[10px] h-5 gap-1 border-amber-500/30 text-amber-600 dark:text-amber-400">
                  TTFT {data.latency.avgTtft}ms
                </Badge>
                <Badge variant="outline" className="text-[10px] h-5 border-border/50 text-muted-foreground">
                  Last {timeRange}
                </Badge>
              </>
            }
            delay={0.3}
          >
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={data.latency.trendData.map((d) => ({
                    ...d,
                    time: formatTimestamp(d.timestamp, timeRange),
                  }))}
                  margin={{ top: 10, right: 20, left: 10, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" vertical={false} />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    yAxisId="ttft"
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v) => `${v}ms`}
                    label={{ value: 'TTFT (ms)', angle: -90, position: 'insideLeft', style: { fontSize: 11, fill: 'oklch(0.7 0.14 75)' } }}
                  />
                  <YAxis
                    yAxisId="gen"
                    orientation="right"
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v) => `${v}s`}
                    label={{ value: 'Gen (s)', angle: 90, position: 'insideRight', style: { fontSize: 11, fill: 'oklch(0.6 0.15 280)' } }}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'oklch(0.65 0.17 165 / 30%)', strokeWidth: 1 }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Line
                    yAxisId="ttft"
                    type="monotone"
                    dataKey="ttft"
                    name="TTFT (ms)"
                    stroke="oklch(0.7 0.14 75)"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 2 }}
                    animationDuration={800}
                  />
                  <Line
                    yAxisId="gen"
                    type="monotone"
                    dataKey="genTime"
                    name="Gen Time (s)"
                    stroke="oklch(0.6 0.15 280)"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 2 }}
                    animationDuration={800}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        ) : null}

        {/* Token Throughput */}
        {isLoading ? (
          <ChartSkeleton />
        ) : data ? (
          <ChartCard
            title="Token Throughput"
            icon={Zap}
            iconColor="text-emerald-500"
            badge={
              <>
                <Badge variant="outline" className="text-[10px] h-5 gap-1 border-emerald-500/30 text-emerald-600 dark:text-emerald-400">
                  <TrendingUp className="h-2.5 w-2.5" />
                  tok/s
                </Badge>
                <Badge variant="outline" className="text-[10px] h-5 border-border/50 text-muted-foreground">
                  Last {timeRange}
                </Badge>
              </>
            }
            delay={0.35}
          >
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={data.latency.trendData.map((d) => ({
                    ...d,
                    time: formatTimestamp(d.timestamp, timeRange),
                  }))}
                  margin={{ top: 10, right: 20, left: 10, bottom: 5 }}
                >
                  <defs>
                    <linearGradient id="tokGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="oklch(0.6 0.17 155)" stopOpacity={0.35} />
                      <stop offset="50%" stopColor="oklch(0.6 0.17 155)" stopOpacity={0.1} />
                      <stop offset="95%" stopColor="oklch(0.6 0.17 155)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" vertical={false} />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    className="text-muted-foreground"
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v) => `${v}`}
                    domain={[15, 40]}
                    label={{ value: 'tok/s', angle: -90, position: 'insideLeft', style: { fontSize: 11, fill: 'oklch(0.6 0.17 155)' } }}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'oklch(0.65 0.17 165 / 30%)', strokeWidth: 1 }} />
                  <ReferenceLine y={30} stroke="oklch(0.6 0.17 155 / 30%)" strokeDasharray="4 4" label={{ value: '30 tok/s', position: 'right', style: { fontSize: 10, fill: 'oklch(0.6 0.17 155 / 60%)' } }} />
                  <Area
                    type="monotone"
                    dataKey="tokensPerSec"
                    name="Tokens/sec"
                    stroke="oklch(0.6 0.17 155)"
                    fill="url(#tokGrad)"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 2 }}
                    animationDuration={800}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        ) : null}
      </div>

      {/* Error Rate - Full Width */}
      {isLoading ? (
        <ChartSkeleton />
      ) : data ? (
        <ChartCard
          title="Success vs Error Rate"
          icon={AlertTriangle}
          iconColor="text-rose-500"
          badge={
            <>
              <Badge
                variant="outline"
                className={cn(
                  'text-[10px] h-5 gap-1',
                  data.errorRate.errorRatePercent > 2
                    ? 'border-rose-500/30 text-rose-600 dark:text-rose-400'
                    : 'border-emerald-500/30 text-emerald-600 dark:text-emerald-400'
                )}
              >
                {data.errorRate.errorRatePercent}% error rate
              </Badge>
              <Badge variant="outline" className="text-[10px] h-5 border-border/50 text-muted-foreground">
                Last {timeRange}
              </Badge>
            </>
          }
          delay={0.4}
        >
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.errorRate.dailyData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                <defs>
                  <linearGradient id="successGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="oklch(0.6 0.15 230)" stopOpacity={0.85} />
                    <stop offset="100%" stopColor="oklch(0.6 0.15 230)" stopOpacity={0.5} />
                  </linearGradient>
                  <linearGradient id="errorBarGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="oklch(0.6 0.2 25)" stopOpacity={0.9} />
                    <stop offset="100%" stopColor="oklch(0.6 0.2 25)" stopOpacity={0.5} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11 }}
                  className="text-muted-foreground"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => {
                    const parts = v.split('-')
                    return `${parts[1]}/${parts[2]}`
                  }}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  className="text-muted-foreground"
                  tickLine={false}
                  axisLine={false}
                  label={{ value: 'Count', angle: -90, position: 'insideLeft', style: { fontSize: 11, fill: 'oklch(0.65 0.04 230)' } }}
                />
                <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'oklch(0.65 0.17 230 / 30%)', strokeWidth: 1 }} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar
                  dataKey="success"
                  name="Success"
                  fill="url(#successGrad)"
                  stackId="a"
                  radius={[0, 0, 0, 0]}
                  maxBarSize={40}
                  animationDuration={800}
                />
                <Bar
                  dataKey="errors"
                  name="Errors"
                  fill="url(#errorBarGrad)"
                  stackId="a"
                  radius={[3, 3, 0, 0]}
                  maxBarSize={40}
                  animationDuration={800}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      ) : null}

      {/* Empty/No Data State */}
      {hasEmptyData && (
        <div className="flex items-center justify-center h-48">
          <div className="text-center space-y-3">
            <div className="w-12 h-12 rounded-xl bg-muted/50 flex items-center justify-center mx-auto">
              <BarChart3 className="h-6 w-6 text-muted-foreground" />
            </div>
            <p className="text-sm font-medium text-muted-foreground">No analytics data available</p>
            <p className="text-xs text-muted-foreground">Data will appear once the server has been running and processing requests</p>
          </div>
        </div>
      )}
    </div>
  )
}
