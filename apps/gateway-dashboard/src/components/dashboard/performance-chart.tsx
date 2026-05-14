'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { useServerStatus } from '@/hooks/use-api'
import { Activity, TrendingUp, Zap } from 'lucide-react'

// Simulated performance data
const performanceData = Array.from({ length: 24 }, (_, i) => ({
  time: `${String(i).padStart(2, '0')}:00`,
  promptTokPerSec: 35 + Math.sin(i * 0.5) * 8 + Math.random() * 5,
  genTokPerSec: 25 + Math.sin(i * 0.5) * 6 + Math.random() * 4,
}))

const currentPromptSpeed = Math.round(performanceData[performanceData.length - 1].promptTokPerSec)
const currentGenSpeed = Math.round(performanceData[performanceData.length - 1].genTokPerSec)

export function PerformanceChart() {
  const { data: serverStatus } = useServerStatus()
  const isRunning = serverStatus?.status === 'running'

  return (
    <Card className="glass-card depth-shadow">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" />
            Performance Over Time
          </CardTitle>
          {isRunning && (
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="text-[10px] h-5 gap-1 border-emerald-500/30 text-emerald-600 dark:text-emerald-400">
                <TrendingUp className="h-2.5 w-2.5" />
                {currentPromptSpeed} tok/s prompt
              </Badge>
              <Badge variant="outline" className="text-[10px] h-5 gap-1 border-cyan-500/30 text-cyan-600 dark:text-cyan-400">
                <Zap className="h-2.5 w-2.5" />
                {currentGenSpeed} tok/s gen
              </Badge>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {!isRunning ? (
          <div className="h-[260px] flex flex-col items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-muted/50 flex items-center justify-center">
              <Activity className="h-6 w-6 text-muted-foreground/50" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-muted-foreground">No performance data</p>
              <p className="text-xs text-muted-foreground/60 mt-1">Start the server to see performance metrics</p>
            </div>
          </div>
        ) : (
          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="promptGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0.35} />
                    <stop offset="50%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="oklch(0.65 0.17 230)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="genGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="oklch(0.6 0.12 250)" stopOpacity={0.35} />
                    <stop offset="50%" stopColor="oklch(0.6 0.12 250)" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="oklch(0.6 0.12 250)" stopOpacity={0} />
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
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'oklch(0.18 0.015 230)',
                    border: '1px solid oklch(1 0 0 / 10%)',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: 'oklch(0.96 0.01 230)',
                  }}
                  itemStyle={{
                    color: 'oklch(0.96 0.01 230)',
                  }}
                />
                <Legend
                  wrapperStyle={{ fontSize: '12px' }}
                />
                <Area
                  type="monotone"
                  dataKey="promptTokPerSec"
                  name="Prompt tok/s"
                  stroke="oklch(0.65 0.17 230)"
                  fill="url(#promptGrad)"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 2 }}
                />
                <Area
                  type="monotone"
                  dataKey="genTokPerSec"
                  name="Gen tok/s"
                  stroke="oklch(0.6 0.12 250)"
                  fill="url(#genGrad)"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
