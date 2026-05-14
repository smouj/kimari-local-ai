'use client'

import { cn } from '@/lib/utils'

interface StatusIndicatorProps {
  status: 'running' | 'starting' | 'stopped' | 'error'
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  className?: string
}

const statusConfig = {
  running: { color: 'bg-emerald-500', label: 'Running', ring: 'ring-emerald-500/30' },
  starting: { color: 'bg-amber-500', label: 'Starting', ring: 'ring-amber-500/30' },
  stopped: { color: 'bg-muted-foreground/40', label: 'Stopped', ring: '' },
  error: { color: 'bg-red-500', label: 'Error', ring: 'ring-red-500/30' },
}

const sizeConfig = {
  sm: { dot: 'h-2.5 w-2.5', text: 'text-xs' },
  md: { dot: 'h-3.5 w-3.5', text: 'text-sm' },
  lg: { dot: 'h-16 w-16', text: 'text-lg' },
}

export function StatusIndicator({ status, size = 'md', showLabel = true, className }: StatusIndicatorProps) {
  const config = statusConfig[status] || statusConfig.stopped
  const sizeC = sizeConfig[size]

  if (size === 'lg') {
    return (
      <div className={cn('flex flex-col items-center gap-3', className)}>
        <div
          className={cn(
            'rounded-full animate-glow-kimari',
            config.color,
            status === 'running' && 'animate-pulse'
          )}
        />
        {showLabel && (
          <span className={cn('font-semibold', sizeC.text)}>{config.label}</span>
        )}
      </div>
    )
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div
        className={cn(
          'rounded-full shrink-0',
          sizeC.dot,
          config.color,
          (status === 'running' || status === 'starting') && 'animate-pulse'
        )}
      />
      {showLabel && (
        <span className={cn('font-medium', sizeC.text)}>{config.label}</span>
      )}
    </div>
  )
}
