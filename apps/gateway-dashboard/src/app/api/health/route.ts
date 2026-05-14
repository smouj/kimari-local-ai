import { NextResponse } from 'next/server';

const startTime = Date.now();

export async function GET() {
  try {
    const uptime = Math.floor((Date.now() - startTime) / 1000);

    return NextResponse.json({
      status: 'ok',
      version: '0.1.73-alpha',
      uptime,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      { status: 'error', message: 'Health check failed' },
      { status: 500 }
    );
  }
}
