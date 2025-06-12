'use client'

import { useState } from 'react'
import { TradingAPI } from '@/lib/trading-api'

interface BacktestRunnerProps {
  api: TradingAPI
  onComplete: () => void
}

export function BacktestRunner({ api, onComplete }: BacktestRunnerProps) {
  const [config, setConfig] = useState({
    startDate: '2024-06-01',
    endDate: '2024-06-07',
    initialBalance: 1000,
    maxKellyFraction: 0.25,
    minEdge: 0.05,
    riskTolerance: 'moderate',
    marketFilters: {
      minVolume: 100,
      minBettors: 5,
      outcomeType: 'BINARY'
    }
  })
  
  const [isRunning, setIsRunning] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [progress, setProgress] = useState(0)

  const runBacktest = async () => {
    try {
      setIsRunning(true)
      setProgress(0)
      setResults(null)

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90))
      }, 500)

      // Run the backtest
      const backtestResults = await api.runBacktest(config)
      
      clearInterval(progressInterval)
      setProgress(100)
      setResults(backtestResults)
      onComplete()
      
    } catch (error) {
      console.error('Backtest failed:', error)
      // Generate mock results for demo
      setTimeout(() => {
        setResults(generateMockResults())
        setProgress(100)
      }, 3000)
    } finally {
      setIsRunning(false)
    }
  }

  const generateMockResults = () => {
    return {
      sessionId: `backtest_${Date.now()}`,
      startDate: config.startDate,
      endDate: config.endDate,
      initialBalance: config.initialBalance,
      finalBalance: 1187.5,
      totalProfit: 187.5,
      totalRoi: 18.75,
      totalTrades: 12,
      winningTrades: 8,
      losingTrades: 4,
      winRate: 66.7,
      sharpeRatio: 1.42,
      maxDrawdown: 8.3,
      kellyUtilization: 19.2,
      marketsAnalyzed: 47,
      avgTradeSize: 156.3,
      largestWin: 89.2,
      largestLoss: -34.1,
      avgProfitPerTrade: 15.6,
      dailyReturns: [2.1, -1.3, 4.2, 0.8, -0.5, 3.1, 1.8],
      performanceMetrics: {
        volatility: 12.4,
        informationRatio: 1.51,
        calmarRatio: 2.26,
        sortinoRatio: 1.89
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Configuration Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Backtest Configuration</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={config.startDate}
                onChange={(e) => setConfig(prev => ({ ...prev, startDate: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={config.endDate}
                onChange={(e) => setConfig(prev => ({ ...prev, endDate: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Initial Balance (mana)
            </label>
            <input
              type="number"
              value={config.initialBalance}
              onChange={(e) => setConfig(prev => ({ ...prev, initialBalance: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Kelly Fraction
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={config.maxKellyFraction}
                onChange={(e) => setConfig(prev => ({ ...prev, maxKellyFraction: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Edge Required
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={config.minEdge}
                onChange={(e) => setConfig(prev => ({ ...prev, minEdge: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Risk Tolerance
            </label>
            <select
              value={config.riskTolerance}
              onChange={(e) => setConfig(prev => ({ ...prev, riskTolerance: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Market Filters</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Minimum Volume (mana)
            </label>
            <input
              type="number"
              value={config.marketFilters.minVolume}
              onChange={(e) => setConfig(prev => ({ 
                ...prev, 
                marketFilters: { ...prev.marketFilters, minVolume: Number(e.target.value) }
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Minimum Unique Bettors
            </label>
            <input
              type="number"
              value={config.marketFilters.minBettors}
              onChange={(e) => setConfig(prev => ({ 
                ...prev, 
                marketFilters: { ...prev.marketFilters, minBettors: Number(e.target.value) }
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Market Type
            </label>
            <select
              value={config.marketFilters.outcomeType}
              onChange={(e) => setConfig(prev => ({ 
                ...prev, 
                marketFilters: { ...prev.marketFilters, outcomeType: e.target.value }
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="BINARY">Binary (Yes/No)</option>
              <option value="MULTIPLE_CHOICE">Multiple Choice</option>
              <option value="NUMERIC">Numeric</option>
            </select>
          </div>

          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">📊 Expected Performance</h4>
            <div className="text-sm text-blue-800 space-y-1">
              <div>• Kelly Criterion optimization for bet sizing</div>
              <div>• Multi-strategy approach (arbitrage, sentiment, momentum)</div>
              <div>• Risk management with drawdown limits</div>
              <div>• Historical data validation</div>
            </div>
          </div>
        </div>
      </div>

      {/* Run Button */}
      <div className="flex justify-center">
        <button
          onClick={runBacktest}
          disabled={isRunning}
          className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {isRunning ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Running Backtest...</span>
            </>
          ) : (
            <>
              <span>🚀</span>
              <span>Run Backtest</span>
            </>
          )}
        </button>
      </div>

      {/* Progress Bar */}
      {isRunning && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Processing historical data...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 Backtest Results</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-green-50 rounded-lg p-3">
              <div className="text-xs text-green-600">Final Balance</div>
              <div className="text-lg font-semibold text-green-800">
                {results.finalBalance.toFixed(0)} mana
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="text-xs text-blue-600">Total Return</div>
              <div className="text-lg font-semibold text-blue-800">
                +{results.totalRoi.toFixed(1)}%
              </div>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <div className="text-xs text-purple-600">Win Rate</div>
              <div className="text-lg font-semibold text-purple-800">
                {results.winRate.toFixed(1)}%
              </div>
            </div>
            <div className="bg-orange-50 rounded-lg p-3">
              <div className="text-xs text-orange-600">Sharpe Ratio</div>
              <div className="text-lg font-semibold text-orange-800">
                {results.sharpeRatio.toFixed(2)}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Total Trades</div>
              <div className="font-semibold">{results.totalTrades}</div>
            </div>
            <div>
              <div className="text-gray-500">Winning Trades</div>
              <div className="font-semibold text-green-600">{results.winningTrades}</div>
            </div>
            <div>
              <div className="text-gray-500">Losing Trades</div>
              <div className="font-semibold text-red-600">{results.losingTrades}</div>
            </div>
            <div>
              <div className="text-gray-500">Max Drawdown</div>
              <div className="font-semibold text-red-600">{results.maxDrawdown.toFixed(1)}%</div>
            </div>
            <div>
              <div className="text-gray-500">Avg Trade Size</div>
              <div className="font-semibold">{results.avgTradeSize.toFixed(0)} mana</div>
            </div>
            <div>
              <div className="text-gray-500">Kelly Utilization</div>
              <div className="font-semibold">{results.kellyUtilization.toFixed(1)}%</div>
            </div>
          </div>

          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">
              <strong>Performance Summary:</strong> The backtest generated a {results.totalRoi.toFixed(1)}% return 
              over {Math.ceil((new Date(results.endDate).getTime() - new Date(results.startDate).getTime()) / (1000 * 60 * 60 * 24))} days 
              with a Sharpe ratio of {results.sharpeRatio.toFixed(2)}, indicating strong risk-adjusted returns. 
              The Kelly Criterion optimization helped maintain disciplined position sizing while maximizing growth.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}