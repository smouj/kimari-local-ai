import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    const serverState = await db.serverState.findFirst();

    if (!serverState) {
      return NextResponse.json(
        { error: 'No server state found' },
        { status: 404 }
      );
    }

    // Calculate uptime if server is running
    let uptime = serverState.uptime;
    if (serverState.status === 'running' && serverState.startedAt) {
      uptime = Math.floor(
        (Date.now() - new Date(serverState.startedAt).getTime()) / 1000
      );
    }

    return NextResponse.json({
      status: serverState.status,
      pid: serverState.pid,
      port: serverState.port,
      host: serverState.host,
      profile: serverState.profile,
      model: serverState.model,
      startedAt: serverState.startedAt,
      uptime,
      lastError: serverState.lastError,
      updatedAt: serverState.updatedAt,
    });
  } catch (error) {
    console.error('Failed to get server status:', error);
    return NextResponse.json(
      { error: 'Failed to get server status' },
      { status: 500 }
    );
  }
}
