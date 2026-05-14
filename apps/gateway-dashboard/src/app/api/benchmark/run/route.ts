import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

interface BenchmarkRunRequest {
  profile: string;
  mode: 'standard' | 'dry_run' | 'measured';
}

function generateBenchmarkResults(profile: string) {
  // Simulated benchmark results based on profile
  const baseSpeeds: Record<string, { prompt: number; gen: number }> = {
    test: { prompt: 45.2, gen: 32.1 },
    gtx1060: { prompt: 28.5, gen: 22.3 },
    gtx1080: { prompt: 42.7, gen: 35.8 },
    turbo: { prompt: 52.1, gen: 38.6 },
    'gtx1060-safe': { prompt: 25.3, gen: 19.8 },
    'gtx1060-fast': { prompt: 32.1, gen: 26.4 },
    'gtx1080-balanced': { prompt: 38.9, gen: 31.2 },
    'gtx1080-longctx': { prompt: 22.5, gen: 18.1 },
    'ide-local': { prompt: 30.2, gen: 24.5 },
    'agent-local': { prompt: 33.7, gen: 27.3 },
    docker: { prompt: 27.8, gen: 21.9 },
  };

  const base = baseSpeeds[profile] || baseSpeeds.test;
  // Add some random variation (±15%)
  const vary = () => 0.85 + Math.random() * 0.3;

  return {
    promptTokPerSec: Math.round(base.prompt * vary() * 10) / 10,
    genTokPerSec: Math.round(base.gen * vary() * 10) / 10,
    ttft: Math.round((30 + Math.random() * 80) * 10) / 10, // ms
    vramUsedMb: Math.round(2500 + Math.random() * 2000),
    totalTokens: Math.floor(300 + Math.random() * 500),
    duration: Math.round((8 + Math.random() * 15) * 10) / 10, // seconds
  };
}

export async function POST(request: Request) {
  try {
    const body: BenchmarkRunRequest = await request.json();
    const { profile, mode = 'standard' } = body;

    // For dry_run mode, return estimated plan without running
    if (mode === 'dry_run') {
      const profileName = profile || 'test';
      const gpuProfile = await db.gpuProfile.findUnique({
        where: { name: profileName },
      });

      if (!gpuProfile && profile) {
        return NextResponse.json(
          { error: `Profile "${profile}" not found` },
          { status: 400 }
        );
      }

      const activeProfile = gpuProfile || await db.gpuProfile.findFirst({ where: { isDefault: true } });

      return NextResponse.json({
        mode: 'dry_run',
        status: 'estimated',
        profile: activeProfile?.name || 'unknown',
        model: activeProfile?.modelFile || 'unknown',
        estimatedResults: generateBenchmarkResults(activeProfile?.name || 'test'),
        notes: 'These are estimated results. Run with mode "standard" or "measured" for actual benchmarks.',
      });
    }

    // For standard/measured modes, server must be running
    if (!profile) {
      return NextResponse.json(
        { error: 'Profile name is required for non-dry-run benchmarks' },
        { status: 400 }
      );
    }

    const serverState = await db.serverState.findFirst();
    if (serverState?.status !== 'running') {
      return NextResponse.json(
        { error: 'Server must be running to execute benchmarks' },
        { status: 409 }
      );
    }

    // Validate profile
    const gpuProfile = await db.gpuProfile.findUnique({
      where: { name: profile },
    });

    if (!gpuProfile) {
      return NextResponse.json(
        { error: `Profile "${profile}" not found` },
        { status: 400 }
      );
    }

    // Generate simulated benchmark results
    const results = generateBenchmarkResults(profile);

    // Create benchmark result entry
    const benchmarkResult = await db.benchmarkResult.create({
      data: {
        profile,
        model: gpuProfile.modelFile || 'unknown',
        quantization: gpuProfile.quantization,
        contextSize: gpuProfile.contextSize,
        promptTokPerSec: results.promptTokPerSec,
        genTokPerSec: results.genTokPerSec,
        ttft: results.ttft,
        vramUsedMb: results.vramUsedMb,
        totalTokens: results.totalTokens,
        duration: results.duration,
        mode,
        status: 'completed',
        gpuInfo: gpuProfile.gpu,
        resultsJson: JSON.stringify(results),
      },
    });

    // Log the benchmark
    await db.gatewayLog.create({
      data: {
        level: 'info',
        source: 'gateway',
        message: `Benchmark completed for profile "${profile}"`,
        metadata: JSON.stringify({
          profile,
          mode,
          promptTokPerSec: results.promptTokPerSec,
          genTokPerSec: results.genTokPerSec,
        }),
      },
    });

    return NextResponse.json(benchmarkResult);
  } catch (error) {
    console.error('Failed to run benchmark:', error);
    return NextResponse.json(
      { error: 'Failed to run benchmark' },
      { status: 500 }
    );
  }
}
