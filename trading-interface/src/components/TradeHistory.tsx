'use client'

import { useState, useEffect } from 'react'
import { TradingAPI } from '@/lib/trading-api'

interface Trade {
  id: string
  marketId: string
  question: string
  action: string
  outcome: string
  amount: number
  entryPrice: number
  exitPrice?: number
  profit?: number
  confidence: number
  strategyType: string
  reasoning: string
  riskAssessment: string
  entryTime: string
  exitTime?: string
  resolved: boolean
}

interface TradeHistoryProps {
  sessionId: string
  api: TradingAPI
}

export function TradeHistory({ sessionId, api }: TradeHistoryProps) {
  const [trades, setTrades] = useState<Trade[]>([])
  const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadTrades()
  }, [sessionId])

  const loadTrades = async () => {
    try {
      setIsLoading(true)
      const tradesData = await api.getSessionTrades(sessionId)
      setTrades(tradesData)
    } catch (error) {
      console.error('Failed to load trades:', error)
      // Generate mock data for demo
      setTrades(generateMockTrades())
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockTrades = (): Trade[] => {
    const mockTrades = [
      {
        id: '1',
        marketId: 'market1',
        question: 'Will Bitcoin exceed $100k by end of 2024?',
        action: 'BUY_NO',
        outcome: 'NO',
        amount: 250,
        entryPrice: 0.65,
        exitPrice: 0.45,
        profit: 125.5,
        confidence: 0.78,
        strategyType: 'mean_reversion',
        reasoning: 'Market appears overoptimistic about crypto rally. Technical indicators suggest resistance at current levels.',
        riskAssessment: 'Medium risk - crypto volatility could cause rapid price movements',
        entryTime: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        exitTime: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        resolved: true
      },
      {
        id: '2',
        marketId: 'market2',
        question: 'Will AI achieve AGI by 2030?',
        action: 'BUY_YES',
        outcome: 'YES',
        amount: 180,
        entryPrice: 0.35,
        profit: undefined,
        confidence: 0.65,
        strategyType: 'sentiment',
        reasoning: 'Recent AI breakthroughs and increased investment suggest faster progress than market expects.',
        riskAssessment: 'High uncertainty - AGI timeline highly speculative',
        entryTime: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        resolved: false
      },
      {
        id: '3',
        marketId: 'market3',
        question: 'Will there be a recession in 2024?',
        action: 'BUY_YES',
        outcome: 'YES',
        amount: 120,
        entryPrice: 0.25,
        exitPrice: 0.15,
        profit: -48.0,
        confidence: 0.55,
        strategyType: 'arbitrage',
        reasoning: 'Economic indicators suggest downturn risk, but market pricing seems disconnected.',
        riskAssessment: 'Low confidence - economic predictions highly uncertain',
        entryTime: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        exitTime: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        resolved: true
      }
    ]
    return mockTrades
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'BUY_YES':
        return 'text-green-600 bg-green-100'
      case 'BUY_NO':
        return 'text-red-600 bg-red-100'
      case 'SELL':
        return 'text-blue-600 bg-blue-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStrategyIcon = (strategy: string) => {
    switch (strategy) {
      case 'arbitrage':
        return '⚖️'
      case 'sentiment':
        return '📰'
      case 'momentum':
        return '📈'
      case 'mean_reversion':
        return '🔄'
      case 'kelly_optimal':
        return '🎯'
      default:
        return '🤖'
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  if (trades.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="text-4xl mb-2">📊</div>
        <p>No trades in this session yet</p>
        <p className="text-sm">Trades will appear here as the AI makes decisions</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Trade List */}
      <div className="space-y-3">
        {trades.map((trade) => (
          <div
            key={trade.id}
            onClick={() => setSelectedTrade(trade)}
            className={`p-4 border rounded-lg cursor-pointer transition-colors ${
              selectedTrade?.id === trade.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getActionColor(trade.action)}`}>
                    {trade.action}
                  </span>
                  <span className="text-xs text-gray-500">
                    {getStrategyIcon(trade.strategyType)} {trade.strategyType.replace('_', ' ')}
                  </span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    trade.resolved ? 'bg-gray-100 text-gray-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {trade.resolved ? 'Resolved' : 'Active'}
                  </span>
                </div>
                
                <div className="text-sm font-medium text-gray-900 mb-2 line-clamp-2">
                  {trade.question}
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Amount:</span>
                    <span className="ml-1 font-medium">{trade.amount.toFixed(0)} mana</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Entry:</span>
                    <span className="ml-1 font-medium">{(trade.entryPrice * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Confidence:</span>
                    <span className="ml-1 font-medium">{(trade.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Time:</span>
                    <span className="ml-1 font-medium">
                      {new Date(trade.entryTime).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="text-right ml-4">
                {trade.profit !== undefined && (
                  <div className={`text-lg font-semibold ${
                    trade.profit >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {trade.profit >= 0 ? '+' : ''}{trade.profit.toFixed(1)}
                  </div>
                )}
                {trade.exitPrice && (
                  <div className="text-xs text-gray-500">
                    Exit: {(trade.exitPrice * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Trade Details Modal */}
      {selectedTrade && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Trade Details</h3>
                <button
                  onClick={() => setSelectedTrade(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                {/* Trade Summary */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-900 mb-2">
                    {selectedTrade.question}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs text-gray-500">Action</div>
                      <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getActionColor(selectedTrade.action)}`}>
                        {selectedTrade.action} {selectedTrade.outcome}
                      </span>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Strategy</div>
                      <div className="font-medium">
                        {getStrategyIcon(selectedTrade.strategyType)} {selectedTrade.strategyType.replace('_', ' ')}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Financial Details */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white border rounded-lg p-3">
                    <div className="text-xs text-gray-500">Amount Invested</div>
                    <div className="text-lg font-semibold">{selectedTrade.amount.toFixed(0)} mana</div>
                  </div>
                  <div className="bg-white border rounded-lg p-3">
                    <div className="text-xs text-gray-500">Entry Price</div>
                    <div className="text-lg font-semibold">{(selectedTrade.entryPrice * 100).toFixed(1)}%</div>
                  </div>
                  {selectedTrade.exitPrice && (
                    <>
                      <div className="bg-white border rounded-lg p-3">
                        <div className="text-xs text-gray-500">Exit Price</div>
                        <div className="text-lg font-semibold">{(selectedTrade.exitPrice * 100).toFixed(1)}%</div>
                      </div>
                      <div className="bg-white border rounded-lg p-3">
                        <div className="text-xs text-gray-500">Profit/Loss</div>
                        <div className={`text-lg font-semibold ${
                          (selectedTrade.profit || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {(selectedTrade.profit || 0) >= 0 ? '+' : ''}{(selectedTrade.profit || 0).toFixed(1)} mana
                        </div>
                      </div>
                    </>
                  )}
                </div>

                {/* AI Reasoning */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">🤖 AI Reasoning</h4>
                  <p className="text-sm text-blue-800">{selectedTrade.reasoning}</p>
                </div>

                {/* Risk Assessment */}
                <div className="bg-yellow-50 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-900 mb-2">⚠️ Risk Assessment</h4>
                  <p className="text-sm text-yellow-800">{selectedTrade.riskAssessment}</p>
                </div>

                {/* Timeline */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">📅 Timeline</h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-500">Entry:</span>
                      <span className="ml-2">{new Date(selectedTrade.entryTime).toLocaleString()}</span>
                    </div>
                    {selectedTrade.exitTime && (
                      <div>
                        <span className="text-gray-500">Exit:</span>
                        <span className="ml-2">{new Date(selectedTrade.exitTime).toLocaleString()}</span>
                      </div>
                    )}
                    <div>
                      <span className="text-gray-500">Status:</span>
                      <span className={`ml-2 font-medium ${
                        selectedTrade.resolved ? 'text-gray-600' : 'text-yellow-600'
                      }`}>
                        {selectedTrade.resolved ? 'Resolved' : 'Active'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}