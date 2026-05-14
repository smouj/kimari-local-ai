'use client'

import { useState } from 'react'
import { useDoctor, useRunDoctor, type DiagnosticCheck } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Stethoscope,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ChevronDown,
  ChevronRight,
  RefreshCw,
  Activity,
  Shield,
  Cpu,
  Box,
  Settings,
  Server,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

const categoryIcons: Record<string, React.ReactNode> = {
  Runtime: <Cpu className="h-3.5 w-3.5" />,
  Core: <Settings className="h-3.5 w-3.5" />,
  Models: <Box className="h-3.5 w-3.5" />,
  Hardware: <Server className="h-3.5 w-3.5" />,
  Security: <Shield className="h-3.5 w-3.5" />,
  Gateway: <Activity className="h-3.5 w-3.5" />,
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'PASS':
      return <CheckCircle2 className="h-4 w-4 text-emerald-500" />
    case 'WARN':
      return <AlertTriangle className="h-4 w-4 text-amber-500" />
    case 'FAIL':
      return <XCircle className="h-4 w-4 text-red-500" />
    default:
      return null
  }
}

function StatusBadge({ status }: { status: 'PASS' | 'WARN' | 'FAIL' }) {
  const variants: Record<string, string> = {
    PASS: 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10',
    WARN: 'border-amber-500/40 text-amber-600 dark:text-amber-400 bg-amber-500/10',
    FAIL: 'border-red-500/40 text-red-600 dark:text-red-400 bg-red-500/10',
  }

  return (
    <Badge variant="outline" className={cn('font-mono text-[10px] px-2', variants[status])}>
      {status}
    </Badge>
  )
}

