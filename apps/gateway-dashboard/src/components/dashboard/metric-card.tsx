'use client'

import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

type CardVariant = 'status' | 'profile' | 'models' | 'memory'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  variant?: CardVariant
  className?: string
}

const variantStyles: Record<CardVariant, { gradient: string; iconBg: string; iconText: string; borderAccent: string; leftBorder: string; barColor: string }> = {
  status: {
    gradient: 'metric-gradient-status',
    iconBg: 'bg-gradient-to-br from-primary/20 to-primary/10',
    iconText: 'text-primary',
    borderAccent: 'hover:border-primary/40',
    leftBorder: 'border-l-primary',
    barColor: 'from-primary/60 via-primary/80 to-primary/60',
  },
  profile: {
    gradient: 'metric-gradient-profile',
    iconBg: 'bg-gradient-to-br from-sky-500/20 to-sky-600/10',
    iconText: 'text-sky-500 dark:text-sky-400',
    borderAccent: 'hover:border-sky-500/40',
    leftBorder: 'border-l-sky-500',
    barColor: 'from-sky-500/60 via-sky-400/80 to-sky-500/60',
  },
  models: {
    gradient: 'metric-gradient-models',
    iconBg: 'bg-gradient-to-br from-blue-500/20 to-blue-600/10',
    iconText: 'text-blue-500 dark:text-blue-400',
    borderAccent: 'hover:border-blue-500/40',
    leftBorder: 'border-l-blue-500',
    barColor: 'from-blue-500/60 via-blue-400/80 to-blue-500/60',
  },
  memory: {
    gradient: 'metric-gradient-memory',
    iconBg: 'bg-gradient-to-br from-indigo-500/20 to-indigo-600/10',
    iconText: 'text-indigo-500 dark:text-indigo-400',
    borderAccent: 'hover:border-indigo-500/40',
    leftBorder: 'border-l-indigo-500',
    barColor: 'from-indigo-500/60 via-indigo-400/80 to-indigo-500/60',
  },
}

const trendStyles = {
  up: { color: 'text-emerald-500 dark:text-emerald-400', bg: 'bg-emerald-500/10', icon: <TrendingUp className="h-4 w-4" /> },
  down: { color: 'text-red-500 dark:text-red-400', bg: 'bg-red-500/10', icon: <TrendingDown className="h-4 w-4" /> },
  neutral: { color: 'text-foreground/60', bg: 'bg-muted/50', icon: <Minus className="h-4 w-4" /> },
}

export function MetricCard({ title, value, subtitle, icon, trend, trendValue, variant = 'status', className }: MetricCardProps) {
  const styles = variantStyles[variant]
  const trendStyle = trend ? trendStyles[trend] : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
      className="hover-scale"
    >
      <Card className={cn(
        'glass-card card-hover-lift depth-shadow card-shine card-glow metric-hover-gradient metric-gradient-border-hover overflow-hidden transition-all duration-200 border-l-[3px]',
        styles.borderAccent,
        styles.leftBorder,
        className
      )}>
        <CardContent className={cn('p-6 relative', styles.gradient)}>
          {/* Subtle top accent line */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

          {/* Subtle inner glow at top (faint light source from above) */}
          <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-b from-foreground/[0.04] to-transparent pointer-events-none" />

          <div className="flex items-start justify-between relative z-[1]">
            <div className="space-y-2">
              <p className="text-[11px] text-foreground/70 font-semibold uppercase tracking-wider">{title}</p>
              <div className="flex items-baseline gap-2">
                <p className="text-3xl font-bold tracking-tight text-foreground">{value}</p>
                {trendStyle && (
                  <span className={cn('inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full', trendStyle.color, trendStyle.bg)}>
                    {trendStyle.icon}
                    {trendValue && <span>{trendValue}</span>}
                  </span>
                )}
              </div>
              {subtitle && (
                <p className="text-xs text-foreground/75 font-medium">{subtitle}</p>
              )}
            </div>
            <div className={cn(
              'flex items-center justify-center w-12 h-12 rounded-xl shrink-0 shadow-sm',
              styles.iconBg,
              styles.iconText
            )}>
              {icon}
            </div>
          </div>

          {/* Animated gradient bar at bottom */}
          <motion.div
            className={cn('absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r relative z-[1]', styles.barColor)}
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
            style={{ transformOrigin: 'left' }}
          />
        </CardContent>
      </Card>
    </motion.div>
  )
}
