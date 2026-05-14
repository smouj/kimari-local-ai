'use client'

import { useState, useEffect } from 'react'
import { useServerStatus, useProfiles, useStartServer, useStopServer } from '@/hooks/use-api'
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
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import { toast } from 'sonner'
import {
  Server,
  Play,
  Square,
  Activity,
  Clock,
  Hash,
  Globe,
  Cpu,
  HardDrive,
  AlertCircle,
  Zap,
  Link,
  ArrowRight,
  Radio,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { ResourceGauge } from './resource-gauge'

function formatUptime(seconds: number): string {
  if (!seconds) return '0s'
  const d = Math.floor(seconds / 86400)
  const h = Math.floor((seconds % 86400) / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  const parts: string[] = []
  if (d > 0) parts.push(`${d}d`)
  if (h > 0) parts.push(`${h}h`)
  if (m > 0) parts.push(`${m}m`)
  if (s > 0 || parts.length === 0) parts.push(`${s}s`)
  return parts.join(' ')
}

function ConnectionDiagram({ isRunning, port, host }: { isRunning: boolean; port?: number; host?: string }) {
  return (
    <div className="flex items-center justify-center gap-4 py-4">
      {/* Client */}
      <div className="flex flex-col items-center gap-1.5 group">
        <div className={cn(
          'w-12 h-12 rounded-xl flex items-center justify-center border-2 transition-all duration-300',
          isRunning ? 'bg-primary/15 border-primary/30 shadow-md shadow-primary/10' : 'bg-muted/50 border-border'
        )}>
          <Globe className="h-5 w-5 text-primary" />
        </div>
        <span className="text-[11px] font-semibold text-foreground/75">Client</span>
      </div>

      {/* Arrow with glow when running */}
      <div className="flex items-center">
        <div className={cn(
          'w-10 h-[3px] rounded-full transition-all duration-300',
          isRunning ? 'bg-gradient-to-r from-primary/70 to-emerald-500/70 shadow-sm shadow-primary/30' : 'bg-border'
        )} />
        <ArrowRight className={cn('h-4 w-4 transition-colors', isRunning ? 'text-emerald-500' : 'text-border')} />
      </div>

      {/* Gateway */}
      <div className="flex flex-col items-center gap-1.5 group">
        <div className={cn(
          'w-12 h-12 rounded-xl flex items-center justify-center border-2 transition-all duration-300',
          isRunning ? 'bg-emerald-500/15 border-emerald-500/30 shadow-md shadow-emerald-500/10' : 'bg-muted/50 border-border'
        )}>
          <Zap className="h-5 w-5 text-emerald-500" />
        </div>
        <span className="text-[11px] font-semibold text-foreground/75">Gateway</span>
      </div>

      {/* Arrow with glow when running */}
      <div className="flex items-center">
        <div className={cn(
          'w-10 h-[3px] rounded-full transition-all duration-300',
          isRunning ? 'bg-gradient-to-r from-emerald-500/70 to-cyan-500/70 shadow-sm shadow-emerald-500/30' : 'bg-border'
        )} />
        <ArrowRight className={cn('h-4 w-4 transition-colors', isRunning ? 'text-cyan-500' : 'text-border')} />
      </div>

      {/* llama-server */}
      <div className="flex flex-col items-center gap-1.5 group">
        <div className={cn(
          'w-12 h-12 rounded-xl flex items-center justify-center border-2 transition-all duration-300',
          isRunning ? 'bg-cyan-500/15 border-cyan-500/30 shadow-md shadow-cyan-500/10' : 'bg-muted/50 border-border'
        )}>
          <Server className="h-5 w-5 text-cyan-500" />
        </div>
        <span className="text-[11px] font-semibold text-foreground/75">llama.cpp</span>
      </div>
    </div>
  )
}

export function ServerView() {
  const { data: serverStatus, isLoading } = useServerStatus()
  const { data: profiles } = useProfiles()
  const startServer = useStartServer()
  const stopServer = useStopServer()
  const [selectedProfile, setSelectedProfile] = useState<string>('')

  const isRunning = serverStatus?.status === 'running'
  const isStarting = serverStatus?.status === 'starting'

  const handleStart = async () => {
    if (!selectedProfile) {
      toast.error('Please select a profile')
      return
    }
    try {
      await startServer.mutateAsync(selectedProfile)
      toast.success('Server starting...', { description: `Profile: ${selectedProfile}` })
    } catch (err) {
      toast.error('Failed to start server', { description: String(err) })
    }
  }

  const handleStop = async () => {
    try {
      await stopServer.mutateAsync()
      toast.success('Server stopped')
    } catch (err) {
      toast.error('Failed to stop server', { description: String(err) })
    }
  }

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center py-20">
          <div className="animate-pulse">
            <div className="h-32 w-32 rounded-full bg-muted shimmer" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Status Indicator */}
      <Card className="glass-card depth-shadow card-shine card-glow overflow-hidden">
        {/* Gradient background behind status */}
        <div className="absolute inset-0 pointer-events-none">
          <div className={cn(
            'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full blur-[100px] transition-opacity',
            isRunning ? 'bg-emerald-500/12 opacity-100' : isStarting ? 'bg-amber-500/12 opacity-100' : 'bg-muted/20 opacity-50'
          )} />
        </div>
        <CardContent className="py-10 relative">
          <div className="flex flex-col items-center gap-5">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.4 }}
            >
              <div className="relative">
                {/* Outer ring - Health indicator with more visual prominence */}
                <div
                  className={cn(
                    'h-36 w-36 rounded-full flex items-center justify-center transition-all duration-500',
                    isRunning
                      ? 'animate-ring-pulse'
                      : isStarting
                      ? 'animate-pulse'
                      : ''
                  )}
                  style={{
                    background: isRunning
                      ? 'conic-gradient(from 0deg, oklch(0.72 0.17 230 / 40%), oklch(0.6 0.15 255 / 25%), oklch(0.72 0.17 230 / 40%))'
                      : isStarting
                      ? 'conic-gradient(from 0deg, oklch(0.75 0.15 85 / 35%), oklch(0.72 0.13 100 / 25%), oklch(0.75 0.15 85 / 35%))'
                      : 'conic-gradient(from 0deg, oklch(0.5 0.02 230 / 20%), oklch(0.4 0.02 230 / 12%), oklch(0.5 0.02 230 / 20%))',
                    boxShadow: isRunning
                      ? '0 0 30px oklch(0.72 0.17 230 / 20%)'
                      : isStarting
                      ? '0 0 20px oklch(0.75 0.15 85 / 15%)'
                      : 'none',
                  }}
                >
                  {/* Middle ring */}
                  <div className={cn(
                    'h-28 w-28 rounded-full flex items-center justify-center transition-all',
                    isRunning ? 'bg-emerald-500/8' : isStarting ? 'bg-amber-500/8' : 'bg-muted/30'
                  )}>
                    {/* Inner core */}
                    <div className="relative">
                      <div
                        className={cn(
                          'h-16 w-16 rounded-full flex items-center justify-center transition-all duration-500',
                          isRunning
                            ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 shadow-lg shadow-emerald-500/40'
                            : isStarting
                            ? 'bg-gradient-to-br from-amber-500 to-amber-600 shadow-lg shadow-amber-500/40'
                            : 'bg-foreground/25'
                        )}
                      >
                        {isRunning ? (
                          <Radio className="h-6 w-6 text-white" />
                        ) : isStarting ? (
                          <div className="h-4 w-4 rounded-full border-2 border-white/60 border-t-transparent animate-spin" />
                        ) : (
                          <Server className="h-6 w-6 text-foreground/50" />
                        )}
                      </div>
                      {/* Glow effect */}
                      {isRunning && (
                        <div className="absolute inset-0 h-16 w-16 rounded-full bg-emerald-500/20 animate-ping" />
                      )}
                    </div>
                  </div>
                </div>

                {/* Animated border ring when running */}
                {isRunning && (
                  <div className="absolute -inset-1 rounded-full gradient-border" />
                )}
              </div>
            </motion.div>

            <div className="text-center">
              <h2 className={cn(
                'text-2xl font-bold',
                isRunning ? 'text-emerald-600 dark:text-emerald-400' : isStarting ? 'text-amber-600 dark:text-amber-400' : ''
              )}>
                {isRunning ? 'Server Running' : isStarting ? 'Server Starting...' : 'Server Offline'}
              </h2>
              <p className="text-sm text-foreground/70 mt-1 flex items-center justify-center gap-2 font-medium">
                {isRunning
                  ? <>Running on port {serverStatus?.port} with profile &quot;{serverStatus?.profile}&quot;</>
                  : isStarting
                  ? <>Please wait while the server initializes...</>
                  : <><span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary/60 opacity-75" /><span className="relative inline-flex rounded-full h-2 w-2 bg-primary" /></span>Select a profile and start the server</>}
              </p>
              {!isRunning && !isStarting && (
                <p className="text-xs text-foreground/60 mt-2 flex items-center justify-center gap-1.5">
                  <Clock className="h-3 w-3" /> Last run: 2 hours ago with profile RTX 4090
                </p>
              )}
            </div>

            {/* Connection Diagram */}
            <ConnectionDiagram
              isRunning={isRunning}
              port={serverStatus?.port}
              host={serverStatus?.host}
            />

            {/* API Endpoint URL */}
            {isRunning && (
              <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-muted/30 border border-border/50">
                <Link className="h-3.5 w-3.5 text-primary" />
                <code className="text-xs font-mono text-foreground/75">
                  http://{serverStatus?.host ?? '127.0.0.1'}:{serverStatus?.port ?? 8080}
                </code>
              </div>
            )}

            {/* Quick Start Section — only when offline */}
            {!isRunning && !isStarting && (
              <div className="w-full mt-2">
                <p className="text-xs font-semibold text-foreground/65 uppercase tracking-wider mb-3">Quick Start</p>
                <div className="grid grid-cols-3 gap-3">
                  {(profiles ?? []).slice(0, 3).map((p) => (
                    <div
                      key={p.id}
                      className="flex flex-col items-center gap-2 p-4 rounded-xl bg-muted/20 border border-border/40 hover:border-primary/30 hover:bg-muted/30 transition-all cursor-pointer group depth-shadow hover-scale"
                      onClick={() => { setSelectedProfile(p.name) }}
                    >
                      <Cpu className="h-5 w-5 text-foreground/60 group-hover:text-primary transition-colors" />
                      <div className="text-center">
                        <p className="text-xs font-semibold text-foreground/90 truncate max-w-[100px]">{p.gpu}</p>
                        <p className="text-[10px] text-foreground/60 mt-0.5">{p.vram}</p>
                      </div>
                      <Button
                        size="sm"
                        className="h-7 text-[11px] px-3 gap-1.5 btn-press bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white shadow-md shadow-emerald-500/15"
                        onClick={(e) => { e.stopPropagation(); setSelectedProfile(p.name); handleStart() }}
                        disabled={startServer.isPending}
                      >
                        <Play className="h-3 w-3" />
                        Start
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Resource Gauges */}
      <Card className="glass-card depth-shadow card-glow">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Cpu className="h-4 w-4 text-primary" />
            Resource Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-around gap-4">
            <ResourceGauge
              value={isRunning ? 52 : 0}
              maxValue={100}
              label="VRAM Usage"
              unit="%"
              color={isRunning ? undefined : 'muted'}
            />
            <ResourceGauge
              value={isRunning ? 58 : 0}
              maxValue={100}
              label="GPU Temp"
              unit="°C"
              color={isRunning ? undefined : 'muted'}
            />
            <ResourceGauge
              value={isRunning ? 34 : 0}
              maxValue={100}
              label="CPU Load"
              unit="%"
              color={isRunning ? undefined : 'muted'}
            />
          </div>
        </CardContent>
      </Card>

      {/* Controls + Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Server Controls */}
        <Card className="glass-card depth-shadow card-glow">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Server className="h-4 w-4 text-primary" />
              Server Controls
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {!isRunning && !isStarting && (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground/85">Select Profile</label>
                  <Select value={selectedProfile} onValueChange={setSelectedProfile}>
                    <SelectTrigger className="hover:border-primary/30 transition-colors">
                      <SelectValue placeholder="Choose a profile..." />
                    </SelectTrigger>
                    <SelectContent>
                      {(profiles ?? []).map((p) => (
                        <SelectItem key={p.id} value={p.name}>
                          <div className="flex items-center gap-2">
                            <Cpu className="h-3 w-3 text-primary" />
                            <span>{p.displayName}</span>
                            <span className="text-xs text-foreground/65">({p.gpu}, {p.vram})</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  className="w-full gap-2 btn-press bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white shadow-md shadow-emerald-500/15"
                  onClick={handleStart}
                  disabled={!selectedProfile || startServer.isPending}
                >
                  <Play className="h-4 w-4" />
                  {startServer.isPending ? 'Starting...' : 'Start Server'}
                </Button>
              </>
            )}

            {(isRunning || isStarting) && (
              <Button
                variant="destructive"
                className="w-full gap-2 btn-press"
                onClick={handleStop}
                disabled={stopServer.isPending}
              >
                <Square className="h-4 w-4" />
                {stopServer.isPending ? 'Stopping...' : 'Stop Server'}
              </Button>
            )}

            {serverStatus?.lastError && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
                <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                <span>{serverStatus.lastError}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Server Info */}
        <Card className="glass-card depth-shadow card-glow">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              Server Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5 p-2.5 rounded-lg bg-muted/20 border border-border/30">
                  <p className="text-[10px] text-foreground/65 flex items-center gap-1 uppercase tracking-wider font-semibold">
                    <Hash className="h-3 w-3" /> PID
                  </p>
                  <p className="text-sm font-mono font-semibold">{serverStatus?.pid ?? '-'}</p>
                </div>
                <div className="space-y-1.5 p-2.5 rounded-lg bg-muted/20 border border-border/30">
                  <p className="text-[10px] text-foreground/65 flex items-center gap-1 uppercase tracking-wider font-semibold">
                    <Globe className="h-3 w-3" /> Port
                  </p>
                  <p className="text-sm font-mono font-semibold">{serverStatus?.port ?? '-'}</p>
                </div>
                <div className="space-y-1.5 p-2.5 rounded-lg bg-muted/20 border border-border/30">
                  <p className="text-[10px] text-foreground/65 flex items-center gap-1 uppercase tracking-wider font-semibold">
                    <Server className="h-3 w-3" /> Host
                  </p>
                  <p className="text-sm font-mono font-semibold">{serverStatus?.host ?? '-'}</p>
                </div>
                <div className="space-y-1.5 p-2.5 rounded-lg bg-muted/20 border border-border/30">
                  <p className="text-[10px] text-foreground/65 flex items-center gap-1 uppercase tracking-wider font-semibold">
                    <Cpu className="h-3 w-3" /> Profile
                  </p>
                  <Badge variant="outline" className="font-mono text-xs">
                    {isRunning || isStarting ? (serverStatus?.profile ?? 'none') : 'none'}
                  </Badge>
                </div>
              </div>

              <Separator className="bg-border/50" />

              {/* Mini metrics bars */}
              {isRunning && (
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-foreground/70 flex items-center gap-1.5 font-medium">
                        <Zap className="h-3 w-3 text-emerald-500" /> Prompt Speed
                      </span>
                      <span className="text-xs font-mono font-semibold text-emerald-500">~35 tok/s</span>
                    </div>
                    <Progress value={70} className="h-1.5 [&>div]:bg-emerald-500" />
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-foreground/70 flex items-center gap-1.5 font-medium">
                        <Activity className="h-3 w-3 text-cyan-500" /> Gen Speed
                      </span>
                      <span className="text-xs font-mono font-semibold text-cyan-500">~25 tok/s</span>
                    </div>
                    <Progress value={50} className="h-1.5 [&>div]:bg-cyan-500" />
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-foreground/70 flex items-center gap-1.5 font-medium">
                        <HardDrive className="h-3 w-3 text-amber-500" /> VRAM Usage
                      </span>
                      <span className="text-xs font-mono font-semibold text-amber-500">4.2 / 8 GB</span>
                    </div>
                    <Progress value={52} className="h-1.5 [&>div]:bg-amber-500" />
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs text-foreground/70 font-medium">
                  <Clock className="h-3 w-3" /> Uptime
                </div>
                <span className="text-xs font-mono font-semibold">
                  {formatUptime(serverStatus?.uptime ?? 0)}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-xs text-foreground/70 font-medium">Status</span>
                <Badge
                  variant="outline"
                  className={cn(
                    'capitalize font-medium',
                    isRunning
                      ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5'
                      : isStarting
                      ? 'border-amber-500/40 text-amber-600 dark:text-amber-400 bg-amber-500/5'
                      : 'border-border text-foreground/70 bg-muted/30'
                  )}
                >
                  {serverStatus?.status ?? 'unknown'}
                </Badge>
              </div>

              {serverStatus?.startedAt && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-foreground/70 font-medium">Started At</span>
                  <span className="text-xs font-mono font-medium">
                    {new Date(serverStatus.startedAt).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
