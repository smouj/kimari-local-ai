'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Sparkles,
  Send,
  Square,
  MessageSquare,
  Bot,
  User,
  Zap,
  Cpu,
  Settings2,
  Server,
  Trash2,
  AlertTriangle,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useServerStatus, useModels } from '@/hooks/use-api'
import { useKimariStore } from '@/lib/store'
import { toast } from 'sonner'
import { MarkdownRenderer } from './markdown-renderer'

// Types
interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  model?: string
}

const STORAGE_KEY = 'kimari-chat-history'
const MAX_HISTORY = 100

function loadMessages(): ChatMessage[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function saveMessages(messages: ChatMessage[]) {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_HISTORY)))
  } catch {
    // localStorage full or unavailable
  }
}

function clearMessages() {
  if (typeof window === 'undefined') return
  localStorage.removeItem(STORAGE_KEY)
}

const suggestedPrompts = [
  {
    icon: Zap,
    title: 'What is Kimari Gateway?',
    description: 'Learn about the local AI gateway and its features',
    prompt: 'What is Kimari Gateway?',
    color: 'text-emerald-500',
    bg: 'bg-emerald-500/10',
  },
  {
    icon: Cpu,
    title: 'Explain GPU quantization',
    description: 'Understand Q4_K_M, Q5_K_M, and other formats',
    prompt: 'Explain GPU quantization',
    color: 'text-cyan-500',
    bg: 'bg-cyan-500/10',
  },
  {
    icon: Settings2,
    title: 'How do I optimize VRAM usage?',
    description: 'Tips for fitting models in limited GPU memory',
    prompt: 'How do I optimize VRAM usage?',
    color: 'text-amber-500',
    bg: 'bg-amber-500/10',
  },
  {
    icon: MessageSquare,
    title: 'What models work best for coding?',
    description: 'Recommended local models for code generation',
    prompt: 'What models work best for coding?',
    color: 'text-primary',
    bg: 'bg-primary/10',
  },
]

// Blinking cursor component for streaming text
function StreamingCursor() {
  return (
    <span className="inline-block w-[6px] h-[18px] ml-[2px] align-text-bottom bg-primary animate-pulse rounded-sm" />
  )
}

// Typing indicator dots
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3">
      <div className="flex items-center gap-1">
        <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce [animation-delay:0ms]" />
        <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce [animation-delay:150ms]" />
        <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce [animation-delay:300ms]" />
      </div>
      <span className="text-xs text-muted-foreground ml-2">Thinking...</span>
    </div>
  )
}

