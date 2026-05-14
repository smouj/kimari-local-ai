'use client'

import { useActivity, type ActivityEvent, type ActivityType } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Play,
  Square,
  BarChart3,
  Download,
  Settings,
  Puzzle,
  Heart,
  Clock,
  type LucideIcon,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

const iconMap: Record<string, LucideIcon> = {
  Play,
  Square,
  BarChart3,
  Download,
  Settings,
  Puzzle,
  Heart,
}

const typeColors: Record<ActivityType, { dot: string; bg: string; ring: string }> = {
  server_start: {
    dot: 'bg-emerald-500',
    bg: 'bg-emerald-500/10',
    ring: 'ring-emerald-500/20',
  },
  server_stop: {
    dot: 'bg-red-500',
    bg: 'bg-red-500/10',
    ring: 'ring-red-500/20',
  },
  benchmark: {
    dot: 'bg-primary',
    bg: 'bg-primary/10',
    ring: 'ring-primary/20',
  },
  model_download: {
    dot: 'bg-cyan-500',
    bg: 'bg-cyan-500/10',
    ring: 'ring-cyan-500/20',
  },
  config_change: {
    dot: 'bg-amber-500',
    bg: 'bg-amber-500/10',
    ring: 'ring-amber-500/20',
  },
  integration_connect: {
    dot: 'bg-purple-500',
    bg: 'bg-purple-500/10',
    ring: 'ring-purple-500/20',
  },
  health_check: {
    dot: 'bg-blue-500',
    bg: 'bg-blue-500/10',
    ring: 'ring-blue-500/20',
  },
}

const statusColors: Record<string, string> = {
  success: 'text-emerald-600 dark:text-emerald-400',
  warning: 'text-amber-600 dark:text-amber-400',
  error: 'text-red-600 dark:text-red-400',
  info: 'text-blue-600 dark:text-blue-400',
}

function formatRelativeTime(timestamp: string): string {
  const now = new Date()
  const date = new Date(timestamp)
  const diffMs = now.getTime() - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHr = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHr / 24)

  if (diffSec < 60) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  if (diffHr < 24) return `${diffHr}h ago`
  return `${diffDay}d ago`
}

function isToday(timestamp: string): boolean {
  const now = new Date()
  const date = new Date(timestamp)
  return (
    now.getFullYear() === date.getFullYear() &&
    now.getMonth() === date.getMonth() &&
    now.getDate() === date.getDate()
  )
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0 },
}

function TimelineItem({ event, isLast }: { event: ActivityEvent; isLast: boolean }) {
  const IconComponent = iconMap[event.icon] || Clock
  const colors = typeColors[event.type]
  const statusColor = statusColors[event.status]

  return (
    <motion.div
      variants={itemVariants}
      className="relative flex gap-3"
    >
      {/* Timeline line + dot */}
      <div className="flex flex-col items-center shrink-0">
        <div
          className={cn(
            'relative z-10 w-8 h-8 rounded-full flex items-center justify-center ring-2',
            colors.bg,
            colors.ring
          )}
        >
          <div className={cn('w-2.5 h-2.5 rounded-full', colors.dot)} />
        </div>
        {!isLast && (
          <div className="w-px flex-1 bg-border/60 min-h-[20px]" />
        )}
      </div>

      {/* Content */}
      <div className={cn('flex-1 pb-4', isLast && 'pb-0')}>
        <div className="flex items-start gap-2">
          <div className={cn('shrink-0 mt-0.5 w-4 h-4 rounded flex items-center justify-center', colors.bg)}>
            <IconComponent className={cn('h-2.5 w-2.5', statusColor)} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-medium leading-tight text-foreground/90">{event.title}</span>
              <span className="text-[10px] text-foreground/55 shrink-0 font-medium">
                {formatRelativeTime(event.timestamp)}
              </span>
            </div>
            <p className="text-xs text-foreground/70 mt-0.5 leading-relaxed line-clamp-2">
              {event.description}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export function ActivityTimeline() {
  const { data, isLoading } = useActivity()

  if (isLoading) {
    return (
      <Card className="glass-card depth-shadow card-glow">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" />
            Activity Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <Skeleton className="w-8 h-8 rounded-full shimmer" />
                  <Skeleton className="w-px h-8 shimmer" />
                </div>
                <div className="flex-1 space-y-1.5">
                  <Skeleton className="h-4 w-3/4 shimmer" />
                  <Skeleton className="h-3 w-full shimmer" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const events = data?.events ?? []
  const todayEvents = events.filter((e) => isToday(e.timestamp))
  const earlierEvents = events.filter((e) => !isToday(e.timestamp))

  return (
    <Card className="glass-card depth-shadow card-glow">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" />
            Activity Timeline
          </CardTitle>
          <Badge variant="secondary" className="text-[10px] h-5 font-medium">
            {events.length} events
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {events.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 gap-3">
            <div className="w-10 h-10 rounded-xl bg-muted/50 flex items-center justify-center">
              <Clock className="h-5 w-5 text-foreground/40" />
            </div>
            <p className="text-sm text-foreground/70">No activity yet</p>
          </div>
        ) : (
          <div className="max-h-[480px] overflow-y-auto pr-1 custom-scrollbar">
            {todayEvents.length > 0 && (
              <div className="mb-4">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-foreground/55 mb-3 ml-11">
                  Today
                </p>
                <motion.div
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                >
                  {todayEvents.map((event, i) => (
                    <TimelineItem
                      key={event.id}
                      event={event}
                      isLast={i === todayEvents.length - 1 && earlierEvents.length === 0}
                    />
                  ))}
                </motion.div>
              </div>
            )}
            {earlierEvents.length > 0 && (
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-wider text-foreground/55 mb-3 ml-11">
                  Earlier
                </p>
                <motion.div
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                >
                  {earlierEvents.map((event, i) => (
                    <TimelineItem
                      key={event.id}
                      event={event}
                      isLast={i === earlierEvents.length - 1}
                    />
                  ))}
                </motion.div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
