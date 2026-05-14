'use client'

import { Sidebar } from './sidebar'
import { Header } from './header'
import { useKimariStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { useServerStatus } from '@/hooks/use-api'
import { usePreferences } from '@/hooks/use-preferences'
import { useIsMobile } from '@/hooks/use-mobile'
import { DashboardOverview } from './overview'
import { ProfilesView } from '@/components/profiles/profiles-view'
import { ModelsView } from '@/components/models/models-view'
import { ServerView } from '@/components/server/server-view'
import { BenchmarksView } from '@/components/benchmarks/benchmarks-view'
import { ConfigView } from '@/components/config/config-view'
import { LogsView } from '@/components/logs/logs-view'
import { IntegrationsView } from '@/components/integrations/integrations-view'
import { DoctorView } from '@/components/doctor/doctor-view'
import { KimariFitView } from '@/components/kimarifit/kimarifit-view'
import { AnalyticsView } from '@/components/analytics/analytics-view'
import { ChatView } from '@/components/chat/chat-view'
import { StatsView } from '@/components/stats/stats-view'
import { ModelCompareView } from '@/components/models/model-compare-view'
import { SettingsView } from '@/components/settings/settings-view'
import { ExportDialog } from '@/components/dashboard/export-dialog'
import { NotificationPanel } from '@/components/notifications/notification-panel'
import { CommandPalette } from '@/components/command-palette/command-palette'
import { ShortcutsHelpDialog } from '@/components/keyboard-shortcuts/shortcuts-help-dialog'
import { SetupWizard } from '@/components/setup/setup-wizard'
import { motion, AnimatePresence } from 'framer-motion'
import { Zap, Github, ExternalLink } from 'lucide-react'
import { useEffect, useState } from 'react'

const viewComponents: Record<string, React.ComponentType> = {
  dashboard: DashboardOverview,
  profiles: ProfilesView,
  models: ModelsView,
  server: ServerView,
  stats: StatsView,
  analytics: AnalyticsView,
  chat: ChatView,
  modelCompare: ModelCompareView,
  doctor: DoctorView,
  benchmarks: BenchmarksView,
  kimarifit: KimariFitView,
  config: ConfigView,
  logs: LogsView,
  integrations: IntegrationsView,
  settings: SettingsView,
}

export function DashboardShell() {
  const { activeView, setupComplete, setSetupComplete, exportDialogOpen, setExportDialogOpen } = useKimariStore()
  const { data: serverStatus } = useServerStatus()
  const isMobile = useIsMobile()
  const ViewComponent = viewComponents[activeView] || DashboardOverview

  const isRunning = serverStatus?.status === 'running'
  const uptime = serverStatus?.uptime ?? 0

  const [currentTime, setCurrentTime] = useState('')

  // Initialize user preferences persistence
  usePreferences()

  useEffect(() => {
    const stored = localStorage.getItem('kimari-setup-complete')
    if (stored === 'true') {
      setSetupComplete(true)
    }
  }, [setSetupComplete])

  // Update current time every second
  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

  if (!setupComplete) {
    return <SetupWizard />
  }

  function formatUptime(seconds: number): string {
    if (!seconds) return '0s'
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    if (h > 0) return `${h}h ${m}m`
    if (m > 0) return `${m}m`
    return `${seconds}s`
  }

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex flex-1">
      {/* On mobile, Sidebar renders as a Sheet overlay (not in flex flow) */}
      {/* On desktop, Sidebar is a flex child with width */}
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 dot-grid-bg relative">
          {/* Subtle top gradient border */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
          <AnimatePresence mode="wait">
            <motion.div
              key={activeView}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <ViewComponent />
            </motion.div>
          </AnimatePresence>
        </main>
        <footer className="footer-gradient-border border-t border-border/60 bg-background/90 backdrop-blur-xl py-2.5 sm:py-3.5 px-3 sm:px-6 mt-auto">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-1 sm:gap-0">
            <div className="flex items-center gap-2 sm:gap-3 text-[10px] sm:text-xs text-foreground/70">
              <div className="flex items-center gap-1.5">
                <Zap className="h-3 w-3 text-primary" />
                <span className="font-semibold text-foreground/85">Kimari</span>
                <span className="font-mono text-[9px] sm:text-[10px] bg-muted/60 px-1.5 py-0.5 rounded text-foreground/60">v0.1.73-alpha</span>
              </div>
              <span className="text-border hidden sm:inline">|</span>
              <span className="font-medium hidden sm:inline">Powered by llama.cpp</span>
            </div>
            <div className="flex items-center gap-2 sm:gap-4 text-[10px] sm:text-xs text-foreground/70">
              <div className="flex items-center gap-1.5">
                <div className={cn(
                  'h-1.5 sm:h-2 w-1.5 sm:w-2 rounded-full',
                  isRunning ? 'bg-emerald-500 status-dot-pulse' : 'bg-foreground/35'
                )} />
                <span className="font-medium">API: {isRunning ? `localhost:${serverStatus?.port ?? '-'}` : 'Offline'}</span>
              </div>
              {isRunning && (
                <>
                  <span className="text-border hidden sm:inline">|</span>
                  <span className="font-medium hidden sm:inline">Uptime: {formatUptime(uptime)}</span>
                </>
              )}
              {currentTime && (
                <>
                  <span className="text-border hidden sm:inline">|</span>
                  <span className="font-mono text-foreground/75 hidden sm:inline">{currentTime}</span>
                </>
              )}
              <a
                href="https://github.com/smouj/kimari-local-ai"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 hover:text-foreground transition-colors"
              >
                <Github className="h-3 w-3" />
                <ExternalLink className="h-2.5 w-2.5" />
              </a>
            </div>
          </div>
        </footer>
      </div>
      </div>
      <NotificationPanel />
      <CommandPalette />
      <ShortcutsHelpDialog />
      <ExportDialog open={exportDialogOpen} onOpenChange={setExportDialogOpen} />
    </div>
  )
}
