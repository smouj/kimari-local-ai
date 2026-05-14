'use client'

import { useState } from 'react'
import { useKimariFit, type KimariFitData } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import {
  Gauge,
  Cpu,
  MemoryStick,
  HardDrive,
  Zap,
  ArrowRight,
  Lightbulb,
  TrendingUp,
  RotateCcw,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

const MODEL_OPTIONS = [
  { value: 'kimari-4b-q4', label: 'Kimari-4B Q4_K_M (2.4 GB)' },
  { value: 'kimari-4b-q5', label: 'Kimari-4B Q5_K_M (2.9 GB)' },
  { value: 'kimari-4b-q8', label: 'Kimari-4B Q8_0 (4.2 GB)' },
  { value: 'phi-3-mini-q4', label: 'Phi-3 Mini Q4_K_M (2.2 GB)' },
  { value: 'phi-3-mini-q5', label: 'Phi-3 Mini Q5_K_M (2.7 GB)' },
  { value: 'deepseek-coder-6.7b-q4', label: 'DeepSeek Coder 6.7B Q4_K_M (3.8 GB)' },
  { value: 'mistral-7b-q4', label: 'Mistral 7B Q4_K_M (4.1 GB)' },
  { value: 'qwen2-7b-q4', label: 'Qwen2 7B Q4_K_M (4.3 GB)' },
  { value: 'llama-3.1-8b-q4', label: 'Llama 3.1 8B Q4_K_M (4.9 GB)' },
  { value: 'mistral-7b-q5', label: 'Mistral 7B Q5_K_M (4.9 GB)' },
  { value: 'qwen2-7b-q5', label: 'Qwen2 7B Q5_K_M (5.1 GB)' },
  { value: 'llama-3.1-8b-q5', label: 'Llama 3.1 8B Q5_K_M (5.7 GB)' },
  { value: 'deepseek-coder-6.7b-q8', label: 'DeepSeek Coder 6.7B Q8_0 (6.8 GB)' },
  { value: 'mistral-7b-q8', label: 'Mistral 7B Q8_0 (7.2 GB)' },
  { value: 'qwen2-7b-q8', label: 'Qwen2 7B Q8_0 (7.4 GB)' },
  { value: 'llama-3.1-8b-q8', label: 'Llama 3.1 8B Q8_0 (8.1 GB)' },
]

const QUANT_OPTIONS = [
  { value: 'Q4_K_S', label: 'Q4_K_S - Smallest size' },
  { value: 'Q4_K_M', label: 'Q4_K_M - Balanced (Recommended)' },
  { value: 'Q5_K_S', label: 'Q5_K_S - Good quality' },
  { value: 'Q5_K_M', label: 'Q5_K_M - High quality' },
  { value: 'Q5_0', label: 'Q5_0 - High quality alt' },
  { value: 'Q6_K', label: 'Q6_K - Very high quality' },
  { value: 'Q8_0', label: 'Q8_0 - Near lossless' },
  { value: 'F16', label: 'F16 - Full precision' },
]

const QUICK_CONFIGS = [
  { label: 'GTX 1060 6GB', vram: 6, modelSize: 'mistral-7b-q4', contextSize: 4096, quantization: 'Q4_K_M' },
  { label: 'GTX 1080 8GB', vram: 8, modelSize: 'llama-3.1-8b-q5', contextSize: 4096, quantization: 'Q5_K_M' },
  { label: 'RTX 3060 12GB', vram: 12, modelSize: 'llama-3.1-8b-q8', contextSize: 8192, quantization: 'Q8_0' },
  { label: 'RTX 4070 12GB', vram: 12, modelSize: 'llama-3.1-8b-q5', contextSize: 8192, quantization: 'Q5_K_M' },
  { label: 'RTX 4090 24GB', vram: 24, modelSize: 'llama-3.1-8b-q8', contextSize: 16384, quantization: 'Q8_0' },
  { label: 'Mac M2 16GB', vram: 16, modelSize: 'llama-3.1-8b-q5', contextSize: 8192, quantization: 'Q5_K_M' },
]

function ScoreRing({ score }: { score: number }) {
  const radius = 80
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  const color = score > 70 ? '#10b981' : score > 40 ? '#eab308' : '#ef4444'
  const bgColor = score > 70 ? 'rgba(16,185,129,0.1)' : score > 40 ? 'rgba(234,179,8,0.1)' : 'rgba(239,68,68,0.1)'

  return (
    <div className="relative flex items-center justify-center">
      <svg width="200" height="200" viewBox="0 0 200 200" className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          stroke="currentColor"
          strokeWidth="8"
          fill="none"
          className="text-muted/30"
        />
        {/* Score arc */}
        <motion.circle
          cx="100"
          cy="100"
          r={radius}
          stroke={color}
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className={cn(
            'text-5xl font-bold font-mono',
            score > 70 ? 'text-emerald-600 dark:text-emerald-400' :
            score > 40 ? 'text-amber-600 dark:text-amber-400' :
            'text-red-600 dark:text-red-400'
          )}
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          {score}
        </motion.span>
        <span className="text-xs text-muted-foreground mt-1">KimariFit</span>
      </div>
      {/* Glow effect */}
      <div
        className="absolute inset-0 rounded-full blur-3xl opacity-20"
        style={{ backgroundColor: color }}
      />
    </div>
  )
}

function GradeBadge({ grade }: { grade: string }) {
  const gradeColors: Record<string, string> = {
    'A+': 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border-emerald-500/40',
    'A': 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
    'B': 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30',
    'C': 'bg-orange-500/15 text-orange-600 dark:text-orange-400 border-orange-500/30',
    'D': 'bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/30',
    'F': 'bg-red-500/20 text-red-600 dark:text-red-400 border-red-500/40',
  }

  return (
    <Badge className={cn('text-2xl font-bold px-4 py-1.5 border', gradeColors[grade] ?? gradeColors['F'])}>
      {grade}
    </Badge>
  )
}

function DetailCard({
  icon,
  label,
  value,
  unit,
  subtext,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: number | string
  unit: string
  subtext?: string
  color: string
}) {
  return (
    <Card className="relative overflow-hidden">
      <div className={cn('absolute top-0 left-0 right-0 h-0.5', color)} />
      <CardContent className="pt-4 pb-3 px-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-muted-foreground">{icon}</span>
          <span className="text-xs text-muted-foreground font-medium">{label}</span>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-xl font-bold font-mono">{value}</span>
          <span className="text-xs text-muted-foreground">{unit}</span>
        </div>
        {subtext && (
          <p className="text-[10px] text-muted-foreground mt-1">{subtext}</p>
        )}
      </CardContent>
    </Card>
  )
}

export function KimariFitView() {
  const [modelSize, setModelSize] = useState('mistral-7b-q4')
  const [vram, setVram] = useState(8)
  const [contextSize, setContextSize] = useState(4096)
  const [quantization, setQuantization] = useState('Q4_K_M')
  const [result, setResult] = useState<KimariFitData | null>(null)

  const kimariFit = useKimariFit()

  const handleCalculate = async () => {
    try {
      const data = await kimariFit.mutateAsync({
        modelSize,
        vram,
        contextSize,
        quantization,
      })
      setResult(data)
    } catch {
      // Error handled by mutation state
    }
  }

  const handleQuickConfig = (config: typeof QUICK_CONFIGS[number]) => {
    setModelSize(config.modelSize)
    setVram(config.vram)
    setContextSize(config.contextSize)
    setQuantization(config.quantization)
    setResult(null)
  }

  const handleReset = () => {
    setModelSize('mistral-7b-q4')
    setVram(8)
    setContextSize(4096)
    setQuantization('Q4_K_M')
    setResult(null)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Configuration Form */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Gauge className="h-4 w-4" />
              Configuration
            </CardTitle>
            <Button variant="ghost" size="sm" className="gap-1.5 text-xs h-7" onClick={handleReset}>
              <RotateCcw className="h-3 w-3" />
              Reset
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Quick Select Buttons */}
          <div>
            <Label className="text-xs font-medium mb-2 block">Quick Select</Label>
            <div className="flex flex-wrap gap-2">
              {QUICK_CONFIGS.map((config) => (
                <Button
                  key={config.label}
                  variant="outline"
                  size="sm"
                  className="text-xs h-7 gap-1.5"
                  onClick={() => handleQuickConfig(config)}
                >
                  <Cpu className="h-3 w-3" />
                  {config.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Main Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-2">
              <Label className="text-xs font-medium">Model Size</Label>
              <Select value={modelSize} onValueChange={setModelSize}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="max-h-64">
                  {MODEL_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-xs font-medium">Quantization</Label>
              <Select value={quantization} onValueChange={setQuantization}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {QUANT_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-xs font-medium">VRAM (GB)</Label>
              <Input
                type="number"
                min={1}
                max={128}
                step={0.5}
                value={vram}
                onChange={(e) => setVram(parseFloat(e.target.value) || 8)}
                className="font-mono"
              />
              <div className="flex gap-1.5">
                {[4, 6, 8, 12, 16, 24].map((v) => (
                  <Button
                    key={v}
                    variant={vram === v ? 'default' : 'outline'}
                    size="sm"
                    className="text-[10px] h-6 px-2 font-mono"
                    onClick={() => setVram(v)}
                  >
                    {v}GB
                  </Button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-xs font-medium">Context Size</Label>
                <span className="text-xs font-mono text-muted-foreground">{contextSize.toLocaleString()} tokens</span>
              </div>
              <Slider
                value={[contextSize]}
                onValueChange={([v]) => setContextSize(v)}
                min={512}
                max={32768}
                step={512}
                className="mt-2"
              />
              <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
                <span>512</span>
                <span>32K</span>
              </div>
            </div>
          </div>

          <Button
            className="w-full gap-2"
            onClick={handleCalculate}
            disabled={kimariFit.isPending}
          >
            {kimariFit.isPending ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Calculating...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4" />
                Calculate KimariFit Score
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="space-y-6"
          >
            {/* Score Display */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col lg:flex-row items-center justify-center gap-8">
                  <ScoreRing score={result.score} />
                  <div className="flex flex-col items-center lg:items-start gap-3">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-semibold">Grade</span>
                      <GradeBadge grade={result.grade} />
                    </div>
                    <p className="text-sm text-muted-foreground max-w-xs text-center lg:text-left">
                      {result.score > 90
                        ? 'Excellent! This configuration will run flawlessly.'
                        : result.score > 70
                        ? 'Good fit. Reliable performance for most workloads.'
                        : result.score > 50
                        ? 'Marginal fit. May experience slowdowns or stability issues.'
                        : 'Poor fit. Consider reducing model size or context window.'}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>VRAM Usage:</span>
                      <Progress value={result.details.vramUsagePercent} className="h-2 w-24" />
                      <span className="font-mono">{result.details.vramUsagePercent}%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Detail Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              <DetailCard
                icon={<HardDrive className="h-4 w-4" />}
                label="Model VRAM"
                value={result.details.modelVram}
                unit="MB"
                subtext="Model weights size"
                color="bg-primary"
              />
              <DetailCard
                icon={<MemoryStick className="h-4 w-4" />}
                label="Context VRAM"
                value={result.details.contextVram}
                unit="MB"
                subtext={`KV cache for ${contextSize.toLocaleString()} tokens`}
                color="bg-blue-500"
              />
              <DetailCard
                icon={<Cpu className="h-4 w-4" />}
                label="Total VRAM"
                value={result.details.totalVram}
                unit="MB"
                subtext="Model + context + overhead"
                color="bg-purple-500"
              />
              <DetailCard
                icon={<TrendingUp className="h-4 w-4" />}
                label="Headroom"
                value={result.details.headroom}
                unit="MB"
                subtext={result.details.headroom > 0 ? 'Available space' : 'Exceeds VRAM!'}
                color={result.details.headroom > 0 ? 'bg-emerald-500' : 'bg-red-500'}
              />
              <DetailCard
                icon={<Zap className="h-4 w-4" />}
                label="Efficiency"
                value={`${Math.round(result.details.efficiency * 100)}%`}
                unit=""
                subtext={`${quantization} quantization`}
                color="bg-amber-500"
              />
            </div>

            {/* Recommendations */}
            {result.recommendations.length > 0 && (
              <Card>
                <CardHeader className="pb-4">
                  <CardTitle className="text-base font-semibold flex items-center gap-2">
                    <Lightbulb className="h-4 w-4 text-amber-500" />
                    Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2.5">
                    {result.recommendations.map((rec, i) => (
                      <motion.li
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="flex items-start gap-2.5 text-sm"
                      >
                        <ArrowRight className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                        <span className="text-muted-foreground leading-relaxed">{rec}</span>
                      </motion.li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
