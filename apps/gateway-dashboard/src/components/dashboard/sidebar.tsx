'use client'

import { useTheme } from 'next-themes'
import { useKimariStore, type ViewType } from '@/lib/store'
import { useIsMobile } from '@/hooks/use-mobile'
import {
  LayoutDashboard,
  Cpu,
  Box,
  Server,
  Activity,
  Stethoscope,
  BarChart3,
  Gauge,
  Settings,
  ScrollText,
  Puzzle,
  ChevronLeft,
  ChevronRight,
  Moon,
  Sun,
  RefreshCw,
  Pin,
  PinOff,
  MessageSquare,
  GitCompare,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { useServerStatus, useUpdateCheck } from '@/hooks/use-api'
import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const navItems: { view: ViewType; label: string; icon: React.ReactNode; group: string }[] = [
  { view: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="h-4 w-4" />, group: 'main' },
  { view: 'profiles', label: 'GPU Profiles', icon: <Cpu className="h-4 w-4" />, group: 'main' },
  { view: 'models', label: 'Models', icon: <Box className="h-4 w-4" />, group: 'main' },
  { view: 'server', label: 'Server', icon: <Server className="h-4 w-4" />, group: 'main' },
  { view: 'chat', label: 'Chat', icon: <MessageSquare className="h-4 w-4" />, group: 'main' },
  { view: 'stats', label: 'Stats', icon: <Activity className="h-4 w-4" />, group: 'main' },
  { view: 'analytics', label: 'Analytics', icon: <BarChart3 className="h-4 w-4" />, group: 'main' },
  { view: 'doctor', label: 'Doctor', icon: <Stethoscope className="h-4 w-4" />, group: 'tools' },
  { view: 'modelCompare', label: 'Model Compare', icon: <GitCompare className="h-4 w-4" />, group: 'tools' },
  { view: 'benchmarks', label: 'Benchmarks', icon: <BarChart3 className="h-4 w-4" />, group: 'tools' },
  { view: 'kimarifit', label: 'KimariFit', icon: <Gauge className="h-4 w-4" />, group: 'tools' },
  { view: 'config', label: 'Configuration', icon: <Settings className="h-4 w-4" />, group: 'tools' },
  { view: 'logs', label: 'Logs', icon: <ScrollText className="h-4 w-4" />, group: 'tools' },
  { view: 'integrations', label: 'Integrations', icon: <Puzzle className="h-4 w-4" />, group: 'tools' },
  { view: 'settings', label: 'Settings', icon: <Settings className="h-4 w-4" />, group: 'system' },
]

const groupLabels: Record<string, string> = {
  main: 'Main',
  tools: 'Tools',
  system: 'System',
}

function SidebarContent({ isMobile = false, onNavClick }: { isMobile?: boolean; onNavClick?: () => void }) {
  const { activeView, setActiveView, sidebarOpen, toggleSidebar } = useKimariStore()
  const [isPinned, setIsPinned] = useState(true)
  const { theme, setTheme } = useTheme()
  const { data: serverStatus } = useServerStatus()
  const setServerStatus = useKimariStore((s) => s.setServerStatus)
  const { data: updateData, refetch: checkUpdate, isFetching: isCheckingUpdate } = useUpdateCheck()
  const [updateChecked, setUpdateChecked] = useState(false)

  useEffect(() => {
    if (serverStatus) {
      setServerStatus(serverStatus)
    }
  }, [serverStatus, setServerStatus])

  const isRunning = serverStatus?.status === 'running'
  const isStarting = serverStatus?.status === 'starting'

  const groups = ['main', 'tools', 'system']

  const handleNavClick = (view: ViewType) => {
    setActiveView(view)
    // On mobile, close sidebar after navigation
    if (isMobile && onNavClick) {
      onNavClick()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Brand */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-border/50">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-primary/70 shrink-0 shadow-lg shadow-primary/20 overflow-hidden">
          <img src="/kimari-logo.png" alt="Kimari" className="h-8 w-8 object-contain" />
        </div>
        <AnimatePresence>
          {(sidebarOpen || isMobile) && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.2 }}
              className="flex flex-col min-w-0 flex-1"
            >
              <span className="font-bold text-lg leading-tight tracking-tight text-sidebar-foreground truncate">
                Kimari
              </span>
              <span className="text-[11px] text-foreground/70 leading-tight font-medium">
                Local AI Gateway
              </span>
            </motion.div>
          )}
        </AnimatePresence>
        {!isMobile && sidebarOpen && (
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 shrink-0 hover:bg-sidebar-accent/60 btn-press"
            onClick={() => setIsPinned(!isPinned)}
          >
            {isPinned ? (
              <Pin className="h-3.5 w-3.5 text-foreground/60" />
            ) : (
              <PinOff className="h-3.5 w-3.5 text-foreground/60" />
            )}
          </Button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-2 overflow-y-auto custom-scrollbar">
        {groups.map((group) => (
          <div key={group} className="mb-2">
            {(sidebarOpen || isMobile) && (
              <div className="px-3 py-1.5">
                <span className="text-[10px] font-semibold uppercase tracking-widest text-foreground/50">
                  {groupLabels[group]}
                </span>
              </div>
            )}
            <div className="space-y-0.5">
              {navItems.filter((item) => item.group === group).map((item) => {
                const isActive = activeView === item.view
                const btn = (
                  <button
                    key={item.view}
                    onClick={() => handleNavClick(item.view)}
                    className={cn(
                      'relative flex items-center gap-3 w-full rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'nav-active-bg text-sidebar-accent-foreground shadow-sm'
                        : 'text-sidebar-foreground/60 hover:bg-sidebar-accent/40 hover:text-sidebar-foreground transition-colors duration-200',
                      !sidebarOpen && !isMobile && 'justify-center px-0',
                      'hover-lift'
                    )}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="sidebar-active-indicator"
                        className="absolute left-0 top-1/2 -translate-y-1/2 w-[4px] h-6 rounded-full bg-primary shadow-md shadow-primary/30"
                        transition={{ type: 'spring', stiffness: 350, damping: 30 }}
                      />
                    )}
                    <span className={cn('shrink-0 transition-colors duration-200', isActive && 'text-primary')}>
                      {item.icon}
                    </span>
                    {(sidebarOpen || isMobile) && (
                      <span className={cn('truncate transition-colors duration-200', isActive && 'font-semibold')}>
                        {item.label}
                      </span>
                    )}
                  </button>
                )

                if (!sidebarOpen && !isMobile) {
                  return (
                    <Tooltip key={item.view}>
                      <TooltipTrigger asChild>{btn}</TooltipTrigger>
                      <TooltipContent side="right" className="font-medium">
                        {item.label}
                      </TooltipContent>
                    </Tooltip>
                  )
                }

                return btn
              })}
            </div>
            {group === 'main' && <Separator className="my-4 bg-border/70" />}
          </div>
        ))}
      </nav>

      <Separator className="bg-border/50" />

      {/* Bottom Section */}
      <div className="p-3 space-y-2.5">
        {/* Theme Toggle */}
        <div className={cn('flex items-center', (sidebarOpen || isMobile) ? 'justify-between' : 'justify-center')}>
          {(sidebarOpen || isMobile) && <span className="text-xs text-foreground/65 font-medium">Theme</span>}
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 hover:bg-sidebar-accent/60 btn-press"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={theme}
                initial={{ rotate: -90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                {theme === 'dark' ? (
                  <Sun className="h-4 w-4" />
                ) : (
                  <Moon className="h-4 w-4" />
                )}
              </motion.div>
            </AnimatePresence>
          </Button>
        </div>

        <Separator className="bg-border/30" />

        {/* Server Status */}
        <div className={cn('flex items-center gap-2', !sidebarOpen && !isMobile && 'justify-center')}>
          <div
            className={cn(
              'h-3.5 w-3.5 rounded-full shrink-0',
              isRunning
                ? 'bg-emerald-500 status-dot-pulse'
                : isStarting
                ? 'bg-amber-500 status-dot-pulse'
                : 'bg-foreground/35'
            )}
          />
          {(sidebarOpen || isMobile) && (
            <span className={cn(
              'text-xs truncate font-medium',
              isRunning ? 'text-emerald-600 dark:text-emerald-400' : isStarting ? 'text-amber-600 dark:text-amber-400' : 'text-foreground/70'
            )}>
              {isRunning ? `Running: ${serverStatus?.profile}` : isStarting ? 'Starting...' : 'Server Offline'}
            </span>
          )}
        </div>

        {/* Check for Updates */}
        {(sidebarOpen || isMobile) && (
          <Button
            variant="ghost"
            size="sm"
            className="w-full h-7 text-[11px] gap-1.5 justify-center text-foreground/65 hover:text-foreground font-medium"
            onClick={() => { checkUpdate(); setUpdateChecked(true) }}
            disabled={isCheckingUpdate}
          >
            <RefreshCw className={cn('h-3 w-3', isCheckingUpdate && 'animate-spin')} />
            {isCheckingUpdate ? 'Checking...' : updateChecked && updateData ? (updateData.updateAvailable ? 'Update available!' : 'Up to date') : 'Check Updates'}
          </Button>
        )}

        {/* Version */}
        {(sidebarOpen || isMobile) && (
          <div className="flex items-center justify-between">
            <Badge variant="outline" className={cn('text-[10px] h-5 px-2 font-mono border-border/50 min-w-0', updateData?.updateAvailable && 'border-amber-500/40 text-amber-600 dark:text-amber-400')}>
              v0.1.73-alpha
            </Badge>
            {updateData?.updateAvailable && (
              <Badge className="text-[11px] h-5 px-1.5 bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30">
                New: v{updateData.latestVersion}
              </Badge>
            )}
          </div>
        )}

        {/* Collapse Toggle (desktop only) */}
        {!isMobile && (
          <Button
            variant="ghost"
            size="icon"
            className={cn('h-8 w-8 hover:bg-sidebar-accent/60 btn-press', sidebarOpen ? 'ml-auto' : 'mx-auto')}
            onClick={toggleSidebar}
          >
            {sidebarOpen ? (
              <ChevronLeft className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>
    </div>
  )
}

export function Sidebar() {
  const isMobile = useIsMobile()
  const { sidebarOpen, setSidebarOpen } = useKimariStore()

  // On mobile, render as a Sheet overlay
  if (isMobile) {
    return (
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="w-[280px] p-0 sidebar-gradient">
          <SheetHeader className="sr-only">
            <SheetTitle>Navigation</SheetTitle>
          </SheetHeader>
          <SidebarContent isMobile onNavClick={() => setSidebarOpen(false)} />
        </SheetContent>
      </Sheet>
    )
  }

  // On desktop, render as a regular aside
  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          'sidebar-gradient flex flex-col border-r border-border transition-all duration-300 ease-in-out h-screen sticky top-0',
          sidebarOpen ? 'w-[280px]' : 'w-[68px]'
        )}
      >
        <SidebarContent />
      </aside>
    </TooltipProvider>
  )
}
