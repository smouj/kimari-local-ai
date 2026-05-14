import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Simulate checking GitHub for latest release
    const currentVersion = '0.1.73-alpha';
    const latestVersion = '0.1.75-alpha';
    const updateAvailable = latestVersion !== currentVersion;

    return NextResponse.json({
      currentVersion,
      latestVersion,
      updateAvailable,
      releaseNotes: updateAvailable
        ? '## v0.1.75-alpha\n\n- Fixed gateway streaming for long responses\n- Added Kimari-4B preview gate\n- Improved CUDA detection\n- New KimariFit score calculator\n- Performance improvements for Q5 quantization'
        : undefined,
      checkedAt: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Update check failed', message: String(error) },
      { status: 500 }
    );
  }
}
