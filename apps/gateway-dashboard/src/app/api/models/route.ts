import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    const models = await db.modelEntry.findMany({
      orderBy: { name: 'asc' },
    });

    // Enrich models with parsed compatible profiles
    const enrichedModels = models.map((model) => ({
      ...model,
      compatibleProfilesList: model.compatibleProfiles
        ? model.compatibleProfiles.split(',').filter(Boolean)
        : [],
    }));

    return NextResponse.json(enrichedModels);
  } catch (error) {
    console.error('Failed to get models:', error);
    return NextResponse.json(
      { error: 'Failed to get models' },
      { status: 500 }
    );
  }
}
