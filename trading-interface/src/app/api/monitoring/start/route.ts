import { NextRequest, NextResponse } from 'next/server'

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    console.log('🤖 Starting agent monitoring')

    // Call the Python FastAPI server
    const response = await fetch(`${PYTHON_API_URL}/api/monitoring/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      console.error('Python API error:', errorData)
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()
    console.log('✅ Agent monitoring started:', data)

    return NextResponse.json(data)
  } catch (error) {
    console.error('Monitoring start API error:', error)
    return NextResponse.json(
      { error: `Failed to start monitoring: ${error.message}` },
      { status: 500 }
    )
  }
}