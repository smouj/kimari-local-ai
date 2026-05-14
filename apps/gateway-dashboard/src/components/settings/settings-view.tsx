'use client'

import { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { useTheme } from 'next-themes'
import { useKimariStore } from '@/lib/store'
import { toast } from 'sonner'
import {
  Settings,
  Palette,
  Sidebar,
  RefreshCw,
  Bell,
  LayoutDashboard,
  Sun,
  Moon,
  Monitor,
  Eye,
  EyeOff,
  Save,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

interface DashboardSectionPrefs {
  welcomeBanner: boolean
  quickLaunch: boolean
  systemResources: boolean
  activityTimeline: boolean
  recentLogs: boolean
}

interface UserPrefs {
  theme: string
  sidebarDefaultOpen: boolean
  refreshInterval: number
  notificationsEnabled: boolean
  soundAlerts: boolean
  dashboardSections: DashboardSectionPrefs
}

const PREFS_STORAGE_KEY = 'kimari-user-preferences'

function loadPrefs(): UserPrefs {
  if (typeof window === 'undefined') {
    return {
      theme: 'dark',
      sidebarDefaultOpen: true,
      refreshInterval: 5,
      notificationsEnabled: true,
      soundAlerts: false,
      dashboardSections: {
        welcomeBanner: true,
        quickLaunch: true,
        systemResources: true,
        activityTimeline: true,
        recentLogs: true,
      },
    }
  }
  try {
    const raw = localStorage.getItem(PREFS_STORAGE_KEY)
    if (!raw) {
      return {
        theme: 'dark',
        sidebarDefaultOpen: true,
        refreshInterval: 5,
        notificationsEnabled: true,
        soundAlerts: false,
        dashboardSections: {
          welcomeBanner: true,
          quickLaunch: true,
          systemResources: true,
          activityTimeline: true,
          recentLogs: true,
        },
      }
    }
    return JSON.parse(raw) as UserPrefs
  } catch {
    return {
      theme: 'dark',
      sidebarDefaultOpen: true,
      refreshInterval: 5,
      notificationsEnabled: true,
      soundAlerts: false,
      dashboardSections: {
        welcomeBanner: true,
        quickLaunch: true,
        systemResources: true,
        activityTimeline: true,
        recentLogs: true,
      },
    }
  }
}

function savePrefs(prefs: UserPrefs) {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(PREFS_STORAGE_KEY, JSON.stringify(prefs))
  } catch {
    // ignore
  }
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
}

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
}

