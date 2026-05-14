'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useDashboard, type GatewayLog } from '@/hooks/use-api'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertCircle, Info, AlertTriangle, Bug, ScrollText } from 'lucide-react'
import { cn } from '@/lib/utils'

const levelConfig: Record<string, { color: string; icon: React.ReactNode; bg: string }> = {
  info: { color: 'text-blue-500', icon: <Info className="h-3.5 w-3.5" />, bg: 'bg-blue-500/10' },
  warn: { color: 'text-amber-500', icon: <AlertTriangle className="h-3.5 w-3.5" />, bg: 'bg-amber-500/10' },
  error: { color: 'text-red-500', icon: <AlertCircle className="h-3.5 w-3.5" />, bg: 'bg-red-500/10' },
  debug: { color: 'text-foreground/70', icon: <Bug className="h-3.5 w-3.5" />, bg: 'bg-muted' },
}

function LogEntry({ log }: { log: GatewayLog }) {
  const config = levelConfig[log.level] || levelConfig.info
  const time = new Date(log.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <div className="flex items-start gap-2 py-1.5 px-1 text-xs hover:bg-muted/50 rounded transition-colors">
      <span className={cn('shrink-0 mt-0.5', config.color)}>{config.icon}</span>
      <Badge variant="outline" className="h-4 text-[10px] px-1 shrink-0 font-mono">
        {log.level}
      </Badge>
      <span className="text-foreground/60 shrink-0 font-mono">{time}</span>
      <span className="truncate text-foreground/85">{log.message}</span>
    </div>
  )
}

export function RecentLogs() {
  const { data, isLoading } = useDashboard()

  if (isLoading) {
    return (
      <Card className="glass-card depth-shadow card-glow">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <ScrollText className="h-4 w-4 text-primary" />
            Recent Logs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-5 w-full shimmer" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const logs = data?.recentLogs ?? []

  return (
    <Card className="glass-card depth-shadow card-glow">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <ScrollText className="h-4 w-4 text-primary" />
            Recent Logs
          </CardTitle>
          <Badge variant="secondary" className="text-[10px] h-5 font-medium">
            {logs.length} entries
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {logs.length === 0 ? (
          <p className="text-sm text-foreground/70 text-center py-6">No logs yet</p>
        ) : (
          <ScrollArea className="h-[260px]">
            <div className="space-y-1">
              {logs.map((log) => (
                <LogEntry key={log.id} log={log} />
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  )
}
