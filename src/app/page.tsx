'use client'

import { useState, useEffect, useRef, useCallback, useMemo, type MouseEvent as ReactMouseEvent } from 'react'
import Image from 'next/image'
import { motion, useInView, AnimatePresence, useScroll, useTransform } from 'framer-motion'
import {
  Terminal, Cpu, Activity, Shield, Zap, Monitor, Download,
  ChevronRight, ExternalLink, CheckCircle2, XCircle, Lock, AlertTriangle,
  Github, Globe, FileCode, BookOpen, Server, BarChart3, Wrench,
  Play, Copy, Check, Moon, Sun, Menu, X, Database,
  Eye, Brain, Layers, Rocket, Gauge, Search, Send, RotateCcw,
  ArrowUp, MessageCircle, Bot, Trash2, AlertCircle, HardDrive, MemoryStick,
  Heart, Twitter, Linkedin, History, Code2, GitBranch, Clock, ZapOff, TerminalSquare, Sparkles, CircleDot,
  Keyboard, Wifi, Settings, Palette, Command, ArrowDown, Timer, Languages, FileText, Code,
  Lightbulb, Share2, Link2, Tag, Milestone, GitCommitHorizontal,
  Volume2, VolumeX, CheckSquare, Square, ArrowRight, AlertOctagon, GaugeCircle, CpuCog, MemoryStick as MemoryIcon,
  Bell, Cookie, ChevronLeft, Award, Wand2, DollarSign, Plus
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area, CartesianGrid, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

// Deterministic number formatting to avoid hydration mismatch
function fmtNum(n: number): string {
  return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// ─── Data ────────────────────────────────────────────────────────────────────

const statusItems = [
  { area: 'Framework / CLI', status: 'usable', label: 'Usable alpha' },
  { area: 'Local GGUF runtime', status: 'usable', label: 'Working' },
  { area: 'OpenAI-compatible endpoint', status: 'usable', label: 'Working' },
  { area: 'GTX 1060 validation', status: 'usable', label: 'Validated' },
  { area: 'Gateway Dashboard', status: 'preview', label: 'Local preview' },
  { area: 'Open WebUI / Continue configs', status: 'usable', label: 'Documented' },
  { area: 'Kimari SFT/private adapter', status: 'private', label: 'Private only' },
  { area: 'Public Kimari-4B weights', status: 'blocked', label: 'Not released' },
  { area: 'Public GGUF Kimari model', status: 'blocked', label: 'Not released' },
  { area: 'Release gate', status: 'blocked', label: 'BLOCKED' },
]

const cliCommands = [
  { category: 'Diagnostics', icon: Activity, commands: [
    { cmd: 'kimari doctor --deep', desc: '14 deep diagnostic checks', tag: 'essential' },
    { cmd: 'kimari info', desc: 'Installation info & version', tag: '' },
    { cmd: 'kimari status', desc: 'Server status', tag: '' },
  ]},
  { category: 'Server', icon: Server, commands: [
    { cmd: 'kimari start', desc: 'Start local API server', tag: 'essential' },
    { cmd: 'kimari stop', desc: 'Stop running server', tag: '' },
    { cmd: 'kimari start --daemon', desc: 'Start in background', tag: '' },
  ]},
  { category: 'Models', icon: Database, commands: [
    { cmd: 'kimari pull test', desc: 'Download test model (TinyLlama)', tag: 'essential' },
    { cmd: 'kimari pull recommended', desc: 'Download Qwen3-4B', tag: '' },
    { cmd: 'kimari models hash <path>', desc: 'Verify SHA256 integrity', tag: '' },
  ]},
  { category: 'Gateway', icon: Monitor, commands: [
    { cmd: 'kimari gateway setup', desc: 'Install dashboard deps', tag: 'essential' },
    { cmd: 'kimari gateway start --open', desc: 'Open local dashboard', tag: '' },
    { cmd: 'kimari gateway status --json', desc: 'Dashboard + gate state', tag: '' },
  ]},
  { category: 'Integrations', icon: Layers, commands: [
    { cmd: 'kimari integrations generate --target openwebui', desc: 'Open WebUI config', tag: '' },
    { cmd: 'kimari integrations generate --target continue', desc: 'Continue.dev config', tag: '' },
    { cmd: 'kimari integrations generate --target openclaw', desc: 'OpenClaw config', tag: '' },
  ]},
  { category: 'Performance', icon: Gauge, commands: [
    { cmd: 'kimari optimize', desc: 'Optimal settings per GPU', tag: '' },
    { cmd: 'kimari perf --matrix', desc: 'All modes compared', tag: '' },
    { cmd: 'kimari benchmark --dry-run', desc: 'Benchmark plan preview', tag: '' },
  ]},
]

const benchmarks = [
  { metric: 'Prompt processing', cuda: 228, cpu: 77, unit: 'tok/s' },
  { metric: 'Token generation', cuda: 73, cpu: 33, unit: 'tok/s' },
]

const gpuProfiles = [
  { name: 'test', gpu: 'Any 6 GB+', vram: '6 GB', quant: 'Q4_K_M', ctx: 4096, status: 'default' },
  { name: 'gtx1060', gpu: 'GTX 1060', vram: '6 GB', quant: 'Q4_K_M', ctx: 8192, status: 'requires-k4b' },
  { name: 'gtx1080', gpu: 'GTX 1080', vram: '8 GB', quant: 'Q5_K_M', ctx: 16384, status: 'requires-k4b' },
  { name: 'turbo', gpu: '6 GB+', vram: '6 GB', quant: 'IQ4_XS', ctx: 8192, status: 'requires-k4b' },
]

const docCategories = [
  { title: 'Getting Started', icon: Rocket, links: [
    { name: 'Install Guide', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/INSTALL_ONE_COMMAND.md' },
    { name: 'Console Guide', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/KIMARI_CONSOLE.md' },
    { name: 'CLI Reference', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/CLI_REFERENCE.md' },
    { name: 'Gateway Dashboard', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/GATEWAY_DASHBOARD.md' },
  ]},
  { title: 'Integrations', icon: Layers, links: [
    { name: 'Open WebUI Setup', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/OPENWEBUI_LOCAL_SETUP.md' },
    { name: 'OpenClaw Setup', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/OPENCLAW_LOCAL_SETUP.md' },
    { name: 'Continue.dev Setup', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/CONTINUE_LOCAL_SETUP.md' },
    { name: 'Local Endpoint Test', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/LOCAL_OPENAI_ENDPOINT_TEST.md' },
  ]},
  { title: 'Model & Training Policy', icon: Shield, links: [
    { name: 'Release Gate', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/KIMARI4B_RELEASE_GATE.md' },
    { name: 'Open-License Policy', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/KIMARI_OPEN_LICENSE_POLICY.md' },
    { name: 'Dataset Policy', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/KIMARI_SFT_V1_DATASET.md' },
    { name: 'Training History', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/KIMARI4B_RUN_HISTORY.md' },
  ]},
  { title: 'Advanced', icon: Wrench, links: [
    { name: 'Performance Tuning', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/PERFORMANCE_TUNING_PLAN.md' },
    { name: 'Model Hashing', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/MODEL_HASHING.md' },
    { name: 'Architecture', href: 'https://github.com/smouj/kimari-local-ai/blob/main/docs/00-03_architecture.md' },
    { name: 'Security Policy', href: 'https://github.com/smouj/kimari-local-ai/blob/main/SECURITY.md' },
  ]},
]

const safetyItems = [
  'Localhost-only defaults',
  'No public bind unless explicitly requested',
  'No token storage in dashboard',
  'No public model upload',
  'No public GGUF',
  'No benchmark claims without reproducible validation',
  'No automatic gate transitions',
]

const roadmapItems = [
  { stage: 'Current', goal: 'Local runtime + Gateway Dashboard polish', active: true },
  { stage: 'Next', goal: 'Private adapter runtime preview', active: false },
  { stage: 'Next', goal: 'Agent Gateway tools & web-search dry-run', active: false },
  { stage: 'Next', goal: 'Manual review of private outputs', active: false },
  { stage: 'Later', goal: 'Private GGUF export', active: false },
  { stage: 'Later', goal: 'GTX 1060 / GTX 1080 validation', active: false },
  { stage: 'Later', goal: 'Public preview decision', active: false },
]

// Terminal simulator responses
const terminalResponses: Record<string, string> = {
  'kimari doctor --deep': `\u256d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e
\u2502 Kimari Doctor \u2014 Deep Diagnostics              \u2502
\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f

  [PASS]  Python version          3.10+ \u2705
  [PASS]  Kimari version          0.1.82-alpha
  [PASS]  Config paths            ~/.config/kimari/
  [PASS]  Config valid            \u2705
  [PASS]  Packaged defaults       Found (6 profiles)
  [PASS]  llama-server binary     /usr/local/bin/llama-server
  [PASS]  CUDA available          CUDA 12.1
  [PASS]  NVIDIA GPU              GeForce GTX 1060 6GB
  [PASS]  Default profile         test
  [PASS]  Secret scanner          Clean
  [PASS]  Benchmark prompts       35 prompts
  [PASS]  Gateway module          Installed
  [PASS]  Integration docs        4 guides
  [WARN]  Preview gate            BLOCKED

  All checks passed (1 warning).`,
  'kimari start': `\u2823 Starting Kimari server...
  Profile:     test
  Model:       tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
  Host:        127.0.0.1
  Port:        11435
  Backend:     llama-server (CUDA)

  \u2705 Server running at http://127.0.0.1:11435/v1`,
  'kimari status': `  \u256d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e
  \u2502 Kimari Server Status               \u2502
  \u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f

  Server:    \u25cf Running
  Profile:   test
  Model:     tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
  Endpoint:  http://127.0.0.1:11435/v1
  GPU:       NVIDIA GeForce GTX 1060 6GB
  VRAM:      1221 MiB / 6144 MiB (20%)
  Uptime:    4m 23s`,
  'kimari pull test': `  \u2823 Downloading test model...
  Model:    tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
  Size:     ~670 MB
  Source:   huggingface.co

  \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588 100%

  \u2705 Download complete
  SHA256: verified`,
  'kimari gateway start --open': `  \u2823 Starting Gateway Dashboard...
  Host:      127.0.0.1
  Port:      3105
  Gate:      BLOCKED

  \u2705 Dashboard running
  Opening http://127.0.0.1:3105 ...`,
  'help': `Available commands to try:
  \u2022 kimari doctor --deep
  \u2022 kimari start
  \u2022 kimari status
  \u2022 kimari pull test
  \u2022 kimari stop
  \u2022 kimari models
  \u2022 kimari optimize
  \u2022 kimari gateway start --open

Type a command and press Enter.`,
  'kimari stop': `  \u23f3 Stopping Kimari server...
  Profile:     test
  Model:       tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

  \u2705 Server stopped successfully.`,
  'kimari models': `  Available models:
  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  Name                     Size      Profile
  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  tinyllama-1.1b-Q4_K_M   670 MB    test (default)
  qwen3-4b-Q5_K_M         2.8 GB    recommended

  Use 'kimari pull <profile>' to download a model.`,
  'kimari optimize': `  \u256d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e
  \u2502 Kimari Optimize \u2014 GPU Settings          \u2502
  \u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f

  GPU:     NVIDIA GeForce GTX 1060 6GB
  VRAM:    6144 MiB

  Recommended settings:
    Context length:  8192
    Batch size:      512
    Threads:         4
    Quantization:    Q4_K_M

  \u2705 Settings applied to profile 'gtx1060'`,
}

// ─── New Data: Comparison Table ─────────────────────────────────────────────

const comparisonData = [
  { feature: 'Old GPU focus', kimari: true, ollama: false, lmstudio: false, tgwui: false },
  { feature: 'CLI-first', kimari: true, ollama: true, lmstudio: false, tgwui: true },
  { feature: 'OpenAI-compatible', kimari: true, ollama: true, lmstudio: true, tgwui: true },
  { feature: 'Gateway Dashboard', kimari: true, ollama: false, lmstudio: true, tgwui: false },
  { feature: 'GPU Profiles', kimari: true, ollama: false, lmstudio: false, tgwui: false },
  { feature: 'Model Hashing', kimari: true, ollama: false, lmstudio: false, tgwui: false },
  { feature: 'Local-only default', kimari: true, ollama: true, lmstudio: true, tgwui: true },
  { feature: 'Open Source', kimari: true, ollama: true, lmstudio: false, tgwui: true },
]

// ─── New Data: System Requirements ──────────────────────────────────────────

const sysRequirements = [
  { name: 'Python 3.10+', status: 'pass' as const, required: true },
  { name: 'NVIDIA GPU (6GB+ VRAM)', status: 'pass' as const, required: true },
  { name: 'CUDA 12.1+', status: 'pass' as const, required: true },
  { name: '4GB free disk space', status: 'pass' as const, required: true },
  { name: 'WSL2 / Linux', status: 'recommended' as const, required: false },
  { name: 'llama.cpp binary', status: 'pass' as const, required: true },
]

// ─── New Data: FAQ ──────────────────────────────────────────────────────────

const faqItems = [
  { q: 'What is Kimari?', a: 'Kimari is a framework for running local LLMs on older NVIDIA GPUs like the GTX 1060 and GTX 1080. It provides a CLI-first workflow, OpenAI-compatible endpoint, Gateway Dashboard, and GPU-specific profiles for optimal performance.' },
  { q: 'Is Kimari-4B available?', a: 'No. Kimari-4B is not released. The release gate is BLOCKED. No public weights, adapters, or GGUF files are available. We will not promise a release date until quality and safety standards are met.' },
  { q: 'Do I need an internet connection?', a: 'Only for initial setup and model download. Once models are downloaded, the runtime is fully local with zero cloud dependency. No API keys, no subscriptions, no telemetry.' },
  { q: 'Which GPUs are supported?', a: 'GTX 1060 6GB, GTX 1080 8GB, and any newer NVIDIA GPU with 6GB+ VRAM. The framework includes pre-tuned profiles for specific hardware to get the best performance.' },
  { q: 'Is it free?', a: 'Yes. Kimari is MIT licensed and fully open-source. No premium tiers, no usage limits, no vendor lock-in.' },
  { q: 'How is this different from Ollama?', a: 'Kimari focuses specifically on older GPU support with pre-tuned profiles, includes an integrated Gateway Dashboard for monitoring, and provides Kimari-specific GPU profiles. Ollama is a broader tool but doesn\'t optimize for legacy hardware.' },
  { q: 'Can I use Open WebUI?', a: 'Yes! Kimari provides an OpenAI-compatible endpoint that works directly with Open WebUI, Continue.dev, OpenClaw, and any tool that supports the OpenAI API format. Use kimari integrations generate --target openwebui to get started.' },
]

// ─── New Data: Gateway Chart Data ───────────────────────────────────────────

const gatewayChartData = [
  { day: 'Mon', requests: 142 },
  { day: 'Tue', requests: 235 },
  { day: 'Wed', requests: 198 },
  { day: 'Thu', requests: 312 },
  { day: 'Fri', requests: 287 },
  { day: 'Sat', requests: 156 },
  { day: 'Sun', requests: 89 },
]

// ─── New Data: Chat Suggestions ─────────────────────────────────────────────

const chatSuggestions = [
  'What is Kimari?',
  'Is Kimari-4B available?',
  'How do I install it?',
  'What GPUs are supported?',
]

// ─── New Data: Version Timeline ──────────────────────────────────────────────

const versionTimeline = [
  { version: 'v0.1.0', date: 'Jan 2026', title: 'Initial CLI framework', description: 'First working CLI with doctor, start, pull commands', type: 'release' as const },
  { version: 'v0.1.4', date: 'Feb 2026', title: 'Gateway Dashboard preview', description: 'Local web dashboard for monitoring runtime', type: 'feature' as const },
  { version: 'v0.1.6', date: 'Mar 2026', title: 'GTX 1060 validated', description: '228 tok/s prompt processing confirmed on real hardware', type: 'milestone' as const },
  { version: 'v0.1.7', date: 'Mar 2026', title: 'Integration guides', description: 'Open WebUI, Continue.dev, OpenClaw configurations', type: 'feature' as const },
  { version: 'v0.1.8', date: 'Apr 2026', title: 'GPU profiles & hashing', description: 'Pre-tuned profiles and SHA256 model verification', type: 'feature' as const },
  { version: 'v0.1.82', date: 'May 2026', title: 'Current alpha', description: 'Gate BLOCKED — quality and safety review in progress', type: 'current' as const },
]

// ─── New Data: GPU Benchmark Extended ────────────────────────────────────────

const gpuBenchmarkData = [
  { gpu: 'GTX 1060 6GB', promptSpeed: 228, genSpeed: 73, vram: 6, quant: 'Q4_K_M', model: 'TinyLlama 1.1B', color: '#3b82f6' },
  { gpu: 'GTX 1080 8GB', promptSpeed: 310, genSpeed: 98, vram: 8, quant: 'Q5_K_M', model: 'TinyLlama 1.1B', color: '#2563eb' },
  { gpu: 'RTX 3060 12GB', promptSpeed: 520, genSpeed: 145, vram: 12, quant: 'Q5_K_M', model: 'Qwen3-4B', color: '#60a5fa' },
  { gpu: 'RTX 4070 12GB', promptSpeed: 890, genSpeed: 230, vram: 12, quant: 'Q6_K', model: 'Qwen3-4B', color: '#93c5fd' },
]

// ─── New Data: Code Snippets ─────────────────────────────────────────────────

const codeSnippets = {
  python: `from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:11435/v1",
    api_key="not-needed"  # Local only
)

response = client.chat.completions.create(
    model="tinyllama-1.1b-chat-v1.0.Q4_K_M",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)`,
  curl: `curl http://127.0.0.1:11435/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'`,
  javascript: `const response = await fetch(
  "http://127.0.0.1:11435/v1/chat/completions",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "tinyllama-1.1b-chat-v1.0.Q4_K_M",
      messages: [{ role: "user", content: "Hello!" }],
    }),
  }
);
const data = await response.json();`,
}

// ─── New Data: Health Check Response ─────────────────────────────────────────

const healthCheckResponse = `{
  "status": "healthy",
  "endpoint": "http://127.0.0.1:11435/v1",
  "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M",
  "gpu": "NVIDIA GTX 1060 6GB",
  "latency_ms": 42,
  "gate": "BLOCKED"
}`

// ─── New Data: VRAM Calculator ────────────────────────────────────────────────

const vramCalculatorGPUs = [
  { id: 'gtx1060', name: 'GTX 1060 6GB', vram: 6 },
  { id: 'gtx1080', name: 'GTX 1080 8GB', vram: 8 },
  { id: 'rtx3060', name: 'RTX 3060 12GB', vram: 12 },
  { id: 'rtx4070', name: 'RTX 4070 12GB', vram: 12 },
]

const vramCalculatorModels = [
  { id: 'tinyllama', name: 'TinyLlama 1.1B', quant: 'Q4_K_M', vramRequired: 1.2, contextLength: 4096 },
  { id: 'qwen3-4b', name: 'Qwen3-4B', quant: 'Q5_K_M', vramRequired: 3.8, contextLength: 8192 },
  { id: 'kimari-4b', name: 'Kimari-4B preview', quant: 'Q4_K_M', vramRequired: 3.2, contextLength: 8192 },
]

// ─── New Data: Keyboard Shortcuts ────────────────────────────────────────────

const keyboardShortcuts = [
  { keys: 'Ctrl+K', description: 'Open CLI search', section: 'cli' },
  { keys: 'Ctrl+/', description: 'Show shortcuts', section: '' },
  { keys: 'T', description: 'Scroll to Terminal', section: 'terminal' },
  { keys: 'C', description: 'Scroll to Chat', section: 'chat' },
  { keys: 'B', description: 'Scroll to Benchmarks', section: 'benchmarks' },
  { keys: 'D', description: 'Scroll to Docs', section: 'docs' },
]

// ─── New Data: Install Command Options ────────────────────────────────────────

const installOSOptions = [
  { id: 'linux', label: 'Linux', flag: '' },
  { id: 'wsl2', label: 'WSL2', flag: '--wsl2' },
  { id: 'macos', label: 'macOS', flag: '--macos' },
]

const installGPUOptions = [
  { id: 'detected', label: 'Auto-detect', flag: '' },
  { id: 'manual', label: 'Manual select', flag: '--gpu' },
]

const installModelOptions = [
  { id: 'test', label: 'Test model (TinyLlama)', flag: '' },
  { id: 'recommended', label: 'Recommended (Qwen3-4B)', flag: '--pull-recommended' },
]

// ─── New Data: Server Status ──────────────────────────────────────────────────

const serverStatusInfo = {
  status: 'Running',
  uptime: '4h 23m',
  model: 'tinyllama-1.1b-chat-v1.0.Q4_K_M',
  endpoint: 'http://127.0.0.1:11435/v1',
  gpu: 'NVIDIA GTX 1060 6GB',
  vramUsed: '1.2 / 6.0 GB',
  gate: 'BLOCKED',
}

// ─── New Data: Performance Estimator ────────────────────────────────────────

const performanceEstimatorGPUs = [
  { id: 'gtx1060', name: 'GTX 1060', vram: 6, cudaCores: 1280, bandwidth: 192 },
  { id: 'gtx1080', name: 'GTX 1080', vram: 8, cudaCores: 2560, bandwidth: 320 },
  { id: 'rtx3060', name: 'RTX 3060', vram: 12, cudaCores: 3584, bandwidth: 360 },
  { id: 'rtx4070', name: 'RTX 4070', vram: 12, cudaCores: 5888, bandwidth: 504 },
]

const performanceEstimatorModels = [
  { id: 'tinyllama', name: 'TinyLlama 1.1B', params: 1.1 },
  { id: 'qwen3-4b', name: 'Qwen3-4B', params: 4 },
]

const performanceEstimatorTasks = [
  { id: 'chat', name: 'Chat', icon: MessageCircle },
  { id: 'code', name: 'Code Generation', icon: Code },
  { id: 'summary', name: 'Summarization', icon: FileText },
  { id: 'translate', name: 'Translation', icon: Languages },
]

// ─── New Data: All Kimari Commands (for Ctrl+K palette) ────────────────────

const allKimariCommands = [
  'kimari doctor --deep', 'kimari info', 'kimari status',
  'kimari start', 'kimari stop', 'kimari start --daemon',
  'kimari pull test', 'kimari pull recommended', 'kimari models hash <path>',
  'kimari gateway setup', 'kimari gateway start --open', 'kimari gateway status --json',
  'kimari integrations generate --target openwebui', 'kimari integrations generate --target continue',
  'kimari integrations generate --target openclaw',
  'kimari optimize', 'kimari perf --matrix', 'kimari benchmark --dry-run',
  'kimari models', 'kimari console',
]

// ─── New Data: Accent Themes ────────────────────────────────────────────────

const accentThemes = [
  { id: 'blue', name: 'Blue', color: '#3b82f6', secondary: '#2563eb' },
  { id: 'cyan', name: 'Cyan', color: '#60a5fa', secondary: '#93c5fd' },
  { id: 'amber', name: 'Amber', color: '#f59e0b', secondary: '#eab308' },
  { id: 'rose', name: 'Rose', color: '#f43f5e', secondary: '#fb7185' },
  { id: 'violet', name: 'Violet', color: '#8b5cf6', secondary: '#a78bfa' },
]

// ─── New Data: Section IDs for Mini-Map ─────────────────────────────────────

const sectionIds = [
  { id: 'overview', label: 'Overview' },
  { id: 'quickstart', label: 'Quick Start' },
  { id: 'status', label: 'Status' },
  { id: 'cli', label: 'CLI' },
  { id: 'benchmarks', label: 'Benchmarks' },
  { id: 'terminal', label: 'Terminal' },
  { id: 'chat', label: 'Chat' },
  { id: 'faq', label: 'FAQ' },
  { id: 'docs', label: 'Docs' },
]

// ─── New Data: Benchmark History ──────────────────────────────────────────────

const benchmarkHistoryData = [
  { version: 'v0.1.0', promptSpeed: 120, genSpeed: 35 },
  { version: 'v0.1.2', promptSpeed: 155, genSpeed: 48 },
  { version: 'v0.1.4', promptSpeed: 185, genSpeed: 58 },
  { version: 'v0.1.6', promptSpeed: 210, genSpeed: 65 },
  { version: 'v0.1.8', promptSpeed: 225, genSpeed: 71 },
  { version: 'v0.1.82', promptSpeed: 228, genSpeed: 73 },
]

// ─── New Data: Changelog Items ────────────────────────────────────────────────

const changelogItems = [
  { date: 'May 2026', type: 'Feature', description: 'Added GPU VRAM calculator and model performance estimator to the landing page', color: '#3b82f6' },
  { date: 'May 2026', type: 'Improve', description: 'Enhanced terminal syntax highlighting with color-coded output and command history', color: '#60a5fa' },
  { date: 'Apr 2026', type: 'Feature', description: 'Gateway Dashboard with real-time server metrics and weekly request analytics', color: '#3b82f6' },
  { date: 'Apr 2026', type: 'Safety', description: 'Reinforced localhost-only defaults and gate BLOCKED status across all endpoints', color: '#f43f5e' },
  { date: 'Mar 2026', type: 'Fix', description: 'Fixed context length overflow on GTX 1060 profile when using Q5_K_M quantization', color: '#f59e0b' },
]

// ─── New Data: VRAM Optimization Tips ──────────────────────────────────────────

const vramOptimizationTips: Record<string, Record<string, { tip: string; detail: string }[]>> = {
  gtx1060: {
    tinyllama: [
      { tip: 'Reduce context length to 2048', detail: 'Saves ~0.3 GB VRAM for faster inference on 6 GB cards' },
      { tip: 'Use IQ4_XS quantization', detail: 'Saves 15% VRAM vs Q4_K_M with minimal quality loss' },
      { tip: 'Close other GPU applications', detail: 'Free VRAM for larger batch sizes and smoother generation' },
    ],
    'qwen3-4b': [
      { tip: 'Use Q4_K_M instead of Q5_K_M', detail: 'Saves ~0.8 GB VRAM, still good quality for 4B model' },
      { tip: 'Set context length to 4096', detail: 'Essential for fitting Qwen3-4B on 6 GB VRAM' },
      { tip: 'Enable flash attention', detail: 'Reduces memory overhead for long sequences' },
    ],
    'kimari-4b': [
      { tip: 'Use IQ4_XS quantization', detail: 'Most compact option to fit Kimari-4B on 6 GB' },
      { tip: 'Set context to 4096 max', detail: 'Critical for keeping within 6 GB VRAM limit' },
      { tip: 'Run with --mlock off', detail: 'Allows OS to swap model pages, reducing resident VRAM' },
    ],
  },
  gtx1080: {
    tinyllama: [
      { tip: 'Increase batch size to 1024', detail: 'Extra VRAM allows larger batches for faster prompt processing' },
      { tip: 'Use Q5_K_M for better quality', detail: '8 GB VRAM can handle higher quantization comfortably' },
      { tip: 'Set context length to 8192', detail: 'Room for longer conversations without VRAM pressure' },
    ],
    'qwen3-4b': [
      { tip: 'Use Q4_K_M quantization', detail: 'Fits well with 8 GB VRAM leaving room for context' },
      { tip: 'Set context length to 8192', detail: 'Good balance of context length and VRAM usage' },
      { tip: 'Monitor VRAM with kimari status', detail: 'Keep an eye on usage during long sessions' },
    ],
    'kimari-4b': [
      { tip: 'Use Q4_K_M for best balance', detail: 'Good quality while fitting within 8 GB' },
      { tip: 'Context length up to 8192', detail: 'Sufficient for most conversations with Kimari-4B' },
    ],
  },
  rtx3060: {
    tinyllama: [
      { tip: 'Use Q6_K or Q8_0 quantization', detail: '12 GB VRAM can handle near-lossless quality' },
      { tip: 'Set context to 16384', detail: 'Plenty of VRAM for very long conversations' },
    ],
    'qwen3-4b': [
      { tip: 'Use Q5_K_M quantization', detail: 'Best quality/size ratio with 12 GB VRAM' },
      { tip: 'Set context length to 16384', detail: 'Full context length supported for rich conversations' },
      { tip: 'Enable parallel sequences', detail: 'Extra VRAM allows multiple concurrent requests' },
    ],
    'kimari-4b': [
      { tip: 'Use Q5_K_M quantization', detail: 'High quality inference with 12 GB VRAM headroom' },
      { tip: 'Full 16384 context supported', detail: 'Maximum context length for Kimari-4B preview' },
    ],
  },
  rtx4070: {
    tinyllama: [
      { tip: 'Use Q8_0 quantization', detail: 'Near-lossless quality with plenty of VRAM to spare' },
      { tip: 'Max out all settings', detail: '12 GB VRAM + fast GPU = best possible experience' },
    ],
    'qwen3-4b': [
      { tip: 'Use Q6_K quantization', detail: 'Near-lossless quality with excellent generation speed' },
      { tip: 'Set context length to 16384', detail: 'Full context with room to spare for batch processing' },
      { tip: 'Run benchmark with kimari perf --matrix', detail: 'Compare all modes to find your optimal configuration' },
    ],
    'kimari-4b': [
      { tip: 'Use Q5_K_M or Q6_K', detail: 'Best quality with the RTX 4070\'s bandwidth advantage' },
      { tip: 'Full 16384 context + parallel sequences', detail: 'Maximum performance configuration for Kimari-4B' },
    ],
  },
}

// ─── New Data: Gateway Server Logs ────────────────────────────────────────────

const gatewayServerLogs = [
  { time: '14:23:01', level: 'info', message: 'Server started on 127.0.0.1:11435' },
  { time: '14:23:02', level: 'info', message: 'Model loaded: tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf' },
  { time: '14:23:02', level: 'info', message: 'CUDA backend initialized (GTX 1060 6GB)' },
  { time: '14:25:18', level: 'info', message: 'POST /v1/chat/completions — 200 OK (42ms)' },
  { time: '14:26:03', level: 'warn', message: 'Context length approaching limit (6.2K/8K tokens)' },
  { time: '14:27:45', level: 'info', message: 'GET /v1/models — 200 OK (3ms)' },
]

// ─── New Data: Gateway Profiles ────────────────────────────────────────────────

const gatewayProfiles = [
  { name: 'test', gpu: 'GTX 1060', model: 'TinyLlama 1.1B', status: 'Active', color: '#3b82f6' },
  { name: 'gtx1060', gpu: 'GTX 1060', model: 'Qwen3-4B Q4_K_M', status: 'Standby', color: '#2563eb' },
  { name: 'turbo', gpu: '6 GB+', model: 'Kimari-4B IQ4_XS', status: 'Blocked', color: '#ef4444' },
]

// ─── New Data: Model Comparison ────────────────────────────────────────────────

const modelComparisonData = [
  { id: 'tinyllama', name: 'TinyLlama 1.1B', speed: 73, vram: 1.2, contextLength: 4096, quality: 35, quant: 'Q4_K_M', params: '1.1B' },
  { id: 'qwen3-4b', name: 'Qwen3-4B', speed: 42, vram: 3.8, contextLength: 8192, quality: 65, quant: 'Q5_K_M', params: '4B' },
  { id: 'kimari-4b', name: 'Kimari-4B preview', speed: 38, vram: 3.2, contextLength: 8192, quality: 70, quant: 'Q4_K_M', params: '4B' },
  { id: 'llama-7b', name: 'Llama 2 7B', speed: 18, vram: 5.5, contextLength: 4096, quality: 75, quant: 'Q4_K_M', params: '7B' },
]

// ─── New Data: Deployment Checklist ────────────────────────────────────────────

const deploymentChecklistItems = [
  { id: 'prereq-python', label: 'Install Python 3.10+', category: 'Prerequisites' },
  { id: 'prereq-cuda', label: 'Install CUDA 12.1+', category: 'Prerequisites' },
  { id: 'prereq-disk', label: 'Ensure 4GB free disk space', category: 'Prerequisites' },
  { id: 'install-kimari', label: 'Run install script', category: 'Install' },
  { id: 'install-pull', label: 'Download test model (kimari pull test)', category: 'Install' },
  { id: 'config-profile', label: 'Select GPU profile', category: 'Configure' },
  { id: 'config-verify', label: 'Run kimari doctor --deep', category: 'Configure' },
  { id: 'test-start', label: 'Start server (kimari start)', category: 'Test' },
  { id: 'test-endpoint', label: 'Verify API endpoint responds', category: 'Test' },
  { id: 'test-gateway', label: 'Open Gateway Dashboard', category: 'Test' },
  { id: 'deploy-integrate', label: 'Configure integration (Open WebUI / Continue)', category: 'Deploy' },
  { id: 'deploy-benchmark', label: 'Run performance benchmark', category: 'Deploy' },
]

// ─── New Data: Error Troubleshooter ────────────────────────────────────────────

const errorDatabase = [
  { id: 'e1', symptom: 'CUDA out of memory', solution: 'Reduce context length with --ctx-size flag, use a smaller quantization (IQ4_XS or Q4_K_M), or close other GPU applications. Run kimari optimize for recommended settings.', category: 'Runtime' },
  { id: 'e2', symptom: 'Model not found', solution: 'Run kimari pull test or kimari pull recommended to download the model. Check that the model file exists in ~/.config/kimari/models/', category: 'Models' },
  { id: 'e3', symptom: 'Port already in use', solution: 'Another process is using port 11435. Run kimari stop first, or use --port flag to specify a different port.', category: 'Server' },
  { id: 'e4', symptom: 'llama-server binary not found', solution: 'Re-run the install script to download llama-server. Ensure /usr/local/bin/llama-server exists and is executable. Run kimari doctor to check.', category: 'Install' },
  { id: 'e5', symptom: 'Slow token generation', solution: 'Ensure CUDA is properly installed and the GPU is being used (check for "CUDA" in kimari status output). CPU-only mode is significantly slower. Run kimari optimize for GPU-specific settings.', category: 'Performance' },
  { id: 'e6', symptom: 'Connection refused', solution: 'Make sure the server is running with kimari start. Check the endpoint URL matches the running server (default: http://127.0.0.1:11435/v1).', category: 'Server' },
  { id: 'e7', symptom: 'GGUF file corrupt', solution: 'Re-download the model with kimari pull. Verify integrity with kimari models hash <path>. The SHA256 should match the published hash.', category: 'Models' },
  { id: 'e8', symptom: 'Gate BLOCKED', solution: 'This is expected. The Kimari-4B release gate is BLOCKED — no public weights are available. Use test or recommended profiles with community models instead.', category: 'Models' },
  { id: 'e9', symptom: 'Gateway dashboard blank', solution: 'Run kimari gateway setup to install dependencies, then kimari gateway start --open. Ensure Node.js 18+ is installed.', category: 'Gateway' },
  { id: 'e10', symptom: 'Context length overflow', solution: 'The requested context length exceeds available VRAM. Reduce --ctx-size or use a smaller model. GTX 1060 6GB supports up to 8192 context with Q4_K_M on TinyLlama.', category: 'Runtime' },
]

// ─── New Data: Technical Term Tooltips ──────────────────────────────────────────

const techTerms: Record<string, { short: string; detail: string; link: string }> = {
  'GGUF': { short: 'GPT-Generated Unified Format', detail: 'A file format for storing large language models in a single file, optimized for efficient loading and inference with llama.cpp.', link: 'https://github.com/ggerganov/ggml/blob/master/docs/gguf.md' },
  'VRAM': { short: 'Video Random Access Memory', detail: 'Dedicated memory on your GPU. Determines which models you can run and how fast they process tokens. More VRAM = larger models and longer contexts.', link: '' },
  'Quantization': { short: 'Model compression technique', detail: 'Reduces model precision (e.g., from 16-bit to 4-bit) to use less VRAM with minimal quality loss. Common formats: Q4_K_M, Q5_K_M, IQ4_XS.', link: '' },
  'Q4_K_M': { short: '4-bit quantization (medium)', detail: 'A 4-bit quantization format that balances model size and quality. Reduces VRAM usage by ~75% compared to FP16 with moderate quality loss.', link: '' },
  'CUDA': { short: 'Compute Unified Device Architecture', detail: 'NVIDIA\'s parallel computing platform. Required for GPU-accelerated inference. CUDA 12.1+ is recommended for Kimari.', link: 'https://developer.nvidia.com/cuda-toolkit' },
  'tok/s': { short: 'Tokens per second', detail: 'Measures how fast the model generates text. Higher is better. Prompt processing speed and generation speed are measured separately.', link: '' },
  'Context Length': { short: 'Maximum input+output token count', detail: 'The total number of tokens the model can process in a single request. Longer contexts require more VRAM. Typical range: 2048-16384.', link: '' },
}

// ─── New Data: GPU Compatibility Quiz ────────────────────────────────────────

const gpuQuizSteps = [
  { id: 1, title: 'Your GPU', question: 'Which GPU do you have?', options: [
    { value: 'gtx1060', label: 'GTX 1060 6GB', icon: '🖥️' },
    { value: 'gtx1080', label: 'GTX 1080 8GB', icon: '🖥️' },
    { value: 'rtx3060', label: 'RTX 3060 12GB', icon: '💻' },
    { value: 'rtx4070', label: 'RTX 4070 12GB', icon: '💻' },
  ]},
  { id: 2, title: 'Use Case', question: 'What will you use it for?', options: [
    { value: 'chat', label: 'Chat / Conversation', icon: '💬' },
    { value: 'code', label: 'Code Generation', icon: '👨‍💻' },
    { value: 'research', label: 'Research / Analysis', icon: '🔬' },
    { value: 'creative', label: 'Creative Writing', icon: '✍️' },
  ]},
  { id: 3, title: 'Priority', question: 'What matters most?', options: [
    { value: 'speed', label: 'Speed (fastest inference)', icon: '⚡' },
    { value: 'quality', label: 'Quality (best output)', icon: '🎯' },
    { value: 'memory', label: 'Memory (lowest VRAM)', icon: '💾' },
    { value: 'balanced', label: 'Balanced', icon: '⚖️' },
  ]},
]

const gpuQuizResults: Record<string, { profile: string; model: string; quant: string; ctx: number; reason: string }> = {
  gtx1060: { profile: 'gtx1060', model: 'TinyLlama 1.1B', quant: 'Q4_K_M', ctx: 8192, reason: 'The GTX 1060 6GB works best with compact models. TinyLlama runs smoothly with room for context.' },
  gtx1080: { profile: 'gtx1080', model: 'Qwen3-4B', quant: 'Q5_K_M', ctx: 16384, reason: 'The GTX 1080 8GB can handle 4B models at higher quantization with extended context length.' },
  rtx3060: { profile: 'test', model: 'Qwen3-4B', quant: 'Q5_K_M', ctx: 16384, reason: 'The RTX 3060 12GB has plenty of VRAM for 4B models at high quality with maximum context.' },
  rtx4070: { profile: 'turbo', model: 'Qwen3-4B', quant: 'Q6_K', ctx: 16384, reason: 'The RTX 4070 12GB with high bandwidth supports near-lossless quantization and fast generation.' },
}

// ─── New Data: Command Builder ────────────────────────────────────────────────

const commandBuilderActions = [
  { id: 'start', label: 'Start server', command: 'kimari start', icon: Play },
  { id: 'stop', label: 'Stop server', command: 'kimari stop', icon: Square },
  { id: 'doctor', label: 'Run diagnostics', command: 'kimari doctor --deep', icon: Activity },
  { id: 'pull', label: 'Pull model', command: 'kimari pull', icon: Download },
  { id: 'optimize', label: 'Optimize GPU', command: 'kimari optimize', icon: Gauge },
  { id: 'gateway', label: 'Start gateway', command: 'kimari gateway start', icon: Monitor },
]

const commandBuilderFlags = [
  { id: 'daemon', label: '--daemon', desc: 'Run in background', appliesTo: ['start'] },
  { id: 'deep', label: '--deep', desc: 'Deep diagnostics', appliesTo: ['doctor'] },
  { id: 'test', label: 'test', desc: 'Test model (TinyLlama)', appliesTo: ['pull'] },
  { id: 'recommended', label: 'recommended', desc: 'Recommended model (Qwen3-4B)', appliesTo: ['pull'] },
  { id: 'open', label: '--open', desc: 'Open in browser', appliesTo: ['gateway'] },
  { id: 'port', label: '--port <number>', desc: 'Custom port', appliesTo: ['start', 'gateway'] },
  { id: 'gpu', label: '--gpu <name>', desc: 'Specify GPU', appliesTo: ['optimize'] },
  { id: 'ctx', label: '--ctx-size <n>', desc: 'Context length', appliesTo: ['start'] },
]

// ─── New Data: Performance Comparison ────────────────────────────────────────

const performanceComparisonData = [
  { metric: 'Avg Latency (ms)', kimari: 42, openai: 320, anthropic: 280, isLocal: true },
  { metric: 'Cost per 1K tokens ($)', kimari: 0, openai: 0.002, anthropic: 0.003, isLocal: true },
  { metric: 'Privacy Score (1-10)', kimari: 10, openai: 3, anthropic: 3, isLocal: true },
  { metric: 'Uptime Control', kimari: 10, openai: 6, anthropic: 6, isLocal: true },
  { metric: 'Customization (1-10)', kimari: 9, openai: 2, anthropic: 2, isLocal: true },
  { metric: 'Offline Capable', kimari: 10, openai: 0, anthropic: 0, isLocal: true },
]

// ─── New Data: Notifications ────────────────────────────────────────────────

const initialNotifications = [
  { id: 1, title: 'New version available', description: 'Kimari v0.1.83-alpha is ready to install', time: '2m ago', type: 'update' as const, read: false },
  { id: 2, title: 'Model download complete', description: 'TinyLlama 1.1B Q4_K_M downloaded successfully', time: '15m ago', type: 'success' as const, read: false },
  { id: 3, title: 'Server status changed', description: 'API server restarted after config update', time: '1h ago', type: 'info' as const, read: false },
  { id: 4, title: 'Gateway Dashboard update', description: 'New analytics charts available', time: '3h ago', type: 'info' as const, read: true },
  { id: 5, title: 'Security notice', description: 'All endpoints remain localhost-only', time: '1d ago', type: 'warning' as const, read: true },
]

// ─── New Data: System Requirements Table ─────────────────────────────────────

const systemRequirementsTableData = [
  { component: 'GPU', minimum: 'NVIDIA GTX 1060 6GB', recommended: 'NVIDIA RTX 3060 12GB+', notes: 'Must support CUDA 12.1+', compatKey: 'gpu' },
  { component: 'VRAM', minimum: '6 GB', recommended: '12 GB+', notes: 'More VRAM = larger models & context', compatKey: 'vram' },
  { component: 'CPU', minimum: '4 cores, 2.5 GHz', recommended: '8+ cores, 3.5 GHz+', notes: 'CPU-only mode is 3-5x slower', compatKey: 'cpu' },
  { component: 'RAM', minimum: '8 GB', recommended: '16 GB+', notes: 'System RAM for offloading & OS', compatKey: 'ram' },
  { component: 'Disk', minimum: '4 GB free', recommended: '20 GB+ SSD', notes: 'Per model: 0.7–6 GB each', compatKey: 'disk' },
  { component: 'OS', minimum: 'Ubuntu 20.04+ / WSL2', recommended: 'Ubuntu 22.04+ native', notes: 'macOS works with Metal backend', compatKey: 'os' },
  { component: 'CUDA', minimum: '12.1', recommended: '12.4+', notes: 'Driver 525+ required for CUDA 12', compatKey: 'cuda' },
]

// ─── New Data: API Endpoint Explorer ─────────────────────────────────────────

const apiEndpoints = [
  {
    method: 'POST',
    path: '/v1/chat/completions',
    description: 'Send a chat message and get a completion response',
    request: JSON.stringify({
      model: 'tinyllama-1.1b-chat-v1.0.Q4_K_M',
      messages: [{ role: 'user', content: 'Hello, how are you?' }],
      temperature: 0.7,
      max_tokens: 256,
    }, null, 2),
    response: JSON.stringify({
      id: 'chatcmpl-abc123',
      object: 'chat.completion',
      model: 'tinyllama-1.1b-chat-v1.0.Q4_K_M',
      choices: [{ index: 0, message: { role: 'assistant', content: 'Hello! I am doing well, thank you for asking. How can I help you today?' }, finish_reason: 'stop' }],
      usage: { prompt_tokens: 12, completion_tokens: 18, total_tokens: 30 },
    }, null, 2),
  },
  {
    method: 'GET',
    path: '/v1/models',
    description: 'List all available models on the server',
    request: '',
    response: JSON.stringify({
      object: 'list',
      data: [
        { id: 'tinyllama-1.1b-chat-v1.0.Q4_K_M', object: 'model', owned_by: 'local' },
        { id: 'qwen3-4b-Q5_K_M', object: 'model', owned_by: 'local' },
      ],
    }, null, 2),
  },
  {
    method: 'POST',
    path: '/v1/completions',
    description: 'Generate text completion for a prompt',
    request: JSON.stringify({
      model: 'tinyllama-1.1b-chat-v1.0.Q4_K_M',
      prompt: 'The capital of France is',
      max_tokens: 16,
      temperature: 0.3,
    }, null, 2),
    response: JSON.stringify({
      id: 'cmpl-xyz789',
      object: 'text_completion',
      model: 'tinyllama-1.1b-chat-v1.0.Q4_K_M',
      choices: [{ text: ' Paris. Paris is the largest city in France', index: 0, finish_reason: 'length' }],
      usage: { prompt_tokens: 5, completion_tokens: 11, total_tokens: 16 },
    }, null, 2),
  },
  {
    method: 'GET',
    path: '/v1/models/{model}',
    description: 'Get details about a specific model',
    request: '',
    response: JSON.stringify({
      id: 'tinyllama-1.1b-chat-v1.0.Q4_K_M',
      object: 'model',
      owned_by: 'local',
      metadata: { quantization: 'Q4_K_M', context_length: 4096, vram_required: '1.2 GB' },
    }, null, 2),
  },
]

// ─── New Data: Model Card Gallery ────────────────────────────────────────────

const modelCards = [
  { name: 'TinyLlama 1.1B', icon: '🦙', params: '1.1B', quant: 'Q4_K_M', vram: '1.2 GB', speed: '73 tok/s', context: '4096', description: 'Fast, compact model for basic chat and testing. Great starting point.' },
  { name: 'Qwen3-4B', icon: '🧠', params: '4B', quant: 'Q5_K_M', vram: '3.8 GB', speed: '42 tok/s', context: '8192', description: 'Balanced model with good quality. Recommended for most use cases.' },
  { name: 'Kimari-4B', icon: '🔮', params: '4B', quant: 'Q4_K_M', vram: '3.2 GB', speed: '38 tok/s', context: '8192', description: 'Future Kimari model. Not released — gate BLOCKED.' },
  { name: 'Llama 2 7B', icon: '🦙', params: '7B', quant: 'Q4_K_M', vram: '5.5 GB', speed: '18 tok/s', context: '4096', description: 'Larger model requiring more VRAM. Best on 8GB+ cards.' },
  { name: 'Phi-3 Mini', icon: '⚡', params: '3.8B', quant: 'Q4_K_M', vram: '2.8 GB', speed: '55 tok/s', context: '4096', description: 'Microsoft\'s compact model. Strong reasoning for its size.' },
  { name: 'Gemma 2 2B', icon: '💎', params: '2B', quant: 'Q5_K_M', vram: '1.8 GB', speed: '62 tok/s', context: '8192', description: 'Google\'s efficient model. Good quality-to-size ratio.' },
]

// ─── New Data: Visual Themes ─────────────────────────────────────────────────

const visualThemes = [
  { id: 'dark', name: 'Dark', preview: { bg: '#09090b', card: '#18181b', text: '#fafafa', accent: '#3b82f6' } },
  { id: 'light', name: 'Light', preview: { bg: '#ffffff', card: '#ffffff', text: '#09090b', accent: '#3b82f6' } },
  { id: 'nord', name: 'Nord', preview: { bg: '#2e3440', card: '#3b4252', text: '#eceff4', accent: '#88c0d0' } },
  { id: 'dracula', name: 'Dracula', preview: { bg: '#282a36', card: '#44475a', text: '#f8f8f2', accent: '#bd93f9' } },
  { id: 'high-contrast', name: 'High Contrast', preview: { bg: '#000000', card: '#0a0a0a', text: '#ffffff', accent: '#00ff88' } },
]

// ─── New Data: Prompt Templates ────────────────────────────────────────────────

const promptTemplates = [
  { id: 'code-assistant', title: 'Code Assistant', category: 'Development', icon: Code2, template: 'You are an expert software engineer. Help me write clean, efficient, and well-documented code. When I describe a problem, provide a complete solution with explanations. Use best practices and include error handling.', description: 'Full-stack coding helper with best practices' },
  { id: 'creative-writing', title: 'Creative Writing', category: 'Creative', icon: Sparkles, template: 'You are a creative writing assistant. Help me craft engaging stories, poems, and narratives. Focus on vivid descriptions, compelling characters, and natural dialogue. Adapt your style to match the tone I request.', description: 'Story and narrative generation assistant' },
  { id: 'code-review', title: 'Code Reviewer', category: 'Development', icon: Shield, template: 'You are a senior code reviewer. Analyze my code for bugs, security vulnerabilities, performance issues, and style problems. Provide specific suggestions for improvement with explanations. Rate the code quality on a scale of 1-10.', description: 'Thorough code review with security focus' },
  { id: 'data-analyst', title: 'Data Analyst', category: 'Analysis', icon: BarChart3, template: 'You are a data analysis expert. Help me interpret data, identify trends, and create insights. When I provide data, give me summary statistics, notable patterns, and actionable recommendations. Use clear, concise language.', description: 'Data interpretation and insight generation' },
  { id: 'technical-writer', title: 'Technical Writer', category: 'Writing', icon: FileText, template: 'You are a technical writer. Help me create clear, accurate documentation for software projects. Write API docs, README files, user guides, and tutorials. Use proper markdown formatting and include code examples where appropriate.', description: 'Documentation and technical content creation' },
  { id: 'debugging-helper', title: 'Debug Assistant', category: 'Development', icon: AlertCircle, template: 'You are a debugging expert. When I share an error message or describe unexpected behavior, help me identify the root cause. Walk me through the debugging process step by step. Suggest specific fixes and explain why they work.', description: 'Step-by-step debugging and error resolution' },
  { id: 'summarizer', title: 'Smart Summarizer', category: 'Analysis', icon: FileText, template: 'You are an expert summarizer. When I provide text, create a concise summary that captures the key points, main arguments, and important details. Offer different summary lengths: brief (1-2 sentences), medium (1 paragraph), and detailed (multiple paragraphs).', description: 'Multi-length text summarization' },
  { id: 'translation-expert', title: 'Translation Expert', category: 'Language', icon: Languages, template: 'You are a professional translator. Translate text between languages while preserving tone, context, and cultural nuances. When translating, also explain any idioms or culturally specific references that don\'t have direct equivalents.', description: 'Context-aware translation with cultural notes' },
]

// ─── New Data: GPU Temperature Profiles ──────────────────────────────────────

const gpuTempProfiles = [
  { id: 'idle', label: 'Idle', temp: 38, fanSpeed: 30, power: 15, color: '#3b82f6', description: 'System idle, no model loaded' },
  { id: 'inference', label: 'Inference', temp: 62, fanSpeed: 55, power: 85, color: '#f59e0b', description: 'Running single inference request' },
  { id: 'heavy', label: 'Heavy Load', temp: 78, fanSpeed: 80, power: 120, color: '#ef4444', description: 'Continuous generation with long context' },
  { id: 'sustained', label: 'Sustained', temp: 72, fanSpeed: 70, power: 105, color: '#f97316', description: 'Extended multi-turn conversation' },
]

// ─── New Data: Download Simulation Models ─────────────────────────────────────

const downloadModels = [
  { id: 'tinyllama-q4', name: 'TinyLlama 1.1B Q4_K_M', size: 670, speed: 12.5, quant: 'Q4_K_M' },
  { id: 'qwen3-q5', name: 'Qwen3-4B Q5_K_M', size: 2800, speed: 12.5, quant: 'Q5_K_M' },
  { id: 'qwen3-q4', name: 'Qwen3-4B Q4_K_M', size: 2400, speed: 12.5, quant: 'Q4_K_M' },
  { id: 'phi3-q4', name: 'Phi-3 Mini Q4_K_M', size: 2300, speed: 12.5, quant: 'Q4_K_M' },
]

// ─── New Data: Enhanced Changelog ──────────────────────────────────────────────

const enhancedChangelogItems = [
  { version: 'v0.1.82', date: 'May 2026', type: 'Feature' as const, title: 'VRAM Calculator & Performance Estimator', description: 'Added interactive GPU VRAM calculator and model performance estimator tools to help users find the right model for their hardware.', details: 'The VRAM calculator shows real-time fit analysis for GPU+model combinations, while the performance estimator predicts latency, throughput, and time-to-first-token across different task types.' },
  { version: 'v0.1.82', date: 'May 2026', type: 'Improve' as const, title: 'Terminal Syntax Highlighting', description: 'Enhanced terminal output with color-coded syntax highlighting for commands, URLs, and status indicators.', details: 'PASS indicators show in blue, WARN in amber, URLs are underlined in cyan, and performance metrics are highlighted in blue bold. Command history with arrow key navigation added.' },
  { version: 'v0.1.8', date: 'Apr 2026', type: 'Feature' as const, title: 'Gateway Dashboard', description: 'Local web dashboard for monitoring runtime metrics, server logs, and request analytics.', details: 'Includes daily request AreaChart, server log viewer with color-coded info/warn levels, interactive profile selector, and real-time server configuration display.' },
  { version: 'v0.1.8', date: 'Apr 2026', type: 'Safety' as const, title: 'Localhost-Only Defaults Reinforced', description: 'Strengthened default security posture across all endpoints and configuration.', details: 'All server endpoints default to 127.0.0.1, no public bind unless explicitly requested via flag, no token storage in dashboard, and no automatic gate transitions.' },
  { version: 'v0.1.7', date: 'Mar 2026', type: 'Feature' as const, title: 'Integration Guides', description: 'Complete setup guides for Open WebUI, Continue.dev, and OpenClaw integrations.', details: 'Auto-configuration via kimari integrations generate --target <tool> generates ready-to-use config files for each supported tool.' },
  { version: 'v0.1.6', date: 'Mar 2026', type: 'Milestone' as const, title: 'GTX 1060 Validation', description: '228 tok/s prompt processing confirmed on real GTX 1060 6GB hardware under WSL2.', details: 'Full benchmark suite run with CUDA 12.1 backend, llama-server runtime, and TinyLlama 1.1B Q4_K_M quantization. Results are reproducible.' },
  { version: 'v0.1.4', date: 'Feb 2026', type: 'Feature' as const, title: 'Gateway Dashboard Preview', description: 'First preview of the local web dashboard for monitoring runtime.', details: 'Basic overview tab with GPU, VRAM, model, and gate status. Server configuration display and daily request counts.' },
  { version: 'v0.1.0', date: 'Jan 2026', type: 'Release' as const, title: 'Initial CLI Framework', description: 'First working CLI with doctor, start, pull, and status commands.', details: 'Python-based CLI with automatic GPU detection, CUDA validation, model download from HuggingFace, and SHA256 integrity verification.' },
]

// ─── New Data: Configuration Wizard Steps ────────────────────────────────────

const wizardGpuOptions = [
  { id: 'gtx1060', label: 'GTX 1060 6GB', vram: 6, cudaCores: 1280 },
  { id: 'gtx1080', label: 'GTX 1080 8GB', vram: 8, cudaCores: 2560 },
  { id: 'rtx3060', label: 'RTX 3060 12GB', vram: 12, cudaCores: 3584 },
  { id: 'rtx4070', label: 'RTX 4070 12GB', vram: 12, cudaCores: 5888 },
  { id: 'other', label: 'Other NVIDIA (6GB+)', vram: 6, cudaCores: 1024 },
]

const wizardUseCases = [
  { id: 'chat', label: 'Chat & Conversation', icon: MessageCircle, desc: 'General-purpose chatbot interaction' },
  { id: 'code', label: 'Code Generation', icon: Code, desc: 'Writing and reviewing code' },
  { id: 'writing', label: 'Creative Writing', icon: Sparkles, desc: 'Stories, articles, and content' },
  { id: 'analysis', label: 'Data Analysis', icon: BarChart3, desc: 'Interpreting data and research' },
]

const wizardPriorities = [
  { id: 'speed', label: 'Speed', desc: 'Fastest inference possible', icon: Zap },
  { id: 'quality', label: 'Quality', desc: 'Best output quality', icon: Award },
  { id: 'memory', label: 'Low VRAM', desc: 'Minimal memory usage', icon: MemoryStick },
  { id: 'balanced', label: 'Balanced', desc: 'Good mix of all factors', icon: Gauge },
]

// ─── Animated Section Wrapper ────────────────────────────────────────────────

function Section({ children, className = '', id = '' }: { children: React.ReactNode; className?: string; id?: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-60px' })
  return (
    <motion.section
      ref={ref}
      id={id}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.section>
  )
}

// ─── Section Divider (Enhanced) ────────────────────────────────────────────

function SectionDivider() {
  return (
    <div className="relative h-px w-full overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/20 to-transparent" />
      {/* Animated flowing dots */}
      <motion.div
        className="absolute top-1/2 -translate-y-1/2 w-16 h-1 rounded-full bg-gradient-to-r from-blue-500/0 via-blue-500/60 to-blue-500/0"
        animate={{ x: ['-16px', 'calc(100vw + 16px)'] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
      />
      <motion.div
        className="absolute top-1/2 -translate-y-1/2 w-10 h-0.5 rounded-full bg-gradient-to-r from-blue-600/0 via-blue-600/40 to-blue-600/0"
        animate={{ x: ['calc(100vw + 10px)', '-10px'] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'linear', delay: 1 }}
      />
    </div>
  )
}

// ─── Copy Button ────────────────────────────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const { toast } = useToast()
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); toast({ title: 'Copied to clipboard!', description: text.slice(0, 60) + (text.length > 60 ? '...' : '') }); setTimeout(() => setCopied(false), 2000) }}
      className="opacity-0 group-hover:opacity-100 transition-all duration-200 p-1 rounded hover:bg-white/10 active:scale-90"
      aria-label="Copy command"
    >
      {copied ? <Check className="w-3.5 h-3.5 text-blue-400" /> : <Copy className="w-3.5 h-3.5 text-zinc-400" />}
    </button>
  )
}

// ─── Status Badge ───────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { icon: React.ReactNode; className: string }> = {
    usable: { icon: <CheckCircle2 className="w-4 h-4" />, className: 'bg-blue-500/10 text-blue-500 border-blue-500/20' },
    preview: { icon: <Eye className="w-4 h-4" />, className: 'bg-amber-500/10 text-amber-500 border-amber-500/20' },
    private: { icon: <Lock className="w-4 h-4" />, className: 'bg-violet-500/10 text-violet-400 border-violet-500/20' },
    blocked: { icon: <XCircle className="w-4 h-4" />, className: 'bg-red-500/10 text-red-500 border-red-500/20' },
  }
  const c = config[status] || config.blocked
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${c.className}`}>
      {c.icon}
      {status === 'usable' ? 'Working' : status === 'preview' ? 'Preview' : status === 'private' ? 'Private' : 'Blocked'}
    </span>
  )
}

// ─── Animated Counter ───────────────────────────────────────────────────────

function AnimatedCounter({ target, suffix = '', prefix = '' }: { target: number; suffix?: string; prefix?: string }) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true })
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!isInView) return
    let start = 0
    const duration = 1500
    const startTime = performance.now()
    const animate = (now: number) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = Math.round(eased * target)
      setCount(current)
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [isInView, target])

  return <span ref={ref}>{prefix}{count}{suffix}</span>
}

// ─── Floating Gradient Orbs (with parallax) ────────────────────────────────

function FloatingOrbs() {
  const { scrollY } = useScroll()
  const y1 = useTransform(scrollY, [0, 1000], [0, -80])
  const y2 = useTransform(scrollY, [0, 1000], [0, -120])
  const y3 = useTransform(scrollY, [0, 1000], [0, -60])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute w-72 h-72 rounded-full bg-blue-500/10 blur-3xl"
        style={{ top: '10%', left: '5%', y: y1 }}
        animate={{ x: [0, 30, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute w-64 h-64 rounded-full bg-blue-600/10 blur-3xl"
        style={{ top: '50%', right: '10%', y: y2 }}
        animate={{ x: [0, -25, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute w-48 h-48 rounded-full bg-cyan-500/8 blur-3xl"
        style={{ bottom: '10%', left: '30%', y: y3 }}
        animate={{ x: [0, 20, 0] }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
      />
    </div>
  )
}

// ─── Particle Background ───────────────────────────────────────────────────

function ParticleField() {
  // Generate particles with deterministic seeded values as strings to avoid hydration mismatch
  const particles = useMemo(() =>
    Array.from({ length: 40 }, (_, i) => {
      const s = (off: number) => {
        const x = Math.sin(i * 9301 + off * 49297 + 233280) * 49297
        return x - Math.floor(x)
      }
      return {
        w: `${(s(1) * 3 + 1).toFixed(2)}px`,
        h: `${(s(2) * 3 + 1).toFixed(2)}px`,
        l: `${(s(3) * 100).toFixed(2)}%`,
        t: `${(s(4) * 100).toFixed(2)}%`,
        bg: `rgba(59,130,246,${(s(5) * 0.3 + 0.1).toFixed(2)})`,
        dur: Number((s(6) * 4 + 3).toFixed(2)),
        del: Number((s(7) * 3).toFixed(2)),
      }
    }), [])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{ width: p.w, height: p.h, left: p.l, top: p.t, background: p.bg }}
          animate={{ y: [0, -30, 0], opacity: [0.2, 0.6, 0.2] }}
          transition={{ duration: p.dur, repeat: Infinity, delay: p.del, ease: 'easeInOut' }}
        />
      ))}
    </div>
  )
}

// ─── Interactive Terminal (with Syntax Highlighting + Command History) ────────

function InteractiveTerminal() {
  const [history, setHistory] = useState<{ type: 'input' | 'output'; text: string }[]>([
    { type: 'output', text: 'Kimari Terminal Simulator v0.1.82-alpha\nType "help" for available commands.\n' }
  ])
  const [input, setInput] = useState('')
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const terminalRef = useRef<HTMLDivElement>(null)

  const handleCommand = useCallback((cmd: string) => {
    const trimmed = cmd.trim().toLowerCase()
    const response = terminalResponses[trimmed] || `Command not found: ${cmd}\nType "help" for available commands.`
    setHistory(prev => [...prev, { type: 'input', text: `$ ${cmd}` }, { type: 'output', text: response }])
    if (cmd.trim()) {
      setCommandHistory(prev => [...prev, cmd.trim()])
    }
    setHistoryIndex(-1)
  }, [])

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [history])

  // Syntax highlighting for terminal output lines
  const highlightLine = (line: string, type: 'input' | 'output') => {
    if (type === 'input') return <span className="text-blue-400">{line}</span>

    // Apply color rules
    if (line.trimStart().startsWith('[PASS]')) {
      return <span className="text-blue-400">{line}</span>
    }
    if (line.trimStart().startsWith('[WARN]')) {
      return <span className="text-amber-400">{line}</span>
    }
    if (line.includes('✅')) {
      return <span className="text-blue-400">{line}</span>
    }
    if (line.includes('⚡')) {
      return <span className="text-amber-400">{line}</span>
    }

    // Highlight URLs (http://)
    if (line.includes('http://')) {
      const parts = line.split(/(http:\/\/[^\s]+)/)
      return (
        <span>
          {parts.map((part, i) =>
            part.startsWith('http://')
              ? <span key={i} className="text-cyan-400 underline decoration-cyan-400/30">{part}</span>
              : <span key={i}>{part}</span>
          )}
        </span>
      )
    }

    // Highlight performance numbers (tok/s, MiB)
    if (/\d+\s*tok\/s/.test(line) || /\d+\s*MiB/.test(line)) {
      return <span className="text-green-400 font-semibold">{line}</span>
    }

    return <span className="text-zinc-300">{line}</span>
  }

  const renderOutput = (text: string, type: 'input' | 'output') => {
    const lines = text.split('\n')
    return lines.map((line, i) => (
      <div key={i}>{highlightLine(line, type)}</div>
    ))
  }

  const historyCount = commandHistory.length
  const displayHistoryPos = historyIndex >= 0 ? `${commandHistory.length - historyIndex}/${historyCount}` : ''

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden shadow-[0_0_0_1px_rgba(59,130,246,0.05),0_8px_32px_rgba(0,0,0,0.3)]">
      {/* Terminal chrome */}
      <div className="bg-zinc-900 border-b border-zinc-800 px-4 py-2.5 flex items-center gap-3">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500/60" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
          <div className="w-3 h-3 rounded-full bg-green-500/60" />
        </div>
        <span className="text-xs text-zinc-500 font-mono">kimari-console</span>
        {displayHistoryPos && (
          <span className="ml-auto text-[10px] text-zinc-600 font-mono">{displayHistoryPos}</span>
        )}
        <button
          onClick={() => setHistory([{ type: 'output', text: 'Terminal cleared.\n' }])}
          className="p-1 hover:bg-zinc-800 rounded transition-colors"
          aria-label="Clear terminal"
        >
          <RotateCcw className="w-3.5 h-3.5 text-zinc-500" />
        </button>
      </div>
      {/* Terminal body */}
      <div ref={terminalRef} className="p-4 h-72 overflow-y-auto font-mono text-sm space-y-1" style={{ scrollbarWidth: 'thin' }}>
        {history.map((entry, i) => (
          <div key={i} className="whitespace-pre-wrap">
            {renderOutput(entry.text, entry.type)}
          </div>
        ))}
      </div>
      {/* Input line */}
      <div className="border-t border-zinc-800 px-4 py-2.5 flex items-center gap-2">
        <span className="text-blue-400 font-mono text-sm">$</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && input.trim()) {
              handleCommand(input)
              setInput('')
            } else if (e.key === 'ArrowUp') {
              e.preventDefault()
              if (commandHistory.length > 0) {
                const newIndex = historyIndex === -1 ? commandHistory.length - 1 : Math.max(0, historyIndex - 1)
                setHistoryIndex(newIndex)
                setInput(commandHistory[newIndex])
              }
            } else if (e.key === 'ArrowDown') {
              e.preventDefault()
              if (historyIndex >= 0) {
                const newIndex = historyIndex + 1
                if (newIndex >= commandHistory.length) {
                  setHistoryIndex(-1)
                  setInput('')
                } else {
                  setHistoryIndex(newIndex)
                  setInput(commandHistory[newIndex])
                }
              }
            }
          }}
          className="flex-1 bg-transparent text-zinc-200 font-mono text-sm outline-none placeholder:text-zinc-600 caret-blue-400"
          placeholder="Type a command... (↑↓ for history)"
          autoFocus
        />
        <span className="text-blue-400 font-mono text-sm animate-pulse select-none">▊</span>
        <button
          onClick={() => { if (input.trim()) { handleCommand(input); setInput('') } }}
          className="p-1.5 hover:bg-zinc-800 rounded transition-colors"
          aria-label="Run command"
        >
          <Send className="w-3.5 h-3.5 text-blue-500" />
        </button>
      </div>
    </div>
  )
}

// ─── AI Chat Simulator ──────────────────────────────────────────────────────

function AIChatSimulator() {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [typingText, setTypingText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [sessionId] = useState(() => `session-${Math.random().toString(36).slice(2, 8)}`)
  const scrollRef = useRef<HTMLDivElement>(null)
  const typingRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading, typingText])

  // Cleanup typing interval on unmount
  useEffect(() => {
    return () => { if (typingRef.current) clearInterval(typingRef.current) }
  }, [])

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading || isTyping) return
    setError(null)
    const userMsg = text.trim()
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setInput('')
    setIsLoading(true)

    // Simulated AI responses for the landing page demo
    const getSimulatedResponse = (msg: string): string => {
      const lower = msg.toLowerCase()
      if (lower.includes('kimari-4b') || lower.includes('weights') || lower.includes('model available') || lower.includes('release')) {
        return 'Kimari-4B is NOT released. The release gate is BLOCKED — no public weights, adapters, or GGUF files are available. We will not promise a release date until quality and safety standards are met.'
      }
      if (lower.includes('install') || lower.includes('setup') || lower.includes('get started')) {
        return 'Install with: curl -fsSL https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.sh | bash\nThen run: kimari doctor --deep && kimari pull test && kimari start'
      }
      if (lower.includes('gpu') || lower.includes('gtx') || lower.includes('vram') || lower.includes('hardware')) {
        return 'Kimari supports GTX 1060 6GB, GTX 1080 8GB, and any NVIDIA GPU with 6GB+ VRAM. Pre-tuned GPU profiles are included for optimal performance. Validated: 228 tok/s prompt on GTX 1060.'
      }
      if (lower.includes('what is kimari') || lower.includes('about') || lower.includes('kimari')) {
        return 'Kimari is an open-source framework for running local LLMs on older NVIDIA GPUs. It provides a CLI-first workflow, OpenAI-compatible endpoint at http://127.0.0.1:11435/v1, Gateway Dashboard, and GPU-specific profiles. MIT licensed.'
      }
      if (lower.includes('ollama') || lower.includes('compare') || lower.includes('difference') || lower.includes('vs')) {
        return 'Unlike Ollama, Kimari focuses specifically on older GPU support with pre-tuned profiles, includes an integrated Gateway Dashboard for monitoring, and provides GPU-specific optimization. Kimari is optimized for GTX 1060/1080 era hardware.'
      }
      if (lower.includes('open webui') || lower.includes('integration') || lower.includes('continue')) {
        return 'Kimari provides OpenAI-compatible endpoint that works with Open WebUI, Continue.dev, and OpenClaw. Run: kimari integrations generate --target openwebui to generate the configuration.'
      }
      if (lower.includes('speed') || lower.includes('performance') || lower.includes('benchmark') || lower.includes('fast')) {
        return 'GTX 1060 6GB: 228 tok/s prompt, 73 tok/s generation. GTX 1080 8GB: 310 tok/s prompt, 98 tok/s generation. Use kimari optimize for GPU-specific settings and kimari perf --matrix to compare all modes.'
      }
      return 'Kimari is a framework for running local LLMs on older NVIDIA GPUs. It uses llama.cpp/GGUF runtime with an OpenAI-compatible endpoint. Currently v0.1.82-alpha. Ask me about installation, GPU support, integrations, or performance!'
    }

    // Simulate network delay then show response
    setTimeout(() => {
      setIsLoading(false)
      setIsTyping(true)
      setTypingText('')
      const fullText = getSimulatedResponse(userMsg)
      let charIndex = 0
      typingRef.current = setInterval(() => {
        charIndex++
        if (charIndex >= fullText.length) {
          if (typingRef.current) clearInterval(typingRef.current)
          setMessages(prev => [...prev, { role: 'assistant', content: fullText }])
          setTypingText('')
          setIsTyping(false)
        } else {
          setTypingText(fullText.slice(0, charIndex))
        }
      }, 20)
    }, 800 + Math.random() * 600)
  }, [isLoading, isTyping])

  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return (
    <Card className="overflow-hidden backdrop-blur-xl bg-white/5 dark:bg-white/5 border border-white/10 shadow-[0_0_0_1px_rgba(59,130,246,0.05),0_8px_32px_rgba(0,0,0,0.1)]">
      <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px">
        <div className="bg-card rounded-t-lg">
          <div className="px-4 py-3 flex items-center justify-between border-b border-border/30">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-semibold">Ask Kimari AI</h3>
                <p className="text-[10px] text-muted-foreground">Powered by local AI knowledge</p>
              </div>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={clearChat}>
                    <Trash2 className="w-3.5 h-3.5 text-muted-foreground" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Clear conversation</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </div>

      <CardContent className="p-0">
        <ScrollArea className="h-80">
          <div ref={scrollRef} className="p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-8">
                <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center mx-auto mb-3">
                  <MessageCircle className="w-6 h-6 text-blue-500" />
                </div>
                <p className="text-sm text-muted-foreground mb-4">Ask anything about Kimari</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {chatSuggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => sendMessage(s)}
                      className="px-3 py-1.5 text-xs rounded-full border border-blue-500/20 bg-blue-500/5 text-blue-600 dark:text-blue-400 hover:bg-blue-500/10 transition-all duration-200 hover:scale-105"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-6 h-6 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0 mt-1">
                    <Bot className="w-3.5 h-3.5 text-blue-500" />
                  </div>
                )}
                <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                    : 'bg-muted/50 border border-border/30'
                }`}>
                  {msg.content}
                </div>
              </motion.div>
            ))}
            {(isLoading || isTyping) && (
              <div className="flex gap-2 justify-start">
                <div className="w-6 h-6 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-3.5 h-3.5 text-blue-500" />
                </div>
                <div className="bg-muted/50 border border-border/30 rounded-2xl px-4 py-3 min-w-[80px]">
                  {isLoading ? (
                    <div className="flex items-center gap-1.5">
                      <motion.div className="w-1.5 h-1.5 rounded-full bg-blue-500" animate={{ scale: [1, 1.3, 1] }} transition={{ duration: 0.8, repeat: Infinity, delay: 0 }} />
                      <motion.div className="w-1.5 h-1.5 rounded-full bg-blue-500" animate={{ scale: [1, 1.3, 1] }} transition={{ duration: 0.8, repeat: Infinity, delay: 0.2 }} />
                      <motion.div className="w-1.5 h-1.5 rounded-full bg-blue-500" animate={{ scale: [1, 1.3, 1] }} transition={{ duration: 0.8, repeat: Infinity, delay: 0.4 }} />
                    </div>
                  ) : (
                    <span className="text-sm text-muted-foreground">
                      {typingText}<span className="animate-pulse text-blue-500">▊</span>
                    </span>
                  )}
                </div>
              </div>
            )}
            {error && (
              <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
                <button onClick={() => sendMessage(messages[messages.length - 1]?.content || '')} className="ml-auto text-xs underline hover:text-red-300">
                  Retry
                </button>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="border-t border-border/30 p-3">
          <form onSubmit={(e) => { e.preventDefault(); sendMessage(input) }} className="flex gap-2">
            <div className="flex-1">
              <FloatingLabelInput
                label="Ask about Kimari..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading || isTyping}
              />
            </div>
            <RippleButton
              type="submit"
              disabled={!input.trim() || isLoading || isTyping}
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white px-3 rounded-lg"
            >
              <Send className="w-4 h-4" />
            </RippleButton>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}

// ─── System Requirements Checker ────────────────────────────────────────────

function SystemRequirementsChecker() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-40px' })

  return (
    <div ref={ref}>
      <Card className="backdrop-blur-xl bg-white/5 dark:bg-white/5 border border-white/10 shadow-[0_0_0_1px_rgba(59,130,246,0.05),0_8px_32px_rgba(0,0,0,0.1)]">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Monitor className="w-4 h-4 text-blue-500" /> System Requirements Check
          </CardTitle>
          <CardDescription>Simulated compatibility check</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {sysRequirements.map((req, i) => (
            <motion.div
              key={req.name}
              initial={{ opacity: 0, x: -20 }}
              animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
              transition={{ delay: i * 0.12, duration: 0.4 }}
              className="flex items-center gap-3 p-2.5 rounded-lg border border-border/30 hover:border-blue-500/20 transition-colors"
            >
              {req.status === 'pass' ? (
                <motion.div initial={{ scale: 0 }} animate={isInView ? { scale: 1 } : { scale: 0 }} transition={{ delay: i * 0.12 + 0.3, type: 'spring', stiffness: 300 }}>
                  <CheckCircle2 className="w-5 h-5 text-blue-500" />
                </motion.div>
              ) : req.status === 'recommended' ? (
                <motion.div initial={{ scale: 0 }} animate={isInView ? { scale: 1 } : { scale: 0 }} transition={{ delay: i * 0.12 + 0.3, type: 'spring', stiffness: 300 }}>
                  <AlertTriangle className="w-5 h-5 text-amber-500" />
                </motion.div>
              ) : (
                <motion.div initial={{ scale: 0 }} animate={isInView ? { scale: 1 } : { scale: 0 }} transition={{ delay: i * 0.12 + 0.3, type: 'spring', stiffness: 300 }}>
                  <XCircle className="w-5 h-5 text-red-500" />
                </motion.div>
              )}
              <span className="text-sm flex-1">{req.name}</span>
              <Badge variant="outline" className={`text-[10px] ${
                req.status === 'pass' ? 'border-blue-500/20 text-blue-500' :
                req.status === 'recommended' ? 'border-amber-500/20 text-amber-500' :
                'border-red-500/20 text-red-500'
              }`}>
                {req.status === 'pass' ? 'PASS' : req.status === 'recommended' ? 'RECOMMENDED' : 'MISSING'}
              </Badge>
            </motion.div>
          ))}
          <div className="pt-2">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="font-medium">Compatibility Score</span>
              <span className="text-blue-500 font-bold font-mono">85%</span>
            </div>
            <Progress value={85} className="h-2" />
          </div>
          <p className="text-xs text-muted-foreground flex items-center gap-1.5">
            <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
            This is a simulated check. Run <code className="bg-muted/50 px-1.5 py-0.5 rounded text-[10px] font-mono">kimari doctor --deep</code> for real diagnostics.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

// ─── Section Heading ─────────────────────────────────────────────────────────

function SectionHeading({ title, subtitle, id }: { title: string; subtitle?: string; id?: string }) {
  return (
    <div className="text-center mb-14" id={id}>
      <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-3">{title}</h2>
      <div className="w-10 h-[3px] bg-gradient-to-r from-blue-500 to-transparent mx-auto mb-4 rounded-full" />
      {subtitle && <p className="text-muted-foreground max-w-lg mx-auto">{subtitle}</p>}
    </div>
  )
}

// ─── Glass Card (Enhanced) ────────────────────────────────────────────────────

function GlassCard({ children, className = '', glow = false }: { children: React.ReactNode; className?: string; glow?: boolean }) {
  return (
    <div className="relative group">
      {glow && (
        <>
          {/* Animated shimmer border */}
          <div className="absolute -inset-0.5 rounded-xl overflow-hidden opacity-0 group-hover:opacity-100 transition-opacity duration-500">
            <div className="absolute inset-[-100%] animate-shimmer-rotate bg-[conic-gradient(from_0deg,transparent_0_340deg,#3b82f6_360deg)]" />
          </div>
          {/* Blur overlay for shimmer */}
          <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/20 to-blue-600/20 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        </>
      )}
      <div className={`relative backdrop-blur-xl bg-white/[0.03] dark:bg-white/[0.03] border border-white/[0.06] hover:border-blue-500/20 rounded-xl shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_2px_8px_rgba(0,0,0,0.1)] transition-all duration-300 group-hover:shadow-[inset_0_1px_0_rgba(59,130,246,0.1),0_2px_16px_rgba(59,130,246,0.08)] ${className}`}>
        {/* Inner glow effect on hover */}
        <div className="absolute inset-0 rounded-xl bg-gradient-to-b from-blue-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
        <div className="relative">{children}</div>
      </div>
    </div>
  )
}

// ─── Code Snippet Showcase ────────────────────────────────────────────────────

function CodeSnippetShowcase() {
  const [activeTab, setActiveTab] = useState<'python' | 'curl' | 'javascript'>('python')
  const [copied, setCopied] = useState(false)
  const [visibleLines, setVisibleLines] = useState(0)
  const { toast } = useToast()

  const currentCode = codeSnippets[activeTab]
  const codeLines = currentCode.split('\n')

  useEffect(() => {
    setVisibleLines(0)
    let lineIdx = 0
    const interval = setInterval(() => {
      lineIdx++
      setVisibleLines(lineIdx)
      if (lineIdx >= codeLines.length) clearInterval(interval)
    }, 50)
    return () => clearInterval(interval)
  }, [activeTab, codeLines.length])

  const handleCopy = () => {
    navigator.clipboard.writeText(codeSnippets[activeTab])
    setCopied(true)
    toast({ title: 'Copied to clipboard!', description: `${activeTab} code snippet copied` })
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <GlassCard glow className="overflow-hidden">
      <div className="px-4 py-3 flex items-center justify-between border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <Code2 className="w-4 h-4 text-blue-500" />
          <span className="text-sm font-semibold">Integration Code</span>
          <Badge className="text-[10px] px-1.5 py-0 bg-blue-500/10 text-blue-500 border-blue-500/20">OpenAI-compatible</Badge>
        </div>
        <button onClick={handleCopy} className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all active:scale-95">
          {copied ? <Check className="w-3.5 h-3.5 text-blue-400" /> : <Copy className="w-3.5 h-3.5" />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <div className="flex border-b border-white/[0.06]">
        {(['python', 'curl', 'javascript'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-xs font-medium transition-all breathing-glow ${
              activeTab === tab
                ? 'text-blue-500 border-b-2 border-blue-500 bg-blue-500/5'
                : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.02]'
            }`}
          >
            {tab === 'python' ? 'Python' : tab === 'curl' ? 'cURL' : 'JavaScript'}
          </button>
        ))}
      </div>
      <div className="p-4 bg-zinc-950/50">
        <pre className="text-sm font-mono text-zinc-300 whitespace-pre-wrap leading-relaxed overflow-x-auto">
          <code>{codeLines.slice(0, visibleLines).map((line, i) => (
            <div key={i} className="code-type-line code-line rounded-sm" style={{ animationDelay: `${i * 0.03}s` }}>
              <span className="code-line-number">{i + 1}</span>
              {line}
            </div>
          ))}</code>
        </pre>
      </div>
    </GlassCard>
  )
}

// ─── API Health Checker ───────────────────────────────────────────────────────

function APIHealthChecker() {
  const [isChecking, setIsChecking] = useState(false)
  const [showResult, setShowResult] = useState(false)
  const [displayedText, setDisplayedText] = useState('')
  const [latency, setLatency] = useState(0)

  const runCheck = useCallback(() => {
    setIsChecking(true)
    setShowResult(false)
    setDisplayedText('')
    setLatency(0)

    // Simulate latency progress
    let progress = 0
    const latencyInterval = setInterval(() => {
      progress += Math.random() * 15 + 5
      if (progress >= 42) progress = 42
      setLatency(Math.round(progress))
      if (progress >= 42) clearInterval(latencyInterval)
    }, 100)

    // Simulate typing effect
    setTimeout(() => {
      setIsChecking(false)
      setShowResult(true)
      let i = 0
      const text = healthCheckResponse
      const typeInterval = setInterval(() => {
        setDisplayedText(text.slice(0, i + 1))
        i++
        if (i >= text.length) clearInterval(typeInterval)
      }, 15)
    }, 1500)
  }, [])

  return (
    <GlassCard glow className="overflow-hidden">
      <div className="px-4 py-3 flex items-center justify-between border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-500" />
          <span className="text-sm font-semibold">API Health Check</span>
          {showResult && (
            <span className="flex items-center gap-1 text-[10px] text-blue-500 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
              healthy
            </span>
          )}
        </div>
        <Button size="sm" variant="ghost" onClick={runCheck} disabled={isChecking} className="text-xs gap-1.5 hover:bg-blue-500/10 hover:text-blue-500">
          {isChecking ? (
            <><motion.div className="w-3 h-3 border-2 border-blue-500/30 border-t-blue-500 rounded-full" animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }} /> Checking...</>
          ) : (
            <><Zap className="w-3 h-3" /> Run Check</>
          )}
        </Button>
      </div>
      <div className="p-4 bg-zinc-950/50 font-mono text-sm min-h-[200px]">
        {isChecking && (
          <div className="space-y-3">
            <p className="text-amber-400">Pinging http://127.0.0.1:11435/v1 ...</p>
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Latency</span>
                <span className="text-blue-400">{latency}ms</span>
              </div>
              <Progress value={(latency / 50) * 100} className="h-1.5" />
            </div>
          </div>
        )}
        {showResult && (
          <pre className="text-blue-300/80 whitespace-pre-wrap leading-relaxed">
            {displayedText}
            {displayedText.length < healthCheckResponse.length && <span className="animate-pulse">▊</span>}
          </pre>
        )}
        {!isChecking && !showResult && (
          <div className="flex items-center justify-center h-[160px] text-muted-foreground text-sm">
            <p>Click "Run Check" to simulate an API health check</p>
          </div>
        )}
      </div>
      {showResult && displayedText.length >= healthCheckResponse.length && (
        <div className="px-4 py-2 border-t border-white/[0.06] text-[10px] text-muted-foreground flex items-center gap-1.5">
          <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
          Simulated response. Run <code className="bg-white/5 px-1 rounded font-mono">kimari status</code> for real server info.
        </div>
      )}
    </GlassCard>
  )
}

// ─── Version Timeline ─────────────────────────────────────────────────────────

function VersionTimeline() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-40px' })

  const typeConfig = {
    release: { color: 'bg-blue-500', border: 'border-blue-500/30', badge: 'Release' },
    feature: { color: 'bg-cyan-500', border: 'border-cyan-500/30', badge: 'Feature' },
    milestone: { color: 'bg-amber-500', border: 'border-amber-500/30', badge: 'Milestone' },
    current: { color: 'bg-red-500', border: 'border-red-500/30', badge: 'Current' },
  }

  return (
    <div ref={ref} className="relative max-w-3xl mx-auto">
      {/* Timeline line */}
      <div className="absolute left-4 md:left-1/2 md:-translate-x-px top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500/50 via-blue-600/30 to-transparent" />

      {versionTimeline.map((item, i) => {
        const config = typeConfig[item.type]
        const isLeft = i % 2 === 0
        return (
          <motion.div
            key={item.version}
            initial={{ opacity: 0, x: isLeft ? -30 : 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: isLeft ? -30 : 30 }}
            transition={{ delay: i * 0.15, duration: 0.5 }}
            className={`relative flex items-start gap-4 mb-8 md:gap-0 ${
              isLeft ? 'md:flex-row' : 'md:flex-row-reverse'
            }`}
          >
            {/* Dot */}
            <div className={`absolute left-4 md:left-1/2 -translate-x-1/2 w-3 h-3 rounded-full ${config.color} z-10 mt-6 ${
              item.type === 'current' ? 'animate-pulse shadow-lg shadow-red-500/50' : ''
            }`} />

            {/* Content */}
            <div className={`ml-10 md:ml-0 md:w-[calc(50%-2rem)] ${isLeft ? 'md:pr-8 md:text-right' : 'md:pl-8 md:text-left'}`}>
              <GlassCard className="p-4">
                <div className={`flex items-center gap-2 mb-2 ${isLeft ? 'md:justify-end' : 'md:justify-start'}`}>
                  <Badge variant="outline" className={`text-[10px] ${config.border} ${config.color.replace('bg-', 'text-')}`}>{config.badge}</Badge>
                  <span className="text-xs font-mono text-muted-foreground">{item.date}</span>
                </div>
                <h4 className="text-sm font-bold mb-1">{item.version} — {item.title}</h4>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </GlassCard>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

// ─── Architecture Diagram ─────────────────────────────────────────────────────

function ArchitectureDiagram() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-40px' })

  return (
    <div ref={ref} className="relative max-w-4xl mx-auto">
      {/* SVG animated dashed connections */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
        {/* Vertical center line */}
        <line x1="50%" y1="8%" x2="50%" y2="82%" stroke="rgba(59,130,246,0.15)" strokeWidth="1" strokeDasharray="6 4" className="animate-dash-flow" />
        {/* Horizontal line */}
        <line x1="15%" y1="48%" x2="85%" y2="48%" stroke="rgba(59,130,246,0.12)" strokeWidth="1" strokeDasharray="6 4" className="animate-dash-flow" />
        {/* Dashboard to API */}
        <line x1="25%" y1="38%" x2="50%" y2="30%" stroke="rgba(59,130,246,0.1)" strokeWidth="1" strokeDasharray="4 4" className="animate-dash-flow" />
        {/* CLI to Runtime */}
        <line x1="75%" y1="55%" x2="50%" y2="60%" stroke="rgba(59,130,246,0.1)" strokeWidth="1" strokeDasharray="4 4" className="animate-dash-flow" />
      </svg>

      {/* Flowing dot animation on vertical line */}
      <motion.div
        className="absolute left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-blue-500 shadow-lg shadow-blue-500/50"
        style={{ zIndex: 1 }}
        animate={{ top: ['8%', '78%'] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut', repeatDelay: 1 }}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
        {/* Left column: Dashboard */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="flex items-center"
        >
          <GlassCard glow className="p-4 w-full text-center">
            <Monitor className="w-5 h-5 text-blue-500 mx-auto mb-2" />
            <h4 className="text-xs font-bold">Gateway Dashboard</h4>
            <p className="text-[10px] text-muted-foreground mt-1">http://127.0.0.1:3105</p>
          </GlassCard>
        </motion.div>

        {/* Center column: Main flow */}
        <div className="space-y-4">
          {[
            { label: 'Your Applications', sub: 'Open WebUI · Continue.dev', icon: Layers, delay: 0 },
            { label: 'OpenAI-Compatible API', sub: 'http://127.0.0.1:11435/v1', icon: Server, delay: 0.1 },
            { label: 'Kimari Runtime', sub: 'llama-server · CUDA · GGUF', icon: Cpu, delay: 0.2 },
            { label: 'NVIDIA Hardware', sub: 'GPU · VRAM · CUDA Cores', icon: HardDrive, delay: 0.3 },
          ].map((node, i) => (
            <motion.div
              key={node.label}
              initial={{ opacity: 0, y: 15 }}
              animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 15 }}
              transition={{ delay: node.delay, duration: 0.4 }}
            >
              <GlassCard glow className={`p-3 text-center ${i === 1 ? 'border-blue-500/20 bg-blue-500/[0.03]' : ''}`}>
                <node.icon className={`w-5 h-5 mx-auto mb-1.5 ${i === 1 ? 'text-blue-500' : 'text-muted-foreground'}`} />
                <h4 className="text-xs font-bold">{node.label}</h4>
                <p className="text-[10px] text-muted-foreground mt-0.5 font-mono">{node.sub}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Right column: CLI */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 20 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="flex items-center"
        >
          <GlassCard glow className="p-4 w-full text-center">
            <Terminal className="w-5 h-5 text-blue-500 mx-auto mb-2" />
            <h4 className="text-xs font-bold">CLI Commands</h4>
            <p className="text-[10px] text-muted-foreground mt-1">kimari doctor · start · pull</p>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  )
}

// ─── GPU Benchmark Simulator ──────────────────────────────────────────────────

function GPUBenchmarkSimulator() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-40px' })

  return (
    <div ref={ref}>
      <TooltipProvider delayDuration={200}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Prompt Processing Chart */}
          <GlassCard glow className="p-4">
            <h4 className="text-sm font-semibold mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-500" /> Prompt Processing (tok/s)
            </h4>
            <div className="space-y-3">
              {gpuBenchmarkData.map((gpu, i) => (
                <motion.div
                  key={gpu.gpu}
                  initial={{ opacity: 0, x: -20 }}
                  animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
                  transition={{ delay: i * 0.1, duration: 0.4 }}
                >
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="cursor-help">
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-muted-foreground">{gpu.gpu}</span>
                          <span className="font-mono font-bold" style={{ color: gpu.color }}>{gpu.promptSpeed} tok/s</span>
                        </div>
                        <div className="h-2.5 rounded-full bg-white/[0.04] overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={isInView ? { width: `${(gpu.promptSpeed / 1000) * 100}%` } : { width: 0 }}
                            transition={{ delay: i * 0.1 + 0.3, duration: 0.8, ease: 'easeOut' }}
                            className="h-full rounded-full"
                            style={{ background: `linear-gradient(to right, ${gpu.color}88, ${gpu.color})` }}
                          />
                        </div>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="text-xs">
                      <div className="space-y-1">
                        <p className="font-semibold">{gpu.gpu}</p>
                        <p>Model: {gpu.model}</p>
                        <p>Quantization: {gpu.quant}</p>
                        <p>VRAM: {gpu.vram} GB</p>
                        <p className="text-blue-400 font-mono">Prompt: {gpu.promptSpeed} tok/s</p>
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </motion.div>
              ))}
            </div>
          </GlassCard>

          {/* Token Generation Chart */}
          <GlassCard glow className="p-4">
            <h4 className="text-sm font-semibold mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-600" /> Token Generation (tok/s)
            </h4>
            <div className="space-y-3">
              {gpuBenchmarkData.map((gpu, i) => (
                <motion.div
                  key={gpu.gpu}
                  initial={{ opacity: 0, x: 20 }}
                  animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 20 }}
                  transition={{ delay: i * 0.1, duration: 0.4 }}
                >
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="cursor-help">
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-muted-foreground">{gpu.gpu}</span>
                          <span className="font-mono font-bold" style={{ color: gpu.color }}>{gpu.genSpeed} tok/s</span>
                        </div>
                        <div className="h-2.5 rounded-full bg-white/[0.04] overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={isInView ? { width: `${(gpu.genSpeed / 250) * 100}%` } : { width: 0 }}
                            transition={{ delay: i * 0.1 + 0.3, duration: 0.8, ease: 'easeOut' }}
                            className="h-full rounded-full"
                            style={{ background: `linear-gradient(to right, ${gpu.color}88, ${gpu.color})` }}
                          />
                        </div>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="text-xs">
                      <div className="space-y-1">
                        <p className="font-semibold">{gpu.gpu}</p>
                        <p>Model: {gpu.model}</p>
                        <p>Quantization: {gpu.quant}</p>
                        <p>VRAM: {gpu.vram} GB</p>
                        <p className="text-blue-400 font-mono">Generation: {gpu.genSpeed} tok/s</p>
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </div>
      </TooltipProvider>
      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-4 justify-center">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
        GTX 1060 results are validated; others are projected estimates.
      </div>
      <div className="flex flex-wrap gap-3 justify-center mt-3">
        {gpuBenchmarkData.map((gpu) => (
          <span key={gpu.gpu} className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: gpu.color }} />
            {gpu.gpu} ({gpu.model})
          </span>
        ))}
      </div>
    </div>
  )
}

// ─── Copy Config Button ──────────────────────────────────────────────────────

function CopyConfigButton({ profile }: { profile: { name: string; gpu: string; vram: string; quant: string; ctx: number } }) {
  const [copied, setCopied] = useState(false)
  const { toast } = useToast()

  const config = JSON.stringify({
    profile: profile.name,
    gpu: profile.gpu,
    vram: profile.vram,
    quantization: profile.quant,
    context_length: profile.ctx,
  }, null, 2)

  const handleCopy = () => {
    navigator.clipboard.writeText(config)
    setCopied(true)
    toast({ title: 'Copied to clipboard!', description: `${profile.name} config JSON copied` })
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-white/10 transition-all active:scale-90"
            aria-label="Copy config"
          >
            {copied ? <Check className="w-3 h-3 text-blue-400" /> : <Copy className="w-3 h-3 text-muted-foreground" />}
          </button>
        </TooltipTrigger>
        <TooltipContent side="top" className="text-xs">
          {copied ? 'Copied!' : 'Copy JSON config'}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

// ─── GPU VRAM Calculator ──────────────────────────────────────────────────────

function GPUVRAMCalculator() {
  const [selectedGpu, setSelectedGpu] = useState('gtx1060')
  const [selectedModel, setSelectedModel] = useState('tinyllama')

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const gpuParam = params.get('gpu')
    const modelParam = params.get('model')
    if (gpuParam && vramCalculatorGPUs.find(g => g.id === gpuParam)) setSelectedGpu(gpuParam)
    if (modelParam && vramCalculatorModels.find(m => m.id === modelParam)) setSelectedModel(modelParam)
  }, [])
  /* eslint-enable react-hooks/set-state-in-effect */
  const [shareCopied, setShareCopied] = useState(false)
  const { toast } = useToast()

  const gpu = vramCalculatorGPUs.find(g => g.id === selectedGpu)!
  const model = vramCalculatorModels.find(m => m.id === selectedModel)!
  const fits = gpu.vram >= model.vramRequired
  const usagePercent = Math.min((model.vramRequired / gpu.vram) * 100, 100)
  const recommendedCtx = gpu.vram >= 12 ? 16384 : gpu.vram >= 8 ? 8192 : 4096
  const recommendedQuant = gpu.vram >= 12 ? 'Q5_K_M' : gpu.vram >= 8 ? 'Q4_K_M' : 'IQ4_XS'

  // Get optimization tips for this GPU+model combo
  const tips = vramOptimizationTips[selectedGpu]?.[selectedModel] || []

  // Share config
  const handleShareConfig = () => {
    const url = new URL(window.location.href)
    url.searchParams.set('gpu', selectedGpu)
    url.searchParams.set('model', selectedModel)
    navigator.clipboard.writeText(url.toString())
    setShareCopied(true)
    toast({ title: 'Config link copied!', description: 'Share this URL to pre-select this GPU/model combo' })
    setTimeout(() => setShareCopied(false), 2000)
  }

  return (
    <GlassCard glow className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h4 className="text-sm font-semibold flex items-center gap-2">
          <MemoryStick className="w-4 h-4 text-blue-500" /> GPU VRAM Calculator
        </h4>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" onClick={handleShareConfig} className="h-7 gap-1.5 text-xs hover:bg-blue-500/10 hover:text-blue-500">
                {shareCopied ? <Check className="w-3.5 h-3.5 text-blue-400" /> : <Share2 className="w-3.5 h-3.5" />}
                {shareCopied ? 'Copied!' : 'Share'}
              </Button>
            </TooltipTrigger>
            <TooltipContent className="text-xs">Copy shareable config link</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="text-xs text-muted-foreground mb-1.5 block">Select GPU</label>
          <Select value={selectedGpu} onValueChange={setSelectedGpu}>
            <SelectTrigger className="w-full bg-muted/30 border-border/30">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {vramCalculatorGPUs.map(g => (
                <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mb-1.5 block">Select Model</label>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-full bg-muted/30 border-border/30">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {vramCalculatorModels.map(m => (
                <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* VRAM Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="text-muted-foreground">VRAM Usage</span>
          <span className="font-mono">
            <span className={fits ? 'text-blue-500' : 'text-red-500'}>{model.vramRequired} GB</span>
            {' / '}
            <span className="text-foreground">{gpu.vram} GB</span>
          </span>
        </div>
        <div className="h-4 rounded-full bg-muted/50 overflow-hidden border border-border/30">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${usagePercent}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            className={`h-full rounded-full ${fits ? 'bg-gradient-to-r from-blue-600 to-blue-600' : 'bg-gradient-to-r from-red-600 to-orange-500'}`}
          />
        </div>
      </div>

      {/* Fit indicator */}
      <div className={`flex items-center gap-2 p-3 rounded-lg border mb-4 ${fits ? 'border-blue-500/20 bg-blue-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
        {fits ? (
          <>
            <CheckCircle2 className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-sm font-medium text-blue-500">Model fits!</p>
              <p className="text-xs text-muted-foreground">Runs comfortably on {gpu.name}</p>
            </div>
          </>
        ) : (
          <>
            <XCircle className="w-5 h-5 text-red-500" />
            <div>
              <p className="text-sm font-medium text-red-500">Model doesn&apos;t fit</p>
              <p className="text-xs text-muted-foreground">Not enough VRAM on {gpu.name}</p>
            </div>
          </>
        )}
      </div>

      {/* Recommendations */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="p-3 rounded-lg bg-muted/30 border border-border/30">
          <p className="text-[10px] text-muted-foreground mb-1">Recommended <TechTermTooltip term="Quantization" /></p>
          <p className="text-sm font-mono font-bold text-blue-500">{recommendedQuant}</p>
        </div>
        <div className="p-3 rounded-lg bg-muted/30 border border-border/30">
          <p className="text-[10px] text-muted-foreground mb-1">Max <TechTermTooltip term="Context Length" /></p>
          <p className="text-sm font-mono font-bold text-blue-500">{fmtNum(recommendedCtx)} tokens</p>
        </div>
      </div>

      {/* VRAM Optimization Tips */}
      {tips.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-1.5 mb-2.5">
            <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
            <p className="text-xs font-semibold text-amber-500">Optimization Tips</p>
          </div>
          <div className="space-y-2">
            {tips.map((tip, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1, duration: 0.3 }}
                className="p-2.5 rounded-lg border border-amber-500/15 bg-amber-500/[0.03]"
              >
                <p className="text-xs font-medium">{tip.tip}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">{tip.detail}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      <p className="text-[10px] text-muted-foreground mt-3 flex items-center gap-1.5">
        <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
        Estimated VRAM values. Actual usage depends on context length and batch size.
      </p>
    </GlassCard>
  )
}

// ─── Install Command Generator ────────────────────────────────────────────────

function InstallCommandGenerator() {
  const [selectedOS, setSelectedOS] = useState('linux')
  const [selectedGPU, setSelectedGPU] = useState('detected')
  const [selectedModel, setSelectedModel] = useState('test')
  const [copied, setCopied] = useState(false)
  const { toast } = useToast()

  const os = installOSOptions.find(o => o.id === selectedOS)!
  const gpu = installGPUOptions.find(g => g.id === selectedGPU)!
  const modelOpt = installModelOptions.find(m => m.id === selectedModel)!

  const command = useMemo(() => {
    let cmd = 'curl -fsSL https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.sh | bash'
    const flags: string[] = []
    if (os.flag) flags.push(os.flag)
    if (gpu.flag) flags.push(gpu.flag)
    if (modelOpt.flag) flags.push(modelOpt.flag)
    if (flags.length > 0) cmd += ' -- ' + flags.join(' ')
    return cmd
  }, [os.flag, gpu.flag, modelOpt.flag])

  const handleCopy = () => {
    navigator.clipboard.writeText(command)
    setCopied(true)
    toast({ title: 'Copied to clipboard!', description: 'Install command copied' })
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <GlassCard className="p-5">
      <h4 className="text-sm font-semibold mb-4 flex items-center gap-2">
        <Settings className="w-4 h-4 text-blue-500" /> Custom Install Command
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <div>
          <label className="text-[10px] text-muted-foreground mb-1 block">OS</label>
          <div className="flex gap-1">
            {installOSOptions.map(opt => (
              <button
                key={opt.id}
                onClick={() => setSelectedOS(opt.id)}
                className={`flex-1 px-2 py-1.5 text-[10px] rounded-md border transition-all duration-200 ${
                  selectedOS === opt.id
                    ? 'border-blue-500/30 bg-blue-500/10 text-blue-500 font-medium'
                    : 'border-border/30 text-muted-foreground hover:border-blue-500/20 hover:text-foreground'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-[10px] text-muted-foreground mb-1 block">GPU Detection</label>
          <div className="flex gap-1">
            {installGPUOptions.map(opt => (
              <button
                key={opt.id}
                onClick={() => setSelectedGPU(opt.id)}
                className={`flex-1 px-2 py-1.5 text-[10px] rounded-md border transition-all duration-200 ${
                  selectedGPU === opt.id
                    ? 'border-blue-500/30 bg-blue-500/10 text-blue-500 font-medium'
                    : 'border-border/30 text-muted-foreground hover:border-blue-500/20 hover:text-foreground'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-[10px] text-muted-foreground mb-1 block">Model</label>
          <div className="flex gap-1">
            {installModelOptions.map(opt => (
              <button
                key={opt.id}
                onClick={() => setSelectedModel(opt.id)}
                className={`flex-1 px-2 py-1.5 text-[10px] rounded-md border transition-all duration-200 ${
                  selectedModel === opt.id
                    ? 'border-blue-500/30 bg-blue-500/10 text-blue-500 font-medium'
                    : 'border-border/30 text-muted-foreground hover:border-blue-500/20 hover:text-foreground'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="group relative bg-zinc-950 dark:bg-zinc-950 border border-zinc-800 rounded-lg p-3 font-mono text-sm">
        <div className="flex items-start gap-2">
          <span className="text-blue-400 select-none shrink-0">$</span>
          <span className="text-zinc-200 dark:text-zinc-200 break-all text-xs leading-relaxed">{command}</span>
        </div>
        <button onClick={handleCopy} className="absolute top-2 right-2 p-1.5 rounded-md hover:bg-white/10 transition-all active:scale-90">
          {copied ? <Check className="w-3.5 h-3.5 text-blue-400" /> : <Copy className="w-3.5 h-3.5 text-zinc-400" />}
        </button>
      </div>
    </GlassCard>
  )
}

// ─── Model Performance Estimator ──────────────────────────────────────────────

function ModelPerformanceEstimator() {
  const [selectedGpu, setSelectedGpu] = useState('gtx1060')
  const [selectedModel, setSelectedModel] = useState('tinyllama')
  const [selectedTask, setSelectedTask] = useState('chat')

  const gpu = performanceEstimatorGPUs.find(g => g.id === selectedGpu)!
  const model = performanceEstimatorModels.find(m => m.id === selectedModel)!
  const task = performanceEstimatorTasks.find(t => t.id === selectedTask)!

  // Calculate estimated performance based on GPU/model/task
  const baseFactor = gpu.cudaCores / 1280 // normalized to GTX 1060
  const modelFactor = 1.1 / model.params // smaller models = faster
  const taskMultipliers: Record<string, { latency: number; tokPerSec: number; ttft: number }> = {
    chat: { latency: 1, tokPerSec: 1, ttft: 1 },
    code: { latency: 1.3, tokPerSec: 0.85, ttft: 1.2 },
    summary: { latency: 0.8, tokPerSec: 1.1, ttft: 0.9 },
    translate: { latency: 0.9, tokPerSec: 0.95, ttft: 1.1 },
  }
  const mult = taskMultipliers[selectedTask]

  const latency = Math.round(180 / (baseFactor * modelFactor) * mult.latency)
  const tokPerSec = Math.round(73 * baseFactor * modelFactor * mult.tokPerSec)
  const ttft = Math.round(120 / (baseFactor * modelFactor) * mult.ttft)
  const maxContext = gpu.vram >= 12 ? 16384 : gpu.vram >= 8 ? 8192 : 4096

  const metrics = [
    { label: 'Latency', value: `${latency}ms`, barPercent: Math.min((latency / 300) * 100, 100), color: latency < 150 ? '#3b82f6' : latency < 250 ? '#f59e0b' : '#ef4444' },
    { label: 'Tokens/sec', value: `${tokPerSec} tok/s`, barPercent: Math.min((tokPerSec / 300) * 100, 100), color: tokPerSec > 100 ? '#3b82f6' : tokPerSec > 50 ? '#f59e0b' : '#ef4444' },
    { label: 'Time to First Token', value: `${ttft}ms`, barPercent: Math.min((ttft / 200) * 100, 100), color: ttft < 100 ? '#3b82f6' : ttft < 150 ? '#f59e0b' : '#ef4444' },
    { label: 'Max Context', value: `${fmtNum(maxContext)} tokens`, barPercent: (maxContext / 16384) * 100, color: '#60a5fa' },
  ]

  return (
    <GlassCard glow className="p-6">
      <h4 className="text-sm font-semibold mb-5 flex items-center gap-2">
        <Gauge className="w-4 h-4 text-blue-500" /> Model Performance Estimator
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="text-xs text-muted-foreground mb-1.5 block">Select GPU</label>
          <Select value={selectedGpu} onValueChange={setSelectedGpu}>
            <SelectTrigger className="w-full bg-muted/30 border-border/30">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {performanceEstimatorGPUs.map(g => (
                <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mb-1.5 block">Select Model</label>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-full bg-muted/30 border-border/30">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {performanceEstimatorModels.map(m => (
                <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mb-1.5 block">Task Type</label>
          <div className="flex gap-1">
            {performanceEstimatorTasks.map(t => (
              <button
                key={t.id}
                onClick={() => setSelectedTask(t.id)}
                className={`flex-1 p-2 rounded-md border transition-all duration-200 flex flex-col items-center gap-1 ${
                  selectedTask === t.id
                    ? 'border-blue-500/30 bg-blue-500/10 text-blue-500'
                    : 'border-border/30 text-muted-foreground hover:border-blue-500/20'
                }`}
              >
                <t.icon className="w-3.5 h-3.5" />
                <span className="text-[9px] leading-tight">{t.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {metrics.map((metric) => (
          <div key={metric.label}>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-muted-foreground">{metric.label}</span>
              <span className="font-mono font-bold" style={{ color: metric.color }}>{metric.value}</span>
            </div>
            <div className="h-3 rounded-full bg-white/[0.04] overflow-hidden border border-border/20">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${metric.barPercent}%` }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
                className="h-full rounded-full"
                style={{ background: `linear-gradient(to right, ${metric.color}88, ${metric.color})` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 p-3 rounded-lg border border-amber-500/20 bg-amber-500/5">
        <div className="flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-medium text-amber-500">Estimated Performance</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">
              These are projected estimates based on GPU specs and model size, not actual benchmarks.
              Real performance depends on quantization, context length, system config, and batch size.
              Only GTX 1060 results have been validated on real hardware.
            </p>
          </div>
        </div>
      </div>
    </GlassCard>
  )
}

// ─── Section Navigation Mini-Map ─────────────────────────────────────────────

function SectionNavigationMiniMap({ activeSection }: { activeSection: string }) {
  return (
    <div className="fixed right-4 top-1/2 -translate-y-1/2 z-40 hidden xl:flex flex-col gap-2.5">
      {sectionIds.map((section) => (
        <button
          key={section.id}
          onClick={() => {
            const el = document.getElementById(section.id)
            if (el) el.scrollIntoView({ behavior: 'smooth' })
          }}
          className="group relative flex items-center justify-end"
          aria-label={`Navigate to ${section.label}`}
        >
          <span className="absolute right-6 px-2 py-1 rounded text-[10px] font-medium bg-muted/90 border border-border/50 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none shadow-lg">
            {section.label}
          </span>
          <div className={`w-2.5 h-2.5 rounded-full border-2 transition-all duration-300 ${
            activeSection === section.id
              ? 'bg-blue-500 border-blue-500 scale-125 shadow-lg shadow-blue-500/50'
              : 'bg-transparent border-zinc-600 hover:border-blue-500/50 hover:scale-110'
          }`} />
        </button>
      ))}
    </div>
  )
}

// ─── Page Load Splash Animation ──────────────────────────────────────────────

function PageLoadSplash({ onComplete }: { onComplete: () => void }) {
  const [phase, setPhase] = useState<'visible' | 'fading' | 'gone'>('visible')
  const [bootLines, setBootLines] = useState<string[]>([])
  const [lightAngle, setLightAngle] = useState(0)
  const [ringProgress, setRingProgress] = useState(0)
  const [logoPulse, setLogoPulse] = useState(false)

  const allBootLines = useMemo(() => [
    'INITIALIZING RUNTIME...',
    'CUDA BACKEND DETECTED ✓',
    'MODEL LOADED ✓',
    'SYSTEM READY',
  ], [])

  const onCompleteRef = useRef(onComplete)
  onCompleteRef.current = onComplete

  useEffect(() => {
    // Reset boot lines on effect start
    setBootLines([])

    // Animate the light orbit
    let angle = 0
    const angleInterval = setInterval(() => {
      angle = (angle + 6) % 360
      setLightAngle(angle)
      setRingProgress(Math.min(100, (angle / 360) * 100))
    }, 20)

    // Boot sequence typing
    let lineIdx = 0
    let fadeTimeout: ReturnType<typeof setTimeout> | null = null
    let goneTimeout: ReturnType<typeof setTimeout> | null = null
    const bootInterval = setInterval(() => {
      if (lineIdx < allBootLines.length) {
        setBootLines(prev => [...prev, allBootLines[lineIdx]])
        lineIdx++
      } else {
        clearInterval(bootInterval)
        setLogoPulse(true)
        fadeTimeout = setTimeout(() => {
          setPhase('fading')
          goneTimeout = setTimeout(() => {
            setPhase('gone')
            onCompleteRef.current()
          }, 600)
        }, 400)
      }
    }, 400)

    return () => {
      clearInterval(angleInterval)
      clearInterval(bootInterval)
      if (fadeTimeout) clearTimeout(fadeTimeout)
      if (goneTimeout) clearTimeout(goneTimeout)
    }
  }, [allBootLines])

  if (phase === 'gone') return null

  return (
    <AnimatePresence>
      {phase !== 'gone' && (
        <motion.div
          className={`fixed inset-0 z-[100] bg-zinc-950 flex items-center justify-center ${phase === 'fading' ? 'animate-splash-fade-out' : ''}`}
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="flex flex-col items-center gap-6">
            {/* Logo with orbiting light ring */}
            <div className="relative w-24 h-24">
              {/* SVG Ring with traveling light */}
              <svg className="absolute inset-0 w-full h-full -m-2" style={{ width: '120px', height: '120px', left: '-12px', top: '-12px' }} viewBox="0 0 120 120">
                {/* Background ring track */}
                <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(59,130,246,0.1)" strokeWidth="1.5" />
                {/* Progress ring */}
                <circle
                  cx="60" cy="60" r="54"
                  fill="none"
                  stroke="rgba(59,130,246,0.3)"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 54 * (ringProgress / 100)} ${2 * Math.PI * 54}`}
                  transform="rotate(-90 60 60)"
                  style={{ transition: 'stroke-dasharray 0.1s linear' }}
                />
                {/* Traveling light point */}
                <circle
                  cx={60 + 54 * Math.cos((lightAngle - 90) * (Math.PI / 180))}
                  cy={60 + 54 * Math.sin((lightAngle - 90) * (Math.PI / 180))}
                  r="4"
                  fill="#3b82f6"
                  style={{ filter: 'drop-shadow(0 0 8px rgba(59,130,246,0.8)) drop-shadow(0 0 20px rgba(59,130,246,0.4))' }}
                />
                {/* Light trail */}
                <circle
                  cx={60 + 54 * Math.cos((lightAngle - 90 - 15) * (Math.PI / 180))}
                  cy={60 + 54 * Math.sin((lightAngle - 90 - 15) * (Math.PI / 180))}
                  r="2.5"
                  fill="rgba(59,130,246,0.5)"
                  style={{ filter: 'drop-shadow(0 0 4px rgba(59,130,246,0.4))' }}
                />
                <circle
                  cx={60 + 54 * Math.cos((lightAngle - 90 - 30) * (Math.PI / 180))}
                  cy={60 + 54 * Math.sin((lightAngle - 90 - 30) * (Math.PI / 180))}
                  r="1.5"
                  fill="rgba(59,130,246,0.25)"
                />
              </svg>
              {/* Logo */}
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className={`w-full h-full rounded-2xl overflow-hidden ${logoPulse ? 'animate-pulse' : ''}`}
                style={logoPulse ? { boxShadow: '0 0 30px rgba(59,130,246,0.6), 0 0 60px rgba(59,130,246,0.3)' } : { boxShadow: '0 0 20px rgba(59,130,246,0.2)' }}
              >
                <Image src="/kimari-logo.png" alt="Kimari Logo" width={96} height={96} className="w-full h-full object-cover" priority />
              </motion.div>
            </div>
            {/* Title */}
            <div className="text-center">
              <h2 className="text-2xl font-black text-white tracking-tight">Kimari</h2>
              <p className="text-xs text-zinc-500 font-mono mt-1">Local AI Runtime</p>
            </div>
            {/* Boot sequence */}
            <div className="font-mono text-[11px] text-zinc-500 space-y-1 h-20 w-64">
              {bootLines.map((line, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2 }}
                  className={typeof line === 'string' && line.includes('READY') ? 'text-blue-400 font-bold' : ''}
                >
                  <span className="text-zinc-600 mr-2">{'>'}</span>
                  {line}
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// ─── Quick Command Search (Ctrl+K Palette) ───────────────────────────────────

function QuickCommandSearch({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const [search, setSearch] = useState('')
  const { toast } = useToast()
  const inputRef = useRef<HTMLInputElement>(null)

  const filteredCommands = useMemo(() => {
    if (!search.trim()) return allKimariCommands
    const q = search.toLowerCase()
    return allKimariCommands.filter(cmd => cmd.toLowerCase().includes(q))
  }, [search])

  const handleSelect = (cmd: string) => {
    navigator.clipboard.writeText(cmd)
    toast({ title: 'Copied to clipboard!', description: cmd })
    onOpenChange(false)
  }

  // Focus input and reset when dialog opens
  const handleOpenChange = useCallback((isOpen: boolean) => {
    if (isOpen) {
      setSearch('')
    }
    onOpenChange(isOpen)
  }, [onOpenChange])

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [open])

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-lg p-0 overflow-hidden">
        <DialogHeader className="sr-only">
          <DialogTitle>Command Palette</DialogTitle>
          <DialogDescription>Search and copy Kimari commands</DialogDescription>
        </DialogHeader>
        <div className="flex items-center gap-2 px-4 py-3 border-b border-border/30 bg-muted/30">
          <Command className="w-4 h-4 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search commands..."
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono rounded bg-muted border border-border/50 text-muted-foreground">ESC</kbd>
        </div>
        <div className="max-h-72 overflow-y-auto p-2" style={{ scrollbarWidth: 'thin' }}>
          {filteredCommands.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">No commands found</div>
          ) : (
            filteredCommands.map((cmd) => (
              <button
                key={cmd}
                onClick={() => handleSelect(cmd)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm hover:bg-blue-500/10 hover:text-blue-500 transition-all duration-150 text-left group/cmd"
              >
                <Terminal className="w-3.5 h-3.5 text-muted-foreground group-hover/cmd:text-blue-500 flex-shrink-0" />
                <span className="font-mono text-xs">{cmd}</span>
                <Copy className="w-3 h-3 ml-auto opacity-0 group-hover/cmd:opacity-100 text-blue-500 transition-opacity flex-shrink-0" />
              </button>
            ))
          )}
        </div>
        <div className="px-4 py-2 border-t border-border/30 text-[10px] text-muted-foreground flex items-center gap-3">
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 rounded bg-muted border border-border/50 text-[9px] font-mono">↑↓</kbd> navigate</span>
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 rounded bg-muted border border-border/50 text-[9px] font-mono">↵</kbd> copy</span>
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 rounded bg-muted border border-border/50 text-[9px] font-mono">Ctrl+K</kbd> open</span>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// ─── Glow Card (mouse-following glow effect) ─────────────────────────────────

function GlowCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top })
  }

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`relative overflow-hidden ${className}`}
    >
      {isHovered && (
        <div
          className="absolute pointer-events-none transition-opacity duration-300 opacity-100"
          style={{
            left: mousePos.x - 100,
            top: mousePos.y - 100,
            width: 200,
            height: 200,
            background: 'radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%)',
            borderRadius: '50%',
          }}
        />
      )}
      {children}
    </div>
  )
}

// ─── Styling Enhancement: Magnetic Cursor Button ──────────────────────────────

function MagneticButton({ children, className = '', ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { children: React.ReactNode; className?: string }) {
  const btnRef = useRef<HTMLButtonElement>(null)
  const [offset, setOffset] = useState({ x: 0, y: 0 })

  const handleMouseMove = (e: ReactMouseEvent<HTMLButtonElement>) => {
    if (!btnRef.current) return
    const rect = btnRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    const distX = e.clientX - centerX
    const distY = e.clientY - centerY
    const dist = Math.sqrt(distX * distX + distY * distY)
    const maxOffset = 6
    if (dist < 80) {
      setOffset({ x: (distX / 80) * maxOffset, y: (distY / 80) * maxOffset })
    }
  }

  const handleMouseLeave = () => {
    setOffset({ x: 0, y: 0 })
  }

  return (
    <button
      ref={btnRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`transition-transform duration-200 ease-out ${className}`}
      style={{ transform: `translate(${offset.x}px, ${offset.y}px)` }}
      {...props}
    >
      {children}
    </button>
  )
}

// ─── Styling Enhancement: useRipple Hook ──────────────────────────────────────

function useRipple() {
  const [ripples, setRipples] = useState<{ x: number; y: number; id: number }[]>([])
  const rippleId = useRef(0)

  const createRipple = (e: ReactMouseEvent<HTMLButtonElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const id = rippleId.current++
    setRipples(prev => [...prev, { x, y, id }])
    setTimeout(() => {
      setRipples(prev => prev.filter(r => r.id !== id))
    }, 600)
  }

  const RippleContainer = () => (
    <span className="absolute inset-0 overflow-hidden rounded-inherit pointer-events-none">
      {ripples.map(ripple => (
        <span
          key={ripple.id}
          className="ripple-effect absolute w-5 h-5 rounded-full bg-white/30"
          style={{ left: ripple.x - 10, top: ripple.y - 10 }}
        />
      ))}
    </span>
  )

  return { createRipple, RippleContainer }
}

// ─── Styling Enhancement: Ripple Button ───────────────────────────────────────

function RippleButton({ children, className = '', onClick, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { children: React.ReactNode; className?: string }) {
  const { createRipple, RippleContainer } = useRipple()

  const handleClick = (e: ReactMouseEvent<HTMLButtonElement>) => {
    createRipple(e)
    if (onClick) onClick(e)
  }

  return (
    <button className={`relative overflow-hidden ${className}`} onClick={handleClick} {...props}>
      <RippleContainer />
      {children}
    </button>
  )
}

// ─── Styling Enhancement: Spotlight Cursor Card ───────────────────────────────

function SpotlightCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const cardRef = useRef<HTMLDivElement>(null)

  const handleMouseMove = (e: ReactMouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100
    cardRef.current.style.setProperty('--mouse-x', `${x}%`)
    cardRef.current.style.setProperty('--mouse-y', `${y}%`)
  }

  return (
    <div ref={cardRef} onMouseMove={handleMouseMove} className={`spotlight-card ${className}`}>
      {children}
    </div>
  )
}

// ─── Styling Enhancement: Text Reveal Heading ─────────────────────────────────

function TextRevealHeading({ title, subtitle }: { title: string; subtitle?: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-40px' })

  const words = title.split(' ')

  return (
    <div ref={ref} className="text-center mb-14">
      <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-3">
        {words.map((word, i) => (
          <span
            key={i}
            className={`inline-block mr-[0.3em] ${isInView ? 'animate-word-reveal' : 'opacity-0'}`}
            style={{ animationDelay: `${i * 0.08}s` }}
          >
            {word}
          </span>
        ))}
      </h2>
      <div className="w-10 h-[3px] bg-gradient-to-r from-blue-500 to-transparent mx-auto mb-4 rounded-full" />
      {subtitle && (
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
          transition={{ delay: words.length * 0.08 + 0.2, duration: 0.5 }}
          className="text-muted-foreground max-w-lg mx-auto"
        >
          {subtitle}
        </motion.p>
      )}
    </div>
  )
}

// ─── Styling Enhancement: Odometer Counter ────────────────────────────────────

function OdometerCounter({ target, suffix = '', prefix = '' }: { target: number; suffix?: string; prefix?: string }) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true })
  const [count, setCount] = useState(0)
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (!isInView || hasAnimated.current) return
    hasAnimated.current = true
    const duration = 2000
    const startTime = performance.now()
    const animate = (now: number) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease-out cubic with slight overshoot for "odometer" feel
      const eased = 1 - Math.pow(1 - progress, 4)
      const current = Math.round(eased * target)
      setCount(current)
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [isInView, target])

  return (
    <span ref={ref} className={isInView ? 'animate-odometer-bounce' : ''} style={{ animationDelay: '0.1s' }}>
      {prefix}{count}{suffix}
    </span>
  )
}

// ─── Styling Enhancement: Floating Label Input ────────────────────────────────

function FloatingLabelInput({ label, value, onChange, ...props }: { label: string; value: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void } & Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'>) {
  const [isFocused, setIsFocused] = useState(false)
  const isActive = isFocused || value.length > 0

  return (
    <div className="relative">
      <input
        value={value}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className="w-full bg-muted/30 border border-border/30 rounded-lg px-3 pt-5 pb-2 text-sm outline-none focus:border-blue-500/50 transition-all duration-200 peer"
        {...props}
      />
      <label
        className={`absolute left-3 transition-all duration-200 pointer-events-none ${
          isActive
            ? 'top-1 text-[10px] text-blue-500 font-medium'
            : 'top-1/2 -translate-y-1/2 text-sm text-muted-foreground'
        }`}
      >
        {label}
      </label>
    </div>
  )
}

// ─── Styling Enhancement: Progress Skeleton ───────────────────────────────────

function ProgressSkeleton({ lines = 4, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }, (_, i) => (
        <div
          key={i}
          className="skeleton-shimmer rounded-lg"
          style={{
            height: i === 0 ? '20px' : '14px',
            width: `${80 - i * 15}%`,
          }}
        />
      ))}
    </div>
  )
}

// ─── Styling Enhancement: Staggered Section Entrance ─────────────────────────

function StaggeredSection({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-60px' })

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.15, delayChildren: 0.1 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
  }

  return (
    <motion.div
      ref={ref}
      variants={containerVariants}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      className={className}
    >
      {Array.isArray(children) ? children.map((child, i) => (
        <motion.div key={i} variants={itemVariants}>{child}</motion.div>
      )) : <motion.div variants={itemVariants}>{children}</motion.div>}
    </motion.div>
  )
}

// ─── Styling Enhancement: Tech Term Tooltip ───────────────────────────────────

function TechTermTooltip({ term }: { term: string }) {
  const info = techTerms[term]
  if (!info) return <span>{term}</span>

  return (
    <TooltipProvider delayDuration={100}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="underline decoration-dotted decoration-blue-500/50 underline-offset-4 cursor-help text-blue-500/80 hover:text-blue-500 transition-colors">
            {term}
          </span>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs p-3 tech-tooltip-card" sideOffset={8}>
          <p className="text-xs font-semibold text-blue-500 mb-1">{info.short}</p>
          <p className="text-xs text-muted-foreground leading-relaxed">{info.detail}</p>
          {info.link && (
            <a href={info.link} target="_blank" rel="noopener noreferrer" className="text-[10px] text-cyan-500 hover:text-cyan-400 mt-1.5 inline-flex items-center gap-1">
              Learn more <ExternalLink className="w-2.5 h-2.5" />
            </a>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

// ─── Styling Enhancement: Ambient Sound Toggle ────────────────────────────────

function AmbientSoundToggle() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(0.3)
  const audioContextRef = useRef<AudioContext | null>(null)
  const gainNodeRef = useRef<GainNode | null>(null)
  const sourceRef = useRef<AudioBufferSourceNode | null>(null)

  const toggleSound = useCallback(() => {
    if (isPlaying) {
      // Stop
      if (sourceRef.current) {
        sourceRef.current.stop()
        sourceRef.current = null
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
        audioContextRef.current = null
      }
      setIsPlaying(false)
    } else {
      // Start - create white noise using Web Audio API
      const ctx = new AudioContext()
      audioContextRef.current = ctx
      const gainNode = ctx.createGain()
      gainNode.gain.value = volume * 0.1 // Very quiet
      gainNodeRef.current = gainNode

      // Create white noise buffer
      const bufferSize = 2 * ctx.sampleRate
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate)
      const data = buffer.getChannelData(0)
      for (let i = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * 0.5
      }

      const source = ctx.createBufferSource()
      source.buffer = buffer
      source.loop = true

      // Apply low-pass filter for a softer "rain" sound
      const filter = ctx.createBiquadFilter()
      filter.type = 'lowpass'
      filter.frequency.value = 800

      source.connect(filter)
      filter.connect(gainNode)
      gainNode.connect(ctx.destination)
      source.start()
      sourceRef.current = source
      setIsPlaying(true)
    }
  }, [isPlaying, volume])

  // Update volume when slider changes
  useEffect(() => {
    if (gainNodeRef.current) {
      gainNodeRef.current.gain.value = volume * 0.1
    }
  }, [volume])

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Toggle ambient sound">
          {isPlaying ? <Volume2 className="w-4 h-4 text-blue-500" /> : <VolumeX className="w-4 h-4" />}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-56 p-3" align="end">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold">Ambient Sound</p>
            <button
              onClick={toggleSound}
              className={`px-2 py-1 rounded text-[10px] font-medium transition-all ${
                isPlaying
                  ? 'bg-blue-500/10 text-blue-500 border border-blue-500/20'
                  : 'bg-muted text-muted-foreground border border-border/30'
              }`}
            >
              {isPlaying ? 'Playing' : 'Play'}
            </button>
          </div>
          <div className="space-y-1.5">
            <p className="text-[10px] text-muted-foreground">Volume</p>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={volume}
              onChange={(e) => setVolume(parseFloat(e.target.value))}
              className="w-full h-1 rounded-full appearance-none bg-muted cursor-pointer accent-blue-500"
            />
          </div>
          <p className="text-[10px] text-muted-foreground">Gentle white noise for focused coding sessions</p>
        </div>
      </PopoverContent>
    </Popover>
  )
}

// ─── New Feature: Model Comparison Tool ───────────────────────────────────────

function ModelComparisonTool() {
  const [selectedModels, setSelectedModels] = useState<string[]>(['tinyllama', 'qwen3-4b', 'kimari-4b'])

  const toggleModel = (id: string) => {
    setSelectedModels(prev => {
      if (prev.includes(id)) {
        if (prev.length <= 2) return prev // Keep at least 2
        return prev.filter(m => m !== id)
      }
      if (prev.length >= 3) return prev // Max 3
      return [...prev, id]
    })
  }

  const comparedModels = modelComparisonData.filter(m => selectedModels.includes(m.id))
  const radarData = [
    { metric: 'Speed', ...Object.fromEntries(comparedModels.map(m => [m.id, m.speed])) },
    { metric: 'Quality', ...Object.fromEntries(comparedModels.map(m => [m.id, m.quality])) },
    { metric: 'VRAM Eff.', ...Object.fromEntries(comparedModels.map(m => [m.id, Math.max(0, 100 - m.vram * 15)])) },
    { metric: 'Context', ...Object.fromEntries(comparedModels.map(m => [m.id, (m.contextLength / 16384) * 100])) },
  ]

  const radarColors = ['#3b82f6', '#60a5fa', '#f59e0b']

  return (
    <GlassCard glow className="p-6">
      <h4 className="text-sm font-semibold mb-5 flex items-center gap-2">
        <GitBranch className="w-4 h-4 text-blue-500" /> Model Comparison Tool
      </h4>

      {/* Model selector chips */}
      <div className="flex flex-wrap gap-2 mb-6">
        {modelComparisonData.map((model) => (
          <button
            key={model.id}
            onClick={() => toggleModel(model.id)}
            className={`px-3 py-1.5 text-xs rounded-full border transition-all duration-200 ${
              selectedModels.includes(model.id)
                ? 'border-blue-500/30 bg-blue-500/10 text-blue-500 font-medium'
                : 'border-border/30 text-muted-foreground hover:border-blue-500/20 hover:text-foreground'
            }`}
          >
            {model.name}
            {selectedModels.includes(model.id) && ' ✓'}
          </button>
        ))}
      </div>

      {/* Comparison table */}
      <div className="overflow-x-auto mb-6">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-white/[0.06]">
              <th className="text-left py-2 pr-4 text-muted-foreground font-medium">Metric</th>
              {comparedModels.map((m, i) => (
                <th key={m.id} className="text-center py-2 px-3 font-semibold" style={{ color: radarColors[i] }}>
                  {m.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              { label: 'Parameters', getValue: (m: typeof comparedModels[0]) => m.params },
              { label: 'Gen Speed', getValue: (m: typeof comparedModels[0]) => `${m.speed} tok/s` },
              { label: 'VRAM Required', getValue: (m: typeof comparedModels[0]) => `${m.vram} GB` },
              { label: 'Context Length', getValue: (m: typeof comparedModels[0]) => fmtNum(m.contextLength) },
              { label: 'Quantization', getValue: (m: typeof comparedModels[0]) => m.quant },
              { label: 'Quality Score', getValue: (m: typeof comparedModels[0]) => `${m.quality}/100` },
            ].map((row) => (
              <tr key={row.label} className="border-b border-white/[0.03]">
                <td className="py-2 pr-4 text-muted-foreground">{row.label}</td>
                {comparedModels.map(m => (
                  <td key={m.id} className="text-center py-2 px-3 font-mono">{row.getValue(m)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Radar chart */}
      {comparedModels.length >= 2 && (
        <div className="h-64 md:h-72">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11, fill: '#a1a1aa' }} />
              <PolarRadiusAxis tick={false} axisLine={false} domain={[0, 100]} />
              {comparedModels.map((m, i) => (
                <Radar key={m.id} name={m.name} dataKey={m.id} stroke={radarColors[i]} fill={radarColors[i]} fillOpacity={0.1} strokeWidth={2} />
              ))}
              <Legend
                wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
              />
              <RechartsTooltip
                contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      <p className="text-[10px] text-muted-foreground mt-3 flex items-center gap-1.5">
        <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
        Quality scores are estimated. Only GTX 1060 speed results are validated. Select 2-3 models to compare.
      </p>
    </GlassCard>
  )
}

// ─── New Feature: Deployment Checklist ────────────────────────────────────────

function DeploymentChecklist({ onComplete }: { onComplete?: () => void }) {
  const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>({})

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const saved = localStorage.getItem('kimari-deployment-checklist')
    if (saved) {
      try { setCheckedItems(JSON.parse(saved)) } catch { /* ignore */ }
    }
  }, [])
  /* eslint-enable react-hooks/set-state-in-effect */

  const toggleItem = (id: string) => {
    setCheckedItems(prev => {
      const next = { ...prev, [id]: !prev[id] }
      localStorage.setItem('kimari-deployment-checklist', JSON.stringify(next))
      // Check for 100% completion
      const newCheckedCount = Object.values(next).filter(Boolean).length
      if (newCheckedCount === totalCount && onComplete) {
        setTimeout(() => onComplete(), 300)
      }
      return next
    })
  }

  const checkedCount = Object.values(checkedItems).filter(Boolean).length
  const totalCount = deploymentChecklistItems.length
  const progressPercent = Math.round((checkedCount / totalCount) * 100)

  const categories = ['Prerequisites', 'Install', 'Configure', 'Test', 'Deploy']

  return (
    <GlassCard glow className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h4 className="text-sm font-semibold flex items-center gap-2">
          <CheckSquare className="w-4 h-4 text-blue-500" /> Deployment Checklist
        </h4>
        <span className="text-xs font-mono text-blue-500">{progressPercent}%</span>
      </div>

      {/* Progress bar */}
      <div className="h-2 rounded-full bg-white/[0.04] overflow-hidden mb-6 border border-border/20">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progressPercent}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          className="h-full rounded-full bg-gradient-to-r from-blue-600 to-blue-600"
        />
      </div>

      {/* Categories */}
      <div className="space-y-5">
        {categories.map((category) => {
          const items = deploymentChecklistItems.filter(i => i.category === category)
          const catChecked = items.filter(i => checkedItems[i.id]).length
          return (
            <div key={category}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold">{category}</span>
                <span className="text-[10px] text-muted-foreground">{catChecked}/{items.length}</span>
              </div>
              <div className="space-y-1.5">
                {items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => toggleItem(item.id)}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left hover:bg-white/[0.02] transition-all duration-200 group"
                  >
                    {checkedItems[item.id] ? (
                      <CheckSquare className="w-4 h-4 text-blue-500 flex-shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-muted-foreground/50 flex-shrink-0 group-hover:text-muted-foreground transition-colors" />
                    )}
                    <span className={`text-xs transition-all duration-200 ${checkedItems[item.id] ? 'line-through text-muted-foreground' : ''}`}>
                      {item.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {progressPercent === 100 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-5 p-3 rounded-lg border border-blue-500/20 bg-blue-500/5 flex items-center gap-2"
        >
          <CheckCircle2 className="w-4 h-4 text-blue-500" />
          <p className="text-xs text-blue-500 font-medium">Deployment complete! Your Kimari setup is ready.</p>
        </motion.div>
      )}

      <p className="text-[10px] text-muted-foreground mt-3">Progress saved to your browser localStorage.</p>
    </GlassCard>
  )
}

// ─── New Feature: Error Troubleshooter ────────────────────────────────────────

function ErrorTroubleshooter() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')

  const categories = ['All', ...Array.from(new Set(errorDatabase.map(e => e.category)))]

  const filteredErrors = useMemo(() => {
    let results = errorDatabase
    if (selectedCategory !== 'All') {
      results = results.filter(e => e.category === selectedCategory)
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      results = results.filter(e =>
        e.symptom.toLowerCase().includes(q) || e.solution.toLowerCase().includes(q)
      )
    }
    return results
  }, [searchQuery, selectedCategory])

  return (
    <GlassCard glow className="p-6">
      <h4 className="text-sm font-semibold mb-5 flex items-center gap-2">
        <AlertOctagon className="w-4 h-4 text-blue-500" /> Error Troubleshooter
      </h4>

      {/* Search input */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Describe your error or symptom..."
          className="w-full bg-muted/30 border border-border/30 rounded-lg pl-9 pr-3 py-2.5 text-sm outline-none focus:border-blue-500/50 transition-all"
        />
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-1.5 mb-5">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-2.5 py-1 text-[10px] rounded-full border transition-all duration-200 ${
              selectedCategory === cat
                ? 'border-blue-500/30 bg-blue-500/10 text-blue-500 font-medium'
                : 'border-border/30 text-muted-foreground hover:border-blue-500/20'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Results */}
      <div className="space-y-3 max-h-72 overflow-y-auto" style={{ scrollbarWidth: 'thin' }}>
        {filteredErrors.length === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            No matching errors found. Try a different search term.
          </div>
        ) : (
          filteredErrors.map((error) => (
            <motion.div
              key={error.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="p-3 rounded-lg border border-border/30 hover:border-blue-500/20 transition-colors"
            >
              <div className="flex items-center gap-2 mb-1.5">
                <AlertOctagon className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                <span className="text-xs font-semibold">{error.symptom}</span>
                <Badge variant="outline" className="text-[9px] px-1.5 py-0 ml-auto border-border/30">{error.category}</Badge>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed pl-5.5">{error.solution}</p>
            </motion.div>
          ))
        )}
      </div>

      <p className="text-[10px] text-muted-foreground mt-3 flex items-center gap-1.5">
        <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
        Common errors and solutions. For detailed diagnostics, run <code className="bg-muted/50 px-1 rounded font-mono text-[9px]">kimari doctor --deep</code>.
      </p>
    </GlassCard>
  )
}

// ─── Gauge Dial Component (outside render) ────────────────────────────────────

function GaugeDial({ value, max, label, unit, color }: { value: number; max: number; label: string; unit: string; color: string }) {
  const percent = Math.min((value / max) * 100, 100)
  const circumference = 2 * Math.PI * 36
  const strokeDashoffset = circumference - (circumference * percent) / 100

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative">
        <svg width="90" height="90" viewBox="0 0 90 90" className="-rotate-90">
          <circle cx="45" cy="45" r="36" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="6" />
          <circle
            cx="45" cy="45" r="36" fill="none"
            stroke={color} strokeWidth="6" strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-black font-mono" style={{ color }}>{Math.round(value)}</span>
          <span className="text-[8px] text-muted-foreground">{unit}</span>
        </div>
      </div>
      <span className="text-[10px] text-muted-foreground mt-1">{label}</span>
    </div>
  )
}

// ─── New Feature: Resource Usage Monitor (Simulated) ──────────────────────────

function ResourceUsageMonitor() {
  const [metrics, setMetrics] = useState({
    gpu: 45, gpuMem: 20, cpu: 12, ram: 38, temp: 62, power: 85,
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        gpu: Math.max(5, Math.min(95, prev.gpu + (Math.random() * 10 - 5))),
        gpuMem: Math.max(10, Math.min(85, prev.gpuMem + (Math.random() * 6 - 3))),
        cpu: Math.max(2, Math.min(50, prev.cpu + (Math.random() * 8 - 4))),
        ram: Math.max(20, Math.min(70, prev.ram + (Math.random() * 4 - 2))),
        temp: Math.max(45, Math.min(80, prev.temp + (Math.random() * 4 - 2))),
        power: Math.max(50, Math.min(120, prev.power + (Math.random() * 10 - 5))),
      }))
    }, 1500)
    return () => clearInterval(interval)
  }, [])

  return (
    <GlassCard glow className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h4 className="text-sm font-semibold flex items-center gap-2">
          <GaugeCircle className="w-4 h-4 text-blue-500" /> Resource Monitor
        </h4>
        <span className="flex items-center gap-1.5 text-[10px] text-blue-500">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
          Live (simulated)
        </span>
      </div>

      {/* Gauges grid */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-4 mb-5">
        <div className="flex justify-center">
          <GaugeDial value={metrics.gpu} max={100} label="GPU" unit="%" color="#3b82f6" />
        </div>
        <div className="flex justify-center">
          <GaugeDial value={metrics.gpuMem} max={100} label="VRAM" unit="%" color="#2563eb" />
        </div>
        <div className="flex justify-center">
          <GaugeDial value={metrics.cpu} max={100} label="CPU" unit="%" color="#60a5fa" />
        </div>
        <div className="flex justify-center">
          <GaugeDial value={metrics.ram} max={100} label="RAM" unit="%" color="#93c5fd" />
        </div>
        <div className="flex justify-center">
          <GaugeDial value={metrics.temp} max={100} label="Temp" unit="°C" color={metrics.temp > 75 ? '#ef4444' : '#f59e0b'} />
        </div>
        <div className="flex justify-center">
          <GaugeDial value={metrics.power} max={150} label="Power" unit="W" color="#a78bfa" />
        </div>
      </div>

      {/* Info bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'GPU', value: 'GTX 1060 6GB' },
          { label: 'Driver', value: 'CUDA 12.1' },
          { label: 'Model', value: 'TinyLlama Q4_K_M' },
          { label: 'Uptime', value: '4h 23m' },
        ].map((info) => (
          <div key={info.label} className="bg-muted/30 rounded-lg p-2.5 border border-border/20">
            <p className="text-[9px] text-muted-foreground">{info.label}</p>
            <p className="text-xs font-mono font-medium">{info.value}</p>
          </div>
        ))}
      </div>

      <p className="text-[10px] text-muted-foreground mt-3 flex items-center gap-1.5">
        <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
        Simulated metrics for demonstration. Real values available via <code className="bg-muted/50 px-1 rounded font-mono text-[9px]">kimari status</code>.
      </p>
    </GlassCard>
  )
}

// ─── Styling: 3D Tilt Card ──────────────────────────────────────────────────

function TiltCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [tilt, setTilt] = useState({ x: 0, y: 0 })

  const handleMouseMove = useCallback((e: ReactMouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width
    const y = (e.clientY - rect.top) / rect.height
    setTilt({ x: (y - 0.5) * -8, y: (x - 0.5) * 8 })
  }, [])

  const handleMouseLeave = useCallback(() => {
    setTilt({ x: 0, y: 0 })
  }, [])

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={className}
      style={{
        perspective: '800px',
        transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
        transition: 'transform 0.15s ease-out',
      }}
    >
      {children}
    </div>
  )
}

// ─── Styling: Cursor Trail Effect ────────────────────────────────────────────

function CursorTrail({ containerRef }: { containerRef: React.RefObject<HTMLElement | null> }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Array<{ x: number; y: number; alpha: number; size: number }>>([])

  useEffect(() => {
    const canvas = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      canvas.width = container.offsetWidth
      canvas.height = container.offsetHeight
    }
    resize()
    const ro = new ResizeObserver(resize)
    ro.observe(container)

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect()
      particlesRef.current.push({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        alpha: 0.8,
        size: Math.max(1, 3 + Math.abs(e.movementX + e.movementY) * 0.1),
      })
      if (particlesRef.current.length > 30) particlesRef.current.shift()
    }

    container.addEventListener('mousemove', handleMouseMove)

    let rafId: number
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      particlesRef.current = particlesRef.current.filter(p => p.alpha > 0.01 && p.size > 0.1)
      for (const p of particlesRef.current) {
        p.alpha *= 0.92
        p.size *= 0.96
        const safeSize = Math.max(0.1, p.size)
        ctx.beginPath()
        ctx.arc(p.x, p.y, safeSize, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(59, 130, 246, ${p.alpha})`
        ctx.fill()
      }
      rafId = requestAnimationFrame(animate)
    }
    rafId = requestAnimationFrame(animate)

    return () => {
      container.removeEventListener('mousemove', handleMouseMove)
      ro.disconnect()
      cancelAnimationFrame(rafId)
    }
  }, [containerRef])

  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none z-10" />
}

// ─── Styling: TypeWriter Text ────────────────────────────────────────────────

function TypeWriterText({ text, speed = 30 }: { text: string; speed?: number }) {
  const [displayed, setDisplayed] = useState(0)

  useEffect(() => {
    if (displayed < text.length) {
      const timer = setTimeout(() => setDisplayed(prev => prev + 1), speed)
      return () => clearTimeout(timer)
    }
  }, [displayed, text.length, speed])

  return (
    <span>
      {text.slice(0, displayed)}
      <span className="typing-cursor" />
    </span>
  )
}

// ─── Styling: Morphing Blob ──────────────────────────────────────────────────

function MorphingBlob({ className = '', variant = 1 }: { className?: string; variant?: number }) {
  return (
    <div
      className={`absolute pointer-events-none ${className} ${
        variant === 1 ? 'animate-morph-blob-1' : 'animate-morph-blob-2'
      }`}
      style={{
        width: '300px',
        height: '300px',
        background: variant === 1
          ? 'radial-gradient(circle, rgba(59,130,246,0.08) 0%, rgba(37,99,235,0.04) 50%, transparent 70%)'
          : 'radial-gradient(circle, rgba(14,165,233,0.06) 0%, rgba(59,130,246,0.03) 50%, transparent 70%)',
      }}
    />
  )
}

// ─── Styling: Section Progress Heading ───────────────────────────────────────

function SectionProgressHeading({ title, subtitle, id }: { title: string; subtitle?: string; id?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      if (!ref.current) return
      const rect = ref.current.getBoundingClientRect()
      const sectionHeight = rect.height + 200
      const scrolled = Math.max(0, -rect.top + 200)
      const pct = Math.min(1, Math.max(0, scrolled / sectionHeight))
      setProgress(pct * 100)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div ref={ref} className="text-center mb-14" id={id}>
      <h2 className="text-3xl font-bold tracking-tight mb-4">{title}</h2>
      {subtitle && <p className="text-muted-foreground max-w-lg mx-auto">{subtitle}</p>}
      <div className="mt-3 mx-auto max-w-xs h-0.5 bg-muted/30 rounded-full overflow-hidden">
        <div className="section-progress-bar h-full rounded-full" style={{ width: `${progress}%` }} />
      </div>
    </div>
  )
}

// ─── New Feature: GPU Compatibility Quiz ──────────────────────────────────────

function GPUCompatibilityQuiz() {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [showResult, setShowResult] = useState(false)

  const currentStep = gpuQuizSteps[step]
  const result = answers[0] ? gpuQuizResults[answers[0]] : null

  const handleSelect = (stepId: number, value: string) => {
    const newAnswers = { ...answers, [stepId]: value }
    setAnswers(newAnswers)
    if (step < gpuQuizSteps.length - 1) {
      setTimeout(() => setStep(step + 1), 300)
    } else {
      setTimeout(() => setShowResult(true), 300)
    }
  }

  const handleReset = () => {
    setStep(0)
    setAnswers({})
    setShowResult(false)
  }

  return (
    <GlassCard glow className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h4 className="text-sm font-semibold flex items-center gap-2">
          <Award className="w-4 h-4 text-blue-500" /> GPU Compatibility Quiz
        </h4>
        {!showResult && (
          <div className="flex items-center gap-1.5">
            {gpuQuizSteps.map((_, i) => (
              <div key={i} className={`w-8 h-1.5 rounded-full transition-all duration-300 ${
                i < step ? 'bg-blue-500' : i === step ? 'bg-blue-500/50' : 'bg-muted/50'
              }`} />
            ))}
          </div>
        )}
      </div>

      <AnimatePresence mode="wait">
        {showResult && result ? (
          <motion.div
            key="result"
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="text-center mb-6">
              <div className="w-16 h-16 rounded-full bg-blue-500/10 border-2 border-blue-500/30 flex items-center justify-center mx-auto mb-3">
                <CheckCircle2 className="w-8 h-8 text-blue-500" />
              </div>
              <h3 className="text-xl font-bold mb-1">Recommended Profile</h3>
              <p className="text-sm text-muted-foreground">Based on your GPU and preferences</p>
            </div>
            <div className="bg-muted/20 rounded-xl p-5 border border-blue-500/20 space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div><span className="text-xs text-muted-foreground">Profile</span><p className="text-sm font-bold font-mono text-blue-500">{result.profile}</p></div>
                <div><span className="text-xs text-muted-foreground">Model</span><p className="text-sm font-bold">{result.model}</p></div>
                <div><span className="text-xs text-muted-foreground">Quantization</span><p className="text-sm font-mono">{result.quant}</p></div>
                <div><span className="text-xs text-muted-foreground">Context</span><p className="text-sm font-mono">{fmtNum(result.ctx)} tokens</p></div>
              </div>
              <div className="pt-2 border-t border-border/30">
                <p className="text-xs text-muted-foreground">{result.reason}</p>
              </div>
              <div className="pt-2 border-t border-border/30">
                <code className="text-xs font-mono bg-muted/50 px-2 py-1 rounded">$ kimari start --profile {result.profile}</code>
              </div>
            </div>
            <div className="flex justify-center mt-4">
              <RippleButton onClick={handleReset} className="px-4 py-2 text-sm rounded-lg border border-border/50 bg-muted/30 hover:bg-muted/50 transition-colors flex items-center gap-2">
                <RotateCcw className="w-3.5 h-3.5" /> Retake Quiz
              </RippleButton>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key={`step-${step}`}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          >
            <div className="mb-4">
              <span className="text-xs text-blue-500 font-semibold">Step {step + 1} of {gpuQuizSteps.length}</span>
              <h3 className="text-lg font-bold mt-1">{currentStep.question}</h3>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {currentStep.options.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => handleSelect(step, opt.value)}
                  className={`p-4 rounded-xl border text-left transition-all duration-200 hover:border-blue-500/40 hover:shadow-md hover:shadow-blue-500/5 hover:-translate-y-0.5 breathing-glow ${
                    answers[step] === opt.value
                      ? 'border-blue-500/50 bg-blue-500/5 shadow-sm shadow-blue-500/10'
                      : 'border-border/40 bg-card'
                  }`}
                >
                  <span className="text-xl mb-2 block">{opt.icon}</span>
                  <span className="text-sm font-medium">{opt.label}</span>
                </button>
              ))}
            </div>
            {step > 0 && (
              <button onClick={() => setStep(step - 1)} className="mt-4 text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors">
                <ChevronLeft className="w-3 h-3" /> Back
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </GlassCard>
  )
}

// ─── New Feature: Command Builder ────────────────────────────────────────────

function CommandBuilder() {
  const [selectedAction, setSelectedAction] = useState<string | null>(null)
  const [selectedFlags, setSelectedFlags] = useState<string[]>([])
  const { toast } = useToast()

  const currentAction = commandBuilderActions.find(a => a.id === selectedAction)
  const availableFlags = commandBuilderFlags.filter(f => selectedAction && f.appliesTo.includes(selectedAction))

  const builtCommand = useMemo(() => {
    if (!currentAction) return ''
    let cmd = currentAction.command
    for (const flagId of selectedFlags) {
      const flag = commandBuilderFlags.find(f => f.id === flagId)
      if (flag) {
        if (flag.label.includes('<')) {
          cmd += ` ${flag.label.replace(/<.*>/, '8192')}`
        } else {
          cmd += ` ${flag.label}`
        }
      }
    }
    return cmd
  }, [currentAction, selectedFlags])

  const toggleFlag = (flagId: string) => {
    setSelectedFlags(prev => prev.includes(flagId) ? prev.filter(f => f !== flagId) : [...prev, flagId])
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(builtCommand)
    toast({ title: 'Copied to clipboard!', description: builtCommand })
  }

  return (
    <GlassCard glow className="p-6">
      <h4 className="text-sm font-semibold flex items-center gap-2 mb-5">
        <Wand2 className="w-4 h-4 text-blue-500" /> Command Builder
      </h4>

      {/* Action selection */}
      <div className="mb-5">
        <label className="text-xs text-muted-foreground mb-2 block">1. Select an action</label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {commandBuilderActions.map((action) => (
            <button
              key={action.id}
              onClick={() => { setSelectedAction(action.id); setSelectedFlags([]) }}
              className={`p-2.5 rounded-lg border text-left transition-all duration-200 breathing-glow ${
                selectedAction === action.id
                  ? 'border-blue-500/50 bg-blue-500/5 shadow-sm shadow-blue-500/10'
                  : 'border-border/40 bg-card hover:border-blue-500/30'
              }`}
            >
              <action.icon className={`w-3.5 h-3.5 mb-1 ${selectedAction === action.id ? 'text-blue-500' : 'text-muted-foreground'}`} />
              <span className="text-xs font-medium block">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Flags */}
      {selectedAction && availableFlags.length > 0 && (
        <div className="mb-5">
          <label className="text-xs text-muted-foreground mb-2 block">2. Add flags</label>
          <div className="flex flex-wrap gap-2">
            {availableFlags.map((flag) => (
              <button
                key={flag.id}
                onClick={() => toggleFlag(flag.id)}
                className={`px-3 py-1.5 rounded-lg border text-xs font-mono transition-all duration-200 breathing-glow ${
                  selectedFlags.includes(flag.id)
                    ? 'border-blue-500/50 bg-blue-500/10 text-blue-500'
                    : 'border-border/40 bg-card hover:border-blue-500/30'
                }`}
                title={flag.desc}
              >
                {flag.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Built command preview */}
      <div>
        <label className="text-xs text-muted-foreground mb-2 block">3. Generated command</label>
        <div className="bg-zinc-950 dark:bg-zinc-950 bg-zinc-100 border border-zinc-800 dark:border-zinc-800 border-zinc-300 rounded-lg p-3 font-mono text-sm group relative">
          {builtCommand ? (
            <div className="flex items-center gap-2">
              <span className="text-blue-400 select-none">$</span>
              <span className="text-zinc-200 dark:text-zinc-200 text-zinc-800">{builtCommand}</span>
              <button onClick={handleCopy} className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-white/10 active:scale-90" aria-label="Copy command">
                <Copy className="w-3.5 h-3.5 text-zinc-400" />
              </button>
            </div>
          ) : (
            <span className="text-zinc-500">Select an action above to build a command...</span>
          )}
        </div>
      </div>
    </GlassCard>
  )
}

// ─── New Feature: Performance Comparison Chart ───────────────────────────────

function PerformanceComparisonChart() {
  return (
    <GlassCard glow className="p-6">
      <h4 className="text-sm font-semibold flex items-center gap-2 mb-5">
        <BarChart3 className="w-4 h-4 text-blue-500" /> Local vs Cloud Performance
      </h4>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={performanceComparisonData} barGap={4} barCategoryGap="20%">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="metric" stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} angle={-20} textAnchor="end" height={60} />
            <YAxis stroke="#71717a" fontSize={11} tickLine={false} axisLine={false} />
            <RechartsTooltip
              contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#a1a1aa' }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
            <Bar dataKey="kimari" name="Kimari (Local)" fill="#3b82f6" radius={[3, 3, 0, 0]} />
            <Bar dataKey="openai" name="OpenAI (Cloud)" fill="#6b7280" radius={[3, 3, 0, 0]} />
            <Bar dataKey="anthropic" name="Anthropic (Cloud)" fill="#9ca3af" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-3">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
        Simulated comparison. Kimari values based on GTX 1060 6GB benchmarks. Cloud values are typical for API services.
      </div>
    </GlassCard>
  )
}

// ─── New Feature: Notification Center ────────────────────────────────────────

function NotificationCenter() {
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState(initialNotifications)
  const unreadCount = notifications.filter(n => !n.read).length

  const dismissNotification = (id: number) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const typeIcons: Record<string, React.ReactNode> = {
    update: <Download className="w-3.5 h-3.5 text-blue-500" />,
    success: <CheckCircle2 className="w-3.5 h-3.5 text-blue-500" />,
    info: <Activity className="w-3.5 h-3.5 text-cyan-500" />,
    warning: <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />,
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8 relative" aria-label="Notifications">
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute top-0.5 right-0.5 w-4 h-4 rounded-full bg-blue-500 text-[9px] text-white flex items-center justify-center font-bold">
              {unreadCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <div className="p-3 border-b border-border/30 flex items-center justify-between">
          <span className="text-sm font-semibold">Notifications</span>
          {unreadCount > 0 && (
            <button onClick={markAllRead} className="text-[10px] text-blue-500 hover:text-blue-400 transition-colors">
              Mark all read
            </button>
          )}
        </div>
        <div className="max-h-72 overflow-y-auto" style={{ scrollbarWidth: 'thin' }}>
          {notifications.length === 0 ? (
            <div className="p-6 text-center text-xs text-muted-foreground">No notifications</div>
          ) : (
            notifications.map((notif, i) => (
              <div
                key={notif.id}
                className={`p-3 border-b border-border/20 last:border-0 hover:bg-muted/20 transition-colors animate-notification-fade ${
                  !notif.read ? 'bg-blue-500/[0.03]' : ''
                }`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div className="flex items-start gap-2.5">
                  <div className="flex-shrink-0 mt-0.5">{typeIcons[notif.type]}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-xs font-medium ${!notif.read ? '' : 'text-muted-foreground'}`}>{notif.title}</span>
                      <button onClick={() => dismissNotification(notif.id)} className="text-muted-foreground hover:text-foreground transition-colors flex-shrink-0" aria-label="Dismiss">
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{notif.description}</p>
                    <span className="text-[9px] text-muted-foreground/60 mt-1 block">{notif.time}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}

// ─── New Feature: Cookie Consent Banner ──────────────────────────────────────

function CookieConsentBanner() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const raf = requestAnimationFrame(() => {
      setVisible(!localStorage.getItem('kimari-cookie-consent'))
    })
    return () => cancelAnimationFrame(raf)
  }, [])

  const handleAccept = () => {
    localStorage.setItem('kimari-cookie-consent', 'accepted')
    setVisible(false)
  }

  const handleDecline = () => {
    localStorage.setItem('kimari-cookie-consent', 'declined')
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[70] p-4 animate-slide-up-banner">
      <div className="max-w-3xl mx-auto bg-card/95 backdrop-blur-xl border border-border/50 rounded-xl shadow-2xl shadow-black/20 p-4">
        <div className="flex items-start gap-3">
          <Cookie className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold mb-1">Privacy Notice</h4>
            <p className="text-xs text-muted-foreground">
              This site uses local storage for preferences (theme, accent color, cookie consent). No tracking cookies, analytics, or data is sent to any server. All processing happens in your browser.
            </p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0 mt-1">
            <button onClick={handleDecline} className="px-3 py-1.5 text-xs rounded-lg border border-border/50 hover:bg-muted/50 transition-colors">
              Decline
            </button>
            <button onClick={handleAccept} className="px-3 py-1.5 text-xs rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors font-medium">
              Accept
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Styling: Dynamic Island Alert ──────────────────────────────────────────

function DynamicIslandAlert() {
  const [isVisible, setIsVisible] = useState(true)
  const [isExpanded, setIsExpanded] = useState(false)
  const [isContracting, setIsContracting] = useState(false)
  const messages = useMemo(() => [
    { title: 'Server running', detail: 'Kimari API active on 127.0.0.1:11435' },
    { title: 'New version available', detail: 'v0.1.83-alpha is ready to install' },
    { title: 'Model loaded', detail: 'TinyLlama 1.1B Q4_K_M ready for inference' },
  ], [])
  const [msgIndex, setMsgIndex] = useState(0)
  const initializedRef = useRef(false)

  useEffect(() => {
    if (!initializedRef.current) {
      initializedRef.current = true
      const idx = Math.floor(Math.random() * messages.length)
      setTimeout(() => setMsgIndex(idx), 100)
    }
    const interval = setInterval(() => {
      setMsgIndex(prev => (prev + 1) % messages.length)
    }, 7000)
    return () => clearInterval(interval)
  }, [messages.length])

  useEffect(() => {
    const expandTimer = setTimeout(() => setIsExpanded(true), 1500)
    const contractTimer = setTimeout(() => {
      setIsContracting(true)
      setTimeout(() => {
        setIsExpanded(false)
        setIsContracting(false)
      }, 400)
    }, 5000)
    const hideTimer = setTimeout(() => setIsVisible(false), 8000)
    return () => { clearTimeout(expandTimer); clearTimeout(contractTimer); clearTimeout(hideTimer) }
  }, [])

  if (!isVisible) return null

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[70] flex justify-center">
      <div
        className={`bg-zinc-900 border border-zinc-700/50 text-white overflow-hidden flex items-center justify-center cursor-pointer shadow-2xl shadow-blue-500/10 ${
          isExpanded ? 'dynamic-island-expanded' : isContracting ? 'dynamic-island-contracting' : 'rounded-[20px] px-3 py-1'
        }`}
        onClick={() => { setIsExpanded(!isExpanded); setIsContracting(false) }}
        style={!isExpanded && !isContracting ? { width: '120px' } : undefined}
      >
        {isExpanded ? (
          <div className="flex items-center gap-3 whitespace-nowrap">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse flex-shrink-0" />
            <div>
              <p className="text-xs font-semibold">{messages[msgIndex].title}</p>
              <p className="text-[10px] text-zinc-400">{messages[msgIndex].detail}</p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-[10px] text-zinc-400">{messages[msgIndex].title}</span>
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Styling: Section Number Badge ──────────────────────────────────────────

function SectionNumberBadge({ number, title }: { number: number; title: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  return (
    <div ref={ref} className="flex items-center gap-3 mb-4">
      {isInView && (
        <span className="animate-badge-enter inline-flex items-center justify-center w-9 h-9 rounded-lg border border-blue-500/30 bg-blue-500/10 text-blue-500 text-xs font-mono font-bold flex-shrink-0">
          {String(number).padStart(2, '0')}
        </span>
      )}
      <h2 className="text-3xl font-bold tracking-tight">{title}</h2>
    </div>
  )
}

// ─── Styling: Staggered Letter Animation Hero Title ─────────────────────────

function StaggeredLetterTitle() {
  const title = "Run useful local AI on older NVIDIA GPUs"
  const words = title.split(' ')
  let letterIndex = 0
  return (
    <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight mb-6">
      {words.map((word, wi) => (
        <span key={wi} className="inline-block mr-[0.3em]">
          {word === 'older' ? (
            <span className="bg-gradient-to-r from-blue-500 via-blue-600 to-sky-500 bg-clip-text text-transparent">
              {word.split('').map((letter) => {
                const idx = letterIndex++
                return (
                  <span
                    key={idx}
                    className="animate-letter-bounce"
                    style={{ animationDelay: `${idx * 0.03}s` }}
                  >
                    {letter}
                  </span>
                )
              })}
            </span>
          ) : word === 'NVIDIA' ? (
            <span className="bg-gradient-to-r from-blue-500 via-blue-600 to-sky-500 bg-clip-text text-transparent">
              {word.split('').map((letter) => {
                const idx = letterIndex++
                return (
                  <span
                    key={idx}
                    className="animate-letter-bounce"
                    style={{ animationDelay: `${idx * 0.03}s` }}
                  >
                    {letter}
                  </span>
                )
              })}
            </span>
          ) : word === 'GPUs' ? (
            <span className="bg-gradient-to-r from-blue-500 via-blue-600 to-sky-500 bg-clip-text text-transparent">
              {word.split('').map((letter) => {
                const idx = letterIndex++
                return (
                  <span
                    key={idx}
                    className="animate-letter-bounce"
                    style={{ animationDelay: `${idx * 0.03}s` }}
                  >
                    {letter}
                  </span>
                )
              })}
            </span>
          ) : (
            word.split('').map((letter) => {
              const idx = letterIndex++
              return (
                <span
                  key={idx}
                  className="animate-letter-bounce"
                  style={{ animationDelay: `${idx * 0.03}s` }}
                >
                  {letter}
                </span>
              )
            })
          )}
        </span>
      ))}
    </h1>
  )
}

// ─── Styling: Magnetic Social Link ──────────────────────────────────────────

function MagneticSocialLink({ href, children, className = '' }: { href: string; children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLAnchorElement>(null)
  const [offset, setOffset] = useState({ x: 0, y: 0 })

  const handleMouseMove = useCallback((e: ReactMouseEvent<HTMLAnchorElement>) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    const distX = e.clientX - centerX
    const distY = e.clientY - centerY
    const dist = Math.sqrt(distX * distX + distY * distY)
    if (dist < 80) {
      setOffset({ x: distX * 0.3, y: distY * 0.3 })
    }
  }, [])

  const handleMouseLeave = useCallback(() => {
    setOffset({ x: 0, y: 0 })
  }, [])

  return (
    <a
      ref={ref}
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={className}
      style={{ transform: `translate(${offset.x}px, ${offset.y}px)`, transition: offset.x === 0 && offset.y === 0 ? 'transform 0.3s ease' : 'transform 0.1s ease' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </a>
  )
}

// ─── Styling: Confetti Effect ───────────────────────────────────────────────

function ConfettiEffect({ active }: { active: boolean }) {
  const particles = useMemo(() => {
    if (!active) return []
    const colors = ['#3b82f6', '#2563eb', '#60a5fa', '#f59e0b', '#f43f5e', '#8b5cf6']
    return Array.from({ length: 40 }, (_, i) => ({
      id: i,
      left: `${(Math.sin(i * 9301 + 49297) * 49297 - Math.floor(Math.sin(i * 9301 + 49297) * 49297)) * 100}%`,
      color: colors[i % colors.length],
      delay: `${(i * 0.05).toFixed(2)}s`,
      size: `${4 + (i % 3) * 3}px`,
    }))
  }, [active])

  if (particles.length === 0) return null

  return (
    <div className="fixed inset-0 pointer-events-none z-[9999]">
      {particles.map((p) => (
        <div
          key={p.id}
          className="confetti-particle"
          style={{
            left: p.left,
            top: '-10px',
            backgroundColor: p.color,
            width: p.size,
            height: p.size,
            animationDelay: p.delay,
            borderRadius: Number(p.size) < 7 ? '50%' : '2px',
          }}
        />
      ))}
    </div>
  )
}

// ─── Styling: Floating Action Menu (FAB) ────────────────────────────────────

function FloatingActionMenu({ onBackToTop, onToggleSound, onOpenShortcuts, onToggleTheme, isDark }: {
  onBackToTop: () => void
  onToggleSound: () => void
  onOpenShortcuts: () => void
  onToggleTheme: () => void
  isDark: boolean
}) {
  const [isOpen, setIsOpen] = useState(false)
  const actions = useMemo(() => [
    { icon: ArrowUp, label: 'Back to top', onClick: onBackToTop },
    { icon: Volume2, label: 'Toggle sound', onClick: onToggleSound },
    { icon: Keyboard, label: 'Shortcuts', onClick: onOpenShortcuts },
    { icon: isDark ? Sun : Moon, label: 'Toggle theme', onClick: onToggleTheme },
  ], [onBackToTop, onToggleSound, onOpenShortcuts, onToggleTheme, isDark])

  return (
    <div className="fixed bottom-6 left-6 z-50 flex flex-col-reverse items-center gap-2">
      <AnimatePresence>
        {isOpen && actions.map((action, i) => (
          <motion.div
            key={action.label}
            initial={{ opacity: 0, scale: 0.3, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.3, y: 20 }}
            transition={{ delay: i * 0.05, duration: 0.2 }}
            className="flex items-center gap-2"
          >
            <span className="text-[10px] text-muted-foreground bg-card border border-border/50 px-2 py-1 rounded-md shadow-sm whitespace-nowrap">
              {action.label}
            </span>
            <button
              onClick={() => { action.onClick(); setIsOpen(false) }}
              className="w-10 h-10 rounded-full bg-card border border-border/50 shadow-lg flex items-center justify-center hover:bg-blue-500/10 hover:border-blue-500/30 transition-all duration-200 active:scale-90"
              aria-label={action.label}
            >
              <action.icon className="w-4 h-4 text-blue-500" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 active:scale-90 ${
          isOpen
            ? 'bg-blue-600 text-white rotate-45'
            : 'bg-gradient-to-br from-blue-500 to-blue-700 text-white'
        }`}
        aria-label="Quick actions"
      >
        <Plus className="w-5 h-5" />
      </button>
    </div>
  )
}

// ─── Styling: Context-Aware Cursor Ring ─────────────────────────────────────

function CursorRing() {
  const [pos, setPos] = useState({ x: -100, y: -100 })
  const [isPointer, setIsPointer] = useState(false)

  useEffect(() => {
    const move = (e: MouseEvent) => {
      setPos({ x: e.clientX, y: e.clientY })
      const target = e.target as HTMLElement
      setIsPointer(
        target.tagName === 'BUTTON' ||
        target.tagName === 'A' ||
        target.closest('button') !== null ||
        target.closest('a') !== null ||
        (target as HTMLElement).dataset?.cursor === 'pointer'
      )
    }
    window.addEventListener('mousemove', move, { passive: true })
    return () => window.removeEventListener('mousemove', move)
  }, [])

  return (
    <div
      className={`cursor-ring hidden lg:block ${isPointer ? 'cursor-ring-pointer' : ''}`}
      style={{ left: pos.x, top: pos.y }}
    />
  )
}

// ─── Styling: Gradient Border on Scroll ─────────────────────────────────────

function GradientBorderOnScroll({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, margin: '-40px' })
  const [hasFlashed, setHasFlashed] = useState(false)

  useEffect(() => {
    if (isInView && !hasFlashed) {
      const timer = setTimeout(() => setHasFlashed(true), 100)
      return () => clearTimeout(timer)
    }
  }, [isInView, hasFlashed])

  return (
    <div
      ref={ref}
      className={`${className} border-2 border-transparent ${hasFlashed ? 'gradient-border-flash' : ''}`}
    >
      {children}
    </div>
  )
}

// ─── New Feature: System Requirements Table ─────────────────────────────────

function SystemRequirementsTable() {
  const [compatState, setCompatState] = useState<Record<string, 'pass' | 'fail'>>(() => ({
    gpu: 'pass', vram: 'pass', cpu: 'pass', ram: 'pass', disk: 'pass', os: 'pass', cuda: 'pass',
  }))

  const toggleCompat = useCallback((key: string) => {
    setCompatState(prev => ({
      ...prev,
      [key]: prev[key] === 'pass' ? 'fail' : 'pass',
    }))
  }, [])

  return (
    <Card className="border-0 overflow-hidden">
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-[120px]">Component</TableHead>
              <TableHead>Minimum</TableHead>
              <TableHead>Recommended</TableHead>
              <TableHead className="hidden sm:table-cell">Notes</TableHead>
              <TableHead className="w-[80px] text-center">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {systemRequirementsTableData.map((row) => {
              const status = compatState[row.compatKey]
              return (
                <TableRow
                  key={row.component}
                  className={`cursor-pointer transition-colors duration-200 ${
                    status === 'pass'
                      ? 'bg-blue-500/[0.03] hover:bg-blue-500/[0.06]'
                      : 'bg-red-500/[0.03] hover:bg-red-500/[0.06]'
                  }`}
                  onClick={() => toggleCompat(row.compatKey)}
                >
                  <TableCell className="font-semibold text-sm">{row.component}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">{row.minimum}</TableCell>
                  <TableCell className="text-sm text-blue-500/80">{row.recommended}</TableCell>
                  <TableCell className="text-xs text-muted-foreground hidden sm:table-cell">{row.notes}</TableCell>
                  <TableCell className="text-center">
                    <button
                      className={`inline-flex items-center justify-center w-7 h-7 rounded-full transition-all duration-200 ${
                        status === 'pass'
                          ? 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20'
                          : 'bg-red-500/10 text-red-500 hover:bg-red-500/20'
                      }`}
                      aria-label={`Toggle ${row.component} compatibility`}
                    >
                      {status === 'pass' ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                    </button>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </CardContent>
      <div className="px-6 py-3 border-t border-border/30 bg-muted/20 flex items-center gap-2 text-xs text-muted-foreground">
        <AlertCircle className="w-3.5 h-3.5" />
        Click any row to toggle simulated compatibility status.
      </div>
    </Card>
  )
}

// ─── New Feature: API Endpoint Explorer ─────────────────────────────────────

function APIEndpointExplorer() {
  const [activeTab, setActiveTab] = useState(0)
  const [copiedField, setCopiedField] = useState<string | null>(null)
  const { toast } = useToast()

  const copyToClipboard = useCallback((text: string, field: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    toast({ title: 'Copied to clipboard!' })
    setTimeout(() => setCopiedField(null), 2000)
  }, [toast])

  const endpoint = apiEndpoints[activeTab]

  return (
    <div className="space-y-4">
      {/* Endpoint tabs */}
      <div className="flex flex-wrap gap-2">
        {apiEndpoints.map((ep, i) => (
          <button
            key={ep.path}
            onClick={() => setActiveTab(i)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono border transition-all duration-200 ${
              activeTab === i
                ? 'bg-blue-500/10 border-blue-500/30 text-blue-500'
                : 'bg-muted/30 border-border/30 text-muted-foreground hover:bg-muted/50'
            }`}
          >
            <span className={`font-bold mr-1.5 ${ep.method === 'GET' ? 'text-cyan-400' : 'text-amber-400'}`}>{ep.method}</span>
            {ep.path}
          </button>
        ))}
      </div>

      {/* Endpoint detail */}
      <Card className="border-0 overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
              endpoint.method === 'GET' ? 'bg-cyan-500/10 text-cyan-400' : 'bg-amber-500/10 text-amber-400'
            }`}>{endpoint.method}</span>
            <code className="text-sm font-mono text-foreground">{endpoint.path}</code>
          </div>
          <p className="text-xs text-muted-foreground mt-1">{endpoint.description}</p>
        </CardHeader>
        <CardContent className="space-y-3">
          {endpoint.request && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Request Body</span>
                <button
                  onClick={() => copyToClipboard(endpoint.request, 'req')}
                  className="p-1 rounded hover:bg-muted/50 transition-colors"
                  aria-label="Copy request"
                >
                  {copiedField === 'req' ? <Check className="w-3 h-3 text-blue-500" /> : <Copy className="w-3 h-3 text-muted-foreground" />}
                </button>
              </div>
              <pre className="text-[11px] font-mono bg-zinc-950 border border-zinc-800 rounded-lg p-3 overflow-x-auto text-zinc-300 leading-relaxed">
                {endpoint.request}
              </pre>
            </div>
          )}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Response</span>
              <button
                onClick={() => copyToClipboard(endpoint.response, 'res')}
                className="p-1 rounded hover:bg-muted/50 transition-colors"
                aria-label="Copy response"
              >
                {copiedField === 'res' ? <Check className="w-3 h-3 text-blue-500" /> : <Copy className="w-3 h-3 text-muted-foreground" />}
              </button>
            </div>
            <pre className="text-[11px] font-mono bg-zinc-950 border border-zinc-800 rounded-lg p-3 overflow-x-auto text-zinc-300 leading-relaxed">
              {endpoint.response}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// ─── New Feature: Interactive Model Card Gallery ────────────────────────────

function ModelCardGallery() {
  const [flippedCards, setFlippedCards] = useState<Set<number>>(() => new Set())

  const toggleFlip = useCallback((index: number) => {
    setFlippedCards(prev => {
      const next = new Set(prev)
      if (next.has(index)) next.delete(index)
      else next.add(index)
      return next
    })
  }, [])

  return (
    <div className="overflow-x-auto pb-4 -mx-4 px-4">
      <div className="flex gap-4" style={{ minWidth: 'max-content' }}>
        {modelCards.map((card, i) => (
          <motion.div
            key={card.name}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.08, duration: 0.4 }}
            className={`w-56 h-72 cursor-pointer flex-shrink-0 [perspective:1000px] ${flippedCards.has(i) ? 'model-card-flipped' : ''}`}
            onClick={() => toggleFlip(i)}
          >
            <div className="model-card-inner w-full h-full">
              {/* Front */}
              <div className="model-card-front w-full h-full rounded-xl border border-border/30 bg-card p-5 flex flex-col items-center justify-center hover:border-blue-500/30 transition-colors">
                <span className="text-4xl mb-3">{card.icon}</span>
                <h4 className="font-bold text-sm text-center mb-1">{card.name}</h4>
                <Badge variant="outline" className="text-[10px] mt-1">{card.params} params</Badge>
                <p className="text-[10px] text-muted-foreground mt-3 text-center">Click to see specs</p>
              </div>
              {/* Back */}
              <div className="model-card-back w-full h-full rounded-xl border border-blue-500/30 bg-card p-4 flex flex-col justify-between">
                <div>
                  <h4 className="font-bold text-xs mb-2 text-blue-500">{card.name}</h4>
                  <div className="space-y-1.5 text-[11px]">
                    <div className="flex justify-between"><span className="text-muted-foreground">Quantization</span><span className="font-mono">{card.quant}</span></div>
                    <div className="flex justify-between"><span className="text-muted-foreground">VRAM</span><span className="font-mono">{card.vram}</span></div>
                    <div className="flex justify-between"><span className="text-muted-foreground">Speed</span><span className="font-mono text-blue-500">{card.speed}</span></div>
                    <div className="flex justify-between"><span className="text-muted-foreground">Context</span><span className="font-mono">{card.context}</span></div>
                  </div>
                </div>
                <p className="text-[10px] text-muted-foreground leading-relaxed">{card.description}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// ─── New Feature: Session Timer ─────────────────────────────────────────────

function SessionTimer() {
  const [seconds, setSeconds] = useState(0)
  const [milestoneFlash, setMilestoneFlash] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds(s => {
        const next = s + 1
        // Milestones: 5min, 10min, 15min, 30min, 60min
        if (next === 300 || next === 600 || next === 900 || next === 1800 || next === 3600) {
          setMilestoneFlash(true)
          setTimeout(() => setMilestoneFlash(false), 600)
        }
        return next
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const hh = String(Math.floor(seconds / 3600)).padStart(2, '0')
  const mm = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0')
  const ss = String(seconds % 60).padStart(2, '0')

  return (
    <div className={`hidden lg:flex items-center gap-1.5 text-[10px] font-mono text-muted-foreground px-2 py-1 rounded-md bg-muted/30 border border-border/30 ${
      milestoneFlash ? 'animate-timer-pulse' : ''
    }`}>
      <Clock className="w-3 h-3" />
      <span>{hh}:{mm}:{ss}</span>
    </div>
  )
}

// ─── New Feature: Accessibility Panel ───────────────────────────────────────

function AccessibilityPanel() {
  const [open, setOpen] = useState(false)
  const [settings, setSettings] = useState({ fontSize: 100, reduceMotion: false, highContrast: false, lineHeight: 150, focusIndicators: false })

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    try {
      const saved = localStorage.getItem('kimari-a11y')
      if (saved) setSettings(JSON.parse(saved))
    } catch { /* ignore */ }
  }, [])
  /* eslint-enable react-hooks/set-state-in-effect */

  const updateSetting = useCallback((key: string, value: number | boolean) => {
    setSettings(prev => {
      const next = { ...prev, [key]: value }
      localStorage.setItem('kimari-a11y', JSON.stringify(next))
      // Apply settings
      const root = document.documentElement
      root.style.setProperty('--a11y-font-scale', `${next.fontSize / 100}`)
      root.style.setProperty('--a11y-line-height', `${next.lineHeight / 100}`)
      root.classList.toggle('reduce-motion', next.reduceMotion)
      root.classList.toggle('high-contrast-mode', next.highContrast)
      root.classList.toggle('focus-indicators', next.focusIndicators)
      if (next.fontSize !== 100) {
        root.style.fontSize = `${next.fontSize}%`
      } else {
        root.style.fontSize = ''
      }
      return next
    })
  }, [])

  // Apply settings on mount
  useEffect(() => {
    const root = document.documentElement
    if (settings.fontSize !== 100) root.style.fontSize = `${settings.fontSize}%`
    root.classList.toggle('reduce-motion', settings.reduceMotion)
    root.classList.toggle('high-contrast-mode', settings.highContrast)
    root.classList.toggle('focus-indicators', settings.focusIndicators)
  }, [])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Accessibility settings">
          <Eye className="w-4 h-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2"><Eye className="w-5 h-5 text-blue-500" /> Accessibility</DialogTitle>
          <DialogDescription>Adjust display and interaction settings.</DialogDescription>
        </DialogHeader>
        <div className="space-y-5 mt-4">
          {/* Font Size */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Font Size</label>
              <span className="text-xs text-muted-foreground font-mono">{settings.fontSize}%</span>
            </div>
            <input
              type="range"
              min="80"
              max="150"
              step="10"
              value={settings.fontSize}
              onChange={e => updateSetting('fontSize', Number(e.target.value))}
              className="w-full accent-blue-500"
              aria-label="Font size"
            />
          </div>
          {/* Line Height */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Line Spacing</label>
              <span className="text-xs text-muted-foreground font-mono">{settings.lineHeight}%</span>
            </div>
            <input
              type="range"
              min="100"
              max="200"
              step="10"
              value={settings.lineHeight}
              onChange={e => updateSetting('lineHeight', Number(e.target.value))}
              className="w-full accent-blue-500"
              aria-label="Line height"
            />
          </div>
          {/* Toggle: Reduce Motion */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Reduce Motion</label>
              <p className="text-[10px] text-muted-foreground">Disables all animations</p>
            </div>
            <button
              onClick={() => updateSetting('reduceMotion', !settings.reduceMotion)}
              className={`w-10 h-6 rounded-full transition-colors duration-200 relative ${settings.reduceMotion ? 'bg-blue-500' : 'bg-muted'}`}
              role="switch"
              aria-checked={settings.reduceMotion}
              aria-label="Reduce motion"
            >
              <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform duration-200 ${settings.reduceMotion ? 'translate-x-4' : ''}`} />
            </button>
          </div>
          {/* Toggle: High Contrast */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">High Contrast</label>
              <p className="text-[10px] text-muted-foreground">Maximizes text contrast</p>
            </div>
            <button
              onClick={() => updateSetting('highContrast', !settings.highContrast)}
              className={`w-10 h-6 rounded-full transition-colors duration-200 relative ${settings.highContrast ? 'bg-blue-500' : 'bg-muted'}`}
              role="switch"
              aria-checked={settings.highContrast}
              aria-label="High contrast mode"
            >
              <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform duration-200 ${settings.highContrast ? 'translate-x-4' : ''}`} />
            </button>
          </div>
          {/* Toggle: Focus Indicators */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Enhanced Focus</label>
              <p className="text-[10px] text-muted-foreground">Stronger focus indicators</p>
            </div>
            <button
              onClick={() => updateSetting('focusIndicators', !settings.focusIndicators)}
              className={`w-10 h-6 rounded-full transition-colors duration-200 relative ${settings.focusIndicators ? 'bg-blue-500' : 'bg-muted'}`}
              role="switch"
              aria-checked={settings.focusIndicators}
              aria-label="Focus indicators"
            >
              <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform duration-200 ${settings.focusIndicators ? 'translate-x-4' : ''}`} />
            </button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// ─── New Feature: Theme Preview Switcher ────────────────────────────────────

function ThemePreviewSwitcher({ currentTheme, onThemeChange }: { currentTheme: string; onThemeChange: (id: string) => void }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Switch visual theme">
          <Palette className="w-4 h-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-3" align="end">
        <p className="text-xs font-semibold mb-3">Visual Theme</p>
        <div className="space-y-2">
          {visualThemes.map((theme) => (
            <button
              key={theme.id}
              onClick={() => onThemeChange(theme.id)}
              className={`w-full flex items-center gap-3 px-2 py-1.5 rounded-lg transition-all duration-200 ${
                currentTheme === theme.id ? 'bg-blue-500/10 border border-blue-500/30' : 'hover:bg-muted/50 border border-transparent'
              }`}
            >
              {/* Preview swatch */}
              <div className="flex rounded-md overflow-hidden border border-border/30 flex-shrink-0">
                <div className="w-4 h-6" style={{ backgroundColor: theme.preview.bg }} />
                <div className="w-3 h-6" style={{ backgroundColor: theme.preview.card }} />
                <div className="w-1 h-6" style={{ backgroundColor: theme.preview.accent }} />
              </div>
              <span className="text-xs font-medium">{theme.name}</span>
              {currentTheme === theme.id && <Check className="w-3 h-3 text-blue-500 ml-auto" />}
            </button>
          ))}
        </div>
        <p className="text-[10px] text-muted-foreground mt-2">Changes background, cards, and text colors</p>
      </PopoverContent>
    </Popover>
  )
}

// ─── Main Page ──────────────────────────────────────────────────────────────

// ─── Styling Enhancement 1: Animated Wave Divider ─────────────────────────────

function WaveDivider() {
  return (
    <div className="relative w-full h-12 overflow-hidden select-none" aria-hidden="true">
      <svg className="absolute bottom-0 w-full h-12" viewBox="0 0 720 64" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path className="wave-divider-path-1" d="M0,32 C80,48 160,16 240,32 C320,48 400,16 480,32 C560,48 640,16 720,32 L720,64 L0,64 Z" fill="rgba(59,130,246,0.06)" />
        <path className="wave-divider-path-2" d="M0,32 C120,52 200,12 320,32 C440,52 520,12 640,32 C700,44 710,28 720,32 L720,64 L0,64 Z" fill="rgba(59,130,246,0.03)" />
      </svg>
      {/* Original flowing dot dividers as fallback */}
      <div className="absolute inset-x-0 top-1/2 flex items-center justify-center gap-1">
        <motion.div className="w-1 h-1 rounded-full bg-blue-500/40" animate={{ x: [-20, 20, -20] }} transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }} />
        <motion.div className="w-1.5 h-1.5 rounded-full bg-blue-500/50" animate={{ x: [20, -20, 20] }} transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }} />
        <motion.div className="w-1 h-1 rounded-full bg-blue-500/40" animate={{ x: [-20, 20, -20] }} transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }} />
      </div>
    </div>
  )
}

// ─── Styling Enhancement 2: Elastic Hover Card ───────────────────────────────

function ElasticCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div
      className={className}
      whileHover={{ scale: 1.03 }}
      transition={{ type: 'spring', stiffness: 400, damping: 10, mass: 0.8 }}
    >
      {children}
    </motion.div>
  )
}

// ─── Styling Enhancement 3: Gradient Mesh Background ─────────────────────────

function GradientMeshBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
      <div className="animate-gradient-mesh-1 absolute w-[500px] h-[500px] rounded-full blur-[120px] opacity-[0.08]"
        style={{ top: '-10%', left: '-5%', background: 'radial-gradient(circle, #3b82f6 0%, transparent 70%)' }} />
      <div className="animate-gradient-mesh-2 absolute w-[400px] h-[400px] rounded-full blur-[100px] opacity-[0.06]"
        style={{ top: '20%', right: '-8%', background: 'radial-gradient(circle, #60a5fa 0%, transparent 70%)' }} />
      <div className="animate-gradient-mesh-3 absolute w-[350px] h-[350px] rounded-full blur-[80px] opacity-[0.05]"
        style={{ bottom: '5%', left: '30%', background: 'radial-gradient(circle, #2563eb 0%, transparent 70%)' }} />
    </div>
  )
}

// ─── Styling Enhancement 4: Neon Glow Heading ────────────────────────────────

function NeonGlowHeading({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`neon-glow-text ${className}`}>
      {children}
    </span>
  )
}

// ─── Styling Enhancement 5: Depth Parallax Card ──────────────────────────────

function DepthParallaxCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const [rotateX, setRotateX] = useState(0)
  const [rotateY, setRotateY] = useState(0)
  const ref = useRef<HTMLDivElement>(null)

  const handleMouseMove = useCallback((e: ReactMouseEvent<HTMLDivElement>) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width - 0.5
    const y = (e.clientY - rect.top) / rect.height - 0.5
    setRotateX(-y * 12)
    setRotateY(x * 12)
  }, [])

  const handleMouseLeave = useCallback(() => {
    setRotateX(0)
    setRotateY(0)
  }, [])

  return (
    <div
      ref={ref}
      className={className}
      style={{ perspective: '800px' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        style={{ transformStyle: 'preserve-3d' }}
        animate={{ rotateX, rotateY }}
        transition={{ type: 'spring', stiffness: 200, damping: 20 }}
      >
        {/* Back shadow layer - creates depth */}
        <div className="absolute inset-1 rounded-xl bg-gradient-to-br from-blue-500/10 to-transparent blur-sm" style={{ transform: 'translateZ(-10px)' }} />
        {/* Main content */}
        <div style={{ transform: 'translateZ(20px)' }}>
          {children}
        </div>
      </motion.div>
    </div>
  )
}

// ─── Styling Enhancement 7: Particle Burst on Hover ──────────────────────────

function ParticleBurstTrigger({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number }>>([])
  const counterRef = useRef(0)

  const handleClick = useCallback((e: ReactMouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const newParticles = Array.from({ length: 8 }, (_, i) => ({
      id: counterRef.current++,
      x: x + (Math.sin(i * Math.PI / 4) * 40),
      y: y + (Math.cos(i * Math.PI / 4) * 40),
    }))
    setParticles(prev => [...prev, ...newParticles])
    setTimeout(() => setParticles(prev => prev.filter(p => !newParticles.find(np => np.id === p.id))), 700)
  }, [])

  return (
    <div className={`relative overflow-hidden ${className}`} onClick={handleClick}>
      {children}
      {particles.map(p => (
        <div
          key={p.id}
          className="particle-burst-item"
          style={{ left: p.x, top: p.y, '--px': `${(p.x - 50) * 2}px`, '--py': `${(p.y - 50) * 2}px` } as React.CSSProperties}
        />
      ))}
    </div>
  )
}

// ─── Styling Enhancement 8: Scroll-Linked Accent Shift ──────────────────────

function ScrollLinkedAccentOverlay() {
  const { scrollY } = useScroll()
  const hue = useTransform(scrollY, [0, 5000], [0, 30])

  return (
    <motion.div
      className="fixed inset-0 pointer-events-none z-0"
      style={{
        background: `radial-gradient(ellipse at 50% 0%, hsla(${hue}, 70%, 50%, 0.02) 0%, transparent 50%)`,
      }}
      aria-hidden="true"
    />
  )
}

// ─── Styling Enhancement 9: Glassmorphism Code Block ─────────────────────────

function GlassmorphismCodeBlock({ code, language = 'bash', className = '' }: { code: string; language?: string; className?: string }) {
  const { toast } = useToast()
  return (
    <div className={`glassmorphism-code p-4 font-mono text-sm relative ${className}`}>
      <div className="flex items-center justify-between mb-2 relative z-10">
        <span className="text-[10px] text-blue-500/60 font-semibold uppercase tracking-wider">{language}</span>
        <button
          onClick={() => { navigator.clipboard.writeText(code); toast({ title: 'Copied to clipboard!' }) }}
          className="text-muted-foreground hover:text-blue-500 transition-colors"
          aria-label="Copy code"
        >
          <Copy className="w-3.5 h-3.5" />
        </button>
      </div>
      <pre className="text-muted-foreground whitespace-pre-wrap break-all relative z-10 text-xs leading-relaxed">{code}</pre>
    </div>
  )
}

// ─── Styling Enhancement 10: Animated Dash Border ────────────────────────────

function AnimatedDashBorder({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`dash-border-hover relative rounded-xl ${className}`}>
      <svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none" aria-hidden="true">
        <rect x="0" y="0" width="100%" height="100%" rx="12" fill="none" stroke="rgba(59,130,246,0.15)" strokeWidth="1" />
      </svg>
      <div className="relative z-10">
        {children}
      </div>
    </div>
  )
}

// ─── Feature 1: GPU Temperature Simulator ─────────────────────────────────────

function GPUTemperatureSimulator() {
  const [activeProfile, setActiveProfile] = useState('idle')
  const [animatedTemp, setAnimatedTemp] = useState(38)
  const profile = gpuTempProfiles.find(p => p.id === activeProfile) || gpuTempProfiles[0]

  useEffect(() => {
    const startTemp = animatedTemp
    const endTemp = profile.temp
    const duration = 800
    const startTime = Date.now()
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3) // ease-out cubic
      setAnimatedTemp(Math.round(startTemp + (endTemp - startTemp) * eased))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [activeProfile, animatedTemp])

  const tempPercent = Math.min(((animatedTemp - 20) / 70) * 100, 100)
  const thermometerColor = animatedTemp < 50 ? '#3b82f6' : animatedTemp < 70 ? '#f59e0b' : '#ef4444'

  return (
    <div className="space-y-6">
      {/* Workload selector */}
      <div className="flex flex-wrap gap-2">
        {gpuTempProfiles.map(p => (
          <button
            key={p.id}
            onClick={() => setActiveProfile(p.id)}
            className={`px-3 py-2 rounded-lg text-xs font-medium border transition-all duration-300 ${
              activeProfile === p.id
                ? 'border-blue-500/30 bg-blue-500/10 text-blue-500'
                : 'border-border/50 text-muted-foreground hover:border-blue-500/20 hover:bg-blue-500/5'
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-[200px_1fr] gap-6">
        {/* Thermometer visualization */}
        <div className="flex flex-col items-center gap-2">
          <div className="relative w-12 h-48 rounded-full border-2 border-border/40 bg-muted/20 overflow-hidden">
            {/* Mercury fill */}
            <motion.div
              className="absolute bottom-0 left-0 right-0 rounded-b-full"
              style={{ background: `linear-gradient(to top, ${thermometerColor}, ${thermometerColor}88)` }}
              initial={{ height: '10%' }}
              animate={{ height: `${tempPercent}%` }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            />
            {/* Temperature marks */}
            {[20, 40, 60, 80].map(mark => (
              <div key={mark} className="absolute left-full ml-1 text-[9px] text-muted-foreground" style={{ bottom: `${((mark - 20) / 70) * 100}%` }}>
                {mark}°
              </div>
            ))}
          </div>
          {/* Bulb */}
          <div className="w-14 h-14 rounded-full border-2 border-border/40 flex items-center justify-center"
            style={{ background: `radial-gradient(circle, ${thermometerColor}33, ${thermometerColor}11)` }}>
            <span className="text-lg font-black" style={{ color: thermometerColor }}>{animatedTemp}°</span>
          </div>
        </div>

        {/* Stats */}
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px rounded-xl">
            <Card className="rounded-xl border-0">
              <CardContent className="pt-5 space-y-3">
                <div className="flex items-center gap-2 mb-2">
                  <GaugeCircle className="w-4 h-4" style={{ color: profile.color }} />
                  <span className="font-semibold text-sm">{profile.label} Mode</span>
                </div>
                <p className="text-xs text-muted-foreground mb-3">{profile.description}</p>
                {[
                  { label: 'Temperature', value: `${animatedTemp}°C`, bar: tempPercent, color: thermometerColor },
                  { label: 'Fan Speed', value: `${profile.fanSpeed}%`, bar: profile.fanSpeed, color: '#60a5fa' },
                  { label: 'Power Draw', value: `${profile.power}W`, bar: Math.min((profile.power / 150) * 100, 100), color: '#f59e0b' },
                ].map(stat => (
                  <div key={stat.label}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-muted-foreground">{stat.label}</span>
                      <span className="font-mono font-medium">{stat.value}</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: stat.color }}
                        initial={{ width: 0 }}
                        animate={{ width: `${stat.bar}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
            <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
            Simulated temperatures. Actual values depend on ambient temp, airflow, and thermal paste.
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Feature 2: Prompt Template Library ──────────────────────────────────────

function PromptTemplateLibrary() {
  const [activeCategory, setActiveCategory] = useState('All')
  const { toast } = useToast()
  const categories = ['All', ...Array.from(new Set(promptTemplates.map(t => t.category)))]

  const filtered = activeCategory === 'All' ? promptTemplates : promptTemplates.filter(t => t.category === activeCategory)

  return (
    <div className="space-y-5">
      {/* Category filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all duration-200 ${
              activeCategory === cat
                ? 'border-blue-500/30 bg-blue-500/10 text-blue-500'
                : 'border-border/50 text-muted-foreground hover:border-blue-500/20 hover:bg-blue-500/5'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Template cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {filtered.map(template => (
          <motion.div
            key={template.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="group p-4 rounded-xl border border-border/40 hover:border-blue-500/30 hover:shadow-md hover:shadow-blue-500/5 transition-all duration-300 bg-card">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <template.icon className="w-3.5 h-3.5 text-blue-500" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold">{template.title}</h4>
                    <Badge variant="outline" className="text-[9px] px-1.5 py-0 mt-0.5">{template.category}</Badge>
                  </div>
                </div>
                <button
                  onClick={() => { navigator.clipboard.writeText(template.template); toast({ title: 'Template copied!' }) }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg hover:bg-blue-500/10 text-muted-foreground hover:text-blue-500"
                  aria-label={`Copy ${template.title} template`}
                >
                  <Copy className="w-3.5 h-3.5" />
                </button>
              </div>
              <p className="text-xs text-muted-foreground mb-2">{template.description}</p>
              <div className="text-[10px] text-muted-foreground/60 line-clamp-2 font-mono leading-relaxed">
                {template.template.slice(0, 120)}...
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// ─── Feature 3: Interactive Changelog Timeline ───────────────────────────────

function InteractiveChangelogTimeline() {
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null)
  const [filterType, setFilterType] = useState<string>('All')
  const types = ['All', ...Array.from(new Set(enhancedChangelogItems.map(i => i.type)))]
  const typeColors: Record<string, string> = { Feature: '#3b82f6', Improve: '#60a5fa', Safety: '#f43f5e', Fix: '#f59e0b', Milestone: '#8b5cf6', Release: '#2563eb' }

  const filtered = filterType === 'All' ? enhancedChangelogItems : enhancedChangelogItems.filter(i => i.type === filterType)

  return (
    <div className="space-y-5">
      {/* Type filter */}
      <div className="flex flex-wrap gap-2">
        {types.map(type => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all duration-200 ${
              filterType === type
                ? 'border-blue-500/30 bg-blue-500/10 text-blue-500'
                : 'border-border/50 text-muted-foreground hover:border-blue-500/20 hover:bg-blue-500/5'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="relative">
        <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500/40 via-blue-600/20 to-transparent" />
        <div className="space-y-3">
          {filtered.map((item, i) => {
            const color = typeColors[item.type] || '#3b82f6'
            const isExpanded = selectedVersion === `${item.version}-${i}`
            return (
              <motion.div
                key={`${item.version}-${i}`}
                initial={{ opacity: 0, x: -10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05, duration: 0.3 }}
              >
                <button
                  onClick={() => setSelectedVersion(isExpanded ? null : `${item.version}-${i}`)}
                  className="w-full text-left"
                >
                  <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-white/[0.02] transition-colors">
                    <div className="relative flex-shrink-0 mt-1">
                      <div className="w-6 h-6 rounded-full border-2 flex items-center justify-center"
                        style={{ borderColor: color, backgroundColor: `${color}15` }}>
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                        <Badge variant="outline" className="text-[9px] px-1.5 py-0"
                          style={{ borderColor: `${color}30`, color, backgroundColor: `${color}10` }}>{item.type}</Badge>
                        <code className="text-[10px] font-mono text-muted-foreground">{item.version}</code>
                        <span className="text-[10px] text-muted-foreground">{item.date}</span>
                      </div>
                      <h4 className="text-sm font-medium">{item.title}</h4>
                      <p className="text-xs text-muted-foreground mt-0.5">{item.description}</p>
                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="overflow-hidden"
                          >
                            <div className="changelog-detail-expand mt-2 p-3 rounded-lg bg-muted/30 border border-border/20">
                              <p className="text-xs text-muted-foreground leading-relaxed">{item.details}</p>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                    <ChevronRight className={`w-4 h-4 text-muted-foreground transition-transform flex-shrink-0 ${isExpanded ? 'rotate-90' : ''}`} />
                  </div>
                </button>
              </motion.div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

// ─── Feature 4: Model Download Progress Simulator ────────────────────────────

function ModelDownloadSimulator() {
  const [selectedModel, setSelectedModel] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [downloading, setDownloading] = useState(false)
  const [downloadComplete, setDownloadComplete] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const model = downloadModels.find(m => m.id === selectedModel)

  const startDownload = useCallback(() => {
    if (!model) return
    setProgress(0)
    setDownloading(true)
    setDownloadComplete(false)
    const totalMs = (model.size / model.speed) * 1000 // simulated time
    const intervalMs = 50
    const incrementPerTick = (intervalMs / totalMs) * 100
    intervalRef.current = setInterval(() => {
      setProgress(prev => {
        const next = prev + incrementPerTick + (Math.random() * incrementPerTick * 0.3)
        if (next >= 100) {
          if (intervalRef.current) clearInterval(intervalRef.current)
          setDownloading(false)
          setDownloadComplete(true)
          return 100
        }
        return next
      })
    }, intervalMs)
  }, [model])

  const cancelDownload = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    setDownloading(false)
    setProgress(0)
  }, [])

  useEffect(() => {
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [])

  const formatSize = (mb: number) => mb >= 1000 ? `${(mb / 1000).toFixed(1)} GB` : `${mb} MB`
  const downloadedSize = model ? (progress / 100) * model.size : 0
  const speed = downloading ? (model ? (model.speed * (0.8 + Math.random() * 0.4)).toFixed(1) : '0') : '0'
  const eta = model && downloading ? Math.max(0, Math.ceil(((model.size - downloadedSize) / model.speed))) : 0

  return (
    <div className="space-y-5">
      {/* Model selector */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {downloadModels.map(m => (
          <button
            key={m.id}
            onClick={() => { if (!downloading) { setSelectedModel(m.id); setProgress(0); setDownloadComplete(false) } }}
            disabled={downloading}
            className={`p-3 rounded-lg border text-left transition-all duration-200 ${
              selectedModel === m.id
                ? 'border-blue-500/30 bg-blue-500/10'
                : 'border-border/40 hover:border-blue-500/20 hover:bg-blue-500/5'
            } ${downloading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <p className="text-xs font-medium truncate">{m.name}</p>
            <p className="text-[10px] text-muted-foreground">{formatSize(m.size)} · {m.quant}</p>
          </button>
        ))}
      </div>

      {model && (
        <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px rounded-xl">
          <Card className="rounded-xl border-0">
            <CardContent className="pt-5 space-y-4">
              {/* Progress bar */}
              <div>
                <div className="flex justify-between text-xs mb-2">
                  <span className="font-medium">{model.name}</span>
                  <span className="font-mono text-muted-foreground">{progress.toFixed(1)}%</span>
                </div>
                <div className="h-3 rounded-full bg-muted overflow-hidden relative">
                  <motion.div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-blue-600 relative"
                    style={{ width: `${progress}%` }}
                    transition={{ duration: 0.1 }}
                  >
                    {downloading && <div className="absolute inset-0 download-shimmer" />}
                  </motion.div>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center">
                  <p className="text-[10px] text-muted-foreground">Downloaded</p>
                  <p className="text-sm font-mono font-medium">{formatSize(Math.round(downloadedSize))}</p>
                </div>
                <div className="text-center">
                  <p className="text-[10px] text-muted-foreground">Speed</p>
                  <p className="text-sm font-mono font-medium">{downloading ? `${speed} MB/s` : '—'}</p>
                </div>
                <div className="text-center">
                  <p className="text-[10px] text-muted-foreground">ETA</p>
                  <p className="text-sm font-mono font-medium">{downloading ? `${eta}s` : downloadComplete ? 'Done' : '—'}</p>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex gap-2">
                {!downloading && !downloadComplete && (
                  <Button onClick={startDownload} size="sm" className="gap-2 text-xs">
                    <Download className="w-3.5 h-3.5" /> Start Download
                  </Button>
                )}
                {downloading && (
                  <Button onClick={cancelDownload} variant="destructive" size="sm" className="gap-2 text-xs">
                    <X className="w-3.5 h-3.5" /> Cancel
                  </Button>
                )}
                {downloadComplete && (
                  <div className="flex items-center gap-2 text-blue-500 text-sm">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Download complete! SHA256: verified</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <p className="text-[10px] text-muted-foreground flex items-center gap-1.5">
        <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
        Simulated download. Actual speed depends on network and HuggingFace CDN.
      </p>
    </div>
  )
}

// ─── Feature 5: Configuration Wizard ─────────────────────────────────────────

function ConfigurationWizard() {
  const [step, setStep] = useState(0)
  const [gpu, setGpu] = useState('')
  const [useCase, setUseCase] = useState('')
  const [priority, setPriority] = useState('')
  const [generated, setGenerated] = useState(false)
  const { toast } = useToast()

  const steps = [
    { title: 'Select Your GPU', completed: !!gpu },
    { title: 'Choose Use Case', completed: !!useCase },
    { title: 'Set Priority', completed: !!priority },
  ]

  const generateConfig = useCallback(() => {
    setGenerated(true)
  }, [])

  const selectedGpu = wizardGpuOptions.find(g => g.id === gpu)
  const selectedUseCase = wizardUseCases.find(u => u.id === useCase)
  const selectedPriority = wizardPriorities.find(p => p.id === priority)

  // Recommend model and quant based on selections
  const recommendedModel = selectedGpu && selectedGpu.vram >= 12 ? 'Qwen3-4B Q5_K_M'
    : selectedGpu && selectedGpu.vram >= 8 ? 'Qwen3-4B Q4_K_M'
    : 'TinyLlama 1.1B Q4_K_M'
  const recommendedCtx = selectedGpu && selectedGpu.vram >= 12 ? 16384
    : selectedGpu && selectedGpu.vram >= 8 ? 8192 : 4096
  const recommendedBatch = selectedGpu && selectedGpu.vram >= 12 ? 1024
    : selectedGpu && selectedGpu.vram >= 8 ? 512 : 256

  const configJson = JSON.stringify({
    profile: gpu || 'test',
    gpu: selectedGpu?.label || 'Auto-detect',
    model: recommendedModel,
    context_length: recommendedCtx,
    batch_size: recommendedBatch,
    threads: 4,
    host: '127.0.0.1',
    port: 11435,
    backend: 'CUDA',
    use_case: useCase || 'general',
    priority: priority || 'balanced',
  }, null, 2)

  const reset = useCallback(() => {
    setStep(0)
    setGpu('')
    setUseCase('')
    setPriority('')
    setGenerated(false)
  }, [])

  return (
    <div className="space-y-6">
      {/* Step indicators */}
      <div className="flex items-center gap-2">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center gap-2 flex-1">
            <div className={`flex items-center gap-2 ${i <= step ? 'text-blue-500' : 'text-muted-foreground'}`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border-2 ${
                i < step ? 'bg-blue-500 border-blue-500 text-white' :
                i === step ? 'border-blue-500 text-blue-500' :
                'border-border text-muted-foreground'
              }`}>
                {i < step ? <Check className="w-3 h-3" /> : i + 1}
              </div>
              <span className="text-xs font-medium hidden sm:inline">{s.title}</span>
            </div>
            {i < steps.length - 1 && (
              <div className={`flex-1 h-0.5 rounded-full transition-colors duration-300 ${i < step ? 'bg-blue-500' : 'bg-border/30'}`} />
            )}
          </div>
        ))}
      </div>

      {/* Step content */}
      <AnimatePresence mode="wait">
        {!generated ? (
          <motion.div key={`step-${step}`} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.2 }}>
            {step === 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold mb-3">Which GPU do you have?</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {wizardGpuOptions.map(g => (
                    <button key={g.id} onClick={() => { setGpu(g.id); setStep(1) }}
                      className={`p-3 rounded-lg border text-left transition-all duration-200 ${
                        gpu === g.id ? 'border-blue-500/30 bg-blue-500/10' : 'border-border/40 hover:border-blue-500/20 hover:bg-blue-500/5'
                      }`}>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{g.label}</span>
                        <Badge variant="outline" className="text-[9px]">{g.vram} GB VRAM</Badge>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-1">{g.cudaCores} CUDA cores</p>
                    </button>
                  ))}
                </div>
              </div>
            )}
            {step === 1 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold mb-3">What will you use it for?</h3>
                <div className="grid grid-cols-2 gap-2">
                  {wizardUseCases.map(u => (
                    <button key={u.id} onClick={() => { setUseCase(u.id); setStep(2) }}
                      className={`p-3 rounded-lg border text-left transition-all duration-200 ${
                        useCase === u.id ? 'border-blue-500/30 bg-blue-500/10' : 'border-border/40 hover:border-blue-500/20 hover:bg-blue-500/5'
                      }`}>
                      <div className="flex items-center gap-2 mb-1">
                        <u.icon className="w-4 h-4 text-blue-500" />
                        <span className="text-sm font-medium">{u.label}</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">{u.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}
            {step === 2 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold mb-3">What matters most?</h3>
                <div className="grid grid-cols-2 gap-2">
                  {wizardPriorities.map(p => (
                    <button key={p.id} onClick={() => { setPriority(p.id); generateConfig() }}
                      className={`p-3 rounded-lg border text-left transition-all duration-200 ${
                        priority === p.id ? 'border-blue-500/30 bg-blue-500/10' : 'border-border/40 hover:border-blue-500/20 hover:bg-blue-500/5'
                      }`}>
                      <div className="flex items-center gap-2 mb-1">
                        <p.icon className="w-4 h-4 text-blue-500" />
                        <span className="text-sm font-medium">{p.label}</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">{p.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div key="result" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.3 }}>
            <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px rounded-xl">
              <Card className="rounded-xl border-0">
                <CardContent className="pt-5 space-y-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-blue-500" />
                    <h3 className="font-semibold">Your Configuration</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div><span className="text-muted-foreground text-xs">GPU</span><p className="font-medium">{selectedGpu?.label}</p></div>
                    <div><span className="text-muted-foreground text-xs">Use Case</span><p className="font-medium">{selectedUseCase?.label}</p></div>
                    <div><span className="text-muted-foreground text-xs">Priority</span><p className="font-medium">{selectedPriority?.label}</p></div>
                    <div><span className="text-muted-foreground text-xs">Model</span><p className="font-mono text-xs">{recommendedModel}</p></div>
                    <div><span className="text-muted-foreground text-xs">Context</span><p className="font-mono text-xs">{recommendedCtx}</p></div>
                    <div><span className="text-muted-foreground text-xs">Batch Size</span><p className="font-mono text-xs">{recommendedBatch}</p></div>
                  </div>
                  <GlassmorphismCodeBlock code={configJson} language="json" />
                  <div className="flex gap-2">
                    <Button size="sm" className="gap-2 text-xs" onClick={() => { navigator.clipboard.writeText(configJson); toast({ title: 'Config copied!' }) }}>
                      <Copy className="w-3.5 h-3.5" /> Copy Config
                    </Button>
                    <Button size="sm" variant="outline" className="gap-2 text-xs" onClick={reset}>
                      <RotateCcw className="w-3.5 h-3.5" /> Start Over
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Back button */}
      {step > 0 && !generated && (
        <Button variant="ghost" size="sm" className="gap-2 text-xs" onClick={() => setStep(step - 1)}>
          <ChevronLeft className="w-3.5 h-3.5" /> Back
        </Button>
      )}
    </div>
  )
}

export default function Home() {
  const [dark, setDark] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeCmdCategory, setActiveCmdCategory] = useState('Diagnostics')
  const [cliSearch, setCliSearch] = useState('')
  const [activeSection, setActiveSection] = useState('overview')
  const [showBackToTop, setShowBackToTop] = useState(false)
  const [scrollProgress, setScrollProgress] = useState(0)
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const [showSplash, setShowSplash] = useState(true)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const [accentTheme, setAccentTheme] = useState('blue')

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const saved = localStorage.getItem('kimari-accent')
    if (saved && accentThemes.find(t => t.id === saved)) {
      setAccentTheme(saved)
      document.documentElement.setAttribute('data-accent', saved)
    }
  }, [])
  /* eslint-enable react-hooks/set-state-in-effect */
  const heroRef = useRef<HTMLElement>(null)
  const [visualTheme, setVisualTheme] = useState('dark')

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const saved = localStorage.getItem('kimari-visual-theme')
    if (saved) setVisualTheme(saved)
  }, [])
  /* eslint-enable react-hooks/set-state-in-effect */
  const [confettiActive, setConfettiActive] = useState(false)
  const [navScrolled, setNavScrolled] = useState(false)

  // Apply visual theme to DOM only (no setState)
  const applyThemeToDOM = useCallback((themeId: string) => {
    localStorage.setItem('kimari-visual-theme', themeId)
    const root = document.documentElement
    // Remove all theme classes
    root.classList.remove('theme-nord', 'theme-dracula', 'high-contrast-mode')
    // Apply theme
    if (themeId === 'light') {
      root.classList.remove('dark')
    } else if (themeId === 'dark') {
      root.classList.add('dark')
    } else if (themeId === 'nord') {
      root.classList.add('dark', 'theme-nord')
    } else if (themeId === 'dracula') {
      root.classList.add('dark', 'theme-dracula')
    } else if (themeId === 'high-contrast') {
      root.classList.add('dark', 'high-contrast-mode')
    }
  }, [])

  // Apply visual theme (state + DOM)
  const applyVisualTheme = useCallback((themeId: string) => {
    setVisualTheme(themeId)
    applyThemeToDOM(themeId)
  }, [applyThemeToDOM])

  // Apply visual theme on mount
  useEffect(() => {
    applyThemeToDOM(visualTheme)
  }, [applyThemeToDOM, visualTheme])

  // Apply accent theme
  useEffect(() => {
    document.documentElement.setAttribute('data-accent', accentTheme)
    localStorage.setItem('kimari-accent', accentTheme)
  }, [accentTheme])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  // Scroll spy + progress
  useEffect(() => {
    const sections = ['overview', 'status', 'cli', 'benchmarks', 'terminal', 'chat', 'gateway', 'faq', 'docs']
    const handleScroll = () => {
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
      setScrollProgress(progress)
      setShowBackToTop(scrollTop > 400)
      setNavScrolled(scrollTop > 50)
      for (const id of sections) {
        const el = document.getElementById(id)
        if (el) {
          const rect = el.getBoundingClientRect()
          if (rect.top <= 120 && rect.bottom > 120) {
            setActiveSection(id)
            break
          }
        }
      }
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      const target = e.target as HTMLElement
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') return

      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
      } else if (e.ctrlKey && e.key === '/') {
        e.preventDefault()
        setShortcutsOpen(true)
      } else if (e.key === 't' || e.key === 'T') {
        const el = document.getElementById('terminal')
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      } else if (e.key === 'c' || e.key === 'C') {
        const el = document.getElementById('chat')
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      } else if (e.key === 'b' || e.key === 'B') {
        const el = document.getElementById('benchmarks')
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      } else if (e.key === 'd' || e.key === 'D') {
        const el = document.getElementById('docs')
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Smooth scroll
  useEffect(() => {
    document.documentElement.style.scrollBehavior = 'smooth'
    return () => { document.documentElement.style.scrollBehavior = '' }
  }, [])

  const filteredCommands = cliCommands.map(cat => ({
    ...cat,
    commands: cat.commands.filter(cmd =>
      cmd.cmd.toLowerCase().includes(cliSearch.toLowerCase()) ||
      cmd.desc.toLowerCase().includes(cliSearch.toLowerCase())
    )
  })).filter(cat => cat.commands.length > 0)

  const navItems = [
    { label: 'Overview', href: '#overview' },
    { label: 'Quickstart', href: '#quickstart' },
    { label: 'Status', href: '#status' },
    { label: 'CLI', href: '#cli' },
    { label: 'Benchmarks', href: '#benchmarks' },
    { label: 'Terminal', href: '#terminal' },
    { label: 'Chat', href: '#chat' },
    { label: 'FAQ', href: '#faq' },
    { label: 'Docs', href: '#docs' },
  ]

  return (
    <div className={`min-h-screen flex flex-col ${dark ? 'dark' : ''}`}>
      {/* ─── Page Load Splash ─── */}
      {showSplash && <PageLoadSplash onComplete={() => setShowSplash(false)} />}

      {/* ─── Dynamic Island Alert ─── */}
      <DynamicIslandAlert />

      {/* ─── Confetti Effect ─── */}
      <ConfettiEffect active={confettiActive} />

      {/* ─── Scroll-Linked Accent Overlay ─── */}
      <ScrollLinkedAccentOverlay />

      {/* ─── Cursor Ring ─── */}
      <CursorRing />

      {/* ─── Quick Command Search Dialog ─── */}
      <QuickCommandSearch open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} />

      {/* ─── Section Navigation Mini-Map ─── */}
      <SectionNavigationMiniMap activeSection={activeSection} />

      {/* ─── Scroll Progress Bar ─── */}
      <div className="fixed top-0 left-0 right-0 z-[60] h-0.5 bg-transparent">
        <motion.div
          className="h-full"
          style={{
            width: `${scrollProgress}%`,
            background: 'linear-gradient(to right, var(--accent-color, #3b82f6), var(--accent-secondary, #2563eb), var(--accent-tertiary, #60a5fa))',
          }}
          transition={{ duration: 0.1, ease: 'linear' }}
        />
      </div>
      <div className="bg-background text-foreground flex-1 flex flex-col">

        {/* ─── Nav ─── */}
        <nav className={`sticky top-0 z-50 border-b border-border/50 glassmorphism-nav ${navScrolled ? 'glassmorphism-nav-scrolled' : 'bg-background/80'}`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Image src="/kimari-logo.png" alt="Kimari Logo" width={32} height={32} className="rounded-lg" priority />
              <span className="font-bold text-lg tracking-tight flex items-center gap-2">
                Kimari
                {/* Live Status Indicator */}
                <Popover>
                  <PopoverTrigger asChild>
                    <button className="relative flex items-center gap-1.5 group/status" aria-label="Server status">
                      <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                      <Wifi className="w-3 h-3 text-blue-500 opacity-0 group-hover/status:opacity-100 transition-opacity" />
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-72 p-0" align="start">
                    <div className="p-3 border-b border-border/30">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        <span className="text-sm font-semibold text-blue-500">{serverStatusInfo.status}</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">Simulated server status</p>
                    </div>
                    <div className="p-3 space-y-2 text-xs">
                      <div className="flex justify-between"><span className="text-muted-foreground">Uptime</span><span className="font-mono">{serverStatusInfo.uptime}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Model</span><span className="font-mono text-[10px]">{serverStatusInfo.model}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Endpoint</span><span className="font-mono text-[10px] text-blue-500">{serverStatusInfo.endpoint}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">GPU</span><span className="font-mono">{serverStatusInfo.gpu}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">VRAM</span><span className="font-mono">{serverStatusInfo.vramUsed}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Gate</span><span className="font-mono text-red-400">{serverStatusInfo.gate}</span></div>
                    </div>
                  </PopoverContent>
                </Popover>
              </span>
              <Badge variant="outline" className="text-[10px] px-1.5 py-0 font-mono">v0.1.82-alpha</Badge>
            </div>
            <div className="hidden lg:flex items-center gap-1">
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className={`px-2.5 py-1.5 rounded-md text-sm transition-all duration-200 ${
                    activeSection === item.href.slice(1)
                      ? 'text-blue-500 bg-blue-500/10 font-medium'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                  }`}
                >
                  {item.label}
                </a>
              ))}
              <div className="w-px h-5 bg-border/50 mx-1" />
              <SessionTimer />
              <NotificationCenter />
              <AmbientSoundToggle />
              <ThemePreviewSwitcher currentTheme={visualTheme} onThemeChange={applyVisualTheme} />
              <AccessibilityPanel />
              <Button variant="ghost" size="icon" onClick={() => setDark(!dark)} className="h-8 w-8">
                {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </Button>
              {/* Accent Color Customizer */}
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Customize accent color">
                    <Palette className="w-4 h-4" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-52 p-3" align="end">
                  <div className="space-y-2.5">
                    <p className="text-xs font-semibold">Accent Color</p>
                    <div className="flex gap-2">
                      {accentThemes.map((theme) => (
                        <button
                          key={theme.id}
                          onClick={() => setAccentTheme(theme.id)}
                          className={`w-7 h-7 rounded-full border-2 transition-all duration-200 hover:scale-110 ${
                            accentTheme === theme.id ? 'border-white scale-110 shadow-lg' : 'border-transparent'
                          }`}
                          style={{ background: `linear-gradient(135deg, ${theme.color}, ${theme.secondary})` }}
                          aria-label={`${theme.name} accent`}
                          title={theme.name}
                        />
                      ))}
                    </div>
                    <p className="text-[10px] text-muted-foreground">Changes accent color across the page</p>
                  </div>
                </PopoverContent>
              </Popover>
              {/* Keyboard Shortcuts Button */}
              <Dialog open={shortcutsOpen} onOpenChange={setShortcutsOpen}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Keyboard shortcuts">
                    <Keyboard className="w-4 h-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-2"><Keyboard className="w-5 h-5 text-blue-500" /> Keyboard Shortcuts</DialogTitle>
                    <DialogDescription>Navigate the page quickly with these shortcuts.</DialogDescription>
                  </DialogHeader>
                  <div className="space-y-2 mt-4">
                    {keyboardShortcuts.map((shortcut) => (
                      <div key={shortcut.keys} className="flex items-center justify-between py-2 px-3 rounded-lg bg-muted/30 border border-border/30">
                        <span className="text-sm">{shortcut.description}</span>
                        <kbd className="px-2 py-0.5 text-xs font-mono rounded-md bg-muted border border-border/50 text-muted-foreground">{shortcut.keys}</kbd>
                      </div>
                    ))}
                  </div>
                  <p className="text-[10px] text-muted-foreground mt-2">Shortcuts are disabled while typing in input fields.</p>
                </DialogContent>
              </Dialog>
              <a href="https://github.com/smouj/kimari-local-ai" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" size="sm" className="gap-2 text-xs hover:scale-105 transition-transform">
                  <Github className="w-3.5 h-3.5" /> GitHub
                </Button>
              </a>
            </div>
            <button className="lg:hidden p-2" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} aria-label="Toggle menu">
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                className="lg:hidden border-t border-border/50 overflow-hidden">
                <div className="px-4 py-3 flex flex-col gap-2">
                  {navItems.map((item) => (
                    <a key={item.label} href={item.href} className={`text-sm px-2 py-1.5 rounded-md transition-colors ${
                      activeSection === item.href.slice(1) ? 'text-blue-500 bg-blue-500/10 font-medium' : 'text-muted-foreground hover:text-foreground'
                    }`} onClick={() => setMobileMenuOpen(false)}>
                      {item.label}
                    </a>
                  ))}
                  <Button variant="ghost" size="sm" onClick={() => setDark(!dark)} className="gap-2 justify-start">
                    {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />} {dark ? 'Light mode' : 'Dark mode'}
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </nav>

        <main className="flex-1">

          {/* ─── Hero ─── */}
          <section id="overview" className="relative overflow-hidden" ref={heroRef}>
            <CursorTrail containerRef={heroRef} />
            <ParticleField />
            <FloatingOrbs />
            <GradientMeshBackground />
            {/* Morphing blobs */}
            <MorphingBlob className="top-[10%] left-[-5%] opacity-60" variant={1} />
            <MorphingBlob className="top-[40%] right-[-8%] opacity-40" variant={2} />
            {/* Aurora borealis effect */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
              <div className="animate-aurora-1 absolute w-[600px] h-[300px] rounded-full blur-[100px] opacity-[0.12] bg-gradient-to-r from-blue-500/40 via-blue-600/30 to-transparent" style={{ top: '5%', left: '-5%' }} />
              <div className="animate-aurora-2 absolute w-[500px] h-[250px] rounded-full blur-[80px] opacity-[0.08] bg-gradient-to-r from-sky-500/30 via-blue-500/20 to-transparent" style={{ top: '20%', right: '-10%' }} />
              <div className="animate-aurora-3 absolute w-[400px] h-[200px] rounded-full blur-[60px] opacity-[0.06] bg-gradient-to-r from-blue-600/30 via-sky-500/20 to-transparent" style={{ bottom: '10%', left: '20%' }} />
            </div>
            <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 via-transparent to-transparent" />
            {/* Enhanced noise texture overlay */}
            <svg className="absolute inset-0 w-full h-full opacity-[0.03] pointer-events-none">
              <filter id="noiseFilter">
                <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
              </filter>
              <rect width="100%" height="100%" filter="url(#noiseFilter)" />
            </svg>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-20 md:py-32 relative">
              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="text-center max-w-3xl mx-auto">
                <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5, delay: 0.1 }}
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-500/20 bg-blue-500/5 text-blue-500 text-xs font-semibold mb-8 relative overflow-hidden">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                  v0.1.82-alpha — gate BLOCKED
                  <span className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/10 to-transparent animate-shimmer-sweep" />
                </motion.div>
                <StaggeredLetterTitle />
                <p className="text-lg text-muted-foreground mb-4 max-w-2xl mx-auto cursor-default group/subtitle" title="Hover for gradient effect">
                  <span className="bg-gradient-to-r from-blue-500 via-blue-600 to-sky-500 bg-clip-text text-transparent bg-[length:200%_auto] group-hover/subtitle:animate-gradient-x transition-all duration-300">
                    <TypeWriterText text="Local-first · Open-source · GGUF runtime · Gateway dashboard · Agent-ready" speed={30} />
                  </span>
                </p>
                <p className="text-sm text-muted-foreground/70 mb-10 max-w-xl mx-auto">
                  Kimari is the <NeonGlowHeading className="text-foreground font-bold">framework</NeonGlowHeading>. Kimari-4B is{' '}
                  <strong className="text-red-400">not released</strong>. No public weights, adapters, or GGUF files are available.
                </p>
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="flex flex-col sm:flex-row items-center justify-center gap-3"
                >
                  <a href="#quickstart">
                    <MagneticButton className="rounded-lg">
                      <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }} className="relative">
                        {/* Animated gradient border button */}
                        <div className="relative group/btn rounded-lg p-[2px] animate-gradient-border">
                          <div className="rounded-[6px] bg-zinc-950 px-6 py-3 flex items-center gap-2 relative z-10">
                            <Rocket className="w-4 h-4 text-blue-400" />
                            <span className="text-white font-semibold">Get Started</span>
                          </div>
                        </div>
                        {/* Subtle glow behind CTA */}
                        <div className="absolute inset-0 rounded-lg bg-blue-500/20 blur-xl opacity-0 group-hover/btn:opacity-100 transition-opacity duration-500 -z-10" />
                      </motion.div>
                    </MagneticButton>
                  </a>
                  <a href="https://github.com/smouj/kimari-local-ai" target="_blank" rel="noopener noreferrer">
                    <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }}>
                      <Button size="lg" variant="outline" className="gap-2"><Github className="w-4 h-4" /> GitHub</Button>
                    </motion.div>
                  </a>
                  <a href="#docs">
                    <Button size="lg" variant="ghost" className="gap-2 text-muted-foreground"><BookOpen className="w-4 h-4" /> Docs</Button>
                  </a>
                </motion.div>
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.4 }}
                className="flex flex-wrap justify-center gap-2 mt-14 max-w-2xl mx-auto">
                {['CLI-first', 'OpenAI-compatible API', 'GTX 1060 validated', 'Gateway Dashboard', 'Open WebUI', 'Continue.dev', 'OpenClaw', 'llama.cpp'].map((f, i) => (
                  <motion.div key={f} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.5 + i * 0.05 }}>
                    <RippleButton className="px-3 py-1 text-xs rounded-full border border-border/60 bg-muted/30 text-muted-foreground hover:bg-muted/50 hover:border-blue-500/30 transition-colors">
                      {f}
                    </RippleButton>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </section>

          {/* ─── Honesty Strip ─── */}
          <div className="border-y border-blue-500/10 bg-blue-500/[0.02] py-4">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 text-center">
              <p className="text-sm text-muted-foreground">
                <strong className="text-blue-500">Kimari</strong> is the framework.{' '}
                <strong className="text-red-400">Kimari-4B</strong> is not released yet. No public weights, adapters, or GGUF.
              </p>
            </div>
          </div>

          <WaveDivider />

          {/* ─── Why Kimari ─── */}
          <Section className="py-20 md:py-28 relative animated-grid-bg">
            <FloatingOrbs />
            <div className="max-w-7xl mx-auto px-4 sm:px-6 relative">
              <div className="text-center mb-14">
                <SectionNumberBadge number={1} title="Why Kimari?" />
                <p className="text-muted-foreground max-w-lg mx-auto">Built for the GPUs you already own.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {[
                  { icon: Cpu, title: 'Older GPU support', desc: 'Designed for GTX 1060 and GTX 1080 — not just the latest cards.' },
                  { icon: Shield, title: 'Zero cloud dependency', desc: 'Everything runs locally. No subscriptions, API keys, or telemetry.' },
                  { icon: Zap, title: 'OpenAI-compatible', desc: 'Drop-in endpoint for existing tools, agents, and integrations.' },
                  { icon: Terminal, title: 'CLI-first', desc: 'One command to install, start, and diagnose. No npm needed.' },
                  { icon: Eye, title: 'Honest status', desc: 'No inflated benchmarks, no "coming soon" claims. Alpha means alpha.' },
                  { icon: Brain, title: 'Future Kimari models', desc: 'Private training/eval infrastructure for future Kimari models.' },
                ].map((item, i) => (
                  <motion.div key={item.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                    transition={{ delay: i * 0.08, duration: 0.5 }}>
                    <ElasticCard>
                    <DepthParallaxCard>
                    <ParticleBurstTrigger>
                    <TiltCard>
                    <SpotlightCard className="rounded-xl">
                    <GlowCard className="rounded-xl">
                      <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px rounded-xl">
                        <Card className="h-full hover:shadow-lg hover:shadow-blue-500/10 hover:scale-[1.02] hover:-translate-y-1 transition-all duration-300 rounded-xl border-0">
                          <CardHeader className="pb-3">
                            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-2 group-hover:bg-blue-500/20 transition-colors">
                              <item.icon className="w-5 h-5 text-blue-500" />
                            </div>
                            <CardTitle className="text-base">{item.title}</CardTitle>
                          </CardHeader>
                          <CardContent><p className="text-sm text-muted-foreground">{item.desc}</p></CardContent>
                        </Card>
                      </div>
                    </GlowCard>
                    </SpotlightCard>
                    </TiltCard>
                    </ParticleBurstTrigger>
                    </DepthParallaxCard>
                    </ElasticCard>
                  </motion.div>
                ))}
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Code Snippet Showcase ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Integration Code" subtitle="Connect your apps in seconds with the OpenAI-compatible API." />
              <AnimatedDashBorder>
                <CodeSnippetShowcase />
              </AnimatedDashBorder>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Statistics Bar ─── */}
          <Section className="py-12">
            <div className="max-w-5xl mx-auto px-4 sm:px-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: 'GPU Profiles', value: 6, suffix: '+', icon: Cpu, gradient: 'from-blue-500/60 to-blue-600/30' },
                  { label: 'Peak Prompt Speed', value: 228, suffix: ' tok/s', icon: Zap, gradient: 'from-blue-600/60 to-blue-700/30' },
                  { label: 'Local-first', value: 100, suffix: '%', icon: Shield, gradient: 'from-sky-500/60 to-sky-600/30' },
                  { label: 'Integration Guides', value: 4, suffix: '', icon: BookOpen, gradient: 'from-blue-400/60 to-blue-600/30' },
                ].map((stat, i) => (
                  <motion.div key={stat.label} initial={{ opacity: 0, scale: 0.9 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}
                    transition={{ delay: i * 0.1, duration: 0.4 }}>
                    <GradientBorderOnScroll className="rounded-xl">
                    <div className="backdrop-blur-xl bg-white/5 dark:bg-white/5 border border-white/10 rounded-xl p-5 text-center hover:shadow-lg hover:shadow-blue-500/5 hover:-translate-y-1 transition-all duration-300 relative overflow-hidden">
                      {/* Gradient top border */}
                      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${stat.gradient}`} />
                      {/* Gradient border glow on hover */}
                      <div className="absolute inset-0 rounded-xl bg-gradient-to-b from-blue-500/10 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                      <stat.icon className="w-5 h-5 text-blue-500 mx-auto mb-2 animate-pulse-glow" />
                      <p className="text-2xl md:text-3xl font-black bg-gradient-to-r from-blue-500 to-blue-600 bg-clip-text text-transparent">
                        <span className="animate-shine-once"><OdometerCounter target={stat.value} suffix={stat.suffix} /></span>
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">{stat.label}</p>
                    </div>
                    </GradientBorderOnScroll>
                  </motion.div>
                ))}
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Status Dashboard ─── */}
          <Section className="py-20 md:py-28 bg-muted/20" id="status" style={{ backgroundImage: 'radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(37,99,235,0.06) 0%, transparent 50%), radial-gradient(ellipse at 50% 80%, rgba(14,165,233,0.04) 0%, transparent 50%)' }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <SectionProgressHeading title="Current Status" subtitle="Transparent project health at a glance." id="status-heading" />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
                <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px rounded-xl">
                  <Card className="rounded-xl border-0 h-full">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base flex items-center gap-2"><Activity className="w-4 h-4 text-blue-500" /> Project Status</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      {statusItems.map((item) => (
                        <div key={item.area} className="flex items-center justify-between py-1.5 border-b border-border/30 last:border-0">
                          <span className="text-sm">{item.area}</span>
                          <StatusBadge status={item.status} />
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>
                <div className="bg-gradient-to-r from-violet-500/20 to-purple-500/20 p-px rounded-xl">
                  <Card className="rounded-xl border-0 h-full">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base flex items-center gap-2"><Brain className="w-4 h-4 text-violet-400" /> Model Status</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      {[
                        { name: 'TinyLlama test profile', status: 'usable' },
                        { name: 'Kimari Runtime 1.5B', status: 'private' },
                        { name: 'Kimari Core 3B', status: 'private' },
                        { name: 'Kimari-4B', status: 'blocked' },
                        { name: 'Official Kimari GGUF', status: 'blocked' },
                      ].map((item) => (
                        <div key={item.name} className="flex items-center justify-between py-1.5 border-b border-border/30 last:border-0">
                          <span className="text-sm">{item.name}</span>
                          <StatusBadge status={item.status} />
                        </div>
                      ))}
                    </CardContent>
                    <Separator className="my-4" />
                    <div>
                      <h4 className="text-sm font-semibold mb-3 flex items-center gap-2"><Shield className="w-4 h-4 text-blue-500" /> Safety Defaults</h4>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        {[
                          { label: 'Host', value: '127.0.0.1' }, { label: 'Public bind', value: 'Disabled' },
                          { label: 'Gate', value: 'BLOCKED' }, { label: 'Tokens in UI', value: 'No' },
                          { label: 'Public upload', value: 'No' }, { label: 'Public GGUF', value: 'No' },
                        ].map((item) => (
                          <div key={item.label} className="flex justify-between py-1 px-2 rounded bg-muted/50">
                            <span className="text-muted-foreground">{item.label}</span>
                            <span className="font-mono font-medium">{item.value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          </Section>

          {/* ─── Quick Start ─── */}
          <Section className="py-20 md:py-28 animated-grid-bg" id="quickstart">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <SectionProgressHeading title="Quick Start" subtitle="From zero to running in under 5 minutes." id="quickstart-heading" />
              <div className="max-w-3xl mx-auto space-y-6">
                {[
                  { step: 1, title: 'Install', code: 'curl -fsSL https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.sh | bash', desc: 'One-command install on Linux/WSL2' },
                  { step: 2, title: 'Open Console', code: 'kimari console', desc: 'Guided setup experience' },
                  { step: 3, title: 'Diagnose', code: 'kimari doctor --deep', desc: '14 diagnostic checks' },
                  { step: 4, title: 'Download Model', code: 'kimari pull test', desc: 'TinyLlama 1.1B test model' },
                  { step: 5, title: 'Start API', code: 'kimari start', desc: 'OpenAI-compatible endpoint at 127.0.0.1:11435/v1' },
                  { step: 6, title: 'Open Dashboard', code: 'kimari gateway start --open', desc: 'Local Gateway Dashboard' },
                ].map((item, i) => (
                  <motion.div key={item.step} initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
                    transition={{ delay: i * 0.1, duration: 0.5 }} className="flex gap-5 items-start">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-blue-500/20">
                      {item.step}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold mb-1">{item.title}</h3>
                      <div className="group relative bg-zinc-950 dark:bg-zinc-950 bg-zinc-100 border border-zinc-800 dark:border-zinc-800 border-zinc-300 rounded-lg p-3 font-mono text-sm">
                        <div className="flex items-center gap-2">
                          <span className="text-blue-400 select-none">$</span>
                          <span className="text-zinc-200 dark:text-zinc-200 text-zinc-800 break-all">{item.code}</span>
                        </div>
                        <div className="absolute top-2 right-2"><CopyButton text={item.code} /></div>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1.5">{item.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
              <div className="max-w-3xl mx-auto mt-10">
                <InstallCommandGenerator />
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── CLI Explorer ─── */}
          <Section className="py-20 md:py-28 bg-muted/20" id="cli" style={{ backgroundImage: 'radial-gradient(ellipse at 70% 30%, rgba(59,130,246,0.07) 0%, transparent 50%), radial-gradient(ellipse at 20% 70%, rgba(37,99,235,0.05) 0%, transparent 50%)' }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <SectionProgressHeading title="CLI Command Explorer" subtitle="Every command at your fingertips." id="cli-heading" />
              {/* Search bar */}
              <div className="max-w-md mx-auto mb-8 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  id="cli-search-input"
                  placeholder="Search commands..."
                  value={cliSearch}
                  onChange={(e) => setCliSearch(e.target.value)}
                  className="pl-9 breathing-glow"
                />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-6 max-w-4xl mx-auto">
                <div className="flex lg:flex-col gap-1.5 overflow-x-auto lg:overflow-visible pb-2 lg:pb-0">
                  {filteredCommands.map((cat) => (
                    <button
                      key={cat.category}
                      onClick={() => setActiveCmdCategory(cat.category)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                        activeCmdCategory === cat.category
                          ? 'bg-blue-500/10 text-blue-500 border border-blue-500/20 shadow-sm shadow-blue-500/5'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted/50 border border-transparent'
                      }`}
                    >
                      <cat.icon className="w-4 h-4" />{cat.category}
                    </button>
                  ))}
                </div>
                <div className="space-y-3">
                  {filteredCommands
                    .filter((cat) => cat.category === activeCmdCategory)
                    .map((cat) => cat.commands.map((cmd, i) => (
                      <motion.div key={cmd.cmd} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05, duration: 0.3 }}
                        className="group bg-zinc-950 dark:bg-zinc-950 bg-zinc-100 border border-zinc-800 dark:border-zinc-800 border-zinc-300 rounded-lg p-4 hover:shadow-lg hover:shadow-blue-500/5 hover:-translate-y-0.5 transition-all duration-300">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-mono text-sm text-blue-400 break-all">$ {cmd.cmd}</span>
                              {cmd.tag === 'essential' && (
                                <Badge className="text-[10px] px-1.5 py-0 bg-blue-500/10 text-blue-500 border-blue-500/20">essential</Badge>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground">{cmd.desc}</p>
                          </div>
                          <CopyButton text={cmd.cmd} />
                        </div>
                      </motion.div>
                    )))}
                  <a href="https://github.com/smouj/kimari-local-ai/blob/main/docs/CLI_REFERENCE.md" target="_blank" rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-sm text-blue-500 hover:text-blue-400 transition-colors mt-2">
                    View full CLI reference <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Command Builder ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <SectionProgressHeading title="Command Builder" subtitle="Visually construct Kimari CLI commands with the right flags." />
              <CommandBuilder />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── System Requirements Checker ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={2} title="System Requirements" />
                <p className="text-muted-foreground max-w-lg mx-auto">Check if your system is ready to run Kimari.</p>
              </div>
              <div className="max-w-xl mx-auto">
                <SystemRequirementsChecker />
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── System Requirements Table ─── */}
          <Section className="py-16">
            <div className="max-w-5xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-8">
                <SectionProgressHeading title="Detailed Requirements" subtitle="Minimum and recommended specs for running Kimari." id="requirements-table-heading" />
              </div>
              <SystemRequirementsTable />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── GPU Compatibility Quiz ─── */}
          <Section className="py-20 md:py-28 animated-grid-bg">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <SectionProgressHeading title="Find Your Profile" subtitle="Answer 3 questions and get a personalized GPU recommendation." />
              <GPUCompatibilityQuiz />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Benchmarks ─── */}
          <Section className="py-20 md:py-28 bg-muted/20" id="benchmarks" style={{ backgroundImage: 'radial-gradient(ellipse at 30% 20%, rgba(59,130,246,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 60%, rgba(14,165,233,0.06) 0%, transparent 50%), radial-gradient(ellipse at 10% 80%, rgba(37,99,235,0.04) 0%, transparent 50%)' }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={3} title="Local Runtime Validation" />
                <p className="text-muted-foreground max-w-lg mx-auto">Tested on a real NVIDIA GTX 1060 6GB under WSL2. Measured in <TechTermTooltip term="tok/s" /> with <TechTermTooltip term="CUDA" /> acceleration.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px rounded-xl">
                  <Card className="rounded-xl border-0 h-full">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base flex items-center gap-2"><BarChart3 className="w-4 h-4 text-blue-500" /> CUDA vs CPU</CardTitle>
                      <CardDescription>NVIDIA GTX 1060 6GB — TinyLlama 1.1B <TechTermTooltip term="Q4_K_M" /></CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-5">
                      {benchmarks.map((b) => (
                        <div key={b.metric}>
                          <div className="flex items-center justify-between text-sm mb-2">
                            <span>{b.metric}</span>
                            <span className="text-xs text-muted-foreground">{b.unit}</span>
                          </div>
                          <div className="space-y-2">
                            <div className="flex items-center gap-3">
                              <span className="text-xs text-blue-500 w-10 text-right font-mono">{b.cuda}</span>
                              <div className="flex-1 h-3 rounded-full bg-muted overflow-hidden">
                                <motion.div initial={{ width: 0 }} whileInView={{ width: `${(b.cuda / 250) * 100}%` }} viewport={{ once: true }}
                                  transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
                                  className="h-full rounded-full bg-gradient-to-r from-blue-500 to-blue-600" />
                              </div>
                              <span className="text-xs text-muted-foreground w-8">CUDA</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="text-xs text-muted-foreground w-10 text-right font-mono">{b.cpu}</span>
                              <div className="flex-1 h-3 rounded-full bg-muted overflow-hidden">
                                <motion.div initial={{ width: 0 }} whileInView={{ width: `${(b.cpu / 250) * 100}%` }} viewport={{ once: true }}
                                  transition={{ duration: 1, delay: 0.4, ease: 'easeOut' }}
                                  className="h-full rounded-full bg-zinc-500" />
                              </div>
                              <span className="text-xs text-muted-foreground w-8">CPU</span>
                            </div>
                          </div>
                        </div>
                      ))}
                      <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                        TinyLlama test model — NOT Kimari-4B. Local validation only.
                      </div>
                    </CardContent>
                  </Card>
                </div>
                <div className="bg-gradient-to-r from-sky-500/20 to-blue-600/20 p-px rounded-xl">
                  <Card className="rounded-xl border-0 h-full">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base flex items-center gap-2"><Monitor className="w-4 h-4 text-blue-500" /> GPU Profiles</CardTitle>
                      <CardDescription>Pre-tuned for specific hardware — <TechTermTooltip term="VRAM" /> and <TechTermTooltip term="Quantization" /> optimized</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {gpuProfiles.map((p) => (
                          <div key={p.name} className={`p-3 rounded-lg border hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 ${p.status === 'default' ? 'border-blue-500/30 bg-blue-500/5' : 'border-border/50'}`}>
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <code className="text-sm font-bold">{p.name}</code>
                                {p.status === 'default' && <Badge className="text-[10px] px-1.5 py-0 bg-blue-500/10 text-blue-500 border-blue-500/20">Default</Badge>}
                              </div>
                              <div className="flex items-center gap-2">
                                {p.status === 'requires-k4b' && <span className="text-[10px] text-muted-foreground">Requires Kimari-4B</span>}
                                <CopyConfigButton profile={p} />
                              </div>
                            </div>
                            <div className="grid grid-cols-3 gap-2 text-xs">
                              <div><span className="text-muted-foreground">GPU</span><p className="font-medium">{p.gpu}</p></div>
                              <div><span className="text-muted-foreground">VRAM</span><p className="font-medium">{p.vram}</p></div>
                              <div><span className="text-muted-foreground">Quant</span><p className="font-mono">{p.quant}</p></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
              <div className="max-w-4xl mx-auto mt-6">
                <Card className="backdrop-blur-xl bg-white/5 dark:bg-white/5 border border-white/10">
                  <CardContent className="pt-5">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                      {[
                        { label: 'GPU', value: 'GTX 1060 6GB' }, { label: 'OS', value: 'WSL2 Ubuntu 24.04' },
                        { label: 'Backend', value: 'llama-server CUDA' }, { label: 'Test Model', value: 'TinyLlama 1.1B Q4_K_M' },
                      ].map((d) => (
                        <div key={d.label}>
                          <p className="text-xs text-muted-foreground mb-0.5">{d.label}</p>
                          <p className="text-sm font-medium">{d.value}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── GPU Benchmark Simulator ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-5xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="GPU Performance Comparison" subtitle="Estimated benchmark performance across different NVIDIA GPUs." />
              <GPUBenchmarkSimulator />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Benchmark History Chart ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Benchmark History" subtitle="Performance progression across Kimari versions on GTX 1060." />
              <GlassCard glow className="p-6">
                <div className="h-72 md:h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={benchmarkHistoryData}>
                      <defs>
                        <linearGradient id="colorPrompt" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorGen" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#60a5fa" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                      <XAxis dataKey="version" stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                      <RechartsTooltip
                        contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }}
                        labelStyle={{ color: '#a1a1aa' }}
                      />
                      <Legend
                        wrapperStyle={{ fontSize: '12px', paddingTop: '12px' }}
                        formatter={(value: string) => <span style={{ color: value === 'promptSpeed' ? '#3b82f6' : '#60a5fa' }}>{value === 'promptSpeed' ? 'Prompt Speed (tok/s)' : 'Generation Speed (tok/s)'}</span>}
                      />
                      <Area type="monotone" dataKey="promptSpeed" stroke="#3b82f6" strokeWidth={2} fill="url(#colorPrompt)" dot={{ r: 4, fill: '#3b82f6', strokeWidth: 0 }} activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }} />
                      <Area type="monotone" dataKey="genSpeed" stroke="#60a5fa" strokeWidth={2} fill="url(#colorGen)" dot={{ r: 4, fill: '#60a5fa', strokeWidth: 0 }} activeDot={{ r: 6, fill: '#60a5fa', stroke: '#fff', strokeWidth: 2 }} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-3">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                  All measurements on GTX 1060 6GB with TinyLlama 1.1B Q4_K_M. Prompt and generation speeds measured separately.
                </div>
              </GlassCard>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── GPU VRAM Calculator ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <SectionHeading title="GPU VRAM Calculator" subtitle="Check if your GPU can run a specific model — see VRAM usage at a glance." />
              <GPUVRAMCalculator />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Model Performance Estimator ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <SectionHeading title="Model Performance Estimator" subtitle="Estimate how a model will perform on your GPU for different tasks." />
              <ModelPerformanceEstimator />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Model Comparison Tool ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Model Comparison" subtitle="Compare models side-by-side across speed, quality, VRAM, and context metrics." />
              <ModelComparisonTool />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Performance Comparison: Local vs Cloud ─── */}
          <Section className="py-20 md:py-28 animated-grid-bg">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <SectionProgressHeading title="Local vs Cloud" subtitle="How running Kimari locally compares to cloud API services." />
              <PerformanceComparisonChart />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Resource Usage Monitor ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <SectionHeading title="Resource Monitor" subtitle="Simulated real-time GPU, memory, and CPU usage gauges." />
              <ResourceUsageMonitor />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── GPU Temperature Simulator ─── */}
          <Section className="py-20 md:py-28 bg-muted/20">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="GPU Temperature Simulator" subtitle="See how GPU temperature changes under different workloads." />
              <GPUTemperatureSimulator />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Model Download Simulator ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Model Download Simulator" subtitle="Simulate downloading different model quantizations with speed and progress." />
              <ModelDownloadSimulator />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Deployment Checklist ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-2xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Deployment Checklist" subtitle="Track your progress from install to production." />
              <DeploymentChecklist onComplete={() => { setConfettiActive(true); setTimeout(() => setConfettiActive(false), 3500) }} />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Error Troubleshooter ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Error Troubleshooter" subtitle="Search for common errors and find solutions quickly." />
              <ErrorTroubleshooter />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Prompt Template Library ─── */}
          <Section className="py-20 md:py-28 bg-muted/20">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Prompt Template Library" subtitle="Ready-to-use system prompts for local LLMs — copy and customize." />
              <PromptTemplateLibrary />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Configuration Wizard ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Configuration Wizard" subtitle="Get a personalized configuration in 3 steps." />
              <ConfigurationWizard />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Comparison Table ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={4} title="How Kimari Compares" />
                <p className="text-muted-foreground max-w-lg mx-auto">See how Kimari stacks up against other local LLM tools.</p>
              </div>
              <div className="max-w-4xl mx-auto overflow-x-auto">
                <Table className="border border-border/30 rounded-lg overflow-hidden">
                  <TableHeader>
                    <TableRow className="bg-muted/30">
                      <TableHead className="font-semibold">Feature</TableHead>
                      <TableHead className="text-center bg-gradient-to-b from-blue-500/10 to-transparent font-bold text-blue-500">
                        <div className="flex items-center justify-center gap-1"><Cpu className="w-3.5 h-3.5" /> Kimari</div>
                      </TableHead>
                      <TableHead className="text-center">Ollama</TableHead>
                      <TableHead className="text-center">LM Studio</TableHead>
                      <TableHead className="text-center">text-gen-webui</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {comparisonData.map((row) => (
                      <TableRow key={row.feature} className="hover:bg-muted/20 transition-colors">
                        <TableCell className="font-medium text-sm">{row.feature}</TableCell>
                        <TableCell className="text-center bg-blue-500/5">
                          {row.kimari ? <CheckCircle2 className="w-5 h-5 text-blue-500 mx-auto" /> : <XCircle className="w-5 h-5 text-zinc-400 mx-auto" />}
                        </TableCell>
                        <TableCell className="text-center">
                          {row.ollama ? <CheckCircle2 className="w-5 h-5 text-blue-500 mx-auto" /> : <XCircle className="w-5 h-5 text-zinc-400 mx-auto" />}
                        </TableCell>
                        <TableCell className="text-center">
                          {row.lmstudio ? <CheckCircle2 className="w-5 h-5 text-blue-500 mx-auto" /> : <XCircle className="w-5 h-5 text-zinc-400 mx-auto" />}
                        </TableCell>
                        <TableCell className="text-center">
                          {row.tgwui ? <CheckCircle2 className="w-5 h-5 text-blue-500 mx-auto" /> : <XCircle className="w-5 h-5 text-zinc-400 mx-auto" />}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Architecture Diagram ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-5xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="How Kimari Works" subtitle="A look inside the local AI runtime architecture." />
              <ArchitectureDiagram />
            </div>
          </Section>
          <WaveDivider />

          {/* ─── Interactive Terminal ─── */}
          <Section className="py-20 md:py-28 bg-muted/20" id="terminal" style={{ backgroundImage: 'radial-gradient(ellipse at 50% 20%, rgba(59,130,246,0.07) 0%, transparent 50%), radial-gradient(ellipse at 80% 70%, rgba(37,99,235,0.05) 0%, transparent 50%)' }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={5} title="Try the Terminal" />
                <p className="text-muted-foreground max-w-lg mx-auto">
                  Interactive simulator — type a Kimari command and see the output. No real server needed.
                </p>
              </div>
              <div className="max-w-3xl mx-auto">
                <InteractiveTerminal />
                <div className="flex flex-wrap gap-2 mt-4 justify-center">
                  {['kimari doctor --deep', 'kimari start', 'kimari status', 'kimari pull test', 'kimari stop', 'kimari models', 'kimari optimize', 'kimari gateway start --open', 'help'].map((cmd) => (
                    <button
                      key={cmd}
                      onClick={() => {
                        const terminal = document.querySelector('[placeholder="Type a command..."]') as HTMLInputElement
                        if (terminal) {
                          terminal.value = cmd
                          terminal.dispatchEvent(new Event('input', { bubbles: true }))
                          terminal.focus()
                        }
                      }}
                      className="px-2.5 py-1 text-xs rounded-md border border-border/50 bg-muted/30 text-muted-foreground hover:text-foreground hover:border-blue-500/30 hover:bg-blue-500/5 transition-all duration-200 font-mono"
                    >
                      {cmd}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── AI Chat Simulator ─── */}
          <Section className="py-20 md:py-28" id="chat">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={6} title="Ask Kimari AI" />
                <p className="text-muted-foreground max-w-lg mx-auto">Chat with an AI assistant that knows everything about Kimari.</p>
              </div>
              <div className="max-w-lg mx-auto">
                <AIChatSimulator />
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── API Health Checker ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="API Health Check" subtitle="Simulate a health check on the local API endpoint." />
              <APIHealthChecker />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Gateway Dashboard Preview ─── */}
          <Section className="py-20 md:py-28 bg-muted/20 relative" id="gateway" style={{ backgroundImage: 'radial-gradient(ellipse at 40% 30%, rgba(59,130,246,0.07) 0%, transparent 50%), radial-gradient(ellipse at 70% 70%, rgba(37,99,235,0.05) 0%, transparent 50%), radial-gradient(ellipse at 10% 60%, rgba(14,165,233,0.04) 0%, transparent 50%)' }}>
            <MorphingBlob className="bottom-[5%] right-[-3%] opacity-30" variant={2} />
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={7} title="Gateway Dashboard" />
                <p className="text-muted-foreground max-w-lg mx-auto">Local monitoring and management from your browser.</p>
              </div>
              <div className="max-w-4xl mx-auto">
                <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px rounded-xl">
                  <Card className="overflow-hidden rounded-xl border-0">
                    <CardContent className="p-0">
                      <div className="bg-zinc-900 border-b border-zinc-800 px-4 py-2.5 flex items-center gap-3">
                        <div className="flex gap-1.5">
                          <div className="w-3 h-3 rounded-full bg-red-500/60" />
                          <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                          <div className="w-3 h-3 rounded-full bg-green-500/60" />
                        </div>
                        <div className="flex-1 bg-zinc-800 rounded px-3 py-1 text-xs text-zinc-400 font-mono text-center">http://127.0.0.1:3105</div>
                      </div>
                      <Tabs defaultValue="overview" className="bg-zinc-950">
                        <div className="border-b border-zinc-800 px-4">
                          <TabsList className="bg-transparent h-auto p-0">
                            {['overview', 'server', 'analytics', 'profiles'].map((tab) => (
                              <TabsTrigger key={tab} value={tab} className="text-xs text-zinc-400 data-[state=active]:text-blue-400 data-[state=active]:bg-blue-500/10 px-3 py-2 rounded-none border-b-2 border-transparent data-[state=active]:border-blue-500 capitalize">
                                {tab}
                              </TabsTrigger>
                            ))}
                          </TabsList>
                        </div>
                        <TabsContent value="overview" className="p-6 md:p-8 space-y-6 mt-0">
                          <div className="grid grid-cols-1 md:grid-cols-[200px_1fr] gap-6">
                            <div className="space-y-1 hidden md:block">
                              {['Overview', 'Server', 'Analytics', 'Profiles', 'Integrations', 'Logs', 'Chat', 'Gate'].map((item, i) => (
                                <div key={item} className={`px-3 py-2 rounded text-sm ${i === 0 ? 'bg-blue-500/10 text-blue-400 font-medium' : 'text-zinc-500'}`}>{item}</div>
                              ))}
                            </div>
                            <div className="space-y-4">
                              <div className="flex items-center justify-between">
                                <h3 className="text-lg font-semibold text-zinc-200">Overview</h3>
                                <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20">Runtime Active</Badge>
                              </div>
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {[
                                  { label: 'GPU', value: 'GTX 1060', color: 'blue' },
                                  { label: 'VRAM', value: '1.2 / 6 GB', color: 'blue' },
                                  { label: 'Model', value: 'TinyLlama', color: 'cyan' },
                                  { label: 'Gate', value: 'BLOCKED', color: 'red' },
                                ].map((s) => (
                                  <div key={s.label} className="bg-zinc-900 rounded-lg p-3 border border-zinc-800">
                                    <p className="text-xs text-zinc-500 mb-1">{s.label}</p>
                                    <p className={`text-sm font-bold ${s.color === 'blue' ? 'text-blue-400' : s.color === 'cyan' ? 'text-cyan-400' : 'text-red-400'}`}>{s.value}</p>
                                  </div>
                                ))}
                              </div>
                              <div className="bg-zinc-900 rounded-lg p-4 border border-zinc-800">
                                <p className="text-xs text-zinc-500 mb-2">VRAM Usage</p>
                                <Progress value={20} className="h-2" />
                                <p className="text-xs text-zinc-500 mt-1">1221 MiB / 6144 MiB (20%)</p>
                              </div>
                            </div>
                          </div>
                        </TabsContent>
                        <TabsContent value="server" className="p-6 space-y-4 mt-0">
                          <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold text-zinc-200">Server Metrics</h3>
                            <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" /> Online
                            </Badge>
                          </div>
                          <div className="grid grid-cols-3 gap-3">
                            {[
                              { label: 'Uptime', value: '4h 23m' },
                              { label: 'Requests', value: '1,247' },
                              { label: 'Avg Latency', value: '42ms' },
                            ].map((s) => (
                              <div key={s.label} className="bg-zinc-900 rounded-lg p-3 border border-zinc-800">
                                <p className="text-xs text-zinc-500 mb-1">{s.label}</p>
                                <p className="text-sm font-bold text-blue-400 font-mono">{s.value}</p>
                              </div>
                            ))}
                          </div>
                          <div className="bg-zinc-900 rounded-lg p-4 border border-zinc-800 space-y-2">
                            <p className="text-xs text-zinc-500">Server Configuration</p>
                            <div className="grid grid-cols-2 gap-2 text-xs">
                              <div className="flex justify-between"><span className="text-zinc-500">Host</span><span className="text-zinc-300 font-mono">127.0.0.1</span></div>
                              <div className="flex justify-between"><span className="text-zinc-500">Port</span><span className="text-zinc-300 font-mono">11435</span></div>
                              <div className="flex justify-between"><span className="text-zinc-500">Profile</span><span className="text-zinc-300 font-mono">test</span></div>
                              <div className="flex justify-between"><span className="text-zinc-500">Backend</span><span className="text-zinc-300 font-mono">CUDA</span></div>
                            </div>
                          </div>
                          {/* Server Logs */}
                          <div className="bg-zinc-900 rounded-lg p-4 border border-zinc-800">
                            <p className="text-xs text-zinc-500 mb-2">Server Log</p>
                            <div className="font-mono text-[10px] space-y-1.5 max-h-40 overflow-y-auto" style={{ scrollbarWidth: 'thin' }}>
                              {gatewayServerLogs.map((log, i) => (
                                <div key={i} className="flex items-start gap-2">
                                  <span className="text-zinc-600 flex-shrink-0">{log.time}</span>
                                  <span className={`px-1 rounded text-[9px] font-bold uppercase flex-shrink-0 ${
                                    log.level === 'info' ? 'bg-blue-500/10 text-blue-400' : 'bg-amber-500/10 text-amber-400'
                                  }`}>{log.level}</span>
                                  <span className="text-zinc-300">{log.message}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </TabsContent>
                        <TabsContent value="analytics" className="p-6 space-y-4 mt-0">
                          <h3 className="text-lg font-semibold text-zinc-200">Daily Requests</h3>
                          <div className="bg-zinc-900 rounded-lg p-4 border border-zinc-800 h-64">
                            <ResponsiveContainer width="100%" height="100%">
                              <AreaChart data={gatewayChartData}>
                                <defs>
                                  <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                  </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                <XAxis dataKey="day" stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} />
                                <RechartsTooltip
                                  contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }}
                                  labelStyle={{ color: '#a1a1aa' }}
                                  itemStyle={{ color: '#3b82f6' }}
                                />
                                <Area type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} fill="url(#colorRequests)" dot={{ r: 4, fill: '#3b82f6', strokeWidth: 0 }} activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }} />
                              </AreaChart>
                            </ResponsiveContainer>
                          </div>
                        </TabsContent>
                        <TabsContent value="profiles" className="p-6 space-y-4 mt-0">
                          <h3 className="text-lg font-semibold text-zinc-200">Profile Selector</h3>
                          <div className="space-y-2">
                            {gatewayProfiles.map((profile) => (
                              <div key={profile.name} className="bg-zinc-900 rounded-lg p-3 border border-zinc-800 flex items-center justify-between hover:border-blue-500/20 transition-colors cursor-pointer">
                                <div className="flex items-center gap-3">
                                  <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${profile.color}15` }}>
                                    <Cpu className="w-4 h-4" style={{ color: profile.color }} />
                                  </div>
                                  <div>
                                    <p className="text-sm font-medium text-zinc-200">{profile.name}</p>
                                    <p className="text-[10px] text-zinc-500">{profile.gpu} · {profile.model}</p>
                                  </div>
                                </div>
                                <Badge className={`text-[10px] ${
                                  profile.status === 'Active' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                  profile.status === 'Standby' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' :
                                  'bg-red-500/10 text-red-400 border-red-500/20'
                                }`}>{profile.status}</Badge>
                              </div>
                            ))}
                          </div>
                        </TabsContent>
                      </Tabs>
                    </CardContent>
                  </Card>
                </div>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-6">
                  <a href="https://github.com/smouj/kimari-local-ai/blob/main/docs/GATEWAY_DASHBOARD.md" target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" size="sm" className="gap-2 text-xs hover:scale-105 transition-transform"><FileCode className="w-3.5 h-3.5" /> Dashboard Docs</Button>
                  </a>
                  <code className="text-xs text-muted-foreground font-mono">$ kimari gateway start --open</code>
                </div>
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── FAQ Accordion ─── */}
          <Section className="py-20 md:py-28" id="faq">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <SectionProgressHeading title="Frequently Asked Questions" subtitle="Common questions about Kimari, answered honestly." id="faq-heading" />
              <div className="max-w-2xl mx-auto">
                <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-px rounded-xl">
                  <div className="bg-card rounded-xl">
                    <Accordion type="single" collapsible className="w-full">
                      {faqItems.map((item, i) => (
                        <AccordionItem key={i} value={`faq-${i}`} className={`faq-accordion-item ${i === faqItems.length - 1 ? 'border-b-0' : ''} transition-all duration-300 px-4`}>
                          <AccordionTrigger className="text-sm font-medium hover:text-blue-500 transition-colors hover:no-underline [&>svg]:transition-transform [&>svg]:duration-300">
                            {item.q}
                          </AccordionTrigger>
                          <AccordionContent className="text-sm text-muted-foreground pb-4">
                            {item.a}
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </div>
                </div>
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── API Endpoint Explorer ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="API Endpoint Explorer" subtitle="OpenAI-compatible endpoints ready for your integrations." />
              <APIEndpointExplorer />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Model Card Gallery ─── */}
          <Section className="py-20 md:py-28 bg-muted/20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Compatible Models" subtitle="Click any card to see detailed specifications." />
              <ModelCardGallery />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Changelog / What's New ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-3xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="What's New" subtitle="Latest changes and improvements — click entries to expand." />
              <InteractiveChangelogTimeline />
              <div className="mt-4">
                <a
                  href="https://github.com/smouj/kimari-local-ai/releases"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-blue-500 hover:text-blue-400 transition-colors"
                >
                  View full changelog on GitHub <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Version Timeline ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
              <TextRevealHeading title="Project Timeline" subtitle="Major milestones on the path to local AI." />
              <VersionTimeline />
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Safety ─── */}
          <Section className="py-20 md:py-28 bg-muted/20" id="safety" style={{ backgroundImage: 'radial-gradient(ellipse at 60% 30%, rgba(59,130,246,0.06) 0%, transparent 50%), radial-gradient(ellipse at 20% 70%, rgba(37,99,235,0.04) 0%, transparent 50%)' }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={8} title="Safety & Privacy" />
                <p className="text-muted-foreground max-w-lg mx-auto">Local-first and conservative by default.</p>
              </div>
              <div className="max-w-2xl mx-auto">
                <div className="bg-gradient-to-r from-red-500/20 to-amber-500/20 p-px rounded-xl">
                  <Card className="rounded-xl border-0">
                    <CardContent className="pt-6">
                      <ul className="space-y-3">
                        {safetyItems.map((item, i) => (
                          <motion.li key={item} initial={{ opacity: 0, x: -10 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
                            transition={{ delay: i * 0.05 }} className="flex items-center gap-3 text-sm">
                            <div className="w-6 h-6 rounded-full bg-red-500/10 flex items-center justify-center flex-shrink-0">
                              <Shield className="w-3.5 h-3.5 text-red-400" />
                            </div>
                            {item}
                          </motion.li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Roadmap ─── */}
          <Section className="py-20 md:py-28">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={9} title="Roadmap" />
                <p className="text-muted-foreground max-w-lg mx-auto">Honest, incremental progress.</p>
              </div>
              <div className="relative max-w-3xl mx-auto">
                {/* Timeline line */}
                <div className="absolute left-4 md:left-1/2 md:-translate-x-px top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500/50 via-blue-600/30 to-transparent" />
                {roadmapItems.map((item, i) => {
                  const isLeft = i % 2 === 0
                  const stageConfig: Record<string, { dotColor: string; badgeClass: string }> = {
                    'Current': { dotColor: 'bg-blue-500', badgeClass: 'bg-blue-500/10 text-blue-500 border-blue-500/20' },
                    'Next': { dotColor: 'bg-cyan-500', badgeClass: 'bg-cyan-500/10 text-cyan-500 border-cyan-500/20' },
                    'Later': { dotColor: 'bg-zinc-500', badgeClass: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20' },
                  }
                  const config = stageConfig[item.stage] || stageConfig['Later']
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: isLeft ? -20 : 20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.1, duration: 0.4 }}
                      className={`relative flex items-start gap-4 mb-6 md:gap-0 ${
                        isLeft ? 'md:flex-row' : 'md:flex-row-reverse'
                      }`}
                    >
                      {/* Timeline dot */}
                      <div className={`absolute left-4 md:left-1/2 -translate-x-1/2 w-3.5 h-3.5 rounded-full ${config.dotColor} z-10 mt-5 ${
                        item.active ? 'animate-pulse shadow-lg shadow-blue-500/50' : ''
                      } border-2 border-background`} />
                      {/* Content */}
                      <div className={`ml-10 md:ml-0 md:w-[calc(50%-2rem)] ${isLeft ? 'md:pr-8 md:text-right' : 'md:pl-8 md:text-left'}`}>
                        <div className="p-3 rounded-lg border border-border/30 bg-card hover:shadow-md hover:-translate-y-0.5 transition-all duration-300">
                          <div className={`flex items-center gap-2 mb-1.5 ${isLeft ? 'md:justify-end' : 'md:justify-start'}`}>
                            <Badge variant="outline" className={`text-[10px] ${config.badgeClass}`}>{item.stage}</Badge>
                          </div>
                          <p className="text-sm">{item.goal}</p>
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Documentation ─── */}
          <Section className="py-20 md:py-28 bg-muted/20" id="docs" style={{ backgroundImage: 'radial-gradient(ellipse at 20% 40%, rgba(59,130,246,0.07) 0%, transparent 50%), radial-gradient(ellipse at 80% 60%, rgba(37,99,235,0.05) 0%, transparent 50%)' }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <SectionNumberBadge number={10} title="Documentation" />
                <p className="text-muted-foreground max-w-lg mx-auto">Everything you need, organized by category.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                {docCategories.map((cat, catIndex) => (
                  <motion.div
                    key={cat.title}
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: '-40px' }}
                    transition={{ delay: catIndex * 0.15, duration: 0.5 }}
                  >
                    <motion.div whileHover={{ y: -4 }} transition={{ duration: 0.2 }}>
                      <Card className="h-full hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/5 transition-all duration-300">
                        <CardHeader className="pb-3">
                          <motion.div
                            className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center mb-2"
                            whileHover={{ rotate: [0, -10, 10, 0], scale: 1.15 }}
                            transition={{ duration: 0.4 }}
                          >
                            <cat.icon className="w-4 h-4 text-blue-500" />
                          </motion.div>
                          <CardTitle className="text-sm">{cat.title}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <ul className="space-y-1.5">
                            {cat.links.map((link) => (
                              <li key={link.name}>
                                <a href={link.href} target="_blank" rel="noopener noreferrer"
                                  className="text-xs text-muted-foreground hover:text-blue-500 transition-colors flex items-center gap-1">
                                  <FileCode className="w-3 h-3 flex-shrink-0" />{link.name}<ExternalLink className="w-2.5 h-2.5 ml-auto flex-shrink-0" />
                                </a>
                              </li>
                            ))}
                          </ul>
                        </CardContent>
                      </Card>
                    </motion.div>
                  </motion.div>
                ))}
              </div>
            </div>
          </Section>

          <WaveDivider />

          {/* ─── Hugging Face ─── */}
          <Section className="py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-10">
                <h2 className="text-3xl font-bold tracking-tight mb-4">Hugging Face</h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 max-w-3xl mx-auto">
                {[
                  { title: 'Kimari Organization', href: 'https://huggingface.co/kimari-ai', desc: 'Official org page' },
                  { title: 'Kimari Fit Lab', href: 'https://huggingface.co/spaces/kimari-ai/kimari-fit-lab', desc: 'GPU compatibility checker' },
                  { title: 'GGUF Collection', href: 'https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66', desc: 'Reference community models' },
                ].map((item) => (
                  <a key={item.title} href={item.href} target="_blank" rel="noopener noreferrer">
                    <Card className="h-full hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/5 hover:-translate-y-1 transition-all duration-300 cursor-pointer">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center gap-2"><Globe className="w-4 h-4 text-blue-500" />{item.title}</CardTitle>
                      </CardHeader>
                      <CardContent><p className="text-xs text-muted-foreground">{item.desc}</p></CardContent>
                    </Card>
                  </a>
                ))}
              </div>
              <p className="text-center text-xs text-muted-foreground mt-4">The Space is a compatibility/demo tool. It does not run Kimari-4B.</p>
            </div>
          </Section>

        </main>

        {/* ─── Footer ─── */}
        <footer className="border-t border-border/50 bg-muted/10 mt-auto relative">
          {/* Gradient top border */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/40 to-transparent" />
          <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
              {/* Product */}
              <div>
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5"><Rocket className="w-3.5 h-3.5 text-blue-500" /> Product</h4>
                <ul className="space-y-2 text-xs text-muted-foreground">
                  <li><a href="#overview" className="footer-link hover:text-blue-500 transition-colors">Overview</a></li>
                  <li><a href="#quickstart" className="footer-link hover:text-blue-500 transition-colors">Quick Start</a></li>
                  <li><a href="#benchmarks" className="footer-link hover:text-blue-500 transition-colors">Benchmarks</a></li>
                  <li><a href="#gateway" className="footer-link hover:text-blue-500 transition-colors">Gateway Dashboard</a></li>
                </ul>
              </div>
              {/* Resources */}
              <div>
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5"><BookOpen className="w-3.5 h-3.5 text-blue-500" /> Resources</h4>
                <ul className="space-y-2 text-xs text-muted-foreground">
                  <li><a href="https://github.com/smouj/kimari-local-ai/blob/main/docs/CLI_REFERENCE.md" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">CLI Reference</a></li>
                  <li><a href="https://github.com/smouj/kimari-local-ai/blob/main/docs/INSTALL_ONE_COMMAND.md" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">Install Guide</a></li>
                  <li><a href="https://github.com/smouj/kimari-local-ai/blob/main/docs/GATEWAY_DASHBOARD.md" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">Dashboard Docs</a></li>
                  <li><a href="#faq" className="footer-link hover:text-blue-500 transition-colors">FAQ</a></li>
                </ul>
              </div>
              {/* Community */}
              <div>
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5"><Heart className="w-3.5 h-3.5 text-blue-500" /> Community</h4>
                <ul className="space-y-2 text-xs text-muted-foreground">
                  <li><a href="https://github.com/smouj/kimari-local-ai" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">GitHub</a></li>
                  <li><a href="https://huggingface.co/kimari-ai" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">Hugging Face</a></li>
                  <li><a href="https://huggingface.co/spaces/kimari-ai/kimari-fit-lab" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">Fit Lab Space</a></li>
                </ul>
              </div>
              {/* Legal */}
              <div>
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5"><Shield className="w-3.5 h-3.5 text-blue-500" /> Legal</h4>
                <ul className="space-y-2 text-xs text-muted-foreground">
                  <li><a href="https://github.com/smouj/kimari-local-ai/blob/main/docs/KIMARI4B_RELEASE_GATE.md" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">Release Gate</a></li>
                  <li><a href="https://github.com/smouj/kimari-local-ai/blob/main/docs/KIMARI_OPEN_LICENSE_POLICY.md" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">License Policy</a></li>
                  <li><a href="https://github.com/smouj/kimari-local-ai/blob/main/SECURITY.md" target="_blank" rel="noopener noreferrer" className="footer-link hover:text-blue-500 transition-colors">Security</a></li>
                  <li>MIT License</li>
                </ul>
              </div>
            </div>
            <Separator className="mb-6" />
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <Image src="/kimari-logo.png" alt="Kimari Logo" width={24} height={24} className="rounded-md" />
                <span className="text-sm font-semibold">Kimari Local AI</span>
                <Badge variant="outline" className="text-[10px] font-mono">v0.1.82-alpha</Badge>
              </div>
              <div className="flex items-center gap-3">
                <MagneticSocialLink href="https://github.com/smouj/kimari-local-ai" className="p-2 rounded-lg hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors">
                  <Github className="w-4 h-4" />
                </MagneticSocialLink>
                <MagneticSocialLink href="https://huggingface.co/kimari-ai" className="p-2 rounded-lg hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors">
                  <Globe className="w-4 h-4" />
                </MagneticSocialLink>
                <MagneticSocialLink href="https://x.com/smouj013" className="p-2 rounded-lg hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors">
                  <Twitter className="w-4 h-4" />
                </MagneticSocialLink>
              </div>
            </div>
            <Separator className="my-4" />
            <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground">
              <p className="flex items-center gap-1">Made with <Heart className="w-3 h-3 text-red-500 fill-red-500" /> for local AI · by <a href="https://x.com/smouj013" target="_blank" rel="noopener noreferrer" className="text-foreground font-medium hover:text-blue-500 transition-colors ml-1">Smouj</a></p>
              <p>Kimari-4B is not released. No public weights or GGUF.</p>
            </div>
          </div>
        </footer>
      </div>

      {/* ─── Back to Top with Progress Ring ─── */}
      <AnimatePresence>
        {showBackToTop && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="fixed bottom-6 right-6 z-50 w-11 h-11 rounded-full text-white shadow-lg shadow-blue-500/25 flex items-center justify-center hover:scale-110 transition-transform group/btt"
            aria-label="Back to top"
          >
            {/* Progress ring background */}
            <svg className="absolute inset-0 w-11 h-11 -rotate-90" viewBox="0 0 44 44">
              <circle cx="22" cy="22" r="19" fill="none" stroke="currentColor" strokeWidth="2" className="text-zinc-800" />
              <circle
                cx="22" cy="22" r="19" fill="none"
                stroke="url(#progressGradient)" strokeWidth="2"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 19}`}
                strokeDashoffset={`${2 * Math.PI * 19 * (1 - scrollProgress / 100)}`}
                className="transition-all duration-150"
              />
              <defs>
                <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#2563eb" />
                </linearGradient>
              </defs>
            </svg>
            {/* Inner circle */}
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
              <ArrowUp className="w-4 h-4" />
            </div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* ─── Floating Action Menu ─── */}
      <FloatingActionMenu
        onBackToTop={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        onToggleSound={() => {
          const btn = document.querySelector('[data-ambient-sound]') as HTMLButtonElement
          if (btn) btn.click()
        }}
        onOpenShortcuts={() => setShortcutsOpen(true)}
        onToggleTheme={() => setDark(!dark)}
        isDark={dark}
      />

      {/* ─── Cookie Consent Banner ─── */}
      <CookieConsentBanner />
    </div>
  )
}
