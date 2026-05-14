import { db } from '@/lib/db';

async function seed() {
  console.log('🌱 Seeding Kimari Gateway database with real system data...');

  // ── Real GPU Profiles (from kimari/defaults/kimari.profiles.json) ──
  const profiles = [
    { name: 'test', displayName: 'Test Model', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, host: '127.0.0.1', cacheK: 'f16', cacheV: 'f16', mode: 'safe', useCase: 'Small provisional GGUF for runtime validation', modelFile: 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf', isDefault: true, status: 'available', order: 0 },
    { name: 'gtx1060', displayName: 'GTX 1060 (6 GB)', gpu: 'NVIDIA GeForce GTX 1060 6GB', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 8192, host: '127.0.0.1', cacheK: 'f16', cacheV: 'f16', mode: 'balanced', useCase: 'Base profile. Optimal quality/speed balance for 6 GB VRAM. Requires Kimari-4B.', modelFile: 'Kimari-4B-Q4_K_M.gguf', isDefault: false, status: 'requires_model', order: 1 },
    { name: 'gtx1080', displayName: 'GTX 1080 (8 GB)', gpu: 'GTX 1080', vram: '8 GB', quantization: 'Q5_K_M', contextSize: 16384, host: '127.0.0.1', cacheK: 'f16', cacheV: 'f16', mode: 'balanced', useCase: 'High profile. Maximum quality with extended context for 8 GB VRAM. Requires Kimari-4B.', modelFile: 'Kimari-4B-Q5_K_M.gguf', isDefault: false, status: 'requires_model', order: 2 },
    { name: 'turbo', displayName: 'Turbo (IQ4_XS)', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'IQ4_XS', contextSize: 8192, host: '127.0.0.1', cacheK: 'q8_0', cacheV: 'q8_0', mode: 'fast', useCase: 'Turbo profile. Fast inference with large context on limited hardware. Requires Kimari-4B.', modelFile: 'Kimari-4B-IQ4_XS.gguf', isDefault: false, status: 'requires_model', order: 3 },
    { name: 'docker', displayName: 'Docker / Open WebUI', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, host: '0.0.0.0', cacheK: 'f16', cacheV: 'f16', mode: 'safe', useCase: 'Docker + Open WebUI deployment', modelFile: 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf', isDefault: false, status: 'network_exposed', order: 4 },
    { name: 'ide-local', displayName: 'IDE Local', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, host: '127.0.0.1', cacheK: 'q8_0', cacheV: 'q8_0', mode: 'ide', useCase: 'Continue, Cursor, VS Code', modelFile: 'Kimari-4B-Q4_K_M.gguf', isDefault: false, status: 'requires_model', order: 5 },
    { name: 'agent-local', displayName: 'Agent Local', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, host: '127.0.0.1', cacheK: 'q8_0', cacheV: 'q8_0', mode: 'agent', useCase: 'OpenClaw, Hermes agents', modelFile: 'Kimari-4B-Q4_K_M.gguf', isDefault: false, status: 'requires_model', order: 6 },
  ];

  for (const profile of profiles) {
    await db.gpuProfile.upsert({
      where: { name: profile.name },
      update: profile,
      create: profile,
    });
  }
  console.log(`  ✅ ${profiles.length} GPU profiles seeded (real hardware)`);

  // ── Real Models ──
  const models = [
    { name: 'tinyllama-1.1b-q4km', displayName: 'TinyLlama 1.1B Chat Q4_K_M', filename: 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf', size: '1.1B', fileSizeMb: 638, quantization: 'Q4_K_M', license: 'Apache 2.0', source: 'https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF', category: 'test', vramRequired: '2 GB', downloaded: true, downloadedAt: new Date('2026-05-12T12:07:00Z'), compatibleProfiles: 'test,gtx1060,gtx1080,docker' },
    { name: 'kimari-4b-q4km', displayName: 'Kimari-4B Q4_K_M', filename: 'Kimari-4B-Q4_K_M.gguf', size: '4B', fileSizeMb: null, quantization: 'Q4_K_M', license: 'Apache 2.0', source: 'https://huggingface.co/kimari-ai/kimari-4b-gguf', category: 'official', vramRequired: '6 GB', downloaded: false, compatibleProfiles: 'gtx1060,turbo,ide-local,agent-local' },
    { name: 'kimari-4b-q5km', displayName: 'Kimari-4B Q5_K_M', filename: 'Kimari-4B-Q5_K_M.gguf', size: '4B', fileSizeMb: null, quantization: 'Q5_K_M', license: 'Apache 2.0', source: 'https://huggingface.co/kimari-ai/kimari-4b-gguf', category: 'official', vramRequired: '8 GB', downloaded: false, compatibleProfiles: 'gtx1080' },
    { name: 'kimari-4b-iq4xs', displayName: 'Kimari-4B IQ4_XS', filename: 'Kimari-4B-IQ4_XS.gguf', size: '4B', fileSizeMb: null, quantization: 'IQ4_XS', license: 'Apache 2.0', source: 'https://huggingface.co/kimari-ai/kimari-4b-gguf', category: 'official', vramRequired: '6 GB', downloaded: false, compatibleProfiles: 'turbo' },
  ];

  for (const model of models) {
    await db.modelEntry.upsert({
      where: { name: model.name },
      update: model,
      create: model,
    });
  }
  console.log(`  ✅ ${models.length} models seeded (TinyLlama downloaded, Kimari-4B pending)`);

  // ── Real Integrations ──
  const integrations = [
    { name: 'ollama', displayName: 'Ollama', description: 'Local LLM runtime — currently running on port 11434 with 7 models loaded', baseUrl: 'http://127.0.0.1:11434', status: 'connected', icon: '🦙', docsUrl: 'https://ollama.com' },
    { name: 'openclaw', displayName: 'OpenClaw', description: 'AI agent backend — manages this Kimari gateway instance', baseUrl: 'http://127.0.0.1:18789', status: 'connected', icon: '🤖', docsUrl: 'https://github.com/openclaw/openclaw' },
    { name: 'llama-server', displayName: 'llama.cpp Server', description: 'llama-server v1 (706fbd8) compiled with CUDA for GTX 1060', baseUrl: 'http://127.0.0.1:11435', status: 'available', icon: '⚡', docsUrl: 'https://github.com/ggerganov/llama.cpp' },
    { name: 'continue', displayName: 'Continue.dev', description: 'IDE coding assistant extension for VS Code and JetBrains', baseUrl: 'http://127.0.0.1:11435/v1', status: 'available', icon: '💻', docsUrl: 'https://continue.dev' },
  ];

  for (const integration of integrations) {
    await db.integration.upsert({
      where: { name: integration.name },
      update: integration,
      create: integration,
    });
  }
  console.log(`  ✅ ${integrations.length} integrations seeded (real running services)`);

  // ── Real Gateway Config ──
  const configs = [
    { key: 'gateway_version', value: '0.1.78-alpha', valueType: 'string', description: 'Kimari Gateway package version' },
    { key: 'gateway_host', value: '127.0.0.1', valueType: 'string', description: 'Gateway bind address' },
    { key: 'gateway_port', value: '3105', valueType: 'number', description: 'Gateway dashboard port' },
    { key: 'server_host', value: '127.0.0.1', valueType: 'string', description: 'llama-server bind address' },
    { key: 'server_port', value: '11435', valueType: 'number', description: 'llama-server port' },
    { key: 'ollama_url', value: 'http://127.0.0.1:11434', valueType: 'string', description: 'Ollama API endpoint (active)' },
    { key: 'default_profile', value: 'test', valueType: 'string', description: 'Default GPU profile' },
    { key: 'llama_server_binary', value: '/home/smouj/.local/bin/llama-server', valueType: 'string', description: 'llama-server binary path' },
    { key: 'models_dir', value: '/home/smouj/.local/share/kimari/models', valueType: 'string', description: 'Local GGUF models directory' },
    { key: 'gpu', value: 'NVIDIA GeForce GTX 1060 6GB', valueType: 'string', description: 'Detected GPU (CUDA compute 6.1)' },
    { key: 'gpu_vram_mb', value: '6143', valueType: 'number', description: 'GPU VRAM in MB' },
    { key: 'auto_start', value: 'false', valueType: 'boolean', description: 'Auto-start server on gateway start' },
    { key: 'log_level', value: 'info', valueType: 'string', description: 'Log level (debug, info, warn, error)' },
    { key: 'auth_token', value: '', valueType: 'string', description: 'Bearer token for non-localhost auth', isSecret: true },
  ];

  for (const config of configs) {
    await db.gatewayConfig.upsert({
      where: { key: config.key },
      update: config,
      create: config,
    });
  }
  console.log(`  ✅ ${configs.length} config entries seeded (real system paths)`);

  // ── Server State ──
  const existingState = await db.serverState.findFirst();
  if (!existingState) {
    await db.serverState.create({
      data: { status: 'stopped', profile: 'test', port: 11435, host: '127.0.0.1' },
    });
    console.log('  ✅ Initial server state created (stopped)');
  }

  // ── Initial Logs (real context) ──
  await db.gatewayLog.createMany({
    data: [
      { level: 'info', source: 'system', message: 'Kimari Gateway Dashboard started on port 3105' },
      { level: 'info', source: 'system', message: 'Package version: 0.1.78-alpha | Training tag: v0.1.79-alpha' },
      { level: 'info', source: 'system', message: 'GPU detected: NVIDIA GeForce GTX 1060 6GB (6143 MiB, CUDA compute 6.1)' },
      { level: 'info', source: 'system', message: 'llama-server binary found at ~/.local/bin/llama-server (v1, CUDA build)' },
      { level: 'info', source: 'system', message: 'Model available: TinyLlama 1.1B Q4_K_M (638 MB, downloaded)' },
      { level: 'info', source: 'integration', message: 'Ollama detected on port 11434 — 7 models loaded' },
      { level: 'info', source: 'integration', message: 'OpenClaw gateway detected on port 18789' },
      { level: 'warn', source: 'system', message: 'Kimari-4B GGUF not yet available — running in alpha mode with TinyLlama test model' },
      { level: 'info', source: 'system', message: 'Default profile: test (TinyLlama 1.1B Q4_K_M, ctx 4096)' },
      { level: 'info', source: 'gateway', message: 'Gate status: BLOCKED — no public weights, no GGUF export, no benchmark claims' },
    ],
  });
  console.log('  ✅ Initial log entries created (real system context)');

  console.log('🎉 Seeding complete!');
}

seed()
  .catch((e) => {
    console.error('❌ Seed failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await db.$disconnect();
  });
