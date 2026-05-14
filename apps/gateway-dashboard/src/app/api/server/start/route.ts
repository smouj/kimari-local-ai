import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

interface StartServerRequest {
  profile: string;
}

export async function POST(request: Request) {
  try {
    const body: StartServerRequest = await request.json();
    const { profile } = body;

    if (!profile) {
      return NextResponse.json(
        { error: 'Profile name is required' },
        { status: 400 }
      );
    }

    // Validate profile exists
    const gpuProfile = await db.gpuProfile.findUnique({
      where: { name: profile },
    });

    if (!gpuProfile) {
      return NextResponse.json(
        { error: `Profile "${profile}" not found` },
        { status: 400 }
      );
    }

    // Check if server is already running
    const serverState = await db.serverState.findFirst();
    if (serverState?.status === 'running' || serverState?.status === 'starting') {
      return NextResponse.json(
        { error: `Server is already ${serverState.status} with profile "${serverState.profile}"` },
        { status: 409 }
      );
    }

    // Get server config for port
    const portConfig = await db.gatewayConfig.findUnique({
      where: { key: 'server_port' },
    });
    const port = portConfig ? parseInt(portConfig.value, 10) : 11435;

    // Get model file for the profile
    const modelFile = gpuProfile.modelFile || null;

    // Simulate PID
    const pid = Math.floor(Math.random() * 10000) + 1000;

    // Update server state to starting
    await db.serverState.update({
      where: { id: serverState!.id },
      data: {
        status: 'starting',
        profile,
        model: modelFile,
        pid,
        port,
        host: gpuProfile.host,
        startedAt: new Date(),
        lastError: null,
      },
    });

    // Log the start event
    await db.gatewayLog.create({
      data: {
        level: 'info',
        source: 'server',
        message: `Starting llama-server with profile "${profile}"`,
        metadata: JSON.stringify({ profile, port, pid, model: modelFile }),
      },
    });

    // Simulate transition to "running" after a brief moment
    // In a real implementation, this would poll the actual server
    setTimeout(async () => {
      try {
        const currentState = await db.serverState.findFirst();
        if (currentState?.status === 'starting' && currentState.profile === profile) {
          await db.serverState.update({
            where: { id: currentState.id },
            data: { status: 'running' },
          });
          await db.gatewayLog.create({
            data: {
              level: 'info',
              source: 'server',
              message: `llama-server is running on port ${port} with profile "${profile}"`,
              metadata: JSON.stringify({ profile, port, pid }),
            },
          });
        }
      } catch (err) {
        console.error('Failed to update server state to running:', err);
      }
    }, 2000);

    return NextResponse.json({
      status: 'started',
      profile,
      port,
      pid,
      model: modelFile,
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    return NextResponse.json(
      { error: 'Failed to start server' },
      { status: 500 }
    );
  }
}
