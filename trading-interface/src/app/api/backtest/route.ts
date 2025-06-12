import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Simulate backtest processing time
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Mock backtest results
    const mockResults = {
      sessionId: `backtest_${Date.now()}`,
      startDate: body.startDate,
      endDate: body.endDate,
      initialBalance: body.initialBalance,
      finalBalance: body.initialBalance * 1.187,
      totalProfit: body.initialBalance * 0.187,
      totalRoi: 18.7,
      totalTrades: 14,
      winningTrades: 10,
      losingTrades: 4,
      winRate: 71.4,
      sharpeRatio: 1.52,
      maxDrawdown: 7.8,
      kellyUtilization: 23.4,
      marketsAnalyzed: 52,
      avgTradeSize: body.initialBalance * 0.15,
      largestWin: body.initialBalance * 0.089,
      largestLoss: body.initialBalance * -0.034,
      avgProfitPerTrade: body.initialBalance * 0.0134,
      dailyReturns: [2.3, -1.1, 3.8, 0.9, -0.7, 2.9, 1.6],
      performanceMetrics: {
        volatility: 11.8,
        informationRatio: 1.48,
        calmarRatio: 2.39,
        sortinoRatio: 1.94
      },
      trades: [
        {
          marketId: 'market1',
          question: 'Will Bitcoin exceed $100k by end of 2024?',
          action: 'BUY_NO',
          amount: body.initialBalance * 0.18,
          profit: body.initialBalance * 0.067,
          strategy: 'mean_reversion'
        },
        {
          marketId: 'market2',
          question: 'Will AI achieve AGI by 2030?',
          action: 'BUY_YES',
          amount: body.initialBalance * 0.12,
          profit: body.initialBalance * 0.045,
          strategy: 'sentiment'
        }
      ]
    }

    return NextResponse.json(mockResults)
  } catch (error) {
    console.error('Error running backtest:', error)
    return NextResponse.json({ error: 'Failed to run backtest' }, { status: 500 })
  }
}