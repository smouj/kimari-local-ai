'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Download, FileJson, FileSpreadsheet, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

interface ExportDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const dataTypes = [
  { value: 'dashboard', label: 'Dashboard', description: 'Server state, profiles, and models' },
  { value: 'logs', label: 'Gateway Logs', description: 'Recent gateway log entries' },
  { value: 'benchmarks', label: 'Benchmarks', description: 'Benchmark results and scores' },
  { value: 'analytics', label: 'Analytics', description: 'Performance and usage analytics' },
]

const formatOptions = [
  { value: 'json', label: 'JSON', icon: FileJson, description: 'Structured data format' },
  { value: 'csv', label: 'CSV', icon: FileSpreadsheet, description: 'Spreadsheet-compatible format' },
]

export function ExportDialog({ open, onOpenChange }: ExportDialogProps) {
  const [dataType, setDataType] = useState('logs')
  const [format, setFormat] = useState('json')
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const filename = `kimari-${dataType}-${timestamp}.${format}`

      // Use client-side download approach
      const link = document.createElement('a')
      link.href = `/api/export?type=${dataType}&format=${format}`
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast.success('Export started', {
        description: `Downloading ${dataType} as ${format.toUpperCase()}`,
      })
      onOpenChange(false)
    } catch {
      toast.error('Export failed', { description: 'Could not generate export file' })
    } finally {
      setIsExporting(false)
    }
  }

  const handleClientSideExport = () => {
    setIsExporting(true)

    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const filename = `kimari-${dataType}-${timestamp}.${format}`

      // Trigger the server-side export endpoint
      const link = document.createElement('a')
      link.href = `/api/export?type=${dataType}&format=${format}`
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast.success('Export started', {
        description: `Downloading ${dataType} as ${format.toUpperCase()}`,
      })
      onOpenChange(false)
    } catch {
      toast.error('Export failed', { description: 'Could not generate export file' })
    } finally {
      setIsExporting(false)
    }
  }

  const selectedType = dataTypes.find((t) => t.value === dataType)
  const selectedFormat = formatOptions.find((f) => f.value === format)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[480px] glass-card border-border/60">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-primary" />
            Export Data
          </DialogTitle>
          <DialogDescription>
            Select the data type and format to export from your Kimari Gateway.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-5 py-2">
          {/* Data Type Selector */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Data Type</Label>
            <div className="grid grid-cols-2 gap-2">
              {dataTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setDataType(type.value)}
                  className={cn(
                    'flex flex-col items-start gap-0.5 rounded-lg border-2 p-3 transition-all duration-200 text-left',
                    dataType === type.value
                      ? 'border-primary bg-primary/5 shadow-sm shadow-primary/10'
                      : 'border-border/50 bg-muted/20 hover:bg-muted/40 hover:border-border/80'
                  )}
                >
                  <span className={cn(
                    'text-sm font-medium',
                    dataType === type.value ? 'text-primary' : 'text-foreground/80'
                  )}>
                    {type.label}
                  </span>
                  <span className="text-[11px] text-foreground/50 line-clamp-1">
                    {type.description}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Format Selector */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Format</Label>
            <div className="grid grid-cols-2 gap-2">
              {formatOptions.map((opt) => {
                const Icon = opt.icon
                return (
                  <button
                    key={opt.value}
                    onClick={() => setFormat(opt.value)}
                    className={cn(
                      'flex items-center gap-3 rounded-lg border-2 p-3 transition-all duration-200',
                      format === opt.value
                        ? 'border-primary bg-primary/5 shadow-sm shadow-primary/10'
                        : 'border-border/50 bg-muted/20 hover:bg-muted/40 hover:border-border/80'
                    )}
                  >
                    <Icon className={cn(
                      'h-5 w-5 shrink-0',
                      format === opt.value ? 'text-primary' : 'text-foreground/60'
                    )} />
                    <div className="flex flex-col items-start">
                      <span className={cn(
                        'text-sm font-medium',
                        format === opt.value ? 'text-primary' : 'text-foreground/80'
                      )}>
                        {opt.label}
                      </span>
                      <span className="text-[11px] text-foreground/50">{opt.description}</span>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Summary */}
          <div className="rounded-lg bg-muted/30 border border-border/50 p-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-foreground/60">Export summary</span>
            </div>
            <div className="flex items-center gap-2 mt-1.5">
              <Badge variant="outline" className="text-xs h-5 border-primary/30 text-primary">
                {selectedType?.label}
              </Badge>
              <Badge variant="outline" className="text-xs h-5 border-emerald-500/30 text-emerald-600 dark:text-emerald-400">
                {selectedFormat?.label}
              </Badge>
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" className="btn-press" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            className="btn-press gap-2 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-md shadow-primary/15"
            onClick={handleClientSideExport}
            disabled={isExporting}
          >
            {isExporting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            {isExporting ? 'Exporting...' : 'Download'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