export function ChatView() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [selectedModel, setSelectedModel] = useState('kimari-local')
  const [showSettings, setShowSettings] = useState(false)
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(512)

  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const { data: serverStatus } = useServerStatus()
  const { data: models } = useModels()
  const { setActiveView } = useKimariStore()

  const isServerRunning = serverStatus?.status === 'running'
  const downloadedModels = models?.filter((m) => m.downloaded) ?? []

  // Load messages on mount
  useEffect(() => {
    queueMicrotask(() => setMessages(loadMessages()))
  }, [])

  // Auto-scroll to bottom on new messages or streaming content
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, streamingContent])

  // Save messages whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      saveMessages(messages)
    }
  }, [messages])

  const handleSend = useCallback(async (customPrompt?: string) => {
    const content = customPrompt || input.trim()
    if (!content || isStreaming) return

    if (!isServerRunning) {
      toast.error('Server must be running to chat. Start the server first.')
      return
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}-user`,
      role: 'user',
      content,
      timestamp: Date.now(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsStreaming(true)
    setStreamingContent('')

    // Prepare messages for API
    const apiMessages = [...messages, userMessage].map((m) => ({
      role: m.role,
      content: m.content,
    }))

    // Create abort controller
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: apiMessages,
          model: selectedModel,
          temperature,
          maxTokens,
        }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response stream')

      const decoder = new TextDecoder()
      let fullContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.done) {
                // Stream complete
              } else if (data.token) {
                fullContent += data.token
                setStreamingContent(fullContent)
              }
            } catch {
              // Ignore parse errors for incomplete chunks
            }
          }
        }
      }

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: fullContent,
        timestamp: Date.now(),
        model: selectedModel,
      }

      setMessages((prev) => [...prev, assistantMessage])
      setStreamingContent('')
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // User cancelled - save partial content as message
        if (streamingContent) {
          const partialMessage: ChatMessage = {
            id: `msg-${Date.now()}-assistant`,
            role: 'assistant',
            content: streamingContent + '...(stopped)',
            timestamp: Date.now(),
            model: selectedModel,
          }
          setMessages((prev) => [...prev, partialMessage])
        }
        setStreamingContent('')
        toast.info('Generation stopped')
      } else {
        toast.error('Failed to get response from the model')
      }
    } finally {
      setIsStreaming(false)
      abortControllerRef.current = null
    }
  }, [input, isStreaming, isServerRunning, messages, selectedModel, temperature, maxTokens, streamingContent])

  const handleStop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }, [])

  const handleClear = useCallback(() => {
    setMessages([])
    clearMessages()
    toast.success('Chat history cleared')
  }, [])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend]
  )

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="h-full flex flex-col p-0">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-primary/10 text-primary">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold">AI Chat Console</h2>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div className={cn(
                'h-1.5 w-1.5 rounded-full',
                isServerRunning ? 'bg-emerald-500' : 'bg-muted-foreground/40'
              )} />
              <p className={cn(
                'text-[11px] font-medium',
                isServerRunning ? 'text-emerald-600 dark:text-emerald-400' : 'text-muted-foreground'
              )}>
                {isServerRunning ? `Connected * ${serverStatus?.model || 'Model loaded'}` : 'Server Offline'}
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Model Selector */}
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-[180px] h-8 text-xs border-border/60 hover:border-primary/30 transition-colors bg-background/50">
              <SelectValue placeholder="Select model" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="kimari-local">Kimari Local (Default)</SelectItem>
              {downloadedModels.map((m) => (
                <SelectItem key={m.id} value={m.name}>
                  {m.displayName} ({m.quantization})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Server Status Badge - destructive/alert style */}
          {!isServerRunning && (
            <Badge variant="outline" className="border-red-500/40 text-red-600 dark:text-red-400 bg-red-500/5 text-[11px] font-medium gap-1.5 px-2.5">
              <AlertTriangle className="h-3 w-3" />
              Server Required
            </Badge>
          )}

          {/* Settings Toggle */}
          <Button
            variant="ghost"
            size="icon"
            className={cn('h-8 w-8', showSettings && 'bg-accent')}
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings2 className="h-4 w-4" />
          </Button>

          {/* Clear Chat */}
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-destructive"
              onClick={handleClear}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Settings Panel */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden border-b border-border/50"
          >
            <div className="flex items-center gap-6 px-6 py-3 bg-muted/30">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-muted-foreground">Temperature:</span>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-24 h-1 accent-primary"
                />
                <span className="text-xs font-mono w-8 text-foreground">{temperature}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-muted-foreground">Max Tokens:</span>
                <Select value={String(maxTokens)} onValueChange={(v) => setMaxTokens(Number(v))}>
                  <SelectTrigger className="w-[100px] h-7 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="256">256</SelectItem>
                    <SelectItem value="512">512</SelectItem>
                    <SelectItem value="1024">1024</SelectItem>
                    <SelectItem value="2048">2048</SelectItem>
                    <SelectItem value="4096">4096</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Message Area */}
      <div className="flex-1 overflow-hidden relative">
        <ScrollArea className="h-full">
          <div ref={scrollRef} className="px-6 py-4 space-y-4 min-h-full">
            {/* Empty State */}
            {messages.length === 0 && !isStreaming && (
              <div className="flex flex-col items-center justify-center min-h-[50vh] gap-8 relative">
                {/* Subtle gradient background */}
                <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-primary/[0.03] via-transparent to-transparent rounded-xl" />

                <div className="flex flex-col items-center gap-5 relative">
                  <div className="flex items-center justify-center h-20 w-20 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20 text-primary shadow-lg shadow-primary/10">
                    <Sparkles className="h-10 w-10" />
                  </div>
                  <div className="text-center">
                    <h1 className="text-2xl font-bold tracking-tight text-foreground">Start a Conversation</h1>
                    <p className="text-sm text-muted-foreground mt-2 max-w-md mx-auto leading-relaxed">
                      Chat with your local AI model through the Kimari Gateway.
                      {isServerRunning
                        ? ' Your server is running and ready to respond.'
                        : ' Start the server first to connect to your local AI model.'}
                    </p>
                  </div>
                  {!isServerRunning && (
                    <Button
                      className="gap-2 btn-press bg-gradient-to-r from-emerald-600/90 to-emerald-500/90 hover:from-emerald-600 hover:to-emerald-500 text-white shadow-lg shadow-emerald-500/20 mt-1"
                      onClick={() => setActiveView('server')}
                    >
                      <Server className="h-4 w-4" />
                      Start Server
                    </Button>
                  )}
                </div>

                {/* Suggested Prompts */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl relative">
                  {suggestedPrompts.map((prompt, idx) => {
                    const IconComp = prompt.icon
                    return (
                      <motion.button
                        key={idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.08 }}
                        onClick={() => isServerRunning && handleSend(prompt.prompt)}
                        disabled={!isServerRunning}
                        className={cn(
                          'flex items-start gap-3 p-4 rounded-xl border text-left transition-all',
                          'depth-shadow',
                          isServerRunning
                            ? 'border-border/50 bg-card hover:border-primary/40 hover:bg-accent/20 cursor-pointer card-shine hover-lift'
                            : 'border-border/30 bg-card/50 opacity-50 cursor-not-allowed'
                        )}
                      >
                        <div className={cn('flex items-center justify-center h-9 w-9 rounded-lg shrink-0 mt-0.5', prompt.bg)}>
                          <IconComp className={cn('h-4 w-4', prompt.color)} />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-semibold leading-tight text-foreground">{prompt.title}</p>
                          <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{prompt.description}</p>
                        </div>
                      </motion.button>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Offline State - prominent warning banner */}
            {messages.length > 0 && !isServerRunning && !isStreaming && (
              <div className="flex items-center gap-3 py-3 px-4 rounded-xl bg-red-500/5 border border-red-500/20 mb-4 depth-shadow">
                <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-red-500/10 shrink-0">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-red-600 dark:text-red-400">Server Offline</p>
                  <p className="text-xs text-red-600/70 dark:text-red-400/70">Start the server to continue chatting.</p>
                </div>
                <Button
                  size="sm"
                  className="h-8 text-xs gap-1.5 btn-press bg-gradient-to-r from-emerald-600/90 to-emerald-500/90 hover:from-emerald-600 hover:to-emerald-500 text-white shrink-0"
                  onClick={() => setActiveView('server')}
                >
                  <Server className="h-3 w-3" />
                  Start Server
                </Button>
              </div>
            )}

            {/* Messages */}
            {messages.map((msg, idx) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: idx === messages.length - 1 ? 0.05 : 0 }}
                className={cn(
                  'flex gap-3',
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {/* Assistant Avatar */}
                {msg.role === 'assistant' && (
                  <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-primary/10 text-primary shrink-0 mt-1">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                {/* Message Bubble */}
                <div
                  className={cn(
                    'max-w-[75%] rounded-2xl px-4 py-3',
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-primary to-primary/80 text-primary-foreground depth-shadow'
                      : msg.role === 'system'
                      ? 'bg-muted/50 text-muted-foreground text-sm italic text-center max-w-full mx-auto glass-card'
                      : 'glass-card depth-shadow border-l-2 border-l-primary/40'
                  )}
                >
                  {msg.role === 'assistant' ? (
                    <MarkdownRenderer content={msg.content} />
                  ) : (
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    <span
                      className={cn(
                        'text-[10px]',
                        msg.role === 'user'
                          ? 'text-primary-foreground/60'
                          : 'text-muted-foreground'
                      )}
                    >
                      {formatTime(msg.timestamp)}
                    </span>
                    {msg.model && msg.role === 'assistant' && (
                      <span className="text-[10px] text-muted-foreground/60">
                        * {msg.model}
                      </span>
                    )}
                  </div>
                </div>

                {/* User Avatar */}
                {msg.role === 'user' && (
                  <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-primary text-primary-foreground shrink-0 mt-1">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </motion.div>
            ))}

            {/* Streaming Content */}
            {isStreaming && streamingContent && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3 justify-start"
              >
                <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-primary/10 text-primary shrink-0 mt-1">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="max-w-[75%] rounded-2xl px-4 py-3 glass-card depth-shadow border-l-2 border-l-primary/40">
                  <MarkdownRenderer content={streamingContent} />
                  <StreamingCursor />
                </div>
              </motion.div>
            )}

            {/* Typing Indicator (before first token) */}
            {isStreaming && !streamingContent && <TypingIndicator />}

            {/* Bottom padding */}
            <div className="h-4" />
          </div>
        </ScrollArea>
      </div>

      {/* Input Area - stronger visual separation */}
      <div className="border-t border-border bg-background/90 backdrop-blur-xl px-6 py-4 relative">
        {/* Separator line accent */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent" />
        <div className="flex items-end gap-3 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                isServerRunning
                  ? 'Type a message... (Ctrl+Enter to send)'
                  : 'Start the server to chat...'
              }
              disabled={!isServerRunning || isStreaming}
              rows={1}
              className={cn(
                'resize-none min-h-[44px] max-h-[160px] pr-12 text-sm',
                'focus-visible:ring-primary/30',
                'placeholder:text-muted-foreground/60'
              )}
              style={{
                height: 'auto',
                overflow: 'hidden',
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement
                target.style.height = 'auto'
                target.style.height = `${Math.min(target.scrollHeight, 160)}px`
              }}
            />
            <div className="absolute right-2 bottom-2 flex items-center gap-1">
              <span className="text-[10px] text-muted-foreground/60 font-mono">
                {input.length > 0 ? `${input.length}` : ''}
              </span>
            </div>
          </div>

          {/* Send / Stop Button */}
          {isStreaming ? (
            <Button
              variant="destructive"
              size="icon"
              className="h-11 w-11 shrink-0 btn-press rounded-xl"
              onClick={handleStop}
            >
              <Square className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              size="icon"
              className="h-11 w-11 shrink-0 btn-press rounded-xl bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-md shadow-primary/15"
              disabled={!input.trim() || !isServerRunning}
              onClick={() => handleSend()}
            >
              <Send className="h-4 w-4 ml-0.5" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
