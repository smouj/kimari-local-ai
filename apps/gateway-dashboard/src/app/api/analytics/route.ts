import { NextRequest, NextResponse } from 'next/server'

function generateGpuMetrics(timeRange: string) {
  const now = new Date()
  let points: number
  let intervalMs: number

  switch (timeRange) {
    case '7d':
      points = 7
      intervalMs = 24 * 60 * 60 * 1000
      break
    case '30d':
      points = 30
      intervalMs = 24 * 60 * 60 * 1000
      break
    default: // 24h
      points = 24
      intervalMs = 60 * 60 * 1000
  }

  const dataPoints = Array.from({ length: points }, (_, i) => {
    const timestamp = new Date(now.getTime() - (points - 1 - i) * intervalMs)
    // Simulate realistic patterns: higher load during business hours, lower at night
    const hourOfDay = timestamp.getHours()
    const isBusinessHour = hourOfDay >= 9 && hourOfDay <= 18
    const loadMultiplier = isBusinessHour ? 1.3 : 0.7
    const noise = () => 0.85 + Math.random() * 0.3

    const vramBase = 4200
    const vramUsed = Math.round(vramBase * loadMultiplier * noise())
    const gpuTemp = Math.round((65 + (isBusinessHour ? 12 : -5) + (Math.random() * 8 - 4)) * 10) / 10
    const powerDraw = Math.round((160 + (isBusinessHour ? 30 : -20) + (Math.random() * 20 - 10)) * 10) / 10

    return {
      timestamp: timestamp.toISOString(),
      vramUsed: Math.min(vramUsed, 7800),
      vramTotal: 8192,
      gpuTemp: Math.max(Math.min(gpuTemp, 89), 42),
      powerDraw: Math.max(Math.min(powerDraw, 250), 80),
    }
  })

  return { timeRange, dataPoints }
}

function generateRequestHistory(timeRange: string) {
  const now = new Date()
  let hourlyData: { hour: string; requests: number; tokens: number; errors: number }[] = []

  if (timeRange === '24h') {
    hourlyData = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000)
      const hourStr = `${String(hour.getHours()).padStart(2, '0')}:00`
      const isBusinessHour = hour.getHours() >= 9 && hour.getHours() <= 18
      const baseRequests = isBusinessHour ? 65 : 15
      const requests = Math.round(baseRequests + Math.random() * (isBusinessHour ? 30 : 10))
      const avgTokens = 300 + Math.random() * 150
      const errors = Math.random() < 0.15 ? Math.round(Math.random() * 3) : 0

      return {
        hour: hourStr,
        requests,
        tokens: Math.round(requests * avgTokens),
        errors,
      }
    })
  } else if (timeRange === '7d') {
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    hourlyData = Array.from({ length: 7 }, (_, i) => {
      const day = new Date(now.getTime() - (6 - i) * 24 * 60 * 60 * 1000)
      const dayName = dayNames[day.getDay()]
      const isWeekday = day.getDay() >= 1 && day.getDay() <= 5
      const baseRequests = isWeekday ? 800 : 350
      const requests = Math.round(baseRequests + Math.random() * (isWeekday ? 200 : 100))
      const avgTokens = 320 + Math.random() * 80
      const errors = Math.round(Math.random() * 5)

      return {
        hour: dayName,
        requests,
        tokens: Math.round(requests * avgTokens),
        errors,
      }
    })
  } else {
    // 30d
    hourlyData = Array.from({ length: 30 }, (_, i) => {
      const day = new Date(now.getTime() - (29 - i) * 24 * 60 * 60 * 1000)
      const dateStr = `${String(day.getMonth() + 1).padStart(2, '0')}/${String(day.getDate()).padStart(2, '0')}`
      const isWeekday = day.getDay() >= 1 && day.getDay() <= 5
      const baseRequests = isWeekday ? 750 : 300
      const requests = Math.round(baseRequests + Math.random() * (isWeekday ? 250 : 120))
      const avgTokens = 310 + Math.random() * 100
      const errors = Math.round(Math.random() * 6)

      return {
        hour: dateStr,
        requests,
        tokens: Math.round(requests * avgTokens),
        errors,
      }
    })
  }

  const total = hourlyData.reduce((sum, d) => sum + d.requests, 0)
  const totalTokens = hourlyData.reduce((sum, d) => sum + d.tokens, 0)

  return {
    total,
    avgTokensPerRequest: Math.round(totalTokens / total),
    hourlyData,
  }
}

