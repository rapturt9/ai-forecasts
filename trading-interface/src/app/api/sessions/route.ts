import { NextRequest, NextResponse } from 'next/server'

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  try {
    console.log('📊 Fetching trading sessions from Python API')

    // Call the Python FastAPI server
    const response = await fetch(`${PYTHON_API_URL}/api/trading/sessions`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      console.warn('Python API not available, using mock data')
      // Fallback to mock data if Python API is not available
      const mockSessions = [
        {
          sessionId: 'session_live_001',
          mode: 'live' as const,
          startTime: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
          endTime: undefined,
          initialBalance: 1000,
          currentBalance: 1187.5,
          totalTrades: 8,
          winningTrades: 6,
          totalProfit: 187.5,
          maxDrawdown: 5.2,
          sharpeRatio: 1.34,
          kellyUtilization: 0.22,
          marketsAnalyzed: 23,
          newsProcessed: 156
        },
        {
          sessionId: 'session_backtest_001',
          mode: 'backtest' as const,
          startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
          endTime: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000),
          initialBalance: 1000,
          currentBalance: 1245.8,
          totalTrades: 15,
          winningTrades: 11,
          totalProfit: 245.8,
          maxDrawdown: 8.1,
          sharpeRatio: 1.67,
          kellyUtilization: 0.28,
          marketsAnalyzed: 67,
          newsProcessed: 234
        },
        {
          sessionId: 'session_backtest_002',
          mode: 'backtest' as const,
          startTime: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
          endTime: new Date(Date.now() - 13 * 24 * 60 * 60 * 1000),
          initialBalance: 1000,
          currentBalance: 892.3,
          totalTrades: 12,
          winningTrades: 5,
          totalProfit: -107.7,
          maxDrawdown: 15.4,
          sharpeRatio: -0.23,
          kellyUtilization: 0.31,
          marketsAnalyzed: 45,
          newsProcessed: 189
        }
      ]
      return NextResponse.json(mockSessions)
    }

    const data = await response.json()
    console.log('✅ Sessions fetched from Python API:', data.length)

    // Transform Python response to match frontend expectations
    const transformedSessions = data.map((session: any) => ({
      sessionId: session.session_id,
      mode: session.status === 'running' ? 'live' : 'backtest',
      startTime: new Date(),
      endTime: session.status === 'completed' ? new Date() : undefined,
      initialBalance: session.balance - session.profit_loss,
      currentBalance: session.balance,
      totalTrades: session.total_trades,
      winningTrades: Math.round(session.total_trades * session.win_rate / 100),
      totalProfit: session.profit_loss,
      maxDrawdown: session.max_drawdown,
      sharpeRatio: session.sharpe_ratio,
      kellyUtilization: 0.25, // Default value
      marketsAnalyzed: session.markets_analyzed,
      newsProcessed: session.markets_analyzed * 5 // Estimate
    }))

    return NextResponse.json(transformedSessions)
  } catch (error) {
    console.error('Sessions API error:', error)
    // Fallback to mock data on error
    const mockSessions = [
      {
        sessionId: 'session_live_001',
        mode: 'live' as const,
        startTime: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        endTime: undefined,
        initialBalance: 1000,
        currentBalance: 1187.5,
        totalTrades: 8,
        winningTrades: 6,
        totalProfit: 187.5,
        maxDrawdown: 5.2,
        sharpeRatio: 1.34,
        kellyUtilization: 0.22,
        marketsAnalyzed: 23,
        newsProcessed: 156
      }
    ]
    return NextResponse.json(mockSessions)
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { mode, config } = body

    // Create a new mock session
    const newSession = {
      sessionId: `session_${mode}_${Date.now()}`,
      mode,
      startTime: new Date(),
      endTime: undefined,
      initialBalance: config.initialBalance || 1000,
      currentBalance: config.initialBalance || 1000,
      totalTrades: 0,
      winningTrades: 0,
      totalProfit: 0,
      maxDrawdown: 0,
      sharpeRatio: 0,
      kellyUtilization: 0,
      marketsAnalyzed: 0,
      newsProcessed: 0
    }

    return NextResponse.json(newSession)
  } catch (error) {
    console.error('Error creating session:', error)
    return NextResponse.json({ error: 'Failed to create session' }, { status: 500 })
  }
}