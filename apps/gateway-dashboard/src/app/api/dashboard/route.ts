import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    // Server status
    const serverState = await db.serverState.findFirst();
    let uptime = serverState?.uptime ?? 0;
    if (serverState?.status === 'running' && serverState.startedAt) {
      uptime = Math.floor(
        (Date.now() - new Date(serverState.startedAt).getTime()) / 1000
      );
    }

    const serverStatus = serverState
      ? {
          status: serverState.status,
          pid: serverState.pid,
          port: serverState.port,
          host: serverState.host,
          profile: serverState.profile,
          model: serverState.model,
          startedAt: serverState.startedAt,
          uptime,
          lastError: serverState.lastError,
        }
      : { status: 'stopped', uptime: 0 };

    // Profile summary
    const profiles = await db.gpuProfile.findMany();
    const runningProfile = serverState?.status === 'running' ? serverState.profile : null;
    const profileSummary = {
      total: profiles.length,
      available: profiles.filter((p) => p.status === 'available').length,
      requiresModel: profiles.filter((p) => p.status === 'requires_model').length,
      networkExposed: profiles.filter((p) => p.status === 'network_exposed').length,
      running: runningProfile,
    };

    // Model summary
    const models = await db.modelEntry.findMany();
    const modelSummary = {
      total: models.length,
      downloaded: models.filter((m) => m.downloaded).length,
      notDownloaded: models.filter((m) => !m.downloaded).length,
      categories: {
        test: models.filter((m) => m.category === 'test').length,
        recommended: models.filter((m) => m.category === 'recommended').length,
        community: models.filter((m) => m.category === 'community').length,
        official: models.filter((m) => m.category === 'official').length,
      },
    };

    // Recent benchmarks (last 5)
    const recentBenchmarks = await db.benchmarkResult.findMany({
      orderBy: { createdAt: 'desc' },
      take: 5,
    });

    // Recent logs (last 10)
    const recentLogs = await db.gatewayLog.findMany({
      orderBy: { createdAt: 'desc' },
      take: 10,
    });

    return NextResponse.json({
      server: serverStatus,
      profiles: profileSummary,
      models: modelSummary,
      recentBenchmarks,
      recentLogs,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Failed to get dashboard data:', error);
    return NextResponse.json(
      { error: 'Failed to get dashboard data' },
      { status: 500 }
    );
  }
}
