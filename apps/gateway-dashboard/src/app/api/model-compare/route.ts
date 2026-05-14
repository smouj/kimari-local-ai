import { NextResponse } from 'next/server'

// Model comparison data — realistic mock data based on model characteristics
interface QualityScores {
  instructionFollowing: number
  codingAbility: number
  reasoning: number
  creativity: number
}

interface PerformanceEstimate {
  promptTokPerSec: number
  genTokPerSec: number
  vramRequiredGb: number
  contextLength: number
}

interface ModelComparisonItem {
  name: string
  displayName: string
  size: string
  quantization: string
  category: string
  performance: PerformanceEstimate
  quality: QualityScores
  compatibleProfiles: string[]
  pros: string[]
  cons: string[]
}

const modelData: Record<string, ModelComparisonItem> = {
  'kimari-4b': {
    name: 'kimari-4b',
    displayName: 'Kimari 4B',
    size: '2.4 GB',
    quantization: 'Q4_K_M',
    category: 'General',
    performance: {
      promptTokPerSec: 85,
      genTokPerSec: 42,
      vramRequiredGb: 3.2,
      contextLength: 8192,
    },
    quality: {
      instructionFollowing: 7,
      codingAbility: 5,
      reasoning: 6,
      creativity: 7,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4060 8GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Fast inference speed', 'Low VRAM requirement', 'Great for chat', 'Kimari optimized'],
    cons: ['Limited reasoning depth', 'Not ideal for complex code', 'Smaller knowledge base'],
  },
  'llama-3.2-3b': {
    name: 'llama-3.2-3b',
    displayName: 'Llama 3.2 3B',
    size: '1.9 GB',
    quantization: 'Q4_K_M',
    category: 'General',
    performance: {
      promptTokPerSec: 110,
      genTokPerSec: 55,
      vramRequiredGb: 2.6,
      contextLength: 8192,
    },
    quality: {
      instructionFollowing: 6,
      codingAbility: 4,
      reasoning: 5,
      creativity: 6,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4060 8GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Very fast inference', 'Minimal VRAM', 'Good for simple tasks'],
    cons: ['Limited capability', 'Weaker reasoning', 'Not suitable for complex tasks'],
  },
  'mistral-7b': {
    name: 'mistral-7b',
    displayName: 'Mistral 7B',
    size: '4.1 GB',
    quantization: 'Q4_K_M',
    category: 'General',
    performance: {
      promptTokPerSec: 52,
      genTokPerSec: 28,
      vramRequiredGb: 5.4,
      contextLength: 32768,
    },
    quality: {
      instructionFollowing: 8,
      codingAbility: 7,
      reasoning: 7,
      creativity: 8,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Excellent context window', 'Strong coding ability', 'Good instruction following', 'Versatile'],
    cons: ['Requires more VRAM', 'Slower than smaller models', '8GB GPUs may struggle'],
  },
  'phi-3-medium': {
    name: 'phi-3-medium',
    displayName: 'Phi-3 Medium 14B',
    size: '7.8 GB',
    quantization: 'Q4_K_M',
    category: 'Reasoning',
    performance: {
      promptTokPerSec: 28,
      genTokPerSec: 14,
      vramRequiredGb: 9.6,
      contextLength: 16384,
    },
    quality: {
      instructionFollowing: 8,
      codingAbility: 8,
      reasoning: 9,
      creativity: 7,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Excellent reasoning', 'Strong coding performance', 'Good instruction following'],
    cons: ['High VRAM requirement', 'Slower generation', 'Not ideal for 8GB GPUs'],
  },
  'deepseek-coder-6.7b': {
    name: 'deepseek-coder-6.7b',
    displayName: 'DeepSeek Coder 6.7B',
    size: '3.8 GB',
    quantization: 'Q4_K_M',
    category: 'Coding',
    performance: {
      promptTokPerSec: 55,
      genTokPerSec: 30,
      vramRequiredGb: 5.0,
      contextLength: 16384,
    },
    quality: {
      instructionFollowing: 7,
      codingAbility: 9,
      reasoning: 7,
      creativity: 6,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Best-in-class coding', 'Large context window', 'Good at code explanation'],
    cons: ['Weaker creative writing', 'Not ideal for general chat', 'Moderate VRAM needs'],
  },
  'qwen2.5-7b': {
    name: 'qwen2.5-7b',
    displayName: 'Qwen 2.5 7B',
    size: '4.3 GB',
    quantization: 'Q4_K_M',
    category: 'General',
    performance: {
      promptTokPerSec: 50,
      genTokPerSec: 26,
      vramRequiredGb: 5.6,
      contextLength: 32768,
    },
    quality: {
      instructionFollowing: 8,
      codingAbility: 7,
      reasoning: 8,
      creativity: 8,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Strong all-rounder', 'Excellent context length', 'Good multilingual support'],
    cons: ['Moderate speed', '8GB GPUs may struggle', 'Requires tuning for best results'],
  },
  'yi-1.5-9b': {
    name: 'yi-1.5-9b',
    displayName: 'Yi 1.5 9B',
    size: '5.2 GB',
    quantization: 'Q4_K_M',
    category: 'General',
    performance: {
      promptTokPerSec: 40,
      genTokPerSec: 20,
      vramRequiredGb: 6.8,
      contextLength: 4096,
    },
    quality: {
      instructionFollowing: 7,
      codingAbility: 7,
      reasoning: 8,
      creativity: 8,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Strong reasoning', 'Good creative writing', 'Solid general performance'],
    cons: ['Short context window', 'Slower inference', 'High VRAM usage'],
  },
  'gemma-2-9b': {
    name: 'gemma-2-9b',
    displayName: 'Gemma 2 9B',
    size: '5.4 GB',
    quantization: 'Q4_K_M',
    category: 'General',
    performance: {
      promptTokPerSec: 38,
      genTokPerSec: 19,
      vramRequiredGb: 7.0,
      contextLength: 8192,
    },
    quality: {
      instructionFollowing: 8,
      codingAbility: 7,
      reasoning: 8,
      creativity: 7,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Google quality model', 'Good safety alignment', 'Strong instruction following'],
    cons: ['Conservative responses', 'Moderate speed', 'Higher VRAM needed'],
  },
}

// Default fallback for unknown models
function generateDefaultModel(name: string): ModelComparisonItem {
  return {
    name,
    displayName: name.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    size: '4.0 GB',
    quantization: 'Q4_K_M',
    category: 'General',
    performance: {
      promptTokPerSec: 50,
      genTokPerSec: 25,
      vramRequiredGb: 5.0,
      contextLength: 8192,
    },
    quality: {
      instructionFollowing: 6,
      codingAbility: 6,
      reasoning: 6,
      creativity: 6,
    },
    compatibleProfiles: ['RTX 3060 12GB', 'RTX 4070 12GB', 'RTX 3090 24GB', 'RTX 4090 24GB'],
    pros: ['Compatible with Kimari Gateway'],
    cons: ['Limited benchmark data available'],
  }
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const modelsParam = searchParams.get('models')

  if (!modelsParam) {
    return NextResponse.json(
      { error: 'Missing models parameter. Usage: ?models=model1,model2,model3' },
      { status: 400 }
    )
  }

  const modelNames = modelsParam.split(',').map((m) => m.trim()).filter(Boolean)

  if (modelNames.length < 2) {
    return NextResponse.json(
      { error: 'At least 2 models required for comparison' },
      { status: 400 }
    )
  }

  if (modelNames.length > 4) {
    return NextResponse.json(
      { error: 'Maximum 4 models can be compared at once' },
      { status: 400 }
    )
  }

  const models = modelNames.map((name) => modelData[name] || generateDefaultModel(name))
  const availableModels = Object.keys(modelData)

  return NextResponse.json({
    models,
    availableModels,
    comparedAt: new Date().toISOString(),
  })
}
