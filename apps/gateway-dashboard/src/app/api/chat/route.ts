import { NextRequest } from 'next/server'

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

function generateMockResponse(messages: ChatMessage[]): string {
  const lastMessage = messages[messages.length - 1]
  if (!lastMessage || lastMessage.role !== 'user') {
    return "I'm ready to help. What would you like to know?"
  }

  const input = lastMessage.content.toLowerCase()

  // Kimari Gateway topics
  if (input.includes('kimari') || input.includes('gateway')) {
    return "Kimari Gateway is a lightweight local AI gateway that bridges your applications to llama.cpp inference servers. It manages GPU profiles, model loading, and provides a unified API for local LLM inference. Think of it as your personal AI infrastructure layer — optimized for running models entirely on your own hardware with full privacy."
  }

  // GPU / VRAM / Quantization topics
  if (input.includes('quantiz') || input.includes('quant') || input.includes('gguf') || input.includes('ggml')) {
    return "GPU quantization reduces model precision to fit larger models into limited VRAM. The most common formats are Q4_K_M (4-bit, good balance of speed and quality), Q5_K_M (5-bit, better quality with modest VRAM increase), and Q8_0 (8-bit, near-lossless). For coding tasks, Q5_K_M is often the sweet spot — you get most of the model's capability while fitting comfortably in 8-12GB VRAM."
  }

  if (input.includes('vram') || input.includes('memory') || input.includes('gpu memory') || input.includes('optimize')) {
    return "To optimize VRAM usage: 1) Choose the right quantization level (Q4_K_M saves ~60% vs FP16). 2) Reduce context size to what you actually need — 2048 tokens uses half the KV cache of 4096. 3) Use Kimari's GPU profiles to auto-configure optimal settings. 4) Enable cache-K and cache-V offloading for multi-GPU setups. The KimariFit score can help you find the right balance."
  }

  // Model / coding topics
  if (input.includes('coding') || input.includes('code') || input.includes('programming') || input.includes('model') && input.includes('best')) {
    return "For coding assistance, the best local models are: DeepSeek-Coder (excellent code generation), CodeLlama (strong completion), and Qwen2.5-Coder (great multilingual support). With 8GB VRAM, DeepSeek-Coder 6.7B Q5_K_M is your best bet. With 16GB+, the 33B variant gives significantly better results. All work great through Kimari Gateway with auto-profile selection."
  }

  // Server / llama.cpp topics
  if (input.includes('server') || input.includes('llama.cpp') || input.includes('inference')) {
    return "Kimari Gateway manages llama.cpp server instances for you. When you start a server, it launches llama.cpp with the optimal parameters for your selected GPU profile — including thread count, batch size, context length, and memory mapping. The gateway handles health monitoring, auto-restart on crashes, and provides a unified OpenAI-compatible API endpoint."
  }

  // Benchmark topics
  if (input.includes('benchmark') || input.includes('performance') || input.includes('speed') || input.includes('token')) {
    return "Benchmarking measures your model's prompt processing speed (tokens/sec) and generation speed (tokens/sec). Key metrics include TTFT (Time To First Token) which affects perceived responsiveness, and generation throughput. Kimari's built-in benchmark tool runs standardized tests across your GPU profiles to help you choose the best configuration for your hardware."
  }

  // General AI/LLM topics
  if (input.includes('ai') || input.includes('llm') || input.includes('language model') || input.includes('neural')) {
    return "Large Language Models (LLMs) are neural networks trained on massive text datasets to understand and generate human language. Running them locally through tools like Kimari Gateway gives you privacy, zero API costs, unlimited usage, and full control over the model. The trade-off is hardware requirements — you need a capable GPU with sufficient VRAM to run models efficiently."
  }

  // Greeting
  if (input.includes('hello') || input.includes('hi') || input.includes('hey') || input.includes('greet')) {
    return "Hello! I'm your local AI assistant running through the Kimari Gateway. I can help you understand GPU profiles, model quantization, VRAM optimization, and anything about running local LLMs. What would you like to explore?"
  }

  // Help
  if (input.includes('help') || input.includes('what can you')) {
    return "I can help with: understanding Kimari Gateway features, choosing the right GPU profile for your hardware, selecting quantization levels for your VRAM budget, optimizing inference performance, explaining model architectures, and troubleshooting common local AI issues. Just ask about any of these topics!"
  }

  // Default response
  const defaults = [
    "That's a great question! When running local AI models, the key considerations are VRAM availability, quantization choice, and context length. Kimari Gateway handles all of these automatically with GPU profiles. Feel free to ask more specific questions about your setup!",
    "I'd recommend exploring the Kimari Gateway's features to get the most out of your local AI setup. The KimariFit score can help you find the optimal configuration for your GPU, and the built-in benchmarking tools let you compare performance across different settings.",
    "Local AI inference is all about balancing quality, speed, and resource usage. With the right GPU profile and quantization, you can run capable models even on consumer hardware. Try asking me about specific topics like VRAM optimization or model selection for more detailed guidance!",
  ]

  return defaults[Math.floor(Math.random() * defaults.length)]
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { messages, model } = body as { messages: ChatMessage[]; model?: string }

    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return new Response(
        JSON.stringify({ error: 'Messages array is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Generate a realistic mock AI response based on the last user message
    const response = generateMockResponse(messages)

    // Use ReadableStream to simulate token-by-token streaming
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      async start(controller) {
        const words = response.split(' ')

        for (let i = 0; i < words.length; i++) {
          const word = words[i]
          const isLast = i === words.length - 1
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ token: isLast ? word : word + ' ', done: false })}\n\n`)
          )
          await new Promise((resolve) => setTimeout(resolve, 30 + Math.random() * 60))
        }

        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ token: '', done: true, model: model || 'kimari-local' })}\n\n`)
        )
        controller.close()
      },
    })

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    })
  } catch {
    return new Response(
      JSON.stringify({ error: 'Invalid request body' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    )
  }
}