export function SettingsView() {
  const { theme, setTheme } = useTheme()
  const { setSidebarOpen } = useKimariStore()
  const [prefs, setPrefs] = useState<UserPrefs>(() => loadPrefs())
  const [hasChanges, setHasChanges] = useState(false)
  const [originalPrefs, setOriginalPrefs] = useState<UserPrefs>(() => loadPrefs())

  const updatePref = useCallback(<K extends keyof UserPrefs>(key: K, value: UserPrefs[K]) => {
    setPrefs((prev) => {
      const next = { ...prev, [key]: value }
      setHasChanges(JSON.stringify(next) !== JSON.stringify(originalPrefs))
      return next
    })
  }, [originalPrefs])

  const updateDashboardSection = useCallback((key: keyof DashboardSectionPrefs, value: boolean) => {
    setPrefs((prev) => {
      const next = {
        ...prev,
        dashboardSections: { ...prev.dashboardSections, [key]: value },
      }
      setHasChanges(JSON.stringify(next) !== JSON.stringify(originalPrefs))
      return next
    })
  }, [originalPrefs])

  const handleSave = () => {
    savePrefs(prefs)
    setOriginalPrefs(prefs)
    setHasChanges(false)

    // Apply theme
    setTheme(prefs.theme)

    // Apply sidebar state
    setSidebarOpen(prefs.sidebarDefaultOpen)

    // Sync to preferences API
    fetch('/api/preferences', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(prefs),
    }).catch(() => {
      // Non-critical, client-side persistence is primary
    })

    toast.success('Preferences saved', { description: 'Your settings have been updated' })
  }

  const handleReset = () => {
    const defaults: UserPrefs = {
      theme: 'dark',
      sidebarDefaultOpen: true,
      refreshInterval: 5,
      notificationsEnabled: true,
      soundAlerts: false,
      dashboardSections: {
        welcomeBanner: true,
        quickLaunch: true,
        systemResources: true,
        activityTimeline: true,
        recentLogs: true,
      },
    }
    setPrefs(defaults)
    setHasChanges(true)
    toast.info('Settings reset to defaults', { description: 'Click Save to apply' })
  }

  const themeOptions = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'system', label: 'System', icon: Monitor },
  ]

  const refreshOptions = [
    { value: '0', label: 'Off' },
    { value: '5', label: '5 seconds' },
    { value: '10', label: '10 seconds' },
    { value: '30', label: '30 seconds' },
  ]

  const dashboardSections: { key: keyof DashboardSectionPrefs; label: string }[] = [
    { key: 'welcomeBanner', label: 'Welcome Banner' },
    { key: 'quickLaunch', label: 'Quick Launch' },
    { key: 'systemResources', label: 'System Resources' },
    { key: 'activityTimeline', label: 'Activity Timeline' },
    { key: 'recentLogs', label: 'Recent Logs' },
  ]

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Settings className="h-5 w-5 text-primary" />
            Settings & Preferences
          </h1>
          <p className="text-sm text-foreground/60 mt-1">
            Configure your Kimari Gateway dashboard experience
          </p>
        </div>
        <div className="flex items-center gap-2">
          {hasChanges && (
            <Badge variant="outline" className="border-amber-500/40 text-amber-600 dark:text-amber-400 text-xs">
              Unsaved changes
            </Badge>
          )}
          <Button variant="outline" className="btn-press" onClick={handleReset}>
            Reset
          </Button>
          <Button
            className="btn-press gap-2 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-md shadow-primary/15"
            onClick={handleSave}
            disabled={!hasChanges}
          >
            <Save className="h-4 w-4" />
            Save Changes
          </Button>
        </div>
      </motion.div>

      <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
        {/* Theme Settings */}
        <motion.div variants={item}>
          <Card className="glass-card depth-shadow bg-card/80">
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Palette className="h-4 w-4 text-primary" />
                Appearance
              </CardTitle>
              <CardDescription>Customize the look and feel of the dashboard</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="space-y-3">
                <Label className="text-sm font-medium">Theme</Label>
                <div className="grid grid-cols-3 gap-3">
                  {themeOptions.map((opt) => {
                    const Icon = opt.icon
                    const isActive = prefs.theme === opt.value
                    return (
                      <button
                        key={opt.value}
                        onClick={() => updatePref('theme', opt.value)}
                        className={cn(
                          'flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all duration-200 hover:border-primary/40',
                          isActive
                            ? 'border-primary bg-primary/5 shadow-md shadow-primary/10'
                            : 'border-border/50 bg-muted/20 hover:bg-muted/40'
                        )}
                      >
                        <Icon className={cn('h-5 w-5', isActive ? 'text-primary' : 'text-foreground/60')} />
                        <span className={cn('text-xs font-medium', isActive ? 'text-primary' : 'text-foreground/70')}>
                          {opt.label}
                        </span>
                      </button>
                    )
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Sidebar Settings */}
        <motion.div variants={item}>
          <Card className="glass-card depth-shadow bg-card/80">
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Sidebar className="h-4 w-4 text-primary" />
                Sidebar
              </CardTitle>
              <CardDescription>Control sidebar behavior and layout</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-sm font-medium">Default Expanded</Label>
                  <p className="text-xs text-foreground/50">Start with sidebar expanded on page load</p>
                </div>
                <Switch
                  checked={prefs.sidebarDefaultOpen}
                  onCheckedChange={(v) => updatePref('sidebarDefaultOpen', v)}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Data Refresh Settings */}
        <motion.div variants={item}>
          <Card className="glass-card depth-shadow bg-card/80">
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <RefreshCw className="h-4 w-4 text-primary" />
                Data Refresh
              </CardTitle>
              <CardDescription>Configure how often dashboard data is refreshed</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-sm font-medium">Auto-refresh Interval</Label>
                  <p className="text-xs text-foreground/50">Polling frequency for dashboard data</p>
                </div>
                <Select
                  value={String(prefs.refreshInterval)}
                  onValueChange={(v) => updatePref('refreshInterval', Number(v))}
                >
                  <SelectTrigger className="w-[140px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {refreshOptions.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Notification Settings */}
        <motion.div variants={item}>
          <Card className="glass-card depth-shadow bg-card/80">
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Bell className="h-4 w-4 text-primary" />
                Notifications
              </CardTitle>
              <CardDescription>Manage notification preferences and alerts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-sm font-medium">Enable Notifications</Label>
                  <p className="text-xs text-foreground/50">Show toast notifications for events</p>
                </div>
                <Switch
                  checked={prefs.notificationsEnabled}
                  onCheckedChange={(v) => updatePref('notificationsEnabled', v)}
                />
              </div>
              <Separator className="bg-border/50" />
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-sm font-medium">Sound Alerts</Label>
                  <p className="text-xs text-foreground/50">Play sound on important events</p>
                </div>
                <Switch
                  checked={prefs.soundAlerts}
                  onCheckedChange={(v) => updatePref('soundAlerts', v)}
                  disabled={!prefs.notificationsEnabled}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Dashboard Layout Settings */}
        <motion.div variants={item}>
          <Card className="glass-card depth-shadow bg-card/80">
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <LayoutDashboard className="h-4 w-4 text-primary" />
                Dashboard Layout
              </CardTitle>
              <CardDescription>Toggle visibility of dashboard sections</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardSections.map((section, idx) => (
                <div key={section.key}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {prefs.dashboardSections[section.key] ? (
                        <Eye className="h-4 w-4 text-primary" />
                      ) : (
                        <EyeOff className="h-4 w-4 text-foreground/40" />
                      )}
                      <Label className="text-sm font-medium">{section.label}</Label>
                    </div>
                    <Switch
                      checked={prefs.dashboardSections[section.key]}
                      onCheckedChange={(v) => updateDashboardSection(section.key, v)}
                    />
                  </div>
                  {idx < dashboardSections.length - 1 && <Separator className="mt-4 bg-border/50" />}
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  )
}
