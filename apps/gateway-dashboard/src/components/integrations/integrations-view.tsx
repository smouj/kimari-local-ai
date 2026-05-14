'use client'

import { useState } from 'react'
import { useIntegrations } from '@/hooks/use-api'
import type { Integration } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { toast } from 'sonner'
import { Globe, Bot, MessageSquare, Code, Copy, ExternalLink, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import oneDark from 'react-syntax-highlighter/dist/esm/styles/prism/one-dark'

const iconMap: Record<string, React.ReactNode> = {
  openwebui: <Globe className="h-6 w-6" />,
  openclaw: <Bot className="h-6 w-6" />,
  hermes: <MessageSquare className="h-6 w-6" />,
  continue: <Code className="h-6 w-6" />,
}

const statusColors: Record<string, string> = {
  available: 'border-emerald-500/30 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5',
  configured: 'border-blue-500/30 text-blue-600 dark:text-blue-400 bg-blue-500/5',
  running: 'border-emerald-500/30 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5',
  error: 'border-red-500/30 text-red-600 dark:text-red-400 bg-red-500/5',
}

const statusBgColors: Record<string, string> = {
  available: 'bg-emerald-500/10',
  configured: 'bg-blue-500/10',
  running: 'bg-emerald-500/10',
  error: 'bg-red-500/10',
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      toast.success('Copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error('Failed to copy')
    }
  }

  return (
    <Button size="sm" variant="outline" className="h-7 gap-1 text-xs" onClick={handleCopy}>
      {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
      {copied ? 'Copied' : 'Copy Config'}
    </Button>
  )
}

function IntegrationCard({ integration }: { integration: Integration }) {
  const icon = iconMap[integration.name] || <Globe className="h-6 w-6" />

  let configJson = ''
  try {
    configJson = integration.configJson ? JSON.stringify(JSON.parse(integration.configJson), null, 2) : ''
  } catch {
    configJson = integration.configJson ?? ''
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <Card className="h-full flex flex-col glass-card depth-shadow">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-500 dark:text-emerald-400 shrink-0">
                {icon}
              </div>
              <div>
                <CardTitle className="text-base">{integration.displayName}</CardTitle>
                <Badge
                  variant="outline"
                  className={cn('text-[10px] capitalize mt-1', statusColors[integration.status])}
                >
                  {integration.status}
                </Badge>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col gap-3">
          {integration.description && (
            <p className="text-sm text-muted-foreground">{integration.description}</p>
          )}

          {integration.baseUrl && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-muted-foreground">Base URL:</span>
              <code className="font-mono bg-muted/50 px-2 py-0.5 rounded text-xs">
                {integration.baseUrl}
              </code>
            </div>
          )}

          {configJson && (
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-muted-foreground">Configuration</span>
                <CopyButton text={configJson} />
              </div>
              <div className="rounded-lg overflow-hidden max-h-[200px] overflow-y-auto custom-scrollbar">
                <SyntaxHighlighter
                  language="json"
                  style={oneDark}
                  customStyle={{
                    margin: 0,
                    padding: '12px',
                    fontSize: '11px',
                    borderRadius: '8px',
                  }}
                >
                  {configJson}
                </SyntaxHighlighter>
              </div>
            </div>
          )}

          {integration.docsUrl && (
            <Button variant="outline" size="sm" className="w-full gap-2 mt-auto" asChild>
              <a href={integration.docsUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-3.5 w-3.5" />
                Documentation
              </a>
            </Button>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

export function IntegrationsView() {
  const { data: integrations, isLoading } = useIntegrations()

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[300px] w-full rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Integrations</h2>
        <p className="text-sm text-muted-foreground">
          Connect Kimari to your favorite tools and services.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {(integrations ?? []).map((integration) => (
          <IntegrationCard key={integration.id} integration={integration} />
        ))}
      </div>
    </div>
  )
}
