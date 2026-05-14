import { NextResponse } from 'next/server';

const startTime = Date.now();

// Read version from package.json at build time
import { readFileSync } from 'fs';
import { join } from 'path';

let version = '0.1.81-alpha';
try {
  const pkg = JSON.parse(readFileSync(join(process.cwd(), 'package.json'), 'utf-8'));
  version = pkg.version || version;
} catch {
  // fallback to hardcoded
}

export async function GET() {
  try {
    const uptime = Math.floor((Date.now() - startTime) / 1000);

    return NextResponse.json({
      status: 'ok',
      version,
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
