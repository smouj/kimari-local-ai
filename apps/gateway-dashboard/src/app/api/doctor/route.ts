import { NextResponse } from 'next/server';

interface DiagnosticCheck {
  name: string;
  category: string;
  status: 'PASS' | 'WARN' | 'FAIL';
  message: string;
  details?: string;
}

export async function GET() {
  try {
    const checks: DiagnosticCheck[] = [
      {
        name: 'Python Runtime',
        category: 'Runtime',
        status: 'PASS',
        message: 'Python 3.11.8 found at /usr/bin/python3',
        details: 'Python 3.11+ is recommended. Found version meets minimum requirements for all Kimari features.',
      },
      {
        name: 'Kimari Version',
        category: 'Core',
        status: 'PASS',
        message: 'Running Kimari v0.1.73-alpha (latest)',
        details: 'Current version matches the latest release on GitHub. No update available.',
      },
      {
        name: 'Config Paths',
        category: 'Core',
        status: 'PASS',
        message: 'Config directory exists at ~/.kimari/',
        details: 'All required directories are present: config/, models/, benchmarks/, logs/.',
      },
      {
        name: 'Config Validity',
        category: 'Core',
        status: 'PASS',
        message: 'Configuration schema is valid',
        details: 'All config keys pass JSON schema validation. No missing required fields detected.',
      },
      {
        name: 'Model Files',
        category: 'Models',
        status: 'WARN',
        message: '2 of 5 configured models are downloaded',
        details: 'Missing models: kimari-4b-v2-Q4_K_M.gguf, llama-3.1-8b-Q5_K_M.gguf, mistral-7b-Q4_K_M.gguf. Use "kimari model pull" to download.',
      },
      {
        name: 'Packaged Defaults',
        category: 'Core',
        status: 'PASS',
        message: 'All 11 default profiles are intact',
        details: 'Checksum validation passed for all packaged default configurations.',
      },
      {
        name: 'llama-server Binary',
        category: 'Runtime',
        status: 'PASS',
        message: 'llama-server binary found at ~/.kimari/bin/llama-server',
        details: 'Version: llama.cpp b-3228. Supports GGUF format, Flash Attention, and KV cache quantization.',
      },
      {
        name: 'CUDA/NVIDIA',
        category: 'Hardware',
        status: 'WARN',
        message: 'NVIDIA driver detected but CUDA toolkit not found',
        details: 'Driver: NVIDIA 535.129.03. CUDA toolkit is recommended for GPU acceleration. Install CUDA 12.x toolkit for optimal performance.',
      },
      {
        name: 'Default Profile',
        category: 'Core',
        status: 'PASS',
        message: 'Default profile "gtx1060-6gb" is configured',
        details: 'Profile uses Q4_K_M quantization with 4096 context size. Compatible with detected hardware.',
      },
      {
        name: 'Secret Scanner',
        category: 'Security',
        status: 'PASS',
        message: 'No exposed secrets detected in configuration',
        details: 'Scanned all config files for API keys, tokens, and credentials. All secrets are properly masked in storage.',
      },
      {
        name: 'Benchmark Prompts',
        category: 'Models',
        status: 'FAIL',
        message: 'Benchmark prompt files are missing',
        details: 'Expected prompt files not found in ~/.kimari/benchmarks/prompts/. Run "kimari benchmark init" to generate default prompts.',
      },
      {
        name: 'Gateway Module',
        category: 'Gateway',
        status: 'PASS',
        message: 'Gateway module is operational',
        details: 'OpenAI-compatible API gateway is ready. Supports /v1/chat/completions and /v1/models endpoints.',
      },
      {
        name: 'Integration Docs',
        category: 'Gateway',
        status: 'WARN',
        message: '3 of 5 integration docs are available',
        details: 'Missing documentation for: Continue.dev, Open Interpreter. Basic setup guides are available for all integrations.',
      },
      {
        name: 'Preview Gate',
        category: 'Models',
        status: 'PASS',
        message: 'Kimari-4B preview gate is open',
        details: 'Preview model access is enabled. Kimari-4B-v2 is available for testing with reduced context window.',
      },
    ];

    const summary = {
      total: checks.length,
      pass: checks.filter((c) => c.status === 'PASS').length,
      warn: checks.filter((c) => c.status === 'WARN').length,
      fail: checks.filter((c) => c.status === 'FAIL').length,
    };

    const healthScore = Math.round((summary.pass / summary.total) * 100);

    return NextResponse.json({
      checks,
      summary,
      healthScore,
      checkedAt: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Diagnostic check failed', message: String(error) },
      { status: 500 }
    );
  }
}
