'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Types
export interface HealthData {
  status: string
  version: string
  uptime: number
  timestamp: string
}

export interface ServerStatusData {
  status: string
  pid?: number | null
  port?: number
  host?: string
  profile?: string | null
  model?: string | null
  startedAt?: string | null
  uptime?: number
  lastError?: string | null
  updatedAt?: string
}

export interface GpuProfile {
  id: string
  name: string
  displayName: string
  gpu: string
  vram: string
  quantization: string
  contextSize: number
  host: string
  cacheK: string
  cacheV: string
  mode: string
  useCase: string
  modelFile: string | null
  isDefault: boolean
  status: string
  order: number
  isRunning: boolean
  createdAt: string
  updatedAt: string
}

export interface ModelEntry {
  id: string
  name: string
  displayName: string
  filename: string
  size: string | null
  fileSizeMb: number | null
  quantization: string
  license: string
  source: string | null
  sha256: string | null
  hashPinned: boolean
  downloaded: boolean
  downloadedAt: string | null
  category: string
  vramRequired: string | null
  compatibleProfiles: string | null
  compatibleProfilesList: string[]
  createdAt: string
  updatedAt: string
}

export interface GatewayConfig {
  id: string
  key: string
  value: string
  valueType: string
  description: string | null
  isSecret: boolean
  updatedAt: string
}

export interface GatewayLog {
  id: string
  level: string
  source: string
  message: string
  metadata: string | null
  createdAt: string
}

export interface Integration {
  id: string
  name: string
  displayName: string
  description: string | null
  configJson: string | null
  baseUrl: string | null
  status: string
  icon: string | null
  docsUrl: string | null
  createdAt: string
  updatedAt: string
}

export interface BenchmarkResult {
  id: string
  profile: string
  model: string
  quantization: string
  contextSize: number
  promptTokPerSec: number | null
  genTokPerSec: number | null
  ttft: number | null
  vramUsedMb: number | null
  totalTokens: number | null
  duration: number | null
  mode: string
  status: string
  notes: string | null
  gpuInfo: string | null
  resultsJson: string | null
  createdAt: string
}

export interface DashboardData {
  server: ServerStatusData
  profiles: {
    total: number
    available: number
    requiresModel: number
    networkExposed: number
    running: string | null
  }
  models: {
    total: number
    downloaded: number
    notDownloaded: number
    categories: Record<string, number>
  }
  recentBenchmarks: BenchmarkResult[]
  recentLogs: GatewayLog[]
  timestamp: string
}

// Query hooks
export function useHealth() {
  return useQuery<HealthData>({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await fetch('/api/health')
      if (!res.ok) throw new Error('Failed to fetch health')
      return res.json()
    },
    refetchInterval: 30000,
  })
}

export function useServerStatus() {
  return useQuery<ServerStatusData>({
    queryKey: ['status'],
    queryFn: async () => {
      const res = await fetch('/api/status')
      if (!res.ok) throw new Error('Failed to fetch status')
      return res.json()
    },
    refetchInterval: 5000,
  })
}

export function useProfiles() {
  return useQuery<GpuProfile[]>({
    queryKey: ['profiles'],
    queryFn: async () => {
      const res = await fetch('/api/profiles')
      if (!res.ok) throw new Error('Failed to fetch profiles')
      return res.json()
    },
  })
}

export function useModels() {
  return useQuery<ModelEntry[]>({
    queryKey: ['models'],
    queryFn: async () => {
      const res = await fetch('/api/models')
      if (!res.ok) throw new Error('Failed to fetch models')
      return res.json()
    },
  })
}

export function useConfig() {
  return useQuery<GatewayConfig[]>({
    queryKey: ['config'],
    queryFn: async () => {
      const res = await fetch('/api/config')
      if (!res.ok) throw new Error('Failed to fetch config')
      return res.json()
    },
  })
}

