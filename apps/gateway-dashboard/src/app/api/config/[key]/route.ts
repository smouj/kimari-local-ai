import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

type RouteContext = {
  params: Promise<{ key: string }>;
};

export async function PUT(request: Request, context: RouteContext) {
  try {
    const { key } = await context.params;
    const body = await request.json();

    if (!body || typeof body.value === 'undefined') {
      return NextResponse.json(
        { error: 'Request body must include "value" field' },
        { status: 400 }
      );
    }

    // Check if config key exists
    const existing = await db.gatewayConfig.findUnique({
      where: { key },
    });

    if (!existing) {
      return NextResponse.json(
        { error: `Config key "${key}" not found` },
        { status: 404 }
      );
    }

    // Update the config value
    const updated = await db.gatewayConfig.update({
      where: { key },
      data: { value: String(body.value) },
    });

    // Log the config change
    await db.gatewayLog.create({
      data: {
        level: 'info',
        source: 'gateway',
        message: `Config updated: ${key}`,
        metadata: JSON.stringify({ key, previousValue: existing.isSecret ? '***' : existing.value }),
      },
    });

    // Mask secret values in response
    const response = {
      ...updated,
      value: updated.isSecret ? '***' : updated.value,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Failed to update config:', error);
    return NextResponse.json(
      { error: 'Failed to update configuration' },
      { status: 500 }
    );
  }
}
