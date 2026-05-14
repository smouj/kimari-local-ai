'use client'

import { useState } from 'react'
import { useProfiles, useStartServer, useServerStatus } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { toast } from 'sonner'
import { Cpu, Play, Globe, Monitor, MemoryStick, Settings2, Zap, Search, ChevronDown, ChevronUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'

const statusColors: Record<string, string> = {
  available: 'border-emerald-500/30 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5',
  requires_model: 'border-amber-500/30 text-amber-600 dark:text-amber-400 bg-amber-500/5',
  network_exposed: 'border-red-500/30 text-red-600 dark:text-red-400 bg-red-500/5',
}

const statusLineColors: Record<string, string> = {
  available: 'bg-emerald-500',
  requires_model: 'bg-amber-500',
  network_exposed: 'bg-red-500',
}

const modeColors: Record<string, string> = {
  safe: 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/30',
  balanced: 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/30',
  fast: 'bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/30',
  ide: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30',
  agent: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
}

export function ProfilesView() {
  const { data: profiles, isLoading } = useProfiles()
  const { data: serverStatus } = useServerStatus()
  const startServer = useStartServer()
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedProfile, setExpandedProfile] = useState<string | null>(null)

  const isRunning = serverStatus?.status === 'running'
  const runningProfile = serverStatus?.profile

  const handleStart = async (profileName: string) => {
    try {
      await startServer.mutateAsync(profileName)
      toast.success('Server starting...', { description: `Profile: ${profileName}` })
    } catch (err) {
      toast.error('Failed to start server', { description: String(err) })
    }
  }

  const filteredProfiles = (profiles ?? []).filter((p) =>
    p.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.gpu.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.mode.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[200px] w-full rounded-xl shimmer" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">GPU Profiles</h2>
          <p className="text-sm text-foreground/70 font-medium">
            Select a profile to start the server with specific GPU and model configurations.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="font-mono font-medium">
            {profiles?.length ?? 0} profiles
          </Badge>
        </div>
      </div>

      {/* Search / Filter Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground/50" />
        <Input
          placeholder="Search profiles by name, GPU, or mode..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9 max-w-md bg-muted/20 border-border/50 hover:border-primary/30 transition-colors"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredProfiles.map((profile, i) => {
          const isProfileRunning = profile.isRunning || runningProfile === profile.name
          const isExpanded = expandedProfile === profile.id

          return (
            <motion.div
              key={profile.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: i * 0.03 }}
              layout
            >
              <Card
                className={cn(
                  'relative overflow-hidden transition-all duration-300 card-hover-lift depth-shadow card-glow',
                  isProfileRunning && 'ring-2 ring-primary/50 glow-blue gradient-border',
                  i % 2 === 0 ? 'profile-row-even' : 'profile-row-odd'
                )}
              >
                {/* Status line at top */}
                <div className={cn(
                  'absolute top-0 left-0 right-0 h-[3px]',
                  isProfileRunning ? 'bg-gradient-to-r from-primary via-emerald-500 to-primary' : statusLineColors[profile.status] ?? 'bg-muted'
                )} />

                <CardHeader className="pb-3 pt-5 px-5">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1.5">
                      <CardTitle className="text-base flex items-center gap-2">
                        <Cpu className="h-4 w-4 text-primary" />
                        {profile.displayName}
                      </CardTitle>
                      <p className="text-xs text-foreground/60 font-mono">{profile.name}</p>
                    </div>
                    <div className="flex flex-wrap items-center justify-end gap-1">
                      {isProfileRunning && (
                        <Badge className="text-[10px] bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 font-medium">
                          Active
                        </Badge>
                      )}
                      {profile.isDefault && (
                        <Badge className="text-[10px] bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/30 font-medium">Default</Badge>
                      )}
                      <Badge
                        variant="outline"
                        className={cn('text-[10px] capitalize font-medium', statusColors[profile.status])}
                      >
                        {profile.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-0 px-5 pb-5 pt-0">
                  {/* Info Grid */}
                  <div className="grid grid-cols-2 gap-3 text-xs pb-3">
                    <div className="flex items-center gap-1.5 text-foreground/65 font-medium">
                      <Monitor className="h-3 w-3" />
                      <span>{profile.gpu}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-foreground/65 font-medium">
                      <MemoryStick className="h-3 w-3" />
                      <span>{profile.vram}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-foreground/65 font-medium">
                      <Settings2 className="h-3 w-3" />
                      <span>{profile.quantization}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-foreground/65 font-medium">
                      <Zap className="h-3 w-3" />
                      <span>{profile.contextSize} ctx</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-foreground/65 font-medium">
                      <Globe className="h-3 w-3" />
                      <span>{profile.host}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Badge
                        variant="secondary"
                        className={cn('text-[10px] capitalize font-medium', modeColors[profile.mode])}
                      >
                        {profile.mode}
                      </Badge>
                    </div>
                  </div>

                  {/* Divider */}
                  <div className="border-t border-border/40" />

                  {/* Expandable details */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="py-3 space-y-2 text-xs">
                          <div className="flex justify-between">
                            <span className="text-foreground/65 font-medium">Cache K</span>
                            <span className="font-mono font-medium">{profile.cacheK}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-foreground/65 font-medium">Cache V</span>
                            <span className="font-mono font-medium">{profile.cacheV}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-foreground/65 font-medium">Use Case</span>
                            <span className="font-medium">{profile.useCase}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-foreground/65 font-medium">Model File</span>
                            <span className="font-mono truncate max-w-[150px] font-medium">{profile.modelFile ?? 'None'}</span>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Action Row */}
                  <div className="pt-3 border-t border-border/40">
                    <div className="flex items-center justify-between">
                      <button
                        onClick={() => setExpandedProfile(isExpanded ? null : profile.id)}
                        className="flex items-center gap-1 text-xs text-foreground/65 hover:text-foreground transition-colors font-medium"
                      >
                        {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                        {isExpanded ? 'Less' : 'More'}
                      </button>
                      <Button
                        size="sm"
                        variant={isProfileRunning ? 'secondary' : 'default'}
                        className={cn(
                          'h-8 min-w-[80px] text-xs gap-1.5 btn-press font-semibold',
                          !isProfileRunning && 'bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white shadow-md shadow-emerald-500/15'
                        )}
                        onClick={() => handleStart(profile.name)}
                        disabled={isProfileRunning || startServer.isPending}
                      >
                        <Play className="h-3 w-3" />
                        {isProfileRunning ? 'Running' : 'Start'}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {filteredProfiles.length === 0 && searchQuery && (
        <div className="flex flex-col items-center justify-center py-12 text-foreground/60">
          <Search className="h-8 w-8 mb-2 opacity-50" />
          <p className="text-sm font-medium">No profiles matching &ldquo;{searchQuery}&rdquo;</p>
        </div>
      )}
    </div>
  )
}
