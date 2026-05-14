import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

interface PullModelRequest {
  model: string;
}

export async function POST(request: Request) {
  try {
    const body: PullModelRequest = await request.json();
    const { model } = body;

    if (!model) {
      return NextResponse.json(
        { error: 'Model name is required' },
        { status: 400 }
      );
    }

    // Find the model
    const modelEntry = await db.modelEntry.findUnique({
      where: { name: model },
    });

    if (!modelEntry) {
      return NextResponse.json(
        { error: `Model "${model}" not found` },
        { status: 404 }
      );
    }

    if (modelEntry.downloaded) {
      return NextResponse.json(
        { error: `Model "${model}" is already downloaded` },
        { status: 409 }
      );
    }

    // Simulate download by marking as downloaded
    const updated = await db.modelEntry.update({
      where: { name: model },
      data: {
        downloaded: true,
        downloadedAt: new Date(),
      },
    });

    // Log the download
    await db.gatewayLog.create({
      data: {
        level: 'info',
        source: 'gateway',
        message: `Model downloaded: ${modelEntry.displayName}`,
        metadata: JSON.stringify({
          model,
          filename: modelEntry.filename,
          fileSizeMb: modelEntry.fileSizeMb,
        }),
      },
    });

    return NextResponse.json({
      status: 'downloaded',
      model: updated.name,
      displayName: updated.displayName,
      filename: updated.filename,
      fileSizeMb: updated.fileSizeMb,
    });
  } catch (error) {
    console.error('Failed to pull model:', error);
    return NextResponse.json(
      { error: 'Failed to pull model' },
      { status: 500 }
    );
  }
}
