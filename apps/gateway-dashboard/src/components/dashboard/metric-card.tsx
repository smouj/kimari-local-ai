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
    iconBg: 'bg-gradient-to-br from-emerald-500/20 to-emerald-600/10',
    iconText: 'text-emerald-500 dark:text-emerald-400',
    borderAccent: 'hover:border-emerald-500/30',
    leftBorder: 'border-l-emerald-500',
    barColor: 'from-emerald-500/60 via-emerald-400/80 to-emerald-500/60',
  },
  profile: {
    gradient: 'metric-gradient-profile',
    iconBg: 'bg-gradient-to-br from-cyan-500/20 to-cyan-600/10',
    iconText: 'text-cyan-500 dark:text-cyan-400',
    borderAccent: 'hover:border-cyan-500/30',
    leftBorder: 'border-l-cyan-500',
    barColor: 'from-cyan-500/60 via-cyan-400/80 to-cyan-500/60',
  },
  models: {
    gradient: 'metric-gradient-models',
    iconBg: 'bg-gradient-to-br from-teal-500/20 to-teal-600/10',
    iconText: 'text-teal-500 dark:text-teal-400',
    borderAccent: 'hover:border-teal-500/30',
    leftBorder: 'border-l-teal-500',
    barColor: 'from-teal-500/60 via-teal-400/80 to-teal-500/60',
  },
  memory: {
    gradient: 'metric-gradient-memory',
    iconBg: 'bg-gradient-to-br from-primary/20 to-primary/10',
    iconText: 'text-primary',
    borderAccent: 'hover:border-primary/30',
    leftBorder: 'border-l-primary',
    barColor: 'from-primary/60 via-primary/80 to-primary/60',
  },
}

const trendStyles = {
  up: { color: 'text-emerald-500 dark:text-emerald-400', icon: <TrendingUp className="h-3.5 w-3.5" /> },
  down: { color: 'text-red-500 dark:text-red-400', icon: <TrendingDown className="h-3.5 w-3.5" /> },
  neutral: { color: 'text-foreground/60', icon: <Minus className="h-3.5 w-3.5" /> },
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
        'glass-card card-hover-lift depth-shadow card-shine card-glow metric-hover-gradient overflow-hidden transition-all duration-200 border-l-[3px]',
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
                  <span className={cn('flex items-center gap-0.5 text-xs font-semibold', trendStyle.color)}>
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
