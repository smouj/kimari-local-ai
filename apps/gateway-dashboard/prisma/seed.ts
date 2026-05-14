import { db } from '@/lib/db';

async function seed() {
  console.log('🌱 Seeding Kimari Gateway database...');

  // Seed GPU Profiles
  const profiles = [
    { name: 'test', displayName: 'Test (Alpha Default)', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, mode: 'safe', useCase: 'Default alpha testing', modelFile: 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf', isDefault: true, status: 'available', order: 0 },
    { name: 'gtx1060', displayName: 'GTX 1060', gpu: 'GTX 1060', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 8192, mode: 'balanced', useCase: 'Main inference', modelFile: 'kimari-4b-q4_k_m.gguf', isDefault: false, status: 'requires_model', order: 1 },
    { name: 'gtx1080', displayName: 'GTX 1080', gpu: 'GTX 1080', vram: '8 GB', quantization: 'Q5_K_M', contextSize: 16384, mode: 'balanced', useCase: 'Quality inference', modelFile: 'kimari-4b-q5_k_m.gguf', isDefault: false, status: 'requires_model', order: 2 },
    { name: 'turbo', displayName: 'Turbo', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'IQ4_XS', contextSize: 8192, mode: 'fast', useCase: 'Speed priority', modelFile: 'kimari-4b-iq4_xs.gguf', isDefault: false, status: 'requires_model', order: 3 },
    { name: 'gtx1060-safe', displayName: 'GTX 1060 Safe', gpu: 'GTX 1060', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, cacheK: 'q8_0', cacheV: 'q8_0', mode: 'safe', useCase: 'Maximum stability, no OOM', isDefault: false, status: 'requires_model', order: 4 },
    { name: 'gtx1060-fast', displayName: 'GTX 1060 Fast', gpu: 'GTX 1060', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 8192, cacheK: 'q8_0', cacheV: 'q8_0', mode: 'fast', useCase: 'Speed priority', isDefault: false, status: 'requires_model', order: 5 },
    { name: 'gtx1080-balanced', displayName: 'GTX 1080 Balanced', gpu: 'GTX 1080', vram: '8 GB', quantization: 'Q5_K_M', contextSize: 8192, cacheK: 'q8_0', cacheV: 'f16', mode: 'balanced', useCase: 'Quality/speed balance', isDefault: false, status: 'requires_model', order: 6 },
    { name: 'gtx1080-longctx', displayName: 'GTX 1080 Long Context', gpu: 'GTX 1080', vram: '8 GB', quantization: 'Q5_K_M', contextSize: 16384, cacheK: 'q8_0', cacheV: 'q8_0', mode: 'balanced', useCase: 'Long conversations', isDefault: false, status: 'requires_model', order: 7 },
    { name: 'ide-local', displayName: 'IDE Local', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, cacheK: 'q8_0', cacheV: 'q8_0', mode: 'ide', useCase: 'Continue, Cursor, VS Code', isDefault: false, status: 'requires_model', order: 8 },
    { name: 'agent-local', displayName: 'Agent Local', gpu: 'Any 6 GB+', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, cacheK: 'q8_0', cacheV: 'q8_0', mode: 'agent', useCase: 'OpenClaw, Hermes agents', isDefault: false, status: 'requires_model', order: 9 },
    { name: 'docker', displayName: 'Docker (Open WebUI)', gpu: 'Open WebUI', vram: '6 GB', quantization: 'Q4_K_M', contextSize: 4096, host: '0.0.0.0', mode: 'safe', useCase: 'Docker + Open WebUI', isDefault: false, status: 'network_exposed', order: 10 },
  ];

  for (const profile of profiles) {
    await db.gpuProfile.upsert({
      where: { name: profile.name },
      update: profile,
      create: profile,
    });
  }
  console.log(`  ✅ ${profiles.length} GPU profiles seeded`);

  // Seed Models
  const models = [
    { name: 'tinyllama-1.1b-q4km', displayName: 'TinyLlama 1.1B Chat Q4_K_M', filename: 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf', size: '1.1B', fileSizeMb: 670, quantization: 'Q4_K_M', license: 'Apache 2.0', source: 'https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF', category: 'test', vramRequired: '2 GB', downloaded: true, compatibleProfiles: 'test,gtx1060,gtx1080' },
    { name: 'qwen3-4b-q4km', displayName: 'Qwen3 4B Instruct Q4_K_M', filename: 'qwen3-4b-instruct.Q4_K_M.gguf', size: '4B', fileSizeMb: 2670, quantization: 'Q4_K_M', license: 'Apache 2.0', source: 'https://huggingface.co/Qwen/Qwen3-4B-Instruct-GGUF', category: 'recommended', vramRequired: '6 GB', downloaded: false, compatibleProfiles: 'gtx1060,gtx1080,turbo' },
    { name: 'qwen25-1.5b-instruct-q4km', displayName: 'Qwen2.5 1.5B Instruct Q4_K_M', filename: 'qwen2.5-1.5b-instruct-q4_k_m.gguf', size: '1.5B', fileSizeMb: 980, quantization: 'Q4_K_M', license: 'Apache 2.0', source: 'https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF', category: 'community', vramRequired: '4 GB', downloaded: false, compatibleProfiles: 'test,gtx1060' },
    { name: 'smollm3-3b-q4km', displayName: 'SmolLM3 3B Q4_K_M', filename: 'smollm3-3b.Q4_K_M.gguf', size: '3B', fileSizeMb: 1980, quantization: 'Q4_K_M', license: 'Apache 2.0', source: 'https://huggingface.co/HuggingFaceTB/SmolLM3-3B-GGUF', category: 'community', vramRequired: '5 GB', downloaded: false, compatibleProfiles: 'gtx1060,gtx1080' },
    { name: 'llama-3.2-3b-q4km', displayName: 'Llama 3.2 3B Q4_K_M', filename: 'llama-3.2-3b.Q4_K_M.gguf', size: '3B', fileSizeMb: 2010, quantization: 'Q4_K_M', license: 'Meta Community', source: 'https://huggingface.co/meta-llama/Llama-3.2-3B-GGUF', category: 'community', vramRequired: '5 GB', downloaded: false, compatibleProfiles: 'gtx1060,gtx1080' },
  ];

  for (const model of models) {
    await db.modelEntry.upsert({
      where: { name: model.name },
      update: model,
      create: model,
    });
  }
  console.log(`  ✅ ${models.length} models seeded`);

  // Seed Gateway Config
  const configs = [
    { key: 'gateway_version', value: '0.1.73-alpha', valueType: 'string', description: 'Kimari Gateway version' },
    { key: 'gateway_host', value: '127.0.0.1', valueType: 'string', description: 'Gateway bind address' },
    { key: 'gateway_port', value: '11436', valueType: 'number', description: 'Gateway port' },
    { key: 'server_host', value: '127.0.0.1', valueType: 'string', description: 'llama-server bind address' },
    { key: 'server_port', value: '11435', valueType: 'number', description: 'llama-server port' },
    { key: 'default_profile', value: 'test', valueType: 'string', description: 'Default GPU profile' },
    { key: 'auto_start', value: 'false', valueType: 'boolean', description: 'Auto-start server on gateway start' },
    { key: 'log_level', value: 'info', valueType: 'string', description: 'Log level (debug, info, warn, error)' },
    { key: 'max_benchmarks', value: '100', valueType: 'number', description: 'Maximum stored benchmark results' },
    { key: 'auth_token', value: '', valueType: 'string', description: 'Bearer token for non-localhost auth', isSecret: true },
    { key: 'cors_enabled', value: 'false', valueType: 'boolean', description: 'Enable CORS headers' },
    { key: 'rate_limit_per_sec', value: '1', valueType: 'number', description: 'Rate limit for mutation endpoints' },
  ];

  for (const config of configs) {
    await db.gatewayConfig.upsert({
      where: { key: config.key },
      update: config,
      create: config,
    });
  }
  console.log(`  ✅ ${configs.length} config entries seeded`);

  // Seed Integrations
  const integrations = [
    { name: 'openwebui', displayName: 'Open WebUI', description: 'Open-source web UI for local LLMs with chat interface, model management, and document upload', baseUrl: 'http://127.0.0.1:11435/v1', status: 'available', icon: '🌐', docsUrl: 'https://github.com/open-webui/open-webui' },
    { name: 'openclaw', displayName: 'OpenClaw', description: 'AI agent backend that uses Kimari as its local Chat Completions provider', baseUrl: 'http://127.0.0.1:11435/v1', status: 'available', icon: '🤖', docsUrl: 'https://github.com/openclaw/openclaw' },
    { name: 'hermes', displayName: 'Hermes Agent', description: 'Local OpenAI-compatible backend for AI agents and automation', baseUrl: 'http://127.0.0.1:11435/v1', status: 'available', icon: '⚡', docsUrl: 'https://github.com/hermes-agent/hermes' },
    { name: 'continue', displayName: 'Continue.dev', description: 'IDE coding assistant extension for VS Code and JetBrains', baseUrl: 'http://127.0.0.1:11435/v1', status: 'available', icon: '💻', docsUrl: 'https://continue.dev' },
  ];

  for (const integration of integrations) {
    await db.integration.upsert({
      where: { name: integration.name },
      update: integration,
      create: integration,
    });
  }
  console.log(`  ✅ ${integrations.length} integrations seeded`);

  // Seed initial server state
  const existingState = await db.serverState.findFirst();
  if (!existingState) {
    await db.serverState.create({
      data: { status: 'stopped', profile: 'test' },
    });
    console.log('  ✅ Initial server state created');
  }

  // Seed initial logs
  await db.gatewayLog.createMany({
    data: [
      { level: 'info', source: 'system', message: 'Kimari Gateway initialized' },
      { level: 'info', source: 'system', message: 'Database seeded with default profiles and models' },
      { level: 'info', source: 'gateway', message: 'Gateway ready on 127.0.0.1:11436' },
      { level: 'info', source: 'system', message: 'Default profile set to "test" (TinyLlama 1.1B Q4_K_M)' },
      { level: 'warn', source: 'system', message: 'Kimari-4B is not yet released. Using TinyLlama for alpha testing.' },
    ],
  });
  console.log('  ✅ Initial log entries created');

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
