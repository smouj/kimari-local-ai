import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    const benchmarks = await db.benchmarkResult.findMany({
      orderBy: { createdAt: 'desc' },
    });

    return NextResponse.json(benchmarks);
  } catch (error) {
    console.error('Failed to get benchmarks:', error);
    return NextResponse.json(
      { error: 'Failed to get benchmarks' },
      { status: 500 }
    );
  }
}
