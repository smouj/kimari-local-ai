import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    const configs = await db.gatewayConfig.findMany({
      orderBy: { key: 'asc' },
    });

    // Mask secret values
    const maskedConfigs = configs.map((config) => ({
      ...config,
      value: config.isSecret && config.value ? '***' : config.value,
    }));

    return NextResponse.json(maskedConfigs);
  } catch (error) {
    console.error('Failed to get config:', error);
    return NextResponse.json(
      { error: 'Failed to get configuration' },
      { status: 500 }
    );
  }
}
