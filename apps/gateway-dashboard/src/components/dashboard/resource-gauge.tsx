'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

export interface ResourceGaugeProps {
  value: number
  max: number
  label: string
  unit: string
  color?: string
}

/**
 * Determine the gauge color based on the value relative to max.
 * green < 60%, amber 60-80%, red > 80%
 */
function getGaugeColor(value: number, max: number): { stroke: string; text: string; glow: string } {
  const pct = (value / max) * 100
  if (pct > 80) {
    return {
      stroke: 'oklch(0.63 0.22 25)',
      text: 'text-red-600 dark:text-red-400',
      glow: 'drop-shadow-[0_0_8px_oklch(0.63_0.22_25_/_35%)]',
    }
  }
  if (pct > 60) {
    return {
      stroke: 'oklch(0.75 0.15 85)',
      text: 'text-amber-600 dark:text-amber-400',
      glow: 'drop-shadow-[0_0_8px_oklch(0.75_0.15_85_/_35%)]',
    }
  }
  return {
    stroke: 'oklch(0.72 0.17 230)',
    text: 'text-emerald-600 dark:text-emerald-400',
    glow: 'drop-shadow-[0_0_8px_oklch(0.72_0.17_230_/_35%)]',
  }
}

export function ResourceGauge({ value, max, label, unit, color }: ResourceGaugeProps) {
  // Use explicit color if provided, otherwise auto-detect from value
  const autoColor = getGaugeColor(value, max)
  const strokeColor = color ?? autoColor.stroke
  const textClass = color ? 'text-primary' : autoColor.text
  const glowClass = color ? '' : autoColor.glow

  const size = 120
  const strokeWidth = 8
  const radius = (size - strokeWidth) / 2
  const center = size / 2
  const circumference = 2 * Math.PI * radius
  // 270-degree arc (3/4 circle)
  const arcLength = circumference * 0.75
  const gapLength = circumference * 0.25
  const rotation = 135
  const pct = max > 0 ? Math.min(value / max, 1) : 0

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={cn('relative', glowClass)}>
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
            className="text-muted/25"
            strokeDasharray={`${arcLength} ${gapLength}`}
            strokeLinecap="round"
            transform={`rotate(${rotation}, ${center}, ${center})`}
          />
          {/* Animated value arc */}
          <motion.circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${gapLength}`}
            strokeLinecap="round"
            transform={`rotate(${rotation}, ${center}, ${center})`}
            initial={{ strokeDashoffset: arcLength }}
            animate={{ strokeDashoffset: arcLength - arcLength * pct }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className={cn('text-2xl font-bold tabular-nums', textClass)}
            key={Math.round(value)}
            initial={{ opacity: 0.5, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            {Math.round(value)}
          </motion.span>
          <span className="text-[11px] text-muted-foreground font-medium -mt-0.5">
            {unit}
          </span>
        </div>
      </div>
      <span className="text-xs font-medium text-muted-foreground text-center">
        {label}
      </span>
    </div>
  )
}
