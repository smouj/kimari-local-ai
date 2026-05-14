'use client'

import { useState } from 'react'
import { useBenchmarks, useProfiles, useRunBenchmark } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { toast } from 'sonner'
import {
  BarChart3,
  Play,
  Clock,
  Zap,
  ArrowUpDown,
  Gauge,
  Timer,
  HardDrive,
  FlaskConical,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { motion } from 'framer-motion'

export function BenchmarksView() {
  const { data: benchmarks, isLoading } = useBenchmarks()
  const { data: profiles } = useProfiles()
  const runBenchmark = useRunBenchmark()
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [selectedMode, setSelectedMode] = useState<string>('standard')

  const handleRun = async () => {
    if (!selectedProfile) {
      toast.error('Please select a profile')
      return
    }
    try {
      const result = await runBenchmark.mutateAsync({ profile: selectedProfile, mode: selectedMode })
      if (result.mode === 'dry_run') {
        toast.success('Dry run completed', { description: 'Results are estimates' })
      } else {
        toast.success('Benchmark completed', { description: `Profile: ${selectedProfile}` })
      }
    } catch (err) {
      toast.error('Benchmark failed', { description: String(err) })
    }
  }

  // Chart data: aggregate by profile
  const chartData = (() => {
    if (!benchmarks?.length) return []
    const byProfile: Record<string, { prompt: number[]; gen: number[] }> = {}
    benchmarks.forEach((b) => {
      if (!byProfile[b.profile]) byProfile[b.profile] = { prompt: [], gen: [] }
      if (b.promptTokPerSec) byProfile[b.profile].prompt.push(b.promptTokPerSec)
      if (b.genTokPerSec) byProfile[b.profile].gen.push(b.genTokPerSec)
    })
    return Object.entries(byProfile).map(([profile, data]) => ({
      profile,
      promptTokPerSec: data.prompt.length ? Math.round((data.prompt.reduce((a, b) => a + b, 0) / data.prompt.length) * 10) / 10 : 0,
      genTokPerSec: data.gen.length ? Math.round((data.gen.reduce((a, b) => a + b, 0) / data.gen.length) * 10) / 10 : 0,
    }))
  })()

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-40 w-full rounded-xl" />
        <Skeleton className="h-60 w-full rounded-xl" />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Run Benchmark */}
      <Card className="glass-card depth-shadow">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Run Benchmark
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row items-end gap-3">
            <div className="space-y-1.5 flex-1 w-full">
              <label className="text-xs font-medium">Profile</label>
              <Select value={selectedProfile} onValueChange={setSelectedProfile}>
                <SelectTrigger>
                  <SelectValue placeholder="Select profile..." />
                </SelectTrigger>
                <SelectContent>
                  {(profiles ?? []).map((p) => (
                    <SelectItem key={p.id} value={p.name}>
                      {p.displayName} ({p.gpu})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5 w-full sm:w-40">
              <label className="text-xs font-medium">Mode</label>
              <Select value={selectedMode} onValueChange={setSelectedMode}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dry_run">Dry Run</SelectItem>
                  <SelectItem value="standard">Standard</SelectItem>
                  <SelectItem value="measured">Measured</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              className="gap-2 w-full sm:w-auto btn-press"
              onClick={handleRun}
              disabled={!selectedProfile || runBenchmark.isPending}
            >
              <Play className="h-4 w-4" />
              {runBenchmark.isPending ? 'Running...' : 'Run Benchmark'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Benchmark Chart */}
      {chartData.length > 0 && (
        <Card className="glass-card depth-shadow">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold">Performance Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="profile" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="promptTokPerSec" name="Prompt tok/s" fill="oklch(0.55 0.17 230)" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="genTokPerSec" name="Gen tok/s" fill="oklch(0.6 0.12 250)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Table */}
      <Card className="glass-card depth-shadow">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold">Benchmark Results</CardTitle>
            <Badge variant="outline" className="font-mono text-[10px]">
              {benchmarks?.length ?? 0} results
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {!benchmarks?.length ? (
            <div className="py-16 flex flex-col items-center justify-center text-muted-foreground">
              <FlaskConical className="h-10 w-10 mb-3 opacity-40" />
              <p className="text-sm font-medium">No benchmark results</p>
              <p className="text-xs mt-1">Run a benchmark above to see performance results here.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Profile</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Model</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Quant</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Prompt tok/s</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Gen tok/s</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">TTFT (ms)</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Duration</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {benchmarks.map((b) => (
                  <TableRow
                    key={b.id}
                    className="hover:bg-muted/50 hover:border-l-2 hover:border-l-primary transition-colors border-l-2 border-l-transparent"
                  >
                    <TableCell>
                      <div className="flex items-center gap-1.5">
                        <Gauge className="h-3.5 w-3.5 text-primary" />
                        <span className="font-medium text-sm">{b.profile}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm font-mono">{b.model}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="font-mono text-[10px]">
                        {b.quantization}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Zap className="h-3 w-3 text-primary" />
                        <span className="font-mono text-sm">{b.promptTokPerSec?.toFixed(1) ?? '-'}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <ArrowUpDown className="h-3 w-3 text-primary" />
                        <span className="font-mono text-sm">{b.genTokPerSec?.toFixed(1) ?? '-'}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Timer className="h-3 w-3 text-muted-foreground" />
                        <span className="font-mono text-sm">{b.ttft?.toFixed(1) ?? '-'}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3 text-muted-foreground" />
                        <span className="font-mono text-sm">{b.duration?.toFixed(1) ?? '-'}s</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(b.createdAt).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
