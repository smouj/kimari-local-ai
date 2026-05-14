import { NextResponse } from 'next/server'

// In-memory preferences store (persisted via localStorage on client side)
// This API serves as a sync point for preferences
const defaultPreferences = {
  theme: 'dark',
  sidebarOpen: true,
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

export async function GET() {
  // Return default preferences - actual persistence is via localStorage
  return NextResponse.json({
    preferences: defaultPreferences,
  })
}

export async function PUT(request: Request) {
  try {
    const body = await request.json()
    // In a production app, this would save to a user profile in the database
    // For now, we just acknowledge the update (client persists to localStorage)
    return NextResponse.json({
      success: true,
      preferences: { ...defaultPreferences, ...body },
    })
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 })
  }
}
