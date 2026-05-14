'use client'

import { useProfiles, useStartServer } from '@/hooks/use-api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useKimariStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { Sparkles, Play, Cpu, ArrowRight } from 'lucide-react'
import { toast } from 'sonner'

export function QuickLauncher() {
  const { data: profiles } = useProfiles()
  const startServer = useStartServer()
  const setActiveView = useKimariStore((s) => s.setActiveView)

  // Take top 3 recommended profiles (or fewer if not enough)
  const recommendedProfiles = (profiles ?? [])
    .filter((p) => p.status === 'available')
    .slice(0, 3)

  if (recommendedProfiles.length === 0) {
    return null
  }

  const handleLaunch = async (profileName: string) => {
    try {
      await startServer.mutateAsync(profileName)
      toast.success('Server starting...', { description: `Profile: ${profileName}` })
    } catch (err) {
      toast.error('Failed to start server', { description: String(err) })
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
    >
      <Card className="glass-card depth-shadow card-glow">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 mb-5">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-primary/25 to-primary/5 flex items-center justify-center shadow-sm shadow-primary/10">
              <Sparkles className="h-4 w-4 text-primary" />
            </div>
            <h3 className="text-base font-semibold">Quick Launch</h3>
            <Badge variant="outline" className="text-[11px] border-primary/40 text-primary/90 ml-auto px-3 py-0.5 shrink-0 font-semibold">
              Recommended for your GPU
            </Badge>
          </div>

          <div className="space-y-2.5">
            {recommendedProfiles.map((profile, index) => (
              <motion.div
                key={profile.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.15 + index * 0.05 }}
                whileHover={{ scale: 1.01 }}
                className="group relative flex items-center gap-3 p-3 rounded-xl border border-border/50 hover:border-primary/40 hover:bg-primary/[0.06] transition-all duration-200 gradient-border overflow-hidden"
              >
                <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center shrink-0 shadow-sm shadow-primary/10">
                  <Cpu className="h-4.5 w-4.5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{profile.displayName}</div>
                  <div className="flex items-center gap-2 text-[11px] text-foreground/65 mt-0.5">
                    <span>{profile.gpu}</span>
                    <span className="text-border">·</span>
                    <span>{profile.vram}</span>
                  </div>
                </div>
                <Button
                  size="sm"
                  className={cn(
                    'gap-1.5 h-8 px-3.5 text-xs btn-press shrink-0 font-semibold',
                    'bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white shadow-md shadow-emerald-500/15',
                    'opacity-80 group-hover:opacity-100 transition-opacity'
                  )}
                  onClick={() => handleLaunch(profile.name)}
                  disabled={startServer.isPending}
                >
                  <Play className="h-3 w-3" />
                  Launch
                </Button>
              </motion.div>
            ))}
          </div>

          <div className="pt-4 mt-2 border-t border-border/40">
            <button
              onClick={() => setActiveView('profiles')}
              className="flex items-center gap-1.5 text-xs text-foreground/65 hover:text-primary font-medium transition-colors"
            >
              View All Profiles
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
