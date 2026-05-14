'use client'

import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { useModelCompare, type ModelComparisonItem } from '@/hooks/use-api'
import {
  GitCompare,
  Cpu,
  Zap,
  MemoryStick,
  Code,
  Brain,
  Sparkles,
  ListChecks,
  Trophy,
  CheckCircle2,
  XCircle,
  Loader2,
  ArrowRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const allModelOptions = [
  { id: 'kimari-4b', label: 'Kimari 4B' },
  { id: 'llama-3.2-3b', label: 'Llama 3.2 3B' },
  { id: 'mistral-7b', label: 'Mistral 7B' },
  { id: 'phi-3-medium', label: 'Phi-3 Medium 14B' },
  { id: 'deepseek-coder-6.7b', label: 'DeepSeek Coder 6.7B' },
  { id: 'qwen2.5-7b', label: 'Qwen 2.5 7B' },
  { id: 'yi-1.5-9b', label: 'Yi 1.5 9B' },
  { id: 'gemma-2-9b', label: 'Gemma 2 9B' },
]

// Quality score bar component
function ScoreBar({ value, max = 10, isBest }: { value: number; max?: number; isBest: boolean }) {
  const percent = (value / max) * 100
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 rounded-full bg-muted/50 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className={cn(
            'h-full rounded-full',
            isBest ? 'bg-emerald-500' : 'bg-primary/60'
          )}
        />
      </div>
      <span className={cn(
        'text-xs font-mono w-5 text-right',
        isBest ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-foreground'
      )}>
        {value}
      </span>
    </div>
  )
}

// Best badge
function BestBadge() {
  return (
    <Badge className="text-[9px] h-4 px-1.5 bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-0.5 font-bold">
      <Trophy className="h-2.5 w-2.5" />
      Best
    </Badge>
  )
}

// Color-code a metric cell
function MetricCell({ value, isBest, isWorst, unit }: { value: string | number; isBest: boolean; isWorst: boolean; unit?: string }) {
  return (
    <div className={cn(
      'flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-mono',
      isBest && 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
      isWorst && 'bg-red-500/5 text-red-600 dark:text-red-400',
      !isBest && !isWorst && 'bg-amber-500/5 text-amber-700 dark:text-amber-300'
    )}>
      {isBest && <Trophy className="h-3 w-3 shrink-0" />}
      <span className="font-semibold">{value}</span>
      {unit && <span className="text-[10px] text-muted-foreground">{unit}</span>}
    </div>
  )
}

