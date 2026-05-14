'use client'

import { useState, useCallback } from 'react'
import { useKimariStore } from '@/lib/store'
import { useCompleteSetup, useProfiles } from '@/hooks/use-api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Zap,
  Monitor,
  Download,
  Rocket,
  ChevronRight,
  ChevronLeft,
  SkipForward,
  Cpu,
  HardDrive,
  Check,
  Loader2,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const STEPS = [
  { id: 'welcome', title: 'Welcome to Kimari', icon: Zap },
  { id: 'gpu', title: 'GPU Configuration', icon: Monitor },
  { id: 'model', title: 'Download Model', icon: Download },
  { id: 'start', title: 'Start Server', icon: Rocket },
]

function WelcomeStep() {
  return (
    <div className="flex flex-col items-center text-center space-y-6">
      <div className="relative">
        <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-primary via-primary/80 to-primary/60 flex items-center justify-center shadow-lg glow-blue overflow-hidden">
          <img src="/kimari-logo.png" alt="Kimari" className="h-16 w-16 object-contain" />
        </div>
        <div className="absolute -inset-2 rounded-3xl bg-primary/10 animate-ring-pulse" />
      </div>
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Welcome to Kimari</h2>
        <p className="text-muted-foreground text-sm max-w-md">
          Your local AI gateway for running LLMs with hardware-optimized profiles. 
          Kimari manages llama.cpp server instances, GPU profiles, and integrations — 
          all from a single dashboard.
        </p>
      </div>
      <div className="grid grid-cols-3 gap-3 w-full max-w-sm">
        {[
          { icon: Monitor, label: 'GPU Profiles' },
          { icon: Download, label: 'Model Manager' },
          { icon: Rocket, label: 'One-Click Start' },
        ].map((item) => (
          <div
            key={item.label}
            className="glass-card rounded-lg p-3 flex flex-col items-center gap-2 text-center"
          >
            <item.icon className="h-5 w-5 text-primary" />
            <span className="text-[11px] font-medium text-muted-foreground">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function GpuStep() {
  const { data: profiles } = useProfiles()
  const [selectedGpu, setSelectedGpu] = useState<string>('rtx-3060')
  const [selectedQuant, setSelectedQuant] = useState<string>('Q4_K_M')

  const gpuOptions = [
    { id: 'rtx-3060', name: 'NVIDIA RTX 3060', vram: '12 GB', icon: '🎮' },
    { id: 'rtx-4070', name: 'NVIDIA RTX 4070', vram: '12 GB', icon: '🚀' },
    { id: 'rtx-3090', name: 'NVIDIA RTX 3090', vram: '24 GB', icon: '💻' },
    { id: 'rx-7600', name: 'AMD RX 7600', vram: '8 GB', icon: '🔴' },
  ]

  const quantOptions = [
    { id: 'Q4_K_M', label: 'Q4_K_M', desc: 'Best balance of quality & speed' },
    { id: 'Q5_K_M', label: 'Q5_K_M', desc: 'Higher quality, more VRAM' },
    { id: 'Q8_0', label: 'Q8_0', desc: 'Near-original quality' },
    { id: 'F16', label: 'F16', desc: 'Full precision, max VRAM' },
  ]

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-xl font-bold tracking-tight">GPU Configuration</h2>
        <p className="text-sm text-muted-foreground">
          Select your GPU and preferred quantization level
        </p>
      </div>

      {profiles && profiles.length > 0 && (
        <div className="glass-card rounded-lg p-3 flex items-center gap-2">
          <Cpu className="h-4 w-4 text-emerald-500" />
          <span className="text-xs text-muted-foreground">
            {profiles.length} GPU profile{profiles.length > 1 ? 's' : ''} auto-detected
          </span>
          <Badge variant="outline" className="ml-auto text-[10px] border-emerald-500/30 text-emerald-500">
            Detected
          </Badge>
        </div>
      )}

      <div className="space-y-3">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Select GPU
        </label>
        <div className="grid grid-cols-2 gap-2">
          {gpuOptions.map((gpu) => (
            <button
              key={gpu.id}
              onClick={() => setSelectedGpu(gpu.id)}
              className={cn(
                'glass-card rounded-lg p-3 text-left transition-all',
                'hover:ring-1 hover:ring-primary/30',
                selectedGpu === gpu.id
                  ? 'ring-1 ring-primary bg-primary/5'
                  : ''
              )}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm">{gpu.icon}</span>
                <span className="text-xs font-medium truncate">{gpu.name}</span>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                <HardDrive className="h-3 w-3" />
                <span>{gpu.vram} VRAM</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Quantization Preference
        </label>
        <div className="space-y-2">
          {quantOptions.map((q) => (
            <button
              key={q.id}
              onClick={() => setSelectedQuant(q.id)}
              className={cn(
                'w-full glass-card rounded-lg p-3 flex items-center gap-3 text-left transition-all',
                'hover:ring-1 hover:ring-primary/30',
                selectedQuant === q.id
                  ? 'ring-1 ring-primary bg-primary/5'
                  : ''
              )}
            >
              <div className={cn(
                'h-5 w-5 rounded-full border-2 flex items-center justify-center shrink-0',
                selectedQuant === q.id
                  ? 'border-primary bg-primary'
                  : 'border-muted-foreground/30'
              )}>
                {selectedQuant === q.id && <Check className="h-3 w-3 text-primary-foreground" />}
              </div>
              <div>
                <div className="text-xs font-medium">{q.label}</div>
                <div className="text-[10px] text-muted-foreground">{q.desc}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function ModelStep() {
  const [downloading, setDownloading] = useState(false)
  const [downloadProgress, setDownloadProgress] = useState(0)

  const recommendedModels = [
    { name: 'Qwen3 4B Instruct', size: '2.4 GB', quant: 'Q4_K_M', recommended: true },
    { name: 'Llama 3.2 3B Instruct', size: '2.0 GB', quant: 'Q4_K_M', recommended: false },
    { name: 'Phi-4 Mini Instruct', size: '1.6 GB', quant: 'Q4_K_M', recommended: false },
  ]

  const handleDownload = useCallback(() => {
    setDownloading(true)
    setDownloadProgress(0)
    const interval = setInterval(() => {
      setDownloadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setDownloading(false)
          return 100
        }
        return prev + Math.random() * 15 + 5
      })
    }, 400)
  }, [])

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-xl font-bold tracking-tight">Download Model</h2>
        <p className="text-sm text-muted-foreground">
          Choose a model to get started. You can always download more later.
        </p>
      </div>

      <div className="space-y-3">
        {recommendedModels.map((model) => (
          <div
            key={model.name}
            className={cn(
              'glass-card rounded-lg p-4',
              model.recommended && 'ring-1 ring-primary/30 bg-primary/5'
            )}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{model.name}</span>
                  {model.recommended && (
                    <Badge className="text-[10px] h-5 bg-primary/20 text-primary border-0">
                      Recommended
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1 text-[10px] text-muted-foreground">
                  <span>{model.size}</span>
                  <span>·</span>
                  <span>{model.quant}</span>
                </div>
              </div>
            </div>
            {model.recommended && (
              <div className="mt-3">
                {downloading ? (
                  <div className="space-y-2">
                    <Progress value={Math.min(downloadProgress, 100)} className="h-2" />
                    <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Downloading...
                      </span>
                      <span>{Math.min(Math.round(downloadProgress), 100)}%</span>
                    </div>
                  </div>
                ) : downloadProgress >= 100 ? (
                  <div className="flex items-center gap-1.5 text-xs text-emerald-500">
                    <Check className="h-3.5 w-3.5" />
                    Downloaded
                  </div>
                ) : (
                  <Button
                    size="sm"
                    onClick={handleDownload}
                    className="h-7 text-xs"
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Download
                  </Button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function StartStep({ onComplete }: { onComplete: () => void }) {
  const completeSetup = useCompleteSetup()

  const config = [
    { label: 'GPU', value: 'NVIDIA RTX 3060 (12 GB)' },
    { label: 'Quantization', value: 'Q4_K_M' },
    { label: 'Model', value: 'Qwen3 4B Instruct' },
    { label: 'Port', value: '8080' },
  ]

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-xl font-bold tracking-tight">Ready to Launch!</h2>
        <p className="text-sm text-muted-foreground">
          Review your configuration and start using Kimari
        </p>
      </div>

      <div className="glass-card rounded-lg p-4 space-y-3">
        <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Configuration Summary
        </h3>
        {config.map((item) => (
          <div key={item.label} className="flex items-center justify-between py-1.5 border-b border-border/30 last:border-0">
            <span className="text-xs text-muted-foreground">{item.label}</span>
            <span className="text-xs font-medium">{item.value}</span>
          </div>
        ))}
      </div>

      <div className="glass-card rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
            <img src="/kimari-logo.png" alt="Kimari" className="h-6 w-6 object-contain" />
          </div>
          <div>
            <p className="text-xs font-medium mb-1">Quick Tip</p>
            <p className="text-[11px] text-muted-foreground">
              You can change your GPU profile and quantization at any time from the 
              Dashboard. Kimari will automatically adjust server parameters for optimal performance.
            </p>
          </div>
        </div>
      </div>

      <Button
        className="w-full h-11 text-sm font-semibold bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
        onClick={() => {
          completeSetup.mutate()
          onComplete()
        }}
        disabled={completeSetup.isPending}
      >
        {completeSetup.isPending ? (
          <Loader2 className="h-4 w-4 animate-spin mr-2" />
        ) : (
          <Rocket className="h-4 w-4 mr-2" />
        )}
        Launch Kimari
      </Button>
    </div>
  )
}

export function SetupWizard() {
  const [currentStep, setCurrentStep] = useState(0)
  const { setSetupComplete } = useKimariStore()

  const handleComplete = useCallback(() => {
    localStorage.setItem('kimari-setup-complete', 'true')
    setSetupComplete(true)
  }, [setSetupComplete])

  const handleSkip = useCallback(() => {
    localStorage.setItem('kimari-setup-complete', 'true')
    setSetupComplete(true)
  }, [setSetupComplete])

  const progress = ((currentStep + 1) / STEPS.length) * 100

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 80 : -80,
      opacity: 0,
    }),
    center: {
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      x: direction < 0 ? 80 : -80,
      opacity: 0,
    }),
  }

  const [direction, setDirection] = useState(0)

  const goNext = () => {
    if (currentStep < STEPS.length - 1) {
      setDirection(1)
      setCurrentStep((s) => s + 1)
    }
  }

  const goBack = () => {
    if (currentStep > 0) {
      setDirection(-1)
      setCurrentStep((s) => s - 1)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5">
      {/* Background effects */}
      <div className="absolute inset-0 dot-grid-bg opacity-30" />
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent" />

      {/* Glow effect */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 h-64 w-64 bg-primary/5 rounded-full blur-3xl" />

      <div className="relative w-full max-w-lg mx-4">
        {/* Step indicator */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            {STEPS.map((step, i) => {
              const StepIcon = step.icon
              return (
                <div
                  key={step.id}
                  className={cn(
                    'flex items-center gap-2 text-xs transition-colors',
                    i <= currentStep
                      ? 'text-primary font-medium'
                      : 'text-muted-foreground/50'
                  )}
                >
                  <div className={cn(
                    'h-7 w-7 rounded-full flex items-center justify-center text-[11px] font-bold transition-all',
                    i < currentStep
                      ? 'bg-primary text-primary-foreground'
                      : i === currentStep
                      ? 'bg-primary/20 text-primary ring-1 ring-primary/50'
                      : 'bg-muted/50 text-muted-foreground/50'
                  )}>
                    {i < currentStep ? (
                      <Check className="h-3.5 w-3.5" />
                    ) : (
                      <StepIcon className="h-3.5 w-3.5" />
                    )}
                  </div>
                  <span className="hidden sm:inline">{step.title}</span>
                </div>
              )
            })}
          </div>
          <Progress value={progress} className="h-1.5" />
          <div className="flex justify-between mt-2">
            <span className="text-[10px] text-muted-foreground">
              Step {currentStep + 1} of {STEPS.length}
            </span>
            <span className="text-[10px] text-muted-foreground">
              {Math.round(progress)}% complete
            </span>
          </div>
        </div>

        {/* Content card */}
        <Card className="glass-card border-border/30 shadow-xl">
          <CardContent className="p-6 sm:p-8 min-h-[400px] flex flex-col">
            <div className="flex-1">
              <AnimatePresence mode="wait" custom={direction}>
                <motion.div
                  key={currentStep}
                  custom={direction}
                  variants={slideVariants}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  transition={{ duration: 0.3, ease: 'easeInOut' }}
                >
                  {currentStep === 0 && <WelcomeStep />}
                  {currentStep === 1 && <GpuStep />}
                  {currentStep === 2 && <ModelStep />}
                  {currentStep === 3 && <StartStep onComplete={handleComplete} />}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Navigation */}
            {currentStep < 3 && (
              <div className="flex items-center justify-between mt-6 pt-4 border-t border-border/30">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={goBack}
                  disabled={currentStep === 0}
                  className="h-8 text-xs"
                >
                  <ChevronLeft className="h-3.5 w-3.5 mr-1" />
                  Back
                </Button>
                <Button
                  size="sm"
                  onClick={goNext}
                  className="h-8 text-xs"
                >
                  Next
                  <ChevronRight className="h-3.5 w-3.5 ml-1" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Skip option */}
        <div className="mt-4 text-center">
          <button
            onClick={handleSkip}
            className="text-xs text-muted-foreground/50 hover:text-muted-foreground transition-colors inline-flex items-center gap-1"
          >
            <SkipForward className="h-3 w-3" />
            Skip setup
          </button>
        </div>
      </div>
    </div>
  )
}
