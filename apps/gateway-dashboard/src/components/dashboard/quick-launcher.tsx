'use client'

import { Card, CardContent } from '@/components/ui/card'
import { useKimariStore } from '@/lib/store'
import { useRunBenchmark, useStartServer } from '@/hooks/use-api'
import { motion } from 'framer-motion'
import { Play, Activity, Stethoscope, Download, Server, Cpu, Gauge, Box } from 'lucide-react'
import { toast } from 'sonner'

interface QuickAction {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  onClick: () => void
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 16, scale: 0.96 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.35, ease: 'easeOut' },
  },
}

export function QuickLauncher() {
  const setActiveView = useKimariStore((s) => s.setActiveView)
  const startServer = useStartServer()
  const runBenchmark = useRunBenchmark()

  const actions: QuickAction[] = [
    {
      id: 'start-server',
      title: 'Start Server',
      description: 'Launch llama.cpp with a GPU profile',
      icon: <Server className="h-5 w-5" />,
      onClick: () => setActiveView('server'),
    },
    {
      id: 'run-benchmark',
      title: 'Run Benchmark',
      description: 'Test model performance and speed',
      icon: <Activity className="h-5 w-5" />,
      onClick: async () => {
        try {
          await runBenchmark.mutateAsync({ profile: 'test', mode: 'standard' })
          toast.success('Benchmark started', { description: 'Running standard benchmark...' })
        } catch (err) {
          toast.error('Benchmark failed', { description: String(err) })
        }
      },
    },
    {
      id: 'system-check',
      title: 'System Check',
      description: 'Run diagnostics and health checks',
      icon: <Stethoscope className="h-5 w-5" />,
      onClick: () => setActiveView('doctor'),
    },
    {
      id: 'download-model',
      title: 'Download Model',
      description: 'Browse and download AI models',
      icon: <Download className="h-5 w-5" />,
      onClick: () => setActiveView('models'),
    },
  ]

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
              <Play className="h-4 w-4 text-primary" />
            </div>
            <h3 className="text-base font-semibold">Quick Launcher</h3>
          </div>

          <motion.div
            className="grid grid-cols-2 lg:grid-cols-4 gap-3"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {actions.map((action) => (
              <motion.button
                key={action.id}
                variants={itemVariants}
                whileHover={{ scale: 1.04, boxShadow: '0 10px 30px -6px oklch(0.65 0.17 230 / 18%), 0 4px 12px -2px oklch(0 0 0 / 8%)' }}
                whileTap={{ scale: 0.97 }}
                onClick={action.onClick}
                disabled={action.id === 'run-benchmark' && runBenchmark.isPending}
                className="group relative flex flex-col items-center gap-3 p-4 rounded-xl border border-border/50 bg-card/50 hover:border-primary/40 hover:bg-primary/[0.04] transition-colors duration-200 text-left focus:outline-none focus:ring-2 focus:ring-primary/30 focus:ring-offset-1"
              >
                <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center text-primary group-hover:from-primary/30 group-hover:to-primary/10 transition-all duration-200 shadow-sm shadow-primary/10">
                  {action.icon}
                </div>
                <div className="text-center">
                  <div className="text-sm font-medium text-foreground/90 group-hover:text-foreground transition-colors">
                    {action.title}
                  </div>
                  <div className="text-[11px] text-muted-foreground mt-0.5 leading-snug">
                    {action.description}
                  </div>
                </div>
              </motion.button>
            ))}
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
