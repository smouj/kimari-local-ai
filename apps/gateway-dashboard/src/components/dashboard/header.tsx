'use client'

import { useKimariStore, type ViewType } from '@/lib/store'
import { Badge } from '@/components/ui/badge'
import { useServerStatus, useNotifications } from '@/hooks/use-api'
import { useIsMobile } from '@/hooks/use-mobile'
import { Server, Menu, Bell, Keyboard, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'

const viewTitles: Record<ViewType, string> = {
  dashboard: 'Dashboard',
  profiles: 'GPU Profiles',
  models: 'Models',
  server: 'Server Controls',
  stats: 'Stats',
  analytics: 'Analytics',
  chat: 'AI Chat',
  modelCompare: 'Model Compare',
  doctor: 'System Doctor',
  benchmarks: 'Benchmarks',
  kimarifit: 'KimariFit Score',
  config: 'Configuration',
  logs: 'Logs',
  integrations: 'Integrations',
  settings: 'Settings',
}

const viewCategories: Record<ViewType, string> = {
  dashboard: 'Overview',
  profiles: 'Management',
  models: 'Management',
  server: 'Management',
  stats: 'Monitoring',
  analytics: 'Analysis',
  chat: 'Interaction',
  modelCompare: 'Analysis',
  doctor: 'Diagnostics',
  benchmarks: 'Analysis',
  kimarifit: 'Analysis',
  config: 'Settings',
  logs: 'Monitoring',
  integrations: 'Connect',
  settings: 'Preferences',
}

export function Header() {
  const { activeView, sidebarOpen, toggleSidebar, toggleNotifications, setExportDialogOpen } = useKimariStore()
  const { data: serverStatus } = useServerStatus()
  const { data: notificationsData } = useNotifications()
  const isMobile = useIsMobile()
  const [kbdPulsed, setKbdPulsed] = useState(false)

  const unreadCount = notificationsData?.unreadCount ?? 0

  const isRunning = serverStatus?.status === 'running'
  const isStarting = serverStatus?.status === 'starting'

  // Pulse the kbd badge on first load
  useEffect(() => {
    const timer = setTimeout(() => setKbdPulsed(true), 100)
    return () => clearTimeout(timer)
  }, [])

  // Show hamburger menu on mobile always, or on desktop when sidebar is collapsed
  const showHamburger = isMobile || !sidebarOpen

  return (
    <header className="sticky top-0 z-10 h-14 sm:h-16 border-b border-border/50 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60 top-border-gradient">
      <div className="flex items-center justify-between h-full px-3 sm:px-6">
        <div className="flex items-center gap-2 sm:gap-4 min-w-0">
          {/* Hamburger menu button */}
          {showHamburger && (
            <Button variant="ghost" size="icon" className="h-9 w-9 shrink-0 hover:bg-accent/60" onClick={toggleSidebar}>
              <Menu className="h-4 w-4" />
            </Button>
          )}
          <div className="flex flex-col min-w-0">
            {/* Breadcrumb */}
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-foreground/70 mb-0.5 bg-muted/30 rounded-md px-2 py-0.5 border-l-2 border-primary/50">
              <span className="font-medium">Kimari</span>
              <span className="text-border">•</span>
              <span className="font-medium">{viewCategories[activeView]}</span>
            </div>
            {/* Page Title */}
            <AnimatePresence mode="wait">
              <motion.h1
                key={activeView}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 8 }}
                transition={{ duration: 0.15 }}
                className="text-base sm:text-xl font-semibold tracking-tight truncate"
              >
                {viewTitles[activeView]}
              </motion.h1>
            </AnimatePresence>
          </div>
          {/* ⌘K badge — hidden on mobile */}
          <kbd
            className={cn(
              'hidden sm:inline-flex items-center gap-1 rounded border border-border/50 bg-muted/50 px-1.5 py-0.5 text-[10px] font-mono text-foreground/60 cursor-pointer hover:bg-muted transition-colors',
              !kbdPulsed && 'animate-kbd-pulse'
            )}
            onClick={() => {
              document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true }))
            }}
          >
            <span className="text-[9px]">⌘</span>K
          </kbd>
          {/* Keyboard shortcuts button — hidden on mobile */}
          <Button
            variant="ghost"
            size="icon"
            className="hidden sm:flex h-7 w-7 hover:bg-accent/60"
            onClick={() => {
              document.dispatchEvent(new KeyboardEvent('keydown', { key: '?' }))
            }}
          >
            <Keyboard className="h-3.5 w-3.5 text-foreground/60" />
          </Button>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
          {/* Export Button — hidden on very small screens */}
          <Button
            variant="ghost"
            size="icon"
            className="hidden sm:flex h-9 w-9 relative hover:bg-accent/60"
            onClick={() => setExportDialogOpen(true)}
          >
            <Download className="h-4 w-4" />
          </Button>
          {/* Notification Bell */}
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 relative hover:bg-accent/60"
            onClick={toggleNotifications}
          >
            <AnimatePresence mode="wait">
              <motion.span
                key={unreadCount}
                className="inline-flex"
                initial={unreadCount > 0 ? { rotate: 0 } : false}
                animate={unreadCount > 0 ? { rotate: [0, 14, -12, 8, -4, 0] } : { rotate: 0 }}
                transition={{ duration: 0.6, ease: 'easeInOut' }}
              >
                <Bell className="h-4 w-4" />
              </motion.span>
            </AnimatePresence>
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center h-4 min-w-4 px-1 rounded-full bg-primary text-primary-foreground text-[9px] font-bold leading-none">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </Button>
          {/* Status Badge — compact on mobile */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
          >
            <Badge
              variant="outline"
              className={cn(
                'flex items-center gap-1.5 sm:gap-2 px-3 sm:px-5 py-2 sm:py-2.5 font-bold text-xs sm:text-sm transition-all border-l-[3px] rounded-md',
                isRunning
                  ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-l-emerald-500'
                  : isStarting
                  ? 'border-amber-500/40 text-amber-600 dark:text-amber-400 bg-amber-500/10 border-l-amber-500'
                  : serverStatus?.status === 'error'
                  ? 'border-red-500/40 text-red-600 dark:text-red-400 bg-red-500/10 border-l-red-500'
                  : 'border-border/70 text-foreground/70 bg-muted/30 border-l-muted-foreground/40'
              )}
            >
              <span className="relative flex h-2.5 sm:h-3 w-2.5 sm:w-3">
                {(isRunning || isStarting) && (
                  <span className={cn(
                    'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
                    isRunning ? 'bg-emerald-400' : 'bg-amber-400'
                  )} />
                )}
                <span className={cn(
                  'relative inline-flex rounded-full h-2.5 sm:h-3 w-2.5 sm:w-3',
                  isRunning ? 'bg-emerald-500' : isStarting ? 'bg-amber-500' : serverStatus?.status === 'error' ? 'bg-red-500' : 'bg-foreground/40'
                )} />
              </span>
              <Server className="h-3.5 w-3.5 hidden sm:block" />
              <span className="hidden sm:inline">{isRunning ? 'Running' : isStarting ? 'Starting' : serverStatus?.status === 'error' ? 'Error' : 'Stopped'}</span>
              <span className="sm:hidden">{isRunning ? 'Live' : isStarting ? '...' : serverStatus?.status === 'error' ? 'Err' : 'Off'}</span>
            </Badge>
          </motion.div>
        </div>
      </div>
    </header>
  )
}
