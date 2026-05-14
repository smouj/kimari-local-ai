import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    const profiles = await db.gpuProfile.findMany({
      orderBy: { order: 'asc' },
    });

    // Get current server state to determine which profile is running
    const serverState = await db.serverState.findFirst();
    const runningProfile = serverState?.status === 'running' ? serverState.profile : null;

    const enrichedProfiles = profiles.map((profile) => ({
      ...profile,
      isRunning: profile.name === runningProfile,
    }));

    return NextResponse.json(enrichedProfiles);
  } catch (error) {
    console.error('Failed to get profiles:', error);
    return NextResponse.json(
      { error: 'Failed to get profiles' },
      { status: 500 }
    );
  }
}
