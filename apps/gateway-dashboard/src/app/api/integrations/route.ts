import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    const integrations = await db.integration.findMany({
      orderBy: { name: 'asc' },
    });

    return NextResponse.json(integrations);
  } catch (error) {
    console.error('Failed to get integrations:', error);
    return NextResponse.json(
      { error: 'Failed to get integrations' },
      { status: 500 }
    );
  }
}
