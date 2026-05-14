'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useKimariStore, type ViewType } from '@/lib/store'
import { useTheme } from 'next-themes'
import { useStartServer, useStopServer, useRunBenchmark } from '@/hooks/use-api'
import { toast } from 'sonner'
import { Keyboard } from 'lucide-react'
import { motion } from 'framer-motion'

interface ShortcutItem {
  keys: string[]
  description: string
}

interface ShortcutSection {
  title: string
  items: ShortcutItem[]
}

const isMac = typeof window !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0
const mod = isMac ? '⌘' : 'Ctrl'

const shortcutSections: ShortcutSection[] = [
  {
    title: 'Navigation',
    items: [
      { keys: [mod, 'K'], description: 'Command Palette' },
      { keys: ['1'], description: 'Dashboard' },
      { keys: ['2'], description: 'GPU Profiles' },
      { keys: ['3'], description: 'Models' },
      { keys: ['4'], description: 'Server' },
      { keys: ['5'], description: 'Analytics' },
      { keys: ['6'], description: 'Doctor' },
      { keys: ['7'], description: 'Benchmarks' },
      { keys: ['8'], description: 'KimariFit' },
      { keys: ['9'], description: 'Configuration' },
    ],
  },
  {
    title: 'Actions',
    items: [
      { keys: [mod, 'Enter'], description: 'Start Server' },
      { keys: [mod, 'Shift', 'X'], description: 'Stop Server' },
      { keys: [mod, 'Shift', 'B'], description: 'Run Benchmark' },
    ],
  },
  {
    title: 'Interface',
    items: [
      { keys: [mod, 'B'], description: 'Toggle Sidebar' },
      { keys: [mod, '\\'], description: 'Toggle Theme' },
      { keys: ['?'], description: 'Show Shortcuts' },
    ],
  },
]

function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="inline-flex items-center justify-center min-w-[24px] h-6 px-1.5 rounded border border-border/60 bg-muted/60 text-[11px] font-mono font-medium text-muted-foreground shadow-sm">
      {children}
    </kbd>
  )
}

export function KeyboardShortcutsDialog() {
  const [open, setOpen] = useState(false)
  const { setActiveView, toggleSidebar } = useKimariStore()
  const { setTheme, theme } = useTheme()
  const startServer = useStartServer()
  const stopServer = useStopServer()
  const runBenchmark = useRunBenchmark()

  const viewMap: Record<string, ViewType> = {
    '1': 'dashboard',
    '2': 'profiles',
    '3': 'models',
    '4': 'server',
    '5': 'analytics',
    '6': 'doctor',
    '7': 'benchmarks',
    '8': 'kimarifit',
    '9': 'config',
  }

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    const target = e.target as HTMLElement
    const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable

    // "?" to open shortcuts (but not in input fields)
    if (e.key === '?' && !isInput) {
      e.preventDefault()
      setOpen((prev) => !prev)
      return
    }

    // Number keys 1-9 for navigation (not in input fields, not with modifiers except alone)
    if (!isInput && !e.metaKey && !e.ctrlKey && !e.altKey) {
      const view = viewMap[e.key]
      if (view) {
        e.preventDefault()
        setActiveView(view)
        return
      }
    }

    // Ctrl/Cmd + B for sidebar toggle
    if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
      e.preventDefault()
      toggleSidebar()
      return
    }

    // Ctrl/Cmd + \ for theme toggle
    if ((e.metaKey || e.ctrlKey) && e.key === '\\') {
      e.preventDefault()
      setTheme(theme === 'dark' ? 'light' : 'dark')
      return
    }

    // Ctrl/Cmd + Enter for start server
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault()
      startServer.mutateAsync('rtx-3060').then(() => {
        toast.success('Server starting...')
      }).catch(() => {
        toast.error('Failed to start server')
      })
      return
    }

    // Ctrl/Cmd + Shift + X for stop server
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === 'x' || e.key === 'X')) {
      e.preventDefault()
      stopServer.mutateAsync().then(() => {
        toast.success('Server stopped')
      }).catch(() => {
        toast.error('Failed to stop server')
      })
      return
    }

    // Ctrl/Cmd + Shift + B for run benchmark
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === 'b' || e.key === 'B')) {
      e.preventDefault()
      runBenchmark.mutateAsync({ profile: 'rtx-3060', mode: 'dry_run' }).then(() => {
        toast.success('Benchmark completed')
      }).catch(() => {
        toast.error('Benchmark failed')
      })
      return
    }
  }, [viewMap, setActiveView, toggleSidebar, setTheme, theme, startServer, stopServer, runBenchmark])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-[520px] glass-card">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard className="h-5 w-5 text-primary" />
            Keyboard Shortcuts
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-6 mt-2">
          {shortcutSections.map((section, sIdx) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: sIdx * 0.05 }}
            >
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                {section.title}
              </h3>
              <div className="space-y-2">
                {section.items.map((item) => (
                  <div
                    key={item.description}
                    className="flex items-center justify-between py-1.5 px-2 rounded-md hover:bg-muted/30 transition-colors"
                  >
                    <span className="text-sm">{item.description}</span>
                    <div className="flex items-center gap-1">
                      {item.keys.map((key, i) => (
                        <span key={i} className="flex items-center gap-1">
                          {i > 0 && <span className="text-[10px] text-muted-foreground/50">+</span>}
                          <Kbd>{key}</Kbd>
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
        <div className="mt-2 pt-4 border-t border-border/50">
          <p className="text-xs text-muted-foreground text-center">
            Press <Kbd>?</Kbd> anytime to toggle this dialog
          </p>
        </div>
      </DialogContent>
    </Dialog>
  )
}
