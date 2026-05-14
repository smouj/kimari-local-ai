'use client'

import { useEffect, useState } from 'react'
import { useKimariStore, type ViewType } from '@/lib/store'
import { useStartServer, useStopServer, useRunDoctor, useUpdateCheck, useRunBenchmark } from '@/hooks/use-api'
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from '@/components/ui/command'
import {
  LayoutDashboard, Cpu, Box, Server, BarChart3, Stethoscope, Activity, Gauge, Settings, ScrollText, Puzzle,
  Play, Square, RefreshCw, Sun, Moon, PanelLeftClose, PanelLeft, Zap, Monitor, MessageSquare, GitCompare,
} from 'lucide-react'
import { useTheme } from 'next-themes'
import { toast } from 'sonner'

const views = [
  { view: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, group: 'Navigation' },
  { view: 'profiles', label: 'GPU Profiles', icon: Cpu, group: 'Navigation' },
  { view: 'models', label: 'Models', icon: Box, group: 'Navigation' },
  { view: 'server', label: 'Server Controls', icon: Server, group: 'Navigation' },
  { view: 'chat', label: 'AI Chat', icon: MessageSquare, group: 'Navigation' },
  { view: 'modelCompare', label: 'Model Compare', icon: GitCompare, group: 'Navigation' },
  { view: 'stats', label: 'Live Stats', icon: Activity, group: 'Navigation'},
  { view: 'analytics', label: 'Analytics', icon: BarChart3, group: 'Navigation' },
  { view: 'doctor', label: 'System Doctor', icon: Stethoscope, group: 'Navigation' },
  { view: 'benchmarks', label: 'Benchmarks', icon: Gauge, group: 'Navigation' },
  { view: 'kimarifit', label: 'KimariFit Score', icon: Gauge, group: 'Navigation' },
  { view: 'config', label: 'Configuration', icon: Settings, group: 'Navigation' },
  { view: 'logs', label: 'Logs', icon: ScrollText, group: 'Navigation' },
  { view: 'integrations', label: 'Integrations', icon: Puzzle, group: 'Navigation' },
  { view: 'settings', label: 'Settings', icon: Settings, group: 'Navigation' },
]

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const { setActiveView, sidebarOpen, toggleSidebar } = useKimariStore()
  const { theme, setTheme } = useTheme()
  const startServer = useStartServer()
  const stopServer = useStopServer()
  const runDoctor = useRunDoctor()
  const runBenchmark = useRunBenchmark()
  const { refetch: checkUpdate } = useUpdateCheck()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((prev) => !prev)
      }
    }
    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  const runAction = async (action: string) => {
    setOpen(false)
    switch (action) {
      case 'start-server':
        try {
          await startServer.mutateAsync('test')
          toast.success('Server starting...')
        } catch {
          toast.error('Failed to start server')
        }
        break
      case 'stop-server':
        try {
          await stopServer.mutateAsync()
          toast.success('Server stopped')
        } catch {
          toast.error('Failed to stop server')
        }
        break
      case 'run-diagnostics':
        try {
          await runDoctor.mutateAsync()
          toast.success('Diagnostics running...')
        } catch {
          toast.error('Failed to run diagnostics')
        }
        break
      case 'run-benchmark':
        try {
          await runBenchmark.mutateAsync({ profile: 'default', mode: 'standard' })
          toast.success('Benchmark started...')
        } catch {
          toast.error('Failed to run benchmark')
        }
        break
      case 'check-updates':
        checkUpdate()
        toast.info('Checking for updates...')
        break
      case 'toggle-theme':
        setTheme(theme === 'dark' ? 'light' : 'dark')
        break
      case 'toggle-sidebar':
        toggleSidebar()
        break
    }
  }

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Navigation">
          {views.map((v) => (
            <CommandItem
              key={v.view}
              onSelect={() => { setActiveView(v.view as ViewType); setOpen(false) }}
            >
              <v.icon className="mr-2 h-4 w-4" />
              {v.label}
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Actions">
          <CommandItem onSelect={() => runAction('start-server')}>
            <Play className="mr-2 h-4 w-4 text-emerald-500" />
            Start Server
          </CommandItem>
          <CommandItem onSelect={() => runAction('stop-server')}>
            <Square className="mr-2 h-4 w-4 text-red-500" />
            Stop Server
          </CommandItem>
          <CommandItem onSelect={() => runAction('run-diagnostics')}>
            <Stethoscope className="mr-2 h-4 w-4 text-primary" />
            Run Diagnostics
          </CommandItem>
          <CommandItem onSelect={() => runAction('run-benchmark')}>
            <Zap className="mr-2 h-4 w-4 text-amber-500" />
            Run Benchmark
          </CommandItem>
          <CommandItem onSelect={() => runAction('check-updates')}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Check for Updates
          </CommandItem>
          <CommandItem onSelect={() => { setActiveView('dashboard'); setOpen(false) }}>
            <Monitor className="mr-2 h-4 w-4 text-primary" />
            View System Resources
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Interface">
          <CommandItem onSelect={() => runAction('toggle-theme')}>
            {theme === 'dark' ? <Sun className="mr-2 h-4 w-4" /> : <Moon className="mr-2 h-4 w-4" />}
            Toggle Theme
          </CommandItem>
          <CommandItem onSelect={() => runAction('toggle-sidebar')}>
            {sidebarOpen ? <PanelLeftClose className="mr-2 h-4 w-4" /> : <PanelLeft className="mr-2 h-4 w-4" />}
            Toggle Sidebar
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