function generateLatency(timeRange: string) {
  const now = new Date()
  let points: number
  let intervalMs: number

  switch (timeRange) {
    case '7d':
      points = 7
      intervalMs = 24 * 60 * 60 * 1000
      break
    case '30d':
      points = 30
      intervalMs = 24 * 60 * 60 * 1000
      break
    default:
      points = 24
      intervalMs = 60 * 60 * 1000
  }

  const trendData = Array.from({ length: points }, (_, i) => {
    const timestamp = new Date(now.getTime() - (points - 1 - i) * intervalMs)
    const hourOfDay = timestamp.getHours()
    const isBusinessHour = hourOfDay >= 9 && hourOfDay <= 18
    // Slightly higher latency during peak hours due to load
    const loadFactor = isBusinessHour ? 1.15 : 0.9

    const ttft = Math.round((140 * loadFactor + (Math.random() * 40 - 20)) * 10) / 10
    const genTime = Math.round((2.3 * loadFactor + (Math.random() * 0.8 - 0.4)) * 100) / 100
    const tokensPerSec = Math.round((28 * (2 - loadFactor) + (Math.random() * 6 - 3)) * 10) / 10

    return {
      timestamp: timestamp.toISOString(),
      ttft: Math.max(ttft, 80),
      genTime: Math.max(genTime, 1.0),
      tokensPerSec: Math.max(tokensPerSec, 18),
    }
  })

  const avgTtft = Math.round(trendData.reduce((sum, d) => sum + d.ttft, 0) / trendData.length * 10) / 10
  const avgGenTime = Math.round(trendData.reduce((sum, d) => sum + d.genTime, 0) / trendData.length * 100) / 100

  return { avgTtft, avgGenTime, trendData }
}

function generateErrorRate(timeRange: string) {
  const now = new Date()
  let days: number

  switch (timeRange) {
    case '7d':
      days = 7
      break
    case '30d':
      days = 30
      break
    default:
      days = 7 // For 24h, still show daily breakdown
  }

  const dailyData = Array.from({ length: days }, (_, i) => {
    const date = new Date(now.getTime() - (days - 1 - i) * 24 * 60 * 60 * 1000)
    const dateStr = date.toISOString().split('T')[0]
    const isWeekday = date.getDay() >= 1 && date.getDay() <= 5

    const success = Math.round((isWeekday ? 180 : 80) + Math.random() * (isWeekday ? 40 : 20))
    const errors = Math.random() < 0.3 ? Math.round(1 + Math.random() * 4) : Math.round(Math.random() * 2)

    return { date: dateStr, success, errors }
  })

  const total = dailyData.reduce((sum, d) => sum + d.success + d.errors, 0)
  const errors = dailyData.reduce((sum, d) => sum + d.errors, 0)

  return {
    total,
    errors,
    errorRatePercent: Math.round((errors / total) * 10000) / 100,
    dailyData,
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const timeRange = searchParams.get('range') || '24h'

  const validRanges = ['24h', '7d', '30d']
  const range = validRanges.includes(timeRange) ? timeRange : '24h'

  const data = {
    gpuMetrics: generateGpuMetrics(range),
    requestHistory: generateRequestHistory(range),
    latency: generateLatency(range),
    errorRate: generateErrorRate(range),
  }

  return NextResponse.json(data)
}
