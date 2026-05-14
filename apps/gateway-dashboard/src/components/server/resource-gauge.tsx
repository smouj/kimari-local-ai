'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ResourceGaugeProps {
  value: number
  maxValue?: number
  label: string
  unit?: string
  color?: 'green' | 'amber' | 'red' | 'muted'
  size?: number
}

function getColorClasses(color: ResourceGaugeProps['color']) {
  switch (color) {
    case 'green':
      return {
        stroke: 'oklch(0.72 0.17 230)',
        strokeClass: 'stroke-emerald-500',
        textClass: 'text-emerald-600 dark:text-emerald-400',
        glowClass: 'drop-shadow-[0_0_6px_oklch(0.72_0.17_230_/_40%)]',
      }
    case 'amber':
      return {
        stroke: 'oklch(0.75 0.15 85)',
        strokeClass: 'stroke-amber-500',
        textClass: 'text-amber-600 dark:text-amber-400',
        glowClass: 'drop-shadow-[0_0_6px_oklch(0.75_0.15_85_/_40%)]',
      }
    case 'red':
      return {
        stroke: 'oklch(0.63 0.22 25)',
        strokeClass: 'stroke-red-500',
        textClass: 'text-red-600 dark:text-red-400',
        glowClass: 'drop-shadow-[0_0_6px_oklch(0.63_0.22_25_/_40%)]',
      }
    case 'muted':
    default:
      return {
        stroke: 'oklch(0.5 0.02 165 / 30%)',
        strokeClass: 'stroke-muted-foreground/30',
        textClass: 'text-muted-foreground/50',
        glowClass: '',
      }
  }
}

function getAutoColor(value: number, maxValue: number): 'green' | 'amber' | 'red' {
  const pct = (value / maxValue) * 100
  if (pct >= 90) return 'red'
  if (pct >= 70) return 'amber'
  return 'green'
}

export function ResourceGauge({
  value,
  maxValue = 100,
  label,
  unit = '%',
  color,
  size = 120,
}: ResourceGaugeProps) {
  const effectiveColor = color ?? getAutoColor(value, maxValue)
  const colors = getColorClasses(effectiveColor)
  const pct = maxValue > 0 ? Math.min(value / maxValue, 1) : 0

  // SVG arc math
  const strokeWidth = size * 0.08
  const radius = (size - strokeWidth) / 2
  const center = size / 2
  const circumference = 2 * Math.PI * radius
  const arcLength = circumference * 0.75 // 270-degree arc
  const gapLength = circumference * 0.25

  // The arc starts from the bottom-left (135 degrees) to bottom-right (45 degrees)
  const rotation = 135

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={cn('relative', colors.glowClass)}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="transform -rotate-90"
        >
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-muted/30"
            strokeDasharray={`${arcLength} ${gapLength}`}
            strokeLinecap="round"
            transform={`rotate(${rotation}, ${center}, ${center})`}
          />
          {/* Value arc */}
          <motion.circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${gapLength}`}
            strokeLinecap="round"
            transform={`rotate(${rotation}, ${center}, ${center})`}
            initial={{ strokeDashoffset: arcLength }}
            animate={{ strokeDashoffset: arcLength - arcLength * pct }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className={cn('text-xl font-bold tabular-nums', colors.textClass)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            {Math.round(value)}
          </motion.span>
          <span className="text-[10px] text-muted-foreground font-medium -mt-0.5">
            {unit}
          </span>
        </div>
      </div>
      <span className={cn('text-xs font-medium text-center', effectiveColor === 'muted' ? 'text-muted-foreground/50' : 'text-muted-foreground')}>
        {label}
      </span>
    </div>
  )
}
