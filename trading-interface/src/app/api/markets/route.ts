import { NextRequest, NextResponse } from 'next/server'

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const limit = searchParams.get('limit') || '50'
    
    console.log('📊 Fetching markets from Python API')

    // Call the Python FastAPI server
    const response = await fetch(`${PYTHON_API_URL}/api/markets`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      console.warn('Python API not available, using mock data')
      // Fallback to mock data if Python API is not available
      const mockMarkets = [
        {
          id: 'market1',
          question: 'Will Bitcoin exceed $100k by end of 2024?',
          probability: 0.65,
          volume: 1250,
          uniqueBettorCount: 23,
          closeTime: Date.now() + 30 * 24 * 60 * 60 * 1000,
          isResolved: false,
          outcomeType: 'BINARY'
        },
        {
          id: 'market2', 
          question: 'Will AI achieve AGI by 2030?',
          probability: 0.35,
          volume: 890,
          uniqueBettorCount: 18,
          closeTime: Date.now() + 180 * 24 * 60 * 60 * 1000,
          isResolved: false,
          outcomeType: 'BINARY'
        },
        {
          id: 'market3',
          question: 'Will there be a recession in 2024?',
          probability: 0.25,
          volume: 2100,
          uniqueBettorCount: 45,
          closeTime: Date.now() + 60 * 24 * 60 * 60 * 1000,
          isResolved: false,
          outcomeType: 'BINARY'
        },
        {
          id: 'market4',
          question: 'Will SpaceX land humans on Mars by 2030?',
          probability: 0.15,
          volume: 750,
          uniqueBettorCount: 12,
          closeTime: Date.now() + 200 * 24 * 60 * 60 * 1000,
          isResolved: false,
          outcomeType: 'BINARY'
        },
        {
          id: 'market5',
          question: 'Will the US election be decided by less than 1% margin?',
          probability: 0.42,
          volume: 3200,
          uniqueBettorCount: 67,
          closeTime: Date.now() + 90 * 24 * 60 * 60 * 1000,
          isResolved: false,
          outcomeType: 'BINARY'
        }
      ]
      return NextResponse.json(mockMarkets.slice(0, parseInt(limit)))
    }

    const data = await response.json()
    console.log('✅ Markets fetched from Python API:', data.length)

    // Transform Python response to match frontend expectations
    const transformedMarkets = data.map((market: any) => ({
      id: market.id,
      question: market.question,
      probability: market.probability,
      volume: market.volume,
      uniqueBettorCount: market.bettors,
      closeTime: Date.now() + 30 * 24 * 60 * 60 * 1000, // Default 30 days
      isResolved: false,
      outcomeType: 'BINARY'
    }))

    return NextResponse.json(transformedMarkets.slice(0, parseInt(limit)))
  } catch (error) {
    console.error('Markets API error:', error)
    // Fallback to mock data on error
    const mockMarkets = [
      {
        id: 'market1',
        question: 'Will Bitcoin exceed $100k by end of 2024?',
        probability: 0.65,
        volume: 1250,
        uniqueBettorCount: 23,
        closeTime: Date.now() + 30 * 24 * 60 * 60 * 1000,
        isResolved: false,
        outcomeType: 'BINARY'
      }
    ]
    return NextResponse.json(mockMarkets.slice(0, parseInt(limit)))
  }
}