function ExpandableRow({ check, index }: { check: DiagnosticCheck; index: number }) {
  const [expanded, setExpanded] = useState(false)

  const rowBg: Record<string, string> = {
    PASS: 'bg-emerald-500/[0.03] dark:bg-emerald-500/[0.05]',
    WARN: 'bg-amber-500/[0.03] dark:bg-amber-500/[0.05]',
    FAIL: 'bg-red-500/[0.03] dark:bg-red-500/[0.05]',
  }

  const rowBorder: Record<string, string> = {
    PASS: 'border-l-[3px] border-l-emerald-500',
    WARN: 'border-l-[3px] border-l-amber-500',
    FAIL: 'border-l-[3px] border-l-red-500',
  }

  return (
    <>
      <TableRow
        className={cn(
          'cursor-pointer transition-colors hover:bg-muted/50',
          rowBg[check.status],
          rowBorder[check.status]
        )}
        onClick={() => setExpanded(!expanded)}
      >
        <TableCell className="w-10">
          <StatusIcon status={check.status} />
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm">{check.name}</span>
            <span className="text-[10px] text-muted-foreground font-mono">
              {check.category}
            </span>
          </div>
        </TableCell>
        <TableCell className="w-20">
          <StatusBadge status={check.status} />
        </TableCell>
        <TableCell className="text-sm text-muted-foreground max-w-xs">
          <span className="line-clamp-1">{check.message}</span>
        </TableCell>
        <TableCell className="w-8">
          {check.details && (
            <motion.div
              animate={{ rotate: expanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
            </motion.div>
          )}
        </TableCell>
      </TableRow>
      <AnimatePresence>
        {expanded && check.details && (
          <TableRow>
            <TableCell colSpan={5} className="p-0">
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className={cn(
                  'px-6 py-3 text-sm border-b',
                  'bg-muted/30 dark:bg-muted/20',
                  rowBg[check.status]
                )}>
                  <div className="flex items-start gap-2">
                    <ChevronRight className="h-3.5 w-3.5 mt-0.5 text-muted-foreground shrink-0" />
                    <span className="text-muted-foreground leading-relaxed">
                      {check.details}
                    </span>
                  </div>
                </div>
              </motion.div>
            </TableCell>
          </TableRow>
        )}
      </AnimatePresence>
    </>
  )
}

export function DoctorView() {
  const { data, isLoading, error } = useDoctor()
  const runDoctor = useRunDoctor()

  const handleRun = async () => {
    try {
      await runDoctor.mutateAsync()
    } catch {
      // Error handled by mutation state
    }
  }

  // Group checks by category
  const groupedChecks = (() => {
    if (!data?.checks) return {}
    const groups: Record<string, DiagnosticCheck[]> = {}
    data.checks.forEach((check) => {
      if (!groups[check.category]) groups[check.category] = []
      groups[check.category].push(check)
    })
    return groups
  })()

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-32 w-full rounded-xl" />
        <Skeleton className="h-60 w-full rounded-xl" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <Card className="border-red-500/30 bg-red-500/5">
          <CardContent className="py-12 text-center">
            <XCircle className="h-12 w-12 mx-auto mb-4 text-red-500" />
            <p className="text-lg font-medium text-red-600 dark:text-red-400">Diagnostics Failed</p>
            <p className="text-sm text-muted-foreground mt-1">{String(error)}</p>
            <Button className="mt-4 gap-2" onClick={handleRun} variant="outline">
              <RefreshCw className="h-4 w-4" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Summary Header */}
      <Card className="depth-shadow">
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center h-14 w-14 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
                <Stethoscope className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-bold tracking-tight">System Diagnostics</h2>
                <p className="text-sm text-muted-foreground">
                  {data?.checkedAt
                    ? `Last checked: ${new Date(data.checkedAt).toLocaleTimeString()}`
                    : 'Run diagnostics to check system health'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Badge className="bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20 font-mono">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  {data?.summary.pass ?? 0} PASS
                </Badge>
                <Badge className="bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30 hover:bg-amber-500/20 font-mono">
                  <AlertTriangle className="h-3 w-3 mr-1" />
                  {data?.summary.warn ?? 0} WARN
                </Badge>
                <Badge className="bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/30 hover:bg-red-500/20 font-mono">
                  <XCircle className="h-3 w-3 mr-1" />
                  {data?.summary.fail ?? 0} FAIL
                </Badge>
              </div>
              <Button
                className="gap-2 btn-press bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-white shadow-lg shadow-primary/20 font-semibold"
                onClick={handleRun}
                disabled={runDoctor.isPending}
              >
                <RefreshCw className={cn('h-4 w-4', runDoctor.isPending && 'animate-spin')} />
                {runDoctor.isPending ? 'Running...' : 'Run Diagnostics'}
              </Button>
            </div>
          </div>

          {/* Health Score Progress Bar */}
          <div className="mt-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Overall Health Score</span>
              <span className={cn(
                'text-5xl font-bold font-mono',
                (data?.healthScore ?? 0) > 70 ? 'text-emerald-600 dark:text-emerald-400' :
                (data?.healthScore ?? 0) > 40 ? 'text-amber-600 dark:text-amber-400' :
                'text-red-600 dark:text-red-400'
              )}>
                {data?.healthScore ?? 0}%
              </span>
            </div>
            <div
              className={cn(
                'h-4 w-full rounded-full overflow-hidden bg-muted/40 relative',
              )}
            >
              <motion.div
                className={cn(
                  'h-full rounded-full relative',
                  (data?.healthScore ?? 0) > 70
                    ? 'bg-gradient-to-r from-emerald-600 via-emerald-400 to-emerald-500'
                    : (data?.healthScore ?? 0) > 40
                    ? 'bg-gradient-to-r from-amber-600 via-amber-400 to-amber-500'
                    : 'bg-gradient-to-r from-red-600 via-red-400 to-red-500'
                )}
                initial={{ width: 0 }}
                animate={{ width: `${data?.healthScore ?? 0}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              >
                {/* Shine overlay on progress bar */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-gradient-shift" />
              </motion.div>
            </div>
            <div className="flex justify-between mt-1.5">
              <span className="text-[10px] text-muted-foreground">
                {(data?.summary.pass ?? 0)} of {(data?.summary.total ?? 14)} checks passed
              </span>
              <span className="text-[10px] text-muted-foreground">
                {data?.healthScore === 100 ? 'All systems nominal' : 'Issues detected'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Diagnostic Checks by Category */}
      {Object.entries(groupedChecks).map(([category, checks]) => (
        <Card key={category} className="depth-shadow">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-bold flex items-center gap-2.5">
              <span className="flex items-center justify-center h-6 w-6 rounded-md bg-primary/10 text-primary">
                {categoryIcons[category] ?? <Activity className="h-3.5 w-3.5" />}
              </span>
              {category}
              <Badge variant="outline" className="font-mono text-[10px] ml-1">
                {checks.length}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10"></TableHead>
                  <TableHead>Check</TableHead>
                  <TableHead className="w-20">Status</TableHead>
                  <TableHead>Message</TableHead>
                  <TableHead className="w-8"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {checks.map((check, index) => (
                  <ExpandableRow key={check.name} check={check} index={index} />
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
