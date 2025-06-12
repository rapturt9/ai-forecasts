import { NextRequest, NextResponse } from 'next/server'

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { sessionType, durationHours, initialBalance } = body

    console.log('🚀 Starting trading session:', { sessionType, durationHours, initialBalance })

    // Call the Python FastAPI server
    const response = await fetch(`${PYTHON_API_URL}/api/trading/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_type: sessionType,
        duration_hours: durationHours || 24,
        initial_balance: initialBalance || 1000.0
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      console.error('Python API error:', errorData)
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()
    console.log('✅ Trading session started:', data)

    return NextResponse.json(data)
  } catch (error) {
    console.error('Trading start API error:', error)
    return NextResponse.json(
      { error: `Failed to start trading session: ${error.message}` },
      { status: 500 }
    )
  }
}