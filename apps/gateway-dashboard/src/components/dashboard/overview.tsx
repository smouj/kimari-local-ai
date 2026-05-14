'use client'

import { useDashboard, useServerStatus, useStartServer, useStopServer } from '@/hooks/use-api'
import { MetricCard } from './metric-card'
import { PerformanceChart } from './performance-chart'
import { RecentLogs } from './recent-logs'
import { ActivityTimeline } from './activity-timeline'
import { IntegrationGrid } from './integration-grid'
import { QuickLauncher } from './quick-launcher'
import { SystemResourcesWidget } from './system-resources-widget'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { toast } from 'sonner'
import {
  Server,
  Cpu,
  Box,
  HardDrive,
  Play,
  Square,
  Activity,
  Zap,
  Clock,
  Hash,
  ArrowRight,
  Sparkles,
  Network,
  Plug,
  CheckCircle2,
} from 'lucide-react'
import { useKimariStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

function formatUptime(seconds: number): string {
  if (!seconds) return '0s'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

function ArchitectureDiagram() {
  return (
    <div className="flex items-center justify-center gap-3 py-5">
      {/* Gateway */}
      <div className="flex flex-col items-center gap-2 group">
        <div className="w-18 h-18 rounded-xl bg-gradient-to-br from-primary/25 to-primary/5 border-2 border-primary/30 flex items-center justify-center transition-transform duration-200 group-hover:scale-110 shadow-lg shadow-primary/15">
          <Zap className="h-8 w-8 text-primary" />
        </div>
        <span className="text-[11px] font-semibold text-foreground/80">Gateway</span>
      </div>

      {/* Animated connecting line with glow */}
      <div className="flex items-center gap-0.5 relative connection-glow">
        <svg width="40" height="14" className="overflow-visible">
          <line
            x1="0" y1="7" x2="30" y2="7"
            stroke="oklch(0.65 0.17 230 / 60%)"
            strokeWidth="2.5"
            strokeDasharray="5 5"
            className="animate-dash-march"
          />
        </svg>
        <ArrowRight className="h-4 w-4 text-primary/70" />
      </div>

      {/* llama-server */}
      <div className="flex flex-col items-center gap-2 group">
        <div className="w-18 h-18 rounded-xl bg-gradient-to-br from-emerald-500/25 to-emerald-500/5 border-2 border-emerald-500/30 flex items-center justify-center transition-transform duration-200 group-hover:scale-110 shadow-lg shadow-emerald-500/15">
          <Server className="h-8 w-8 text-emerald-500" />
        </div>
        <span className="text-[11px] font-semibold text-foreground/80">llama.cpp</span>
      </div>

      {/* Animated connecting line with glow */}
      <div className="flex items-center gap-0.5 relative connection-glow">
        <svg width="40" height="14" className="overflow-visible">
          <line
            x1="0" y1="7" x2="30" y2="7"
            stroke="oklch(0.55 0.14 255 / 60%)"
            strokeWidth="2.5"
            strokeDasharray="5 5"
            className="animate-dash-march"
          />
        </svg>
        <ArrowRight className="h-4 w-4 text-emerald-500/70" />
      </div>

      {/* Integrations */}
      <div className="flex flex-col items-center gap-2 group">
        <div className="w-18 h-18 rounded-xl bg-gradient-to-br from-cyan-500/25 to-cyan-500/5 border-2 border-cyan-500/30 flex items-center justify-center transition-transform duration-200 group-hover:scale-110 shadow-lg shadow-cyan-500/15">
          <Plug className="h-8 w-8 text-cyan-500" />
        </div>
        <span className="text-[11px] font-semibold text-foreground/80">Integrations</span>
      </div>
    </div>
  )
}

export function DashboardOverview() {
  const { data, isLoading } = useDashboard()
  const { data: serverStatus } = useServerStatus()
  const startServer = useStartServer()
  const stopServer = useStopServer()
  const setActiveView = useKimariStore((s) => s.setActiveView)

  const isRunning = serverStatus?.status === 'running'
  const isStarting = serverStatus?.status === 'starting'

  const handleStartServer = async () => {
    try {
      await startServer.mutateAsync('test')
      toast.success('Server starting...', { description: 'Profile: test' })
    } catch (err) {
      toast.error('Failed to start server', { description: String(err) })
    }
  }

  const handleStopServer = async () => {
    try {
      await stopServer.mutateAsync()
      toast.success('Server stopped')
    } catch (err) {
      toast.error('Failed to stop server', { description: String(err) })
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[110px] w-full rounded-xl shimmer" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Skeleton className="h-[340px] w-full rounded-xl shimmer" />
          <Skeleton className="h-[340px] w-full rounded-xl shimmer" />
        </div>
      </div>
    )
  }

  const server = data?.server
  const profiles = data?.profiles
  const models = data?.models

  return (
    <div className="space-y-6 p-6">
      {/* Welcome Banner (when server stopped) */}
      {!isRunning && !isStarting && (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Card className="glass-card depth-shadow card-shine card-glow overflow-hidden border-primary/30 bg-card/80 relative">
            {/* Background pattern */}
            <div className="absolute inset-0 pointer-events-none opacity-30" style={{ backgroundImage: 'repeating-linear-gradient(135deg, transparent, transparent 10px, oklch(0.65 0.17 230 / 4%) 10px, oklch(0.65 0.17 230 / 4%) 11px)' }} />
            {/* Soft radial glow behind banner */}
            <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse 60% 50% at 50% 50%, oklch(0.65 0.17 230 / 10%), transparent)' }} />
            <CardContent className="p-6 relative">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-primary/25 to-primary/5 shrink-0 shadow-lg shadow-primary/10">
                  <Sparkles className="h-7 w-7 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-bold tracking-tight text-foreground">Welcome to Kimari Gateway</h1>
                    <Badge variant="outline" className="gap-1.5 status-badge-ready text-[11px] h-6 px-2.5 font-semibold border-2">
                      <CheckCircle2 className="h-3 w-3" />
                      System Ready
                    </Badge>
                  </div>
                  <p className="text-sm text-foreground/70 mt-1.5">
                    Your local AI gateway is currently offline. Start the server with a GPU profile to begin.
                  </p>
                  <ArchitectureDiagram />
                </div>
                <div className="flex gap-2 shrink-0">
                  <Button
                    className="gap-2 btn-press bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white shadow-lg shadow-emerald-500/25 px-6 py-2.5 text-sm font-semibold"
                    onClick={handleStartServer}
                    disabled={startServer.isPending}
                  >
                    <Play className="h-4 w-4" />
                    Start Server
                  </Button>
                  <Button
                    variant="outline"
                    className="gap-2 btn-press"
                    onClick={() => setActiveView('profiles')}
                  >
                    <Cpu className="h-4 w-4" />
                    Profiles
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Quick Launcher (when server stopped) */}
      {!isRunning && !isStarting && <QuickLauncher />}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Server Status"
          value={isRunning ? 'Running' : isStarting ? 'Starting' : 'Stopped'}
          subtitle={isRunning ? `Port ${server?.port ?? '-'}` : undefined}
          icon={<Server className="h-5 w-5" />}
          trend={isRunning ? 'up' : 'down'}
          trendValue={isRunning ? 'live' : undefined}
          variant="status"
        />
        <MetricCard
          title="Active Profile"
          value={isRunning || isStarting ? (server?.profile ?? 'None') : 'None'}
          subtitle={isRunning ? `Uptime: ${formatUptime(server?.uptime ?? 0)}` : 'Server not running'}
          icon={<Cpu className="h-5 w-5" />}
          variant="profile"
        />
        <MetricCard
          title="Models Available"
          value={`${models?.downloaded ?? 0} of ${models?.total ?? 0}`}
          subtitle={`${models?.notDownloaded ?? 0} not downloaded`}
          icon={<Box className="h-5 w-5" />}
          trend="neutral"
          variant="models"
        />
        <MetricCard
          title="Memory Usage"
          value={isRunning ? `${(0.7 + Math.min((server?.uptime ?? 0) * 0.0001, 0.3)).toFixed(1)} GB / 8 GB` : '0 MB'}
          subtitle={isRunning ? 'VRAM allocated' : 'No active model'}
          icon={<HardDrive className="h-5 w-5" />}
          trend={isRunning ? 'up' : 'neutral'}
          trendValue={isRunning ? `${Math.round(9 + Math.min((server?.uptime ?? 0) * 0.001, 7))}%` : undefined}
          variant="memory"
        />
      </div>

      {/* Quick Actions + Server Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <Card className="glass-card depth-shadow card-glow bg-card/80">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Zap className="h-4 w-4 text-primary" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              className="w-full justify-start gap-2 btn-press bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white shadow-md shadow-emerald-500/15"
              onClick={handleStartServer}
              disabled={isRunning || isStarting || startServer.isPending}
            >
              <Play className="h-4 w-4" />
              {isStarting ? 'Starting...' : 'Start Server'}
            </Button>
            <Button
              variant="destructive"
              className="w-full justify-start gap-2 btn-press"
              onClick={handleStopServer}
              disabled={!isRunning || stopServer.isPending}
            >
              <Square className="h-4 w-4" />
              Stop Server
            </Button>
            <div className="pt-1 border-t border-border">
              <Button
                variant="outline"
                className="w-full justify-start gap-2 btn-press hover:border-primary/30 hover:bg-primary/5"
                onClick={() => setActiveView('benchmarks')}
              >
                <Activity className="h-4 w-4 text-primary" />
                Run Benchmark
              </Button>
              <div className="mt-2">
                <Button
                  variant="outline"
                  className="w-full justify-start gap-2 btn-press hover:border-primary/30 hover:bg-primary/5"
                  onClick={() => setActiveView('integrations')}
                >
                  <Network className="h-4 w-4 text-primary" />
                  Manage Integrations
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Server Health */}
        <Card className="glass-card depth-shadow card-glow bg-card/80">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              Server Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70 flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5" /> Status
                </span>
                <Badge
                  variant="outline"
                  className={cn(
                    'capitalize px-3 py-1 text-sm font-medium',
                    isRunning
                      ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5'
                      : isStarting
                      ? 'border-amber-500/40 text-amber-600 dark:text-amber-400 bg-amber-500/5'
                      : 'border-border text-foreground/70 bg-muted/30'
                  )}
                >
                  {server?.status ?? 'unknown'}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70 flex items-center gap-2">
                  <Clock className="h-3.5 w-3.5" /> Uptime
                </span>
                <span className="font-mono text-sm font-medium">{formatUptime(server?.uptime ?? 0)}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70 flex items-center gap-2">
                  <Hash className="h-3.5 w-3.5" /> PID
                </span>
                <span className="font-mono text-sm font-medium">{server?.pid ?? '-'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70 flex items-center gap-2">
                  <Server className="h-3.5 w-3.5" /> Port
                </span>
                <span className="font-mono text-sm font-medium">{server?.port ?? '-'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70">Profile</span>
                <Badge variant="outline" className="font-mono">
                  {isRunning || isStarting ? (server?.profile ?? 'none') : 'none'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Profile Summary */}
        <Card className="glass-card depth-shadow card-glow bg-card/80">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Cpu className="h-4 w-4 text-primary" />
              Profile Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70">Total Profiles</span>
                <span className="font-semibold">{profiles?.total ?? 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70">Available</span>
                <Badge variant="outline" className="border-emerald-500/30 text-emerald-600 dark:text-emerald-400">
                  {profiles?.available ?? 0}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70">Requires Model</span>
                <Badge variant="outline" className="border-amber-500/30 text-amber-600 dark:text-amber-400">
                  {profiles?.requiresModel ?? 0}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground/70">Network Exposed</span>
                <Badge variant="outline" className="border-red-500/30 text-red-600 dark:text-red-400">
                  {profiles?.networkExposed ?? 0}
                </Badge>
              </div>
              {profiles?.running && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-foreground/70">Running</span>
                  <Badge className="bg-primary">{profiles.running}</Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Activity Timeline + Performance & Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Timeline — takes 1 column */}
        <ActivityTimeline />
        {/* Performance Chart + Recent Logs stacked — takes 2 columns */}
        <div className="lg:col-span-2 space-y-6">
          <PerformanceChart />
          <RecentLogs />
        </div>
      </div>

      {/* System Resources */}
      <SystemResourcesWidget />

      {/* Integration Status */}
      <IntegrationGrid />
    </div>
  )
}
