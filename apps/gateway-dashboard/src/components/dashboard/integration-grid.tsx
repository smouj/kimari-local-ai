'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useIntegrations } from '@/hooks/use-api'
import { Skeleton } from '@/components/ui/skeleton'
import { Globe, Bot, MessageSquare, Code, Settings2, ArrowUpRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

const iconMap: Record<string, React.ReactNode> = {
  openwebui: <Globe className="h-5 w-5" />,
  openclaw: <Bot className="h-5 w-5" />,
  hermes: <MessageSquare className="h-5 w-5" />,
  continue: <Code className="h-5 w-5" />,
}

const iconBgMap: Record<string, string> = {
  openwebui: 'from-blue-500/20 to-blue-600/5 border-blue-500/20',
  openclaw: 'from-purple-500/20 to-purple-600/5 border-purple-500/20',
  hermes: 'from-amber-500/20 to-amber-600/5 border-amber-500/20',
  continue: 'from-teal-500/20 to-teal-600/5 border-teal-500/20',
}

const statusColors: Record<string, string> = {
  available: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
  configured: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/30',
  running: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
  error: 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/30',
}

const statusLineColors: Record<string, string> = {
  available: 'bg-emerald-500',
  configured: 'bg-blue-500',
  running: 'bg-emerald-500',
  error: 'bg-red-500',
}

export function IntegrationGrid() {
  const { data: integrations, isLoading } = useIntegrations()

  if (isLoading) {
    return (
      <Card className="glass-card depth-shadow">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-semibold">Integrations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-28 w-full rounded-lg shimmer" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="glass-card depth-shadow">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Globe className="h-4 w-4 text-primary" />
            Integrations
          </CardTitle>
          <Badge variant="outline" className="text-[10px] h-5 shrink-0 border-border text-muted-foreground">
            {(integrations ?? []).length} connected
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(integrations ?? []).map((integration, i) => (
            <motion.div
              key={integration.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2, delay: i * 0.05 }}
              className="relative group flex flex-col items-center gap-2 p-4 rounded-lg border border-border bg-muted/20 hover:bg-muted/40 transition-all duration-200 card-hover-lift overflow-hidden"
            >
              {/* Status line at top */}
              <div className={cn('absolute top-0 left-0 right-0 h-[2px]', statusLineColors[integration.status] ?? 'bg-muted')} />

              <div className={cn(
                'flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br border shrink-0',
                iconBgMap[integration.name] ?? 'from-primary/20 to-primary/5 border-primary/20'
              )}>
                {iconMap[integration.name] || <Globe className="h-5 w-5" />}
              </div>
              <span className="text-xs font-medium text-center">{integration.displayName}</span>
              <Badge
                variant="outline"
                className={cn('text-[10px] h-5 capitalize', statusColors[integration.status])}
              >
                {integration.status}
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-[10px] gap-1 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-foreground"
              >
                <Settings2 className="h-2.5 w-2.5" />
                Configure
                <ArrowUpRight className="h-2.5 w-2.5" />
              </Button>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