export function useLogs(level?: string, source?: string, limit?: number) {
  const params = new URLSearchParams()
  if (level) params.set('level', level)
  if (source) params.set('source', source)
  if (limit) params.set('limit', String(limit))

  return useQuery<GatewayLog[]>({
    queryKey: ['logs', level, source, limit],
    queryFn: async () => {
      const res = await fetch(`/api/logs?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to fetch logs')
      return res.json()
    },
    refetchInterval: 10000,
  })
}

export function useIntegrations() {
  return useQuery<Integration[]>({
    queryKey: ['integrations'],
    queryFn: async () => {
      const res = await fetch('/api/integrations')
      if (!res.ok) throw new Error('Failed to fetch integrations')
      return res.json()
    },
  })
}

export function useBenchmarks() {
  return useQuery<BenchmarkResult[]>({
    queryKey: ['benchmarks'],
    queryFn: async () => {
      const res = await fetch('/api/benchmarks')
      if (!res.ok) throw new Error('Failed to fetch benchmarks')
      return res.json()
    },
  })
}

export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const res = await fetch('/api/dashboard')
      if (!res.ok) throw new Error('Failed to fetch dashboard')
      return res.json()
    },
    refetchInterval: 10000,
  })
}

// Mutation hooks
export function useStartServer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (profile: string) => {
      const res = await fetch('/api/server/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to start server')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['status'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['profiles'] })
      queryClient.invalidateQueries({ queryKey: ['logs'] })
    },
  })
}

export function useStopServer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/server/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to stop server')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['status'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['profiles'] })
      queryClient.invalidateQueries({ queryKey: ['logs'] })
    },
  })
}

export function useRunBenchmark() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ profile, mode }: { profile: string; mode: string }) => {
      const res = await fetch('/api/benchmark/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile, mode }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to run benchmark')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['benchmarks'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['logs'] })
    },
  })
}

export function usePullModel() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (model: string) => {
      const res = await fetch('/api/models/pull', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to pull model')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['logs'] })
    },
  })
}

export function useUpdateConfig() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ key, value }: { key: string; value: string }) => {
      const res = await fetch(`/api/config/${encodeURIComponent(key)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to update config')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config'] })
      queryClient.invalidateQueries({ queryKey: ['logs'] })
    },
  })
}

// Doctor types
export interface DiagnosticCheck {
  name: string
  category: string
  status: 'PASS' | 'WARN' | 'FAIL'
  message: string
  details?: string
}

export interface DoctorData {
  checks: DiagnosticCheck[]
  summary: {
    total: number
    pass: number
    warn: number
    fail: number
  }
  healthScore: number
  checkedAt: string
}

export function useDoctor() {
  return useQuery<DoctorData>({
    queryKey: ['doctor'],
    queryFn: async () => {
      const res = await fetch('/api/doctor')
      if (!res.ok) throw new Error('Failed to run diagnostics')
      return res.json()
    },
    staleTime: 0,
  })
}

export function useRunDoctor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/doctor')
      if (!res.ok) throw new Error('Failed to run diagnostics')
      return res.json() as Promise<DoctorData>
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['doctor'], data)
    },
  })
}

// KimariFit types
export interface KimariFitRequest {
  modelSize: string
  vram: number
  contextSize: number
  quantization: string
}

export interface KimariFitDetails {
  modelVram: number
  contextVram: number
  overheadVram: number
  totalVram: number
  headroom: number
  efficiency: number
  vramUsagePercent: number
}

export interface KimariFitData {
  score: number
  grade: string
  details: KimariFitDetails
  recommendations: string[]
  calculatedAt: string
}

export function useKimariFit() {
  return useMutation<KimariFitData, Error, KimariFitRequest>({
    mutationFn: async (params: KimariFitRequest) => {
      const res = await fetch('/api/kimarifit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to calculate KimariFit')
      return data
    },
  })
}

// Update types
export interface UpdateData {
  currentVersion: string
  latestVersion: string
  updateAvailable: boolean
  releaseNotes?: string
  checkedAt: string
}

export function useUpdateCheck() {
  return useQuery<UpdateData>({
    queryKey: ['update'],
    queryFn: async () => {
      const res = await fetch('/api/update')
      if (!res.ok) throw new Error('Failed to check for updates')
      return res.json()
    },
    staleTime: 60000,
    enabled: false,
  })
}

// Analytics types
export interface GpuMetricPoint {
  timestamp: string
  vramUsed: number
  vramTotal: number
  gpuTemp: number
  powerDraw: number
}

export interface HourlyDataPoint {
  hour: string
  requests: number
  tokens: number
  errors: number
}

export interface LatencyTrendPoint {
  timestamp: string
  ttft: number
  genTime: number
  tokensPerSec: number
}

export interface DailyErrorPoint {
  date: string
  success: number
  errors: number
}

export interface AnalyticsData {
  gpuMetrics: {
    timeRange: string
    dataPoints: GpuMetricPoint[]
  }
  requestHistory: {
    total: number
    avgTokensPerRequest: number
    hourlyData: HourlyDataPoint[]
  }
  latency: {
    avgTtft: number
    avgGenTime: number
    trendData: LatencyTrendPoint[]
  }
  errorRate: {
    total: number
    errors: number
    errorRatePercent: number
    dailyData: DailyErrorPoint[]
  }
}

