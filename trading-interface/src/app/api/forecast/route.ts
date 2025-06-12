import { NextRequest, NextResponse } from 'next/server'

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { question, background, prior, timeHorizon } = body

    if (!question) {
      return NextResponse.json(
        { error: 'Question is required' },
        { status: 400 }
      )
    }

    console.log('🔮 Calling Python forecasting API:', { question, background, prior, timeHorizon })

    // Call the Python FastAPI server to start forecast generation
    const response = await fetch(`${PYTHON_API_URL}/api/forecast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        background: background || "",
        prior_probability: prior,
        time_horizon: timeHorizon || "1 year"
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      console.error('Python API error:', errorData)
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()
    console.log('✅ Forecast generation started:', data.session_id)
    
    // Return immediate response with session ID for polling
    const transformedResponse = {
      question,
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
    console.error('Forecast API error:', error)
    return NextResponse.json(
      { error: `Failed to generate forecast: ${error.message}` },
      { status: 500 }
    )
  }
}