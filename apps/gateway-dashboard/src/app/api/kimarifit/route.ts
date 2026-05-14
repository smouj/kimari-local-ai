import { NextResponse } from 'next/server';

interface KimariFitRequest {
  modelSize: string;
  vram: number;
  contextSize: number;
  quantization: string;
}

// Approximate model sizes in GB for different configurations
const MODEL_SIZES: Record<string, number> = {
  'kimari-4b-q4': 2.4,
  'kimari-4b-q5': 2.9,
  'kimari-4b-q8': 4.2,
  'llama-3.1-8b-q4': 4.9,
  'llama-3.1-8b-q5': 5.7,
  'llama-3.1-8b-q8': 8.1,
  'mistral-7b-q4': 4.1,
  'mistral-7b-q5': 4.9,
  'mistral-7b-q8': 7.2,
  'phi-3-mini-q4': 2.2,
  'phi-3-mini-q5': 2.7,
  'phi-3-mini-q8': 3.9,
  'qwen2-7b-q4': 4.3,
  'qwen2-7b-q5': 5.1,
  'qwen2-7b-q8': 7.4,
  'deepseek-coder-6.7b-q4': 3.8,
  'deepseek-coder-6.7b-q5': 4.5,
  'deepseek-coder-6.7b-q8': 6.8,
};

// Context memory: approximate KV cache size based on model parameters and context
// Rule of thumb: ~18 MB per 1K tokens per billion parameters (fp16 KV cache)
// We estimate parameter count from quantized model size
function getContextVram(contextSize: number, modelSizeGb: number, quantization: string): number {
  // Approximate parameter count from quantized model size
  // Q4: ~0.55 GB per billion params, Q5: ~0.65, Q6: ~0.75, Q8: ~0.95, F16: ~1.9
  const bytesPerParam: Record<string, number> = {
    Q4_K_S: 0.5, Q4_K_M: 0.55, Q5_K_S: 0.6, Q5_K_M: 0.65, Q5_0: 0.63,
    Q6_K: 0.75, Q8_0: 0.95, F16: 1.9,
  }
  const bpp = bytesPerParam[quantization] ?? 0.55
  const paramsInBillions = modelSizeGb / bpp
  const mbPer1kTokens = paramsInBillions * 18
  return Math.round((contextSize / 1024) * mbPer1kTokens * 1.1) // 10% overhead
}

// Quantization efficiency factor
const QUANT_EFFICIENCY: Record<string, number> = {
  Q4_K_M: 0.85,
  Q4_K_S: 0.82,
  Q5_K_M: 0.88,
  Q5_K_S: 0.85,
  Q5_0: 0.87,
  Q6_K: 0.91,
  Q8_0: 0.95,
  F16: 1.0,
};

function getGrade(score: number): string {
  if (score > 90) return 'A+';
  if (score > 80) return 'A';
  if (score > 70) return 'B';
  if (score > 60) return 'C';
  if (score > 50) return 'D';
  return 'F';
}

export async function POST(request: Request) {
  try {
    const body: KimariFitRequest = await request.json();
    const { modelSize, vram, contextSize, quantization } = body;

    if (!modelSize || !vram || !contextSize || !quantization) {
      return NextResponse.json(
        { error: 'Missing required fields: modelSize, vram, contextSize, quantization' },
        { status: 400 }
      );
    }

    const modelVramGb = MODEL_SIZES[modelSize] ?? (parseFloat(modelSize) || 5.0);
    const modelVramMb = modelVramGb * 1024;
    const contextVramMb = getContextVram(contextSize, modelVramGb, quantization);
    const overheadMb = Math.round(modelVramMb * 0.05); // 5% framework overhead
    const totalVramMb = modelVramMb + contextVramMb + overheadMb;
    const vramTotalMb = vram * 1024;
    const headroomMb = vramTotalMb - totalVramMb;
    const efficiency = QUANT_EFFICIENCY[quantization] ?? 0.85;

    // Calculate KimariFit score
    let score = 0;

    // 1. VRAM fit (0-40 points): does the model + context fit in VRAM?
    const vramRatio = totalVramMb / vramTotalMb;
    if (vramRatio <= 0.7) {
      score += 40;
    } else if (vramRatio <= 0.85) {
      score += 30;
    } else if (vramRatio <= 0.95) {
      score += 20;
    } else if (vramRatio <= 1.0) {
      score += 10;
    } else {
      score += 0;
    }

    // 2. Headroom (0-25 points): extra space for batching, system, etc.
    const headroomPct = (headroomMb / vramTotalMb) * 100;
    if (headroomPct >= 30) {
      score += 25;
    } else if (headroomPct >= 20) {
      score += 20;
    } else if (headroomPct >= 10) {
      score += 15;
    } else if (headroomPct >= 5) {
      score += 10;
    } else if (headroomPct >= 0) {
      score += 5;
    }

    // 3. Context size efficiency (0-15 points)
    if (contextSize >= 8192 && headroomPct >= 15) {
      score += 15;
    } else if (contextSize >= 4096 && headroomPct >= 10) {
      score += 12;
    } else if (contextSize >= 2048 && headroomPct >= 5) {
      score += 8;
    } else if (contextSize >= 1024) {
      score += 5;
    }

    // 4. Quantization efficiency (0-20 points)
    score += Math.round(efficiency * 20);

    // Cap at 100
    score = Math.min(100, Math.max(0, score));

    const grade = getGrade(score);

    // Generate recommendations
    const recommendations: string[] = [];

    if (vramRatio > 1.0) {
      recommendations.push('Model exceeds available VRAM. Consider a smaller quantization (Q4_K_M) or a smaller model variant.');
    } else if (vramRatio > 0.9) {
      recommendations.push('Very tight VRAM fit. Consider reducing context size or using Q4 quantization for more headroom.');
    }

    if (headroomMb < 500) {
      recommendations.push('Low VRAM headroom may cause issues with concurrent requests or system processes.');
    }

    if (contextSize > 8192 && headroomPct < 20) {
      recommendations.push('Large context size with limited headroom. Consider reducing context to 4096 for stability.');
    }

    if (quantization === 'F16' && vramRatio > 0.6) {
      recommendations.push('F16 quantization uses significant VRAM. Consider Q5_K_M for near-lossless quality with better memory efficiency.');
    }

    if (quantization === 'Q4_K_S') {
      recommendations.push('Q4_K_S provides the smallest size but may degrade output quality. Consider Q4_K_M or Q5_K_M for better results.');
    }

    if (score >= 90) {
      recommendations.push('Excellent fit! This configuration should run smoothly with room for concurrent requests.');
    } else if (score >= 70) {
      recommendations.push('Good fit. Performance should be reliable for most workloads.');
    }

    if (vram >= 24) {
      recommendations.push('High VRAM GPU detected. You could run larger models or increase context size for better results.');
    }

    return NextResponse.json({
      score,
      grade,
      details: {
        modelVram: Math.round(modelVramMb),
        contextVram: contextVramMb,
        overheadVram: overheadMb,
        totalVram: Math.round(totalVramMb),
        headroom: Math.round(headroomMb),
        efficiency: Math.round(efficiency * 100) / 100,
        vramUsagePercent: Math.round((totalVramMb / vramTotalMb) * 100),
      },
      recommendations,
      calculatedAt: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'KimariFit calculation failed', message: String(error) },
      { status: 500 }
    );
  }
}