export function useAnalytics(timeRange: string = '24h') {
  return useQuery<AnalyticsData>({
    queryKey: ['analytics', timeRange],
    queryFn: async () => {
      const res = await fetch(`/api/analytics?range=${timeRange}`)
      if (!res.ok) throw new Error('Failed to fetch analytics')
      return res.json()
    },
    refetchInterval: 30000,
  })
}

// Notification types
export interface NotificationItem {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  read: boolean
  createdAt: string
  source: string
}

export interface NotificationsData {
  notifications: NotificationItem[]
  unreadCount: number
}

export function useNotifications() {
  return useQuery<NotificationsData>({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await fetch('/api/notifications')
      if (!res.ok) throw new Error('Failed to fetch notifications')
      return res.json()
    },
    refetchInterval: 15000,
  })
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (notificationId: string) => {
      const res = await fetch('/api/notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'markRead', notificationId }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to mark as read')
      return data
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['notifications'], data)
    },
  })
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'markAllRead' }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to mark all as read')
      return data
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['notifications'], data)
    },
  })
}

// Setup types
export interface SetupStep {
  id: string
  title: string
  completed: boolean
}

export interface SetupData {
  isFirstTime: boolean
  steps: SetupStep[]
  currentStep: number
}

export function useSetupStatus() {
  return useQuery<SetupData>({
    queryKey: ['setup'],
    queryFn: async () => {
      const res = await fetch('/api/setup')
      if (!res.ok) throw new Error('Failed to check setup status')
      return res.json()
    },
  })
}

export function useCompleteSetup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to complete setup')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['setup'] })
    },
  })
}

// Preferences types
export interface DashboardSectionPrefs {
  welcomeBanner: boolean
  quickLaunch: boolean
  systemResources: boolean
  activityTimeline: boolean
  recentLogs: boolean
}

export interface PreferencesData {
  theme: string
  sidebarDefaultOpen: boolean
  refreshInterval: number
  notificationsEnabled: boolean
  soundAlerts: boolean
  dashboardSections: DashboardSectionPrefs
}

export function usePreferencesApi() {
  return useQuery<{ preferences: PreferencesData }>({
    queryKey: ['preferences-api'],
    queryFn: async () => {
      const res = await fetch('/api/preferences')
      if (!res.ok) throw new Error('Failed to fetch preferences')
      return res.json()
    },
    staleTime: 60000,
  })
}

export function useUpdatePreferences() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (prefs: Partial<PreferencesData>) => {
      const res = await fetch('/api/preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(prefs),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to update preferences')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['preferences-api'] })
    },
  })
}

