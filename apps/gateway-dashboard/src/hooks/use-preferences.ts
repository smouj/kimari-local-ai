'use client'

import { useEffect, useCallback, useRef } from 'react'
import { useKimariStore, type ViewType } from '@/lib/store'
import { useTheme } from 'next-themes'

const PREFS_KEY = 'kimari-prefs'

interface UserPreferences {
  theme: string
  sidebarOpen: boolean
  activeView: ViewType
  setupComplete: boolean
}

function loadPreferences(): Partial<UserPreferences> {
  if (typeof window === 'undefined') return {}
  try {
    const raw = localStorage.getItem(PREFS_KEY)
    if (!raw) return {}
    return JSON.parse(raw) as Partial<UserPreferences>
  } catch {
    return {}
  }
}

function savePreferences(prefs: UserPreferences) {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs))
  } catch {
    // localStorage may be full or unavailable
  }
}

export function usePreferences() {
  const store = useKimariStore()
  const { theme } = useTheme()
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const initializedRef = useRef(false)

  // Load preferences on mount
  useEffect(() => {
    if (typeof window === 'undefined' || initializedRef.current) return
    initializedRef.current = true

    const prefs = loadPreferences()

    // Restore sidebar state
    if (typeof prefs.sidebarOpen === 'boolean') {
      store.setSidebarOpen(prefs.sidebarOpen)
    }

    // Restore active view (only if setup is complete)
    if (prefs.setupComplete && prefs.activeView) {
      store.setActiveView(prefs.activeView)
    }

    // Restore setup complete state
    if (typeof prefs.setupComplete === 'boolean') {
      store.setSetupComplete(prefs.setupComplete)
    }
  }, [])

  // Sync store state to localStorage (debounced)
  const syncPreferences = useCallback(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }
    debounceRef.current = setTimeout(() => {
      savePreferences({
        theme: theme ?? 'dark',
        sidebarOpen: store.sidebarOpen,
        activeView: store.activeView,
        setupComplete: store.setupComplete,
      })
    }, 300)
  }, [theme, store.sidebarOpen, store.activeView, store.setupComplete])

  // Listen for store changes and sync
  useEffect(() => {
    syncPreferences()
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [syncPreferences])

  // Also save setup complete to its own key for backward compat
  useEffect(() => {
    localStorage.setItem('kimari-setup-complete', String(store.setupComplete))
  }, [store.setupComplete])
}
