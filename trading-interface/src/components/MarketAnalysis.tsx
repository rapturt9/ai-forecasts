'use client'

import { useState, useEffect } from 'react'
import { MarketData, TradingAPI, TradingDecision } from '@/lib/trading-api'

interface MarketAnalysisProps {
  markets: MarketData[]
  api: TradingAPI
}

export function MarketAnalysis({ markets, api }: MarketAnalysisProps) {
  const [selectedMarket, setSelectedMarket] = useState<MarketData | null>(null)
  const [analysis, setAnalysis] = useState<any>(null)
  const [decision, setDecision] = useState<TradingDecision | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const analyzeMarket = async (market: MarketData) => {
    try {
      setIsAnalyzing(true)
      setSelectedMarket(market)
      
      // Get comprehensive analysis
      const analysisResult = await api.analyzeMarket(market.id)
      setAnalysis(analysisResult)
      
      // Get trading decision
      const tradingDecision = await api.makeTradingDecision(market.id)
      setDecision(tradingDecision)
      
    } catch (error) {
      console.error('Failed to analyze market:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'BUY_YES':
        return 'text-green-600 bg-green-100'
      case 'BUY_NO':
        return 'text-red-600 bg-red-100'
      case 'HOLD':
        return 'text-gray-600 bg-gray-100'
      default:
        return 'text-blue-600 bg-blue-100'
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

  return (
    <div className="space-y-6">
      {/* Market Selection */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Select Market to Analyze</h3>
        <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
          {markets.slice(0, 8).map((market) => (
            <button
              key={market.id}
              onClick={() => analyzeMarket(market)}
              disabled={isAnalyzing}
              className={`p-3 text-left border rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors ${
                selectedMarket?.id === market.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
              }`}
            >
              <div className="text-sm font-medium text-gray-900 line-clamp-2">
                {market.question}
              </div>
              <div className="mt-1 flex justify-between text-xs text-gray-500">
                <span>Prob: {(market.probability * 100).toFixed(1)}%</span>
                <span>Vol: {market.volume.toFixed(0)}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Analysis Results */}
      {isAnalyzing && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Analyzing market...</p>
        </div>
      )}

      {selectedMarket && decision && !isAnalyzing && (
        <div className="space-y-4">
          {/* Trading Decision Summary */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-semibold text-gray-900">Trading Decision</h3>
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${getActionColor(decision.action)}`}>
                {decision.action}
              </span>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <div className="text-xs text-gray-500">Outcome</div>
                <div className="font-semibold">{decision.outcome}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Amount</div>
                <div className="font-semibold">{decision.amount.toFixed(0)} mana</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Confidence</div>
                <div className="font-semibold">{(decision.confidence * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Expected Return</div>
                <div className={`font-semibold ${decision.expectedReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {decision.expectedReturn.toFixed(1)} mana
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2 mb-3">
              <span>{getStrategyIcon(decision.strategyType)}</span>
              <span className="text-sm font-medium capitalize">{decision.strategyType.replace('_', ' ')}</span>
              <span className={`px-2 py-1 text-xs rounded-full ${
                decision.timeSensitivity === 'high' ? 'bg-red-100 text-red-800' :
                decision.timeSensitivity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {decision.timeSensitivity} urgency
              </span>
            </div>
          </div>

          {/* Detailed Reasoning */}
          <div className="bg-white border rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">AI Reasoning</h4>
            <p className="text-sm text-gray-700 mb-4">{decision.reasoning}</p>
            
            {decision.supportingEvidence.length > 0 && (
              <div className="mb-4">
                <h5 className="text-sm font-medium text-green-800 mb-2">✅ Supporting Evidence</h5>
                <ul className="space-y-1">
                  {decision.supportingEvidence.map((evidence, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      {evidence}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {decision.contrarianFactors.length > 0 && (
              <div>
                <h5 className="text-sm font-medium text-red-800 mb-2">⚠️ Risk Factors</h5>
                <ul className="space-y-1">
                  {decision.contrarianFactors.map((factor, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Market Conditions */}
          {decision.marketConditions && (
            <div className="bg-white border rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3">Market Conditions</h4>
              <div className="grid grid-cols-3 gap-4">
                {decision.marketConditions.liquidity && (
                  <div>
                    <div className="text-xs text-gray-500">Liquidity</div>
                    <div className="font-medium">
                      {(decision.marketConditions.liquidity.overall_liquidity * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
                {decision.marketConditions.volatility !== undefined && (
                  <div>
                    <div className="text-xs text-gray-500">Volatility</div>
                    <div className="font-medium">
                      {(decision.marketConditions.volatility * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
                {decision.marketConditions.sentiment !== undefined && (
                  <div>
                    <div className="text-xs text-gray-500">Sentiment</div>
                    <div className={`font-medium ${
                      decision.marketConditions.sentiment > 0 ? 'text-green-600' : 
                      decision.marketConditions.sentiment < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {decision.marketConditions.sentiment > 0 ? 'Positive' : 
                       decision.marketConditions.sentiment < 0 ? 'Negative' : 'Neutral'}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Risk Assessment */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-semibold text-yellow-800 mb-2">🛡️ Risk Assessment</h4>
            <p className="text-sm text-yellow-700">{decision.riskAssessment}</p>
          </div>
        </div>
      )}

      {!selectedMarket && !isAnalyzing && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">🔍</div>
          <p>Select a market above to see AI analysis</p>
          <p className="text-sm">Get detailed reasoning and trading recommendations</p>
        </div>
      )}
    </div>
  )
}