// Export helper
export function triggerExport(type: 'logs' | 'benchmarks' | 'dashboard' | 'analytics', format: 'csv' | 'json') {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `kimari-${type}-${timestamp}.${format}`
  const link = document.createElement('a')
  link.href = `/api/export?type=${type}&format=${format}`
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Activity Timeline types
export type ActivityType =
  | 'server_start'
  | 'server_stop'
  | 'benchmark'
  | 'model_download'
  | 'config_change'
  | 'integration_connect'
  | 'health_check'

export type ActivityStatus = 'success' | 'warning' | 'error' | 'info'

export interface ActivityEvent {
  id: string
  type: ActivityType
  title: string
  description: string
  icon: string
  timestamp: string
  status: ActivityStatus
}

export interface ActivityData {
  events: ActivityEvent[]
  total: number
}

export function useActivity() {
  return useQuery<ActivityData>({
    queryKey: ['activity'],
    queryFn: async () => {
      const res = await fetch('/api/activity')
      if (!res.ok) throw new Error('Failed to fetch activity')
      return res.json()
    },
    refetchInterval: 10000,
  })
}

// Stats types
export interface TokenStats {
  prompt: number
  generation: number
}

export interface VramUsage {
  used: number
  total: number
  percent: number
}

export interface GpuStats {
  temperature: number
  powerDraw: number
  fanSpeed: number
  clockSpeed: number
}

export interface RequestStats {
  active: number
  total: number
  avgLatency: number
  queueDepth: number
}

export interface MemoryStats {
  modelSize: number
  contextSize: number
  overhead: number
  total: number
}

export interface ServerInfo {
  uptime: number
  lastRequest: string
  model: string
  profile: string
}

export interface ServerStats {
  tokensPerSec: TokenStats
  vramUsage: VramUsage
  gpuStats: GpuStats
  requestStats: RequestStats
  memoryStats: MemoryStats
  serverInfo: ServerInfo
}

export interface StatsData {
  serverRunning: boolean
  stats: ServerStats | null
}

export function useStats() {
  return useQuery<StatsData>({
    queryKey: ['stats'],
    queryFn: async () => {
      const res = await fetch('/api/stats')
      if (!res.ok) throw new Error('Failed to fetch stats')
      return res.json()
    },
    refetchInterval: 3000,
  })
}

// System Resources types (enhanced)
export interface CpuCoreInfo {
  core: number
  usage: number
  frequency: number
}

export interface CpuResources {
  usage: number
  cores: CpuCoreInfo[]
  coreCount: number
  temperature: number
  frequency: string
}

export interface MemoryResources {
  used: number
  cached: number
  free: number
  total: number
  percent: number
  swapUsed: number
  swapTotal: number
  swapPercent: number
}

export interface VramHistoryPoint {
  tick: number
  value: number
}

export interface GpuResources {
  vramUsed: number
  vramTotal: number
  vramPercent: number
  vramHistory: VramHistoryPoint[]
  temperature: number
  hotspot: number
  powerDraw: number
}

export interface DiskResources {
  used: number
  total: number
  percent: number
  readMbps: number
  writeMbps: number
}

export interface NetworkResources {
  inMbps: number
  outMbps: number
  connections: number
  latency: number
}

export interface TemperatureReadings {
  cpuPackage: number
  gpuHotspot: number
  gpuCore: number
}

export interface SystemResourcesData {
  cpu: CpuResources
  memory: MemoryResources
  gpu: GpuResources
  disk: DiskResources
  network: NetworkResources
  temperatures: TemperatureReadings
  uptime: number
}

export function useSystemResources() {
  return useQuery<SystemResourcesData>({
    queryKey: ['system-resources'],
    queryFn: async () => {
      const res = await fetch('/api/system-resources')
      if (!res.ok) throw new Error('Failed to fetch system resources')
      return res.json()
    },
    refetchInterval: 3000,
  })
}

// Quick Actions types
export interface QuickAction {
  id: string
  label: string
  description: string
  icon: string
  category: 'server' | 'diagnostics' | 'maintenance'
  shortcut?: string
  confirmRequired: boolean
  confirmMessage?: string
  estimatedDuration: number
}

export interface QuickActionCategory {
  id: string
  label: string
  description: string
}

export interface QuickActionsData {
  actions: QuickAction[]
  categories: QuickActionCategory[]
}

export interface QuickActionResult {
  success: boolean
  actionId: string
  message: string
  details?: string
  timestamp: string
}

export function useQuickActions() {
  return useQuery<QuickActionsData>({
    queryKey: ['quick-actions'],
    queryFn: async () => {
      const res = await fetch('/api/quick-actions')
      if (!res.ok) throw new Error('Failed to fetch quick actions')
      return res.json()
    },
    staleTime: 60000,
  })
}

export function useExecuteQuickAction() {
  const queryClient = useQueryClient()
  return useMutation<QuickActionResult, Error, string>({
    mutationFn: async (actionId: string) => {
      const res = await fetch('/api/quick-actions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actionId }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to execute action')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['status'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['logs'] })
    },
  })
}

// Model Comparison types
export interface QualityScores {
  instructionFollowing: number
  codingAbility: number
  reasoning: number
  creativity: number
}

export interface PerformanceEstimate {
  promptTokPerSec: number
  genTokPerSec: number
  vramRequiredGb: number
  contextLength: number
}

export interface ModelComparisonItem {
  name: string
  displayName: string
  size: string
  quantization: string
  category: string
  performance: PerformanceEstimate
  quality: QualityScores
  compatibleProfiles: string[]
  pros: string[]
  cons: string[]
}

export interface ModelComparisonData {
  models: ModelComparisonItem[]
  availableModels: string[]
  comparedAt: string
}

export function useModelCompare(models: string[]) {
  return useQuery<ModelComparisonData>({
    queryKey: ['model-compare', models.sort().join(',')],
    queryFn: async () => {
      const res = await fetch(`/api/model-compare?models=${models.join(',')}`)
      if (!res.ok) throw new Error('Failed to fetch model comparison')
      return res.json()
    },
    enabled: models.length >= 2,
  })
}
