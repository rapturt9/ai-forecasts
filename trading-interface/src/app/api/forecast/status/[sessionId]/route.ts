import { NextRequest, NextResponse } from 'next/server'

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const { sessionId } = params

    console.log('📊 Polling forecast status for session:', sessionId)

    // Call the Python FastAPI server to get forecast status
    const response = await fetch(`${PYTHON_API_URL}/api/forecast/${sessionId}`, {
      method: 'GET',
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
    console.log('✅ Forecast status received:', data.confidence_level)
    
    // Transform Python response to match frontend expectations
    const transformedResponse = {
      question: data.question || "Processing...",
      probability: data.forecast_probability,
      confidence: data.confidence_level,
      reasoning: data.reasoning,
      strategies: data.strategies,
      baseRate: data.base_rate,
      evidenceQuality: data.evidence_quality,
      newsSourcesCount: data.news_sources_count,
      totalArticles: data.total_articles,
      sessionId: data.session_id,
      searchTimeframe: {
        start: "2024-01-01",
        end: new Date().toISOString().split('T')[0]
      }
    }

    return NextResponse.json(transformedResponse)
  } catch (error) {
    console.error('Forecast status API error:', error)
    return NextResponse.json(
      { error: `Failed to get forecast status: ${error.message}` },
      { status: 500 }
    )
  }
}