import { NextResponse } from 'next/server'

interface SetupStep {
  id: string
  title: string
  completed: boolean
}

const steps: SetupStep[] = [
  { id: 'welcome', title: 'Welcome to Kimari', completed: false },
  { id: 'gpu', title: 'GPU Configuration', completed: false },
  { id: 'model', title: 'Download Model', completed: false },
  { id: 'start', title: 'Start Server', completed: false },
]

let setupComplete = false

export async function GET() {
  return NextResponse.json({
    isFirstTime: !setupComplete,
    steps: steps.map((s) => ({
      ...s,
      completed: setupComplete ? true : s.completed,
    })),
    currentStep: setupComplete ? steps.length : steps.findIndex((s) => !s.completed),
  })
}

export async function POST() {
  setupComplete = true
  steps.forEach((s) => {
    s.completed = true
  })

  return NextResponse.json({ success: true })
}
