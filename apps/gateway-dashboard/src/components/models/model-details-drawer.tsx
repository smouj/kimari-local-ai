'use client'

import { useState } from 'react'
import { usePullModel, useStartServer, useProfiles } from '@/hooks/use-api'
import type { ModelEntry } from '@/hooks/use-api'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { toast } from 'sonner'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Download,
  Check,
  Copy,
  ExternalLink,
  Box,
  HardDrive,
  FileCode,
  Shield,
  Hash,
  Cpu,
  Calendar,
  Play,
  Globe,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const categoryColors: Record<string, string> = {
  test: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30',
  recommended: 'bg-primary/10 text-primary border-primary/30',
  community: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/30',
  official: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
}

const categoryLabels: Record<string, string> = {
  test: 'Test',
  recommended: 'Recommended',
  community: 'Community',
  official: 'Official',
}

interface ModelDetailsDrawerProps {
  model: ModelEntry | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ModelDetailsDrawer({ model, open, onOpenChange }: ModelDetailsDrawerProps) {
  const pullModel = usePullModel()
  const startServer = useStartServer()
  const { data: profiles } = useProfiles()
  const [copiedHash, setCopiedHash] = useState(false)
  const [copiedId, setCopiedId] = useState(false)

  if (!model) return null

  const compatibleProfiles = (profiles ?? []).filter(
    (p) => model.compatibleProfilesList?.includes(p.name) ?? false
  )

  const handlePull = async () => {
    try {
      await pullModel.mutateAsync(model.name)
      toast.success('Model downloaded', { description: model.displayName })
    } catch (err) {
      toast.error('Failed to download model', { description: String(err) })
    }
  }

  const handleCopyHash = async () => {
    if (!model.sha256) return
    await navigator.clipboard.writeText(model.sha256)
    setCopiedHash(true)
    setTimeout(() => setCopiedHash(false), 2000)
    toast.success('SHA256 hash copied to clipboard')
  }

  const handleCopyId = async () => {
    await navigator.clipboard.writeText(model.name)
    setCopiedId(true)
    setTimeout(() => setCopiedId(false), 2000)
    toast.success('Model ID copied to clipboard')
  }

  const handleLaunch = async (profileName: string) => {
    try {
      await startServer.mutateAsync(profileName)
      toast.success('Server started', { description: `Using profile ${profileName}` })
      onOpenChange(false)
    } catch (err) {
      toast.error('Failed to start server', { description: String(err) })
    }
  }

  const truncatedHash = model.sha256
    ? `${model.sha256.slice(0, 16)}...${model.sha256.slice(-8)}`
    : null

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-lg overflow-y-auto p-0"
      >
        <SheetHeader className="p-6 pb-4 border-b border-border/50">
          <AnimatePresence mode="wait">
            <motion.div
              key={model.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.25 }}
            >
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-primary/10 p-2 shrink-0">
                  <Box className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <SheetTitle className="text-lg font-bold leading-tight">
                    {model.displayName}
                  </SheetTitle>
                  <SheetDescription className="font-mono text-xs mt-1">
                    {model.filename}
                  </SheetDescription>
                </div>
              </div>

              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {model.downloaded ? (
                  <Badge className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1">
                    <Check className="h-3 w-3" /> Downloaded
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-muted-foreground">
                    Not Downloaded
                  </Badge>
                )}
                <Badge
                  variant="outline"
                  className={cn('text-[10px] capitalize', categoryColors[model.category])}
                >
                  {categoryLabels[model.category] ?? model.category}
                </Badge>
              </div>
            </motion.div>
          </AnimatePresence>
        </SheetHeader>

