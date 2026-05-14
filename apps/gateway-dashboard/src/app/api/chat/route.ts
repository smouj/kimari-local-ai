import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const messages = body.messages || []

    // Try real Ollama backend first
    const ollamaUrl = 'http://127.0.0.1:11434/v1/chat/completions'
    try {
      const res = await fetch(ollamaUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama3.2:1b',
          messages,
          stream: false,
          max_tokens: 512,
        }),
        signal: AbortSignal.timeout(30000),
      })

      if (res.ok) {
        const data = await res.json()
        const assistantMessage = data.choices?.[0]?.message?.content || 'No response generated.'
        return NextResponse.json({
          message: assistantMessage,
          model: data.model || 'llama3.2:1b',
          source: 'ollama',
          tokensUsed: data.usage?.total_tokens || 0,
        })
      }
    } catch {
      // Ollama not available, fall through to mock
    }

    // Try llama-server
    const llamaUrl = 'http://127.0.0.1:11435/v1/chat/completions'
    try {
      const res = await fetch(llamaUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages,
          stream: false,
          max_tokens: 512,
        }),
        signal: AbortSignal.timeout(30000),
      })

      if (res.ok) {
        const data = await res.json()
        const assistantMessage = data.choices?.[0]?.message?.content || 'No response generated.'
        return NextResponse.json({
          message: assistantMessage,
          model: data.model || 'llama-server',
          source: 'llama-server',
          tokensUsed: data.usage?.total_tokens || 0,
        })
      }
    } catch {
      // llama-server not available either
    }

    // Fallback: no backend available
    return NextResponse.json({
      message: '⚠️ No LLM backend is currently running. Start Ollama (`ollama serve`) or llama-server (`kimari start --profile test`) to enable live chat.',
      model: 'none',
      source: 'fallback',
      tokensUsed: 0,
    })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Chat request failed' },
      { status: 500 }
    )
  }
}
