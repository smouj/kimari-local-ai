'use client'

import { useState } from 'react'
import { useModels, usePullModel } from '@/hooks/use-api'
import type { ModelEntry } from '@/hooks/use-api'
import { Card, CardContent } from '@/components/ui/card'
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
import { Download, Box, Check, Search, PackageOpen } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ModelDetailsDrawer } from './model-details-drawer'

const categoryColors: Record<string, string> = {
  test: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  recommended: 'bg-primary/10 text-primary',
  community: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  official: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
}

export function ModelsView() {
  const { data: models, isLoading } = useModels()
  const pullModel = usePullModel()
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedModel, setSelectedModel] = useState<ModelEntry | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredModels = (models ?? []).filter((m) => {
    const matchesCategory = selectedCategory === 'all' || m.category === selectedCategory
    const matchesSearch = searchQuery === '' ||
      m.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.filename.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const handlePull = async (modelName: string) => {
    try {
      await pullModel.mutateAsync(modelName)
      toast.success('Model downloaded', { description: modelName })
    } catch (err) {
      toast.error('Failed to download model', { description: String(err) })
    }
  }

  const handleRowClick = (model: ModelEntry) => {
    setSelectedModel(model)
    setDrawerOpen(true)
  }

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-10 w-64" />
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      </div>
    )
  }

  const categories = ['all', ...new Set((models ?? []).map((m) => m.category))]

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">Models</h2>
          <p className="text-sm text-muted-foreground">
            Manage downloaded and available AI models.
          </p>
        </div>
      </div>

      {/* Search + Category Filters */}
      <div className="flex flex-col gap-3">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search models by name or filename..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-9"
          />
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {categories.map((cat) => (
            <Button
              key={cat}
              size="sm"
              variant={selectedCategory === cat ? 'default' : 'outline'}
              className="h-7 text-xs capitalize"
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </Button>
          ))}
        </div>
      </div>

      <Card className="glass-card depth-shadow">
        <CardContent className="p-0">
          {filteredModels.length === 0 ? (
            <div className="py-16 flex flex-col items-center justify-center text-muted-foreground">
              <PackageOpen className="h-10 w-10 mb-3 opacity-40" />
              <p className="text-sm font-medium">No models found</p>
              <p className="text-xs mt-1">
                {searchQuery
                  ? `No models matching "${searchQuery}". Try a different search term.`
                  : 'No models in this category. Try selecting a different filter.'}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[250px] uppercase tracking-wider text-xs font-semibold text-muted-foreground">Model</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Size</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Quantization</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">VRAM</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Category</TableHead>
                  <TableHead className="uppercase tracking-wider text-xs font-semibold text-muted-foreground">Status</TableHead>
                  <TableHead className="text-right uppercase tracking-wider text-xs font-semibold text-muted-foreground">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredModels.map((model) => (
                  <TableRow
                    key={model.id}
                    className="cursor-pointer hover:bg-muted/50 hover:border-l-2 hover:border-l-primary transition-colors border-l-2 border-l-transparent"
                    onClick={() => handleRowClick(model)}
                  >
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Box className="h-4 w-4 text-primary shrink-0" />
                        <div>
                          <p className="font-medium text-sm">{model.displayName}</p>
                          <p className="text-[11px] text-muted-foreground font-mono">{model.filename}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{model.size ?? '-'}</span>
                      <span className="text-xs text-muted-foreground ml-1">
                        {model.fileSizeMb ? `(${Math.round(model.fileSizeMb)} MB)` : ''}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="font-mono text-[11px]">
                        {model.quantization}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{model.vramRequired ?? '-'}</span>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="secondary"
                        className={cn('text-[10px] capitalize', categoryColors[model.category])}
                      >
                        {model.category}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {model.downloaded ? (
                        <Badge className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1">
                          <Check className="h-3 w-3" /> Downloaded
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-muted-foreground">
                          Not downloaded
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      {!model.downloaded && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-7 text-xs gap-1"
                          onClick={(e) => {
                            e.stopPropagation()
                            handlePull(model.name)
                          }}
                          disabled={pullModel.isPending}
                        >
                          <Download className="h-3 w-3" />
                          Pull
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Model Details Drawer */}
      <ModelDetailsDrawer
        model={selectedModel}
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
      />
    </div>
  )
}
