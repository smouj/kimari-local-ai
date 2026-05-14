'use client'

import { useState } from 'react'
import { useConfig, useUpdateConfig } from '@/hooks/use-api'
import type { GatewayConfig } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { toast } from 'sonner'
import { Settings, Save, Eye, EyeOff, Key, FileText, Hash, ToggleLeft } from 'lucide-react'
import { cn } from '@/lib/utils'

const typeIcons: Record<string, React.ReactNode> = {
  string: <FileText className="h-3 w-3" />,
  number: <Hash className="h-3 w-3" />,
  boolean: <ToggleLeft className="h-3 w-3" />,
  json: <FileText className="h-3 w-3" />,
}

function ConfigRow({ config, onSave }: { config: GatewayConfig; onSave: (key: string, value: string) => void }) {
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState(config.value)
  const [revealed, setRevealed] = useState(false)

  const handleSave = () => {
    onSave(config.key, value)
    setEditing(false)
  }

  const handleCancel = () => {
    setValue(config.value)
    setEditing(false)
  }

  return (
    <TableRow>
      <TableCell>
        <div className="flex items-center gap-2">
          {typeIcons[config.valueType] || <Settings className="h-3 w-3" />}
          <span className="font-mono text-sm font-medium">{config.key}</span>
        </div>
      </TableCell>
      <TableCell>
        {editing ? (
          <div className="flex items-center gap-2">
            <Input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="h-8 text-sm font-mono"
              type={config.isSecret && !revealed ? 'password' : 'text'}
            />
            <Button size="sm" className="h-8 gap-1" onClick={handleSave}>
              <Save className="h-3 w-3" />
            </Button>
            <Button size="sm" variant="ghost" className="h-8" onClick={handleCancel}>
              Cancel
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className={cn('font-mono text-sm', config.isSecret && !revealed && 'text-muted-foreground')}>
              {config.isSecret && !revealed ? '••••••••' : config.value}
            </span>
            {config.isSecret && (
              <Button
                size="icon"
                variant="ghost"
                className="h-6 w-6"
                onClick={() => setRevealed(!revealed)}
              >
                {revealed ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              className="h-6 text-xs"
              onClick={() => setEditing(true)}
            >
              Edit
            </Button>
          </div>
        )}
      </TableCell>
      <TableCell>
        <Badge variant="outline" className="text-[10px] font-mono">
          {config.valueType}
        </Badge>
      </TableCell>
      <TableCell>
        {config.isSecret && (
          <Badge className="text-[10px] bg-amber-500/10 text-amber-600 dark:text-amber-400 gap-1">
            <Key className="h-2.5 w-2.5" /> Secret
          </Badge>
        )}
      </TableCell>
      <TableCell className="text-xs text-muted-foreground max-w-[200px] truncate">
        {config.description ?? '-'}
      </TableCell>
    </TableRow>
  )
}

export function ConfigView() {
  const { data: configs, isLoading } = useConfig()
  const updateConfig = useUpdateConfig()

  const handleSave = async (key: string, value: string) => {
    try {
      await updateConfig.mutateAsync({ key, value })
      toast.success('Configuration updated', { description: key })
    } catch (err) {
      toast.error('Failed to update config', { description: String(err) })
    }
  }

  // Group configs by category (prefix before _)
  const grouped = (configs ?? []).reduce<Record<string, GatewayConfig[]>>((acc, config) => {
    const prefix = config.key.includes('_') ? config.key.split('_')[0] : 'general'
    if (!acc[prefix]) acc[prefix] = []
    acc[prefix].push(config)
    return acc
  }, {})

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Configuration</h2>
        <p className="text-sm text-muted-foreground">
          Manage gateway configuration settings. Secret values are masked by default.
        </p>
      </div>

      {Object.entries(grouped).map(([category, items]) => (
        <Card key={category} className="glass-card depth-shadow">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold capitalize flex items-center gap-2">
              <Settings className="h-4 w-4" />
              {category}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Key</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Flags</TableHead>
                  <TableHead>Description</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((config) => (
                  <ConfigRow key={config.id} config={config} onSave={handleSave} />
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
