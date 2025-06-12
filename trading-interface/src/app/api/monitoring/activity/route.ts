import { NextRequest, NextResponse } from 'next/server'

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('sessionId')

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      )
    }

    console.log('📊 Fetching agent activity for session:', sessionId)

    // Call the Python FastAPI server
    const response = await fetch(`${PYTHON_API_URL}/api/monitoring/activity/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      console.warn('Python API not available, using mock data')
      // Fallback to mock data if Python API is not available
      const mockActivity = [
        {
          timestamp: new Date().toISOString(),
          agent_type: "Risk Assessment",
          action: "BUY_NO",
          market_question: "Will Bitcoin decrease by 36% this year?",
          confidence: 86.0,
          edge: 1.4,
          status: "success"
        }
      ]
      return NextResponse.json(mockActivity)
    }

    const data = await response.json()
    console.log('✅ Agent activity fetched:', data.length)

    return NextResponse.json(data)
  } catch (error) {
    console.error('Activity API error:', error)
    // Fallback to mock data on error
    const mockActivity = [
      {
        timestamp: new Date().toISOString(),
        agent_type: "Risk Assessment",
        action: "BUY_NO", 
        market_question: "Will Bitcoin decrease by 36% this year?",
        confidence: 86.0,
        edge: 1.4,
        status: "success"
      }
    ]
    return NextResponse.json(mockActivity)
  }
}