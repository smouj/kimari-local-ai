'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useKimariStore } from '@/lib/store'
import { useQuickActions, useExecuteQuickAction } from '@/hooks/use-api'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Play, Square, RotateCcw, Zap, Stethoscope, Trash2, Download, Loader2,
  ChevronDown, ChevronUp, Clock,
} from 'lucide-react'
import { toast } from 'sonner'
import { useState, useEffect, useCallback } from 'react'
import { cn } from '@/lib/utils'

const iconMap: Record<string, React.ReactNode> = {
  Play: <Play className="h-5 w-5" />,
  Square: <Square className="h-5 w-5" />,
  RotateCcw: <RotateCcw className="h-5 w-5" />,
  Zap: <Zap className="h-5 w-5" />,
  Stethoscope: <Stethoscope className="h-5 w-5" />,
  Trash2: <Trash2 className="h-5 w-5" />,
  Download: <Download className="h-5 w-5" />,
}

interface ActionHistoryItem {
  id: string
  actionId: string
  label: string
  timestamp: string
  success: boolean
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 16, scale: 0.96 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.35, ease: 'easeOut' },
  },
}

export function QuickLauncher() {
  const setActiveView = useKimariStore((s) => s.setActiveView)
  const { data: quickActionsData } = useQuickActions()
  const executeAction = useExecuteQuickAction()

  const [confirmAction, setConfirmAction] = useState<string | null>(null)
  const [runningActions, setRunningActions] = useState<Set<string>>(new Set())
  const [showHistory, setShowHistory] = useState(false)
  const [actionHistory, setActionHistory] = useState<ActionHistoryItem[]>([])

  // Load history from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem('kimari-action-history')
      if (stored) {
        setActionHistory(JSON.parse(stored))
      }
    } catch {
      // ignore
    }
  }, [])

  // Save history to localStorage
  const saveHistory = useCallback((history: ActionHistoryItem[]) => {
    setActionHistory(history)
    try {
      localStorage.setItem('kimari-action-history', JSON.stringify(history.slice(0, 20)))
    } catch {
      // ignore
    }
  }, [])

  const executeActionById = useCallback(async (actionId: string) => {
    const action = quickActionsData?.actions.find((a) => a.id === actionId)
    if (!action) return

    // If it's a navigation-only action, handle directly
    if (actionId === 'start_server') {
      setActiveView('server')
      return
    }
    if (actionId === 'download_model') {
      setActiveView('models')
      return
    }

    // Execute the action
    setRunningActions((prev) => new Set(prev).add(actionId))

    try {
      const result = await executeAction.mutateAsync(actionId)

      if (result.success) {
        toast.success(result.message, { description: result.details })
      } else {
        toast.error(result.message)
      }

      // Add to history
      const historyItem: ActionHistoryItem = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        actionId,
        label: action.label,
        timestamp: new Date().toISOString(),
        success: result.success,
      }
      saveHistory([historyItem, ...actionHistory].slice(0, 20))
    } catch (err) {
      toast.error('Action failed', { description: String(err) })
      const historyItem: ActionHistoryItem = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        actionId,
        label: action.label,
        timestamp: new Date().toISOString(),
        success: false,
      }
      saveHistory([historyItem, ...actionHistory].slice(0, 20))
    } finally {
      setRunningActions((prev) => {
        const next = new Set(prev)
        next.delete(actionId)
        return next
      })
      setConfirmAction(null)
    }
  }, [quickActionsData, executeAction, setActiveView, actionHistory, saveHistory])

  const handleActionClick = useCallback((actionId: string) => {
    const action = quickActionsData?.actions.find((a) => a.id === actionId)
    if (!action) return

    if (action.confirmRequired) {
      setConfirmAction(actionId)
    } else {
      executeActionById(actionId)
    }
  }, [quickActionsData, executeActionById])

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Only trigger if not in an input field and no modifier keys (except shift)
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement ||
        e.metaKey || e.ctrlKey || e.altKey
      ) return

      const key = e.key.toUpperCase()
      const action = quickActionsData?.actions.find((a) => a.shortcut === key)
      if (action && !runningActions.has(action.id)) {
        e.preventDefault()
        handleActionClick(action.id)
      }
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [quickActionsData, runningActions, handleActionClick])

  const actions = quickActionsData?.actions || []
  const categories = quickActionsData?.categories || []
  const confirmActionData = actions.find((a) => a.id === confirmAction)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
    >
      <Card className="glass-card depth-shadow card-glow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-primary/25 to-primary/5 flex items-center justify-center shadow-sm shadow-primary/10">
                <Play className="h-4 w-4 text-primary" />
              </div>
              <h3 className="text-base font-semibold">Quick Launcher</h3>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-[11px] gap-1 text-muted-foreground hover:text-foreground"
              onClick={() => setShowHistory(!showHistory)}
            >
              <Clock className="h-3 w-3" />
              History
              {showHistory ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </Button>
          </div>

          {/* Action Categories */}
          <div className="space-y-5">
            {categories.map((category) => {
              const categoryActions = actions.filter((a) => a.category === category.id)
              if (categoryActions.length === 0) return null

              return (
                <div key={category.id}>
                  <div className="text-[10px] font-semibold uppercase tracking-widest text-foreground/50 mb-2.5">
                    {category.label}
                  </div>
                  <motion.div
                    className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5"
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                  >
                    {categoryActions.map((action) => {
                      const isRunning = runningActions.has(action.id)
                      return (
                        <motion.button
                          key={action.id}
                          variants={itemVariants}
                          whileHover={{ scale: 1.04, boxShadow: '0 10px 30px -6px oklch(0.65 0.17 230 / 18%), 0 4px 12px -2px oklch(0 0 0 / 8%)' }}
                          whileTap={{ scale: 0.97 }}
                          onClick={() => handleActionClick(action.id)}
                          disabled={isRunning}
                          className={cn(
                            'group relative flex flex-col items-center gap-2.5 p-3.5 rounded-xl border border-border/50 bg-card/50',
                            'hover:border-primary/40 hover:bg-primary/[0.04] transition-colors duration-200 text-left',
                            'focus:outline-none focus:ring-2 focus:ring-primary/30 focus:ring-offset-1',
                            isRunning && 'opacity-80 cursor-wait'
                          )}
                        >
                          <div className="relative h-9 w-9 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center text-primary group-hover:from-primary/30 group-hover:to-primary/10 transition-all duration-200 shadow-sm shadow-primary/10">
                            {isRunning ? (
                              <Loader2 className="h-5 w-5 animate-spin" />
                            ) : (
                              iconMap[action.icon] || <Zap className="h-5 w-5" />
                            )}
                          </div>
                          <div className="text-center w-full">
                            <div className="text-xs font-medium text-foreground/90 group-hover:text-foreground transition-colors truncate">
                              {action.label}
                            </div>
                            <div className="text-[10px] text-muted-foreground mt-0.5 leading-snug line-clamp-2">
                              {action.description}
                            </div>
                          </div>
                          {action.shortcut && (
                            <kbd className="absolute top-1.5 right-1.5 inline-flex items-center justify-center h-4 min-w-4 px-1 rounded border border-border/50 bg-muted/50 text-[8px] font-mono text-muted-foreground">
                              {action.shortcut}
                            </kbd>
                          )}
                          {isRunning && (
                            <div className="absolute bottom-0 left-0 right-0 h-1 rounded-b-xl overflow-hidden">
                              <motion.div
                                className="h-full bg-primary/60"
                                initial={{ width: '0%' }}
                                animate={{ width: '100%' }}
                                transition={{ duration: action.estimatedDuration, ease: 'linear' }}
                              />
                            </div>
                          )}
                        </motion.button>
                      )
                    })}
                  </motion.div>
                </div>
              )
            })}
          </div>

          {/* Action History */}
          <AnimatePresence>
            {showHistory && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="mt-5 pt-4 border-t border-border/50">
                  <div className="text-[10px] font-semibold uppercase tracking-widest text-foreground/50 mb-3">
                    Recent Actions
                  </div>
                  {actionHistory.length === 0 ? (
                    <div className="text-xs text-muted-foreground text-center py-4">
                      No actions executed yet
                    </div>
                  ) : (
                    <div className="space-y-1.5 max-h-48 overflow-y-auto custom-scrollbar">
                      {actionHistory.slice(0, 10).map((item) => (
                        <div key={item.id} className="flex items-center gap-2 text-xs py-1.5 px-2 rounded-md bg-muted/20">
                          <div className={cn(
                            'h-1.5 w-1.5 rounded-full shrink-0',
                            item.success ? 'bg-emerald-500' : 'bg-red-500'
                          )} />
                          <span className="font-medium text-foreground/80 truncate">{item.label}</span>
                          <span className="ml-auto text-[10px] text-muted-foreground font-mono shrink-0">
                            {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Confirm Dialog */}
          <AlertDialog open={!!confirmAction} onOpenChange={(open) => { if (!open) setConfirmAction(null) }}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Confirm Action</AlertDialogTitle>
                <AlertDialogDescription>
                  {confirmActionData?.confirmMessage || `Are you sure you want to execute "${confirmActionData?.label}"?`}
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel onClick={() => setConfirmAction(null)}>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={() => confirmAction && executeActionById(confirmAction)}
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  Execute
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>
    </motion.div>
  )
}
