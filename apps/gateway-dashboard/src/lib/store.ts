'use client'

import { create } from 'zustand'

export type ViewType = 'dashboard' | 'profiles' | 'models' | 'server' | 'stats' | 'analytics' | 'doctor' | 'benchmarks' | 'kimarifit' | 'config' | 'logs' | 'integrations' | 'chat' | 'modelCompare' | 'system' | 'settings'

interface ServerStatus {
  status: string
  pid?: number | null
  port?: number
  host?: string
  profile?: string | null
  model?: string | null
  startedAt?: string | null
  uptime?: number
  lastError?: string | null
}

interface KimariStore {
  activeView: ViewType
  lastView: ViewType | null
  sidebarOpen: boolean
  serverStatus: ServerStatus
  notificationsOpen: boolean
  setupComplete: boolean
  exportDialogOpen: boolean
  setActiveView: (view: ViewType) => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setServerStatus: (status: ServerStatus) => void
  toggleNotifications: () => void
  setNotificationsOpen: (open: boolean) => void
  setSetupComplete: (v: boolean) => void
  setExportDialogOpen: (open: boolean) => void
}

export const useKimariStore = create<KimariStore>((set) => ({
  activeView: 'dashboard',
  lastView: null,
  sidebarOpen: true,
  serverStatus: { status: 'stopped', uptime: 0 },
  notificationsOpen: false,
  setupComplete: false,
  exportDialogOpen: false,
  setActiveView: (view) => set((state) => ({ activeView: view, lastView: state.activeView })),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setServerStatus: (status) => set({ serverStatus: status }),
  toggleNotifications: () => set((state) => ({ notificationsOpen: !state.notificationsOpen })),
  setNotificationsOpen: (open) => set({ notificationsOpen: open }),
  setSetupComplete: (v) => set({ setupComplete: v }),
  setExportDialogOpen: (open) => set({ exportDialogOpen: open }),
}))