export function ModelCompareView() {
  const [selectedModels, setSelectedModels] = useState<string[]>(['kimari-4b', 'mistral-7b'])
  const { data, isLoading, error } = useModelCompare(selectedModels)

  const toggleModel = (modelId: string) => {
    setSelectedModels((prev) => {
      if (prev.includes(modelId)) {
        if (prev.length <= 2) return prev // minimum 2
        return prev.filter((m) => m !== modelId)
      }
      if (prev.length >= 4) return prev // maximum 4
      return [...prev, modelId]
    })
  }

  // Compute best/worst for each numeric metric
  const comparison = useMemo(() => {
    if (!data?.models) return null
    const models = data.models

    // For each metric, find the best and worst values
    const promptSpeeds = models.map((m) => m.performance.promptTokPerSec)
    const genSpeeds = models.map((m) => m.performance.genTokPerSec)
    const vramReqs = models.map((m) => m.performance.vramRequiredGb)
    const ctxLengths = models.map((m) => m.performance.contextLength)
    const instructionScores = models.map((m) => m.quality.instructionFollowing)
    const codingScores = models.map((m) => m.quality.codingAbility)
    const reasoningScores = models.map((m) => m.quality.reasoning)
    const creativityScores = models.map((m) => m.quality.creativity)

    return {
      promptSpeed: { best: Math.max(...promptSpeeds), worst: Math.min(...promptSpeeds) },
      genSpeed: { best: Math.max(...genSpeeds), worst: Math.min(...genSpeeds) },
      vramReq: { best: Math.min(...vramReqs), worst: Math.max(...vramReqs) }, // lower is better
      ctxLength: { best: Math.max(...ctxLengths), worst: Math.min(...ctxLengths) },
      instruction: { best: Math.max(...instructionScores), worst: Math.min(...instructionScores) },
      coding: { best: Math.max(...codingScores), worst: Math.min(...codingScores) },
      reasoning: { best: Math.max(...reasoningScores), worst: Math.min(...reasoningScores) },
      creativity: { best: Math.max(...creativityScores), worst: Math.min(...creativityScores) },
    }
  }, [data])

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

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3"
      >
        <div className="flex items-center justify-center h-10 w-10 rounded-xl bg-primary/10 text-primary">
          <GitCompare className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-foreground">Model Comparison</h2>
          <p className="text-sm text-muted-foreground">Compare models side-by-side on performance, quality, and compatibility</p>
        </div>
      </motion.div>

      {/* Model Selector */}
      <Card className="glass-card depth-shadow">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <ListChecks className="h-4 w-4 text-primary" />
            Select Models to Compare
            <Badge variant="outline" className="text-[10px] font-mono border-border/50">
              {selectedModels.length}/4
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {allModelOptions.map((model) => {
              const isSelected = selectedModels.includes(model.id)
              const canToggle = isSelected || selectedModels.length < 4
              return (
                <label
                  key={model.id}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all',
                    isSelected
                      ? 'border-primary/40 bg-primary/5 shadow-sm'
                      : canToggle
                      ? 'border-border/40 bg-card hover:border-primary/20 hover:bg-accent/20'
                      : 'border-border/20 bg-muted/30 opacity-50 cursor-not-allowed'
                  )}
                >
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={() => canToggle && toggleModel(model.id)}
                    disabled={!canToggle}
                  />
                  <span className="text-sm font-medium truncate">{model.label}</span>
                </label>
              )
            })}
          </div>
          <p className="text-[11px] text-muted-foreground mt-3">
            Select 2–4 models to compare. Metrics are color-coded: <span className="text-emerald-600 dark:text-emerald-400 font-semibold">green = best</span>,{' '}
            <span className="text-amber-700 dark:text-amber-300 font-semibold">amber = middle</span>,{' '}
            <span className="text-red-600 dark:text-red-400 font-semibold">red = worst</span>.
          </p>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-3 text-sm text-muted-foreground">Comparing models...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-red-500/30 bg-red-500/5">
          <CardContent className="p-6 text-center">
            <p className="text-sm text-red-600 dark:text-red-400">Failed to load comparison data. Please try again.</p>
          </CardContent>
        </Card>
      )}

      {/* Comparison Content */}
      {data && comparison && (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="space-y-6"
        >
          {/* Comparison Table - Horizontally scrollable on mobile */}
          <div className="overflow-x-auto -mx-6 px-6">
            <div className="min-w-[640px]">
              {/* Column Headers - Model Names */}
              <div className="grid gap-4 mb-4" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                <div /> {/* Spacer for label column */}
                {data.models.map((model, idx) => (
                  <motion.div key={model.name} variants={item} className="text-center">
                    <div className="glass-card depth-shadow rounded-xl p-4 border border-primary/10">
                      <div className="flex items-center justify-center gap-2 mb-1">
                        <Cpu className="h-4 w-4 text-primary" />
                        <span className="font-semibold text-sm text-foreground">{model.displayName}</span>
                      </div>
                      <div className="flex items-center justify-center gap-1.5">
                        <Badge variant="outline" className="text-[10px] border-border/50">{model.quantization}</Badge>
                        <Badge variant="outline" className="text-[10px] border-border/50">{model.category}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1.5">{model.size}</p>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Performance Section */}
              <motion.div variants={item}>
                <Card className="glass-card depth-shadow mb-4">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-semibold flex items-center gap-2">
                      <Zap className="h-4 w-4 text-primary" />
                      Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {/* Prompt Speed */}
                    <div className="grid gap-4 items-center" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <ArrowRight className="h-3.5 w-3.5" />
                        Prompt Speed
                      </div>
                      {data.models.map((model) => (
                        <div key={model.name} className="flex items-center gap-2 justify-center">
                          <MetricCell
                            value={model.performance.promptTokPerSec}
                            isBest={model.performance.promptTokPerSec === comparison.promptSpeed.best}
                            isWorst={model.performance.promptTokPerSec === comparison.promptSpeed.worst}
                            unit="tok/s"
                          />
                          {model.performance.promptTokPerSec === comparison.promptSpeed.best && <BestBadge />}
                        </div>
                      ))}
                    </div>

                    {/* Gen Speed */}
                    <div className="grid gap-4 items-center" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Sparkles className="h-3.5 w-3.5" />
                        Generation Speed
                      </div>
                      {data.models.map((model) => (
                        <div key={model.name} className="flex items-center gap-2 justify-center">
                          <MetricCell
                            value={model.performance.genTokPerSec}
                            isBest={model.performance.genTokPerSec === comparison.genSpeed.best}
                            isWorst={model.performance.genTokPerSec === comparison.genSpeed.worst}
                            unit="tok/s"
                          />
                          {model.performance.genTokPerSec === comparison.genSpeed.best && <BestBadge />}
                        </div>
                      ))}
                    </div>

                    {/* VRAM Required */}
                    <div className="grid gap-4 items-center" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <MemoryStick className="h-3.5 w-3.5" />
                        VRAM Required
                      </div>
                      {data.models.map((model) => (
                        <div key={model.name} className="flex items-center gap-2 justify-center">
                          <MetricCell
                            value={model.performance.vramRequiredGb}
                            isBest={model.performance.vramRequiredGb === comparison.vramReq.best}
                            isWorst={model.performance.vramRequiredGb === comparison.vramReq.worst}
                            unit="GB"
                          />
                          {model.performance.vramRequiredGb === comparison.vramReq.best && <BestBadge />}
                        </div>
                      ))}
                    </div>

                    {/* Context Length */}
                    <div className="grid gap-4 items-center" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Brain className="h-3.5 w-3.5" />
                        Context Length
                      </div>
                      {data.models.map((model) => (
                        <div key={model.name} className="flex items-center gap-2 justify-center">
                          <MetricCell
                            value={model.performance.contextLength.toLocaleString()}
                            isBest={model.performance.contextLength === comparison.ctxLength.best}
                            isWorst={model.performance.contextLength === comparison.ctxLength.worst}
                            unit="tokens"
                          />
                          {model.performance.contextLength === comparison.ctxLength.best && <BestBadge />}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Quality Scores Section */}
              <motion.div variants={item}>
                <Card className="glass-card depth-shadow mb-4">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-semibold flex items-center gap-2">
                      <Brain className="h-4 w-4 text-primary" />
                      Quality Scores
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Instruction Following */}
                    <div className="grid gap-4 items-center" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <ListChecks className="h-3.5 w-3.5" />
                        Instruction Following
                      </div>
                      {data.models.map((model) => (
                        <div key={model.name} className="flex items-center gap-2 justify-center">
                          <div className="w-full max-w-[140px]">
                            <ScoreBar
                              value={model.quality.instructionFollowing}
                              isBest={model.quality.instructionFollowing === comparison.instruction.best}
                            />
                          </div>
                          {model.quality.instructionFollowing === comparison.instruction.best && <BestBadge />}
                        </div>
                      ))}
                    </div>

                    {/* Coding Ability */}
                    <div className="grid gap-4 items-center" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Code className="h-3.5 w-3.5" />
                        Coding Ability
                      </div>
                      {data.models.map((model) => (
                        <div key={model.name} className="flex items-center gap-2 justify-center">
                          <div className="w-full max-w-[140px]">
                            <ScoreBar
                              value={model.quality.codingAbility}
                              isBest={model.quality.codingAbility === comparison.coding.best}
                            />
                          </div>
                          {model.quality.codingAbility === comparison.coding.best && <BestBadge />}
                        </div>
                      ))}
                    </div>

                    {/* Reasoning */}
                    <div className="grid gap-4 items-center" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Brain className="h-3.5 w-3.5" />
                        Reasoning
                      </div>
                      {data.models.map((model) => (
                        <div key={model.name} className="flex items-center gap-2 justify-center">
                          <div className="w-full max-w-[140px]">
                            <ScoreBar
                              value={model.quality.reasoning}
                              isBest={model.quality.reasoning === comparison.reasoning.best}
                            />
                          </div>
                          {model.quality.reasoning === comparison.reasoning.best && <BestBadge />}
                        </div>
                      ))}
                    </div>

                    {/* Creativity */}
                    <div className="grid gap-4 items-center" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Sparkles className="h-3.5 w-3.5" />
                        Creativity
                      </div>
                      {data.models.map((model) => (
                        <div key={model.name} className="flex items-center gap-2 justify-center">
                          <div className="w-full max-w-[140px]">
                            <ScoreBar
                              value={model.quality.creativity}
                              isBest={model.quality.creativity === comparison.creativity.best}
                            />
                          </div>
                          {model.quality.creativity === comparison.creativity.best && <BestBadge />}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Compatibility Section */}
              <motion.div variants={item}>
                <Card className="glass-card depth-shadow mb-4">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-semibold flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-primary" />
                      GPU Compatibility
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div /> {/* Spacer */}
                      {data.models.map((model) => (
                        <div key={model.name} className="space-y-1.5">
                          {model.compatibleProfiles.map((profile) => (
                            <div
                              key={profile}
                              className="flex items-center gap-1.5 text-xs text-foreground/80 px-2 py-1 rounded-md bg-emerald-500/5 border border-emerald-500/20"
                            >
                              <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0" />
                              {profile}
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Pros & Cons Section */}
              <motion.div variants={item}>
                <Card className="glass-card depth-shadow">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-semibold">Pros & Cons</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4" style={{ gridTemplateColumns: `200px repeat(${data.models.length}, 1fr)` }}>
                      <div /> {/* Spacer */}
                      {data.models.map((model) => (
                        <div key={model.name} className="space-y-3">
                          {/* Pros */}
                          <div>
                            <p className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider mb-1.5">Pros</p>
                            {model.pros.map((pro, i) => (
                              <div key={i} className="flex items-start gap-1.5 text-xs text-foreground/80 mb-1.5">
                                <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0 mt-0.5" />
                                <span>{pro}</span>
                              </div>
                            ))}
                          </div>
                          {/* Cons */}
                          <div>
                            <p className="text-[11px] font-semibold text-red-600 dark:text-red-400 uppercase tracking-wider mb-1.5">Cons</p>
                            {model.cons.map((con, i) => (
                              <div key={i} className="flex items-start gap-1.5 text-xs text-foreground/80 mb-1.5">
                                <XCircle className="h-3 w-3 text-red-500 shrink-0 mt-0.5" />
                                <span>{con}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Empty / No selection state */}
      {selectedModels.length < 2 && !isLoading && (
        <Card className="glass-card depth-shadow">
          <CardContent className="p-12 text-center">
            <GitCompare className="h-12 w-12 text-muted-foreground/30 mx-auto mb-4" />
            <h3 className="text-base font-semibold text-foreground mb-2">Select at least 2 models</h3>
            <p className="text-sm text-muted-foreground">Choose models above to see a side-by-side comparison.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