        <div className="p-6 space-y-6">
          {/* Details Grid */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.1 }}
          >
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Details
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <DetailItem
                icon={<FileCode className="h-3.5 w-3.5" />}
                label="Quantization"
                value={
                  <Badge variant="outline" className="font-mono text-[11px]">
                    {model.quantization}
                  </Badge>
                }
              />
              <DetailItem
                icon={<HardDrive className="h-3.5 w-3.5" />}
                label="File Size"
                value={
                  <span className="text-sm">
                    {model.size ?? '-'}
                    {model.fileSizeMb ? ` (${Math.round(model.fileSizeMb)} MB)` : ''}
                  </span>
                }
              />
              <DetailItem
                icon={<Shield className="h-3.5 w-3.5" />}
                label="License"
                value={<span className="text-sm">{model.license}</span>}
              />
              <DetailItem
                icon={<Globe className="h-3.5 w-3.5" />}
                label="Source"
                value={
                  model.source ? (
                    <a
                      href={model.source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline inline-flex items-center gap-1"
                    >
                      View <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : (
                    <span className="text-sm text-muted-foreground">N/A</span>
                  )
                }
              />
              <DetailItem
                icon={<Cpu className="h-3.5 w-3.5" />}
                label="VRAM Required"
                value={
                  <span className="text-sm">{model.vramRequired ?? 'N/A'}</span>
                }
              />
              <DetailItem
                icon={<Calendar className="h-3.5 w-3.5" />}
                label="Downloaded"
                value={
                  <span className="text-sm">
                    {model.downloadedAt
                      ? new Date(model.downloadedAt).toLocaleDateString()
                      : 'N/A'}
                  </span>
                }
              />
            </div>
          </motion.div>

          {/* SHA256 Hash */}
          {model.sha256 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.15 }}
            >
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                Hash
              </h3>
              <div className="flex items-center gap-2 bg-muted/50 rounded-lg p-3 border border-border/50">
                <Hash className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                <code className="text-[11px] font-mono flex-1 break-all">
                  {truncatedHash}
                </code>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 p-0 shrink-0"
                  onClick={handleCopyHash}
                >
                  {copiedHash ? (
                    <Check className="h-3.5 w-3.5 text-emerald-500" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                </Button>
              </div>
            </motion.div>
          )}

          {/* Compatible Profiles */}
          {compatibleProfiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.2 }}
            >
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                Compatible Profiles
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {compatibleProfiles.map((profile) => (
                  <Card
                    key={profile.id}
                    className="glass-card depth-shadow border-border/50"
                  >
                    <CardContent className="p-3 flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium truncate">{profile.displayName}</p>
                          {profile.isRunning && (
                            <Badge className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 text-[10px] gap-0.5">
                              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                              Active
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {profile.gpu} · {profile.vram} VRAM
                        </p>
                      </div>
                      {!profile.isRunning && model.downloaded && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-7 text-xs gap-1 btn-press shrink-0 ml-2"
                          onClick={() => handleLaunch(profile.name)}
                          disabled={startServer.isPending}
                        >
                          <Play className="h-3 w-3" />
                          Launch
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </motion.div>
          )}

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.25 }}
          >
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Actions
            </h3>
            <div className="flex flex-col gap-2">
              {!model.downloaded && (
                <Button
                  onClick={handlePull}
                  disabled={pullModel.isPending}
                  className="gap-2 btn-press w-full"
                >
                  <Download className="h-4 w-4" />
                  {pullModel.isPending ? 'Downloading...' : 'Pull / Download Model'}
                </Button>
              )}
              <Button
                variant="outline"
                onClick={handleCopyId}
                className="gap-2 btn-press w-full"
              >
                {copiedId ? (
                  <Check className="h-4 w-4 text-emerald-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
                {copiedId ? 'Copied!' : 'Copy Model ID'}
              </Button>
              {model.source && (
                <Button variant="outline" className="gap-2 btn-press w-full" asChild>
                  <a href={model.source} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4" />
                    View Source
                  </a>
                </Button>
              )}
            </div>
          </motion.div>
        </div>
      </SheetContent>
    </Sheet>
  )
}

function DetailItem({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: React.ReactNode
}) {
  return (
    <div className="glass-card depth-shadow rounded-lg p-3 border border-border/50">
      <div className="flex items-center gap-1.5 mb-1">
        <span className="text-muted-foreground">{icon}</span>
        <span className="text-[11px] text-muted-foreground uppercase tracking-wider font-medium">
          {label}
        </span>
      </div>
      <div>{value}</div>
    </div>
  )
}
