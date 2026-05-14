import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function POST() {
  try {
    const serverState = await db.serverState.findFirst();

    if (!serverState) {
      return NextResponse.json(
        { error: 'No server state found' },
        { status: 404 }
      );
    }

    if (serverState.status !== 'running' && serverState.status !== 'starting') {
      return NextResponse.json(
        { error: 'Server is not running' },
        { status: 404 }
      );
    }

    const previousProfile = serverState.profile;
    const previousPid = serverState.pid;
    const previousPort = serverState.port;

    // Update server state to stopped
    await db.serverState.update({
      where: { id: serverState.id },
      data: {
        status: 'stopped',
        pid: null,
        startedAt: null,
        uptime: 0,
      },
    });

    // Log the stop event
    await db.gatewayLog.create({
      data: {
        level: 'info',
        source: 'server',
        message: `llama-server stopped (profile: "${previousProfile}")`,
        metadata: JSON.stringify({ profile: previousProfile, pid: previousPid, port: previousPort }),
      },
    });

    return NextResponse.json({
      status: 'stopped',
      profile: previousProfile,
      pid: previousPid,
    });
  } catch (error) {
    console.error('Failed to stop server:', error);
    return NextResponse.json(
      { error: 'Failed to stop server' },
      { status: 500 }
    );
  }
}
