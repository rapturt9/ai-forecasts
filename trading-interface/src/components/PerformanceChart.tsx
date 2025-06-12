'use client'

import { useState, useEffect } from 'react'
import { TradingSession, TradingAPI } from '@/lib/trading-api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

interface PerformanceChartProps {
  session: TradingSession
  api: TradingAPI
}

export function PerformanceChart({ session, api }: PerformanceChartProps) {
  const [performanceData, setPerformanceData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadPerformanceData()
  }, [session.sessionId])

  const loadPerformanceData = async () => {
    try {
      setIsLoading(true)
      
      // Generate mock performance data for demo
      const data = generateMockPerformanceData(session)
      setPerformanceData(data)
      
    } catch (error) {
      console.error('Failed to load performance data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockPerformanceData = (session: TradingSession) => {
    const startTime = new Date(session.startTime)
    const now = new Date()
    const duration = now.getTime() - startTime.getTime()
    const hours = Math.max(1, Math.floor(duration / (1000 * 60 * 60)))
    
    const data = []
    let balance = session.initialBalance
    
    for (let i = 0; i <= Math.min(hours, 24); i++) {
      const time = new Date(startTime.getTime() + i * 60 * 60 * 1000)
      
      // Simulate some volatility
      const change = (Math.random() - 0.5) * 20
      balance = Math.max(0, balance + change)
      
      data.push({
        time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        balance: balance,
        profit: balance - session.initialBalance,
        timestamp: time.getTime()
      })
    }
    
    // Ensure final balance matches session
    if (data.length > 0) {
      data[data.length - 1].balance = session.currentBalance
      data[data.length - 1].profit = session.totalProfit
    }
    
    return data
  }

  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const currentProfit = session.totalProfit
  const currentReturn = ((session.currentBalance - session.initialBalance) / session.initialBalance) * 100

  return (
    <div className="space-y-4">
      {/* Performance Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500">Current Balance</div>
          <div className="text-lg font-semibold">{session.currentBalance.toFixed(0)} mana</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500">Total P&L</div>
          <div className={`text-lg font-semibold ${currentProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {currentProfit >= 0 ? '+' : ''}{currentProfit.toFixed(1)} mana
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500">Return</div>
          <div className={`text-lg font-semibold ${currentReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {currentReturn >= 0 ? '+' : ''}{currentReturn.toFixed(1)}%
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500">Sharpe Ratio</div>
          <div className="text-lg font-semibold">
            {session.sharpeRatio > 0 ? session.sharpeRatio.toFixed(2) : 'N/A'}
          </div>
        </div>
      </div>

      {/* Balance Chart */}
      <div className="h-64">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Portfolio Balance Over Time</h4>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              domain={['dataMin - 50', 'dataMax + 50']}
            />
            <Tooltip 
              formatter={(value: number, name: string) => [
                `${value.toFixed(1)} mana`,
                name === 'balance' ? 'Balance' : 'Profit'
              ]}
              labelFormatter={(label) => `Time: ${label}`}
            />
            <Area
              type="monotone"
              dataKey="balance"
              stroke="#3B82F6"
              fill="#3B82F6"
              fillOpacity={0.1}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <div className="text-gray-500">Total Trades</div>
          <div className="font-semibold">{session.totalTrades}</div>
        </div>
        <div>
          <div className="text-gray-500">Win Rate</div>
          <div className="font-semibold">
            {session.totalTrades > 0 
              ? ((session.winningTrades / session.totalTrades) * 100).toFixed(1)
              : 0}%
          </div>
        </div>
        <div>
          <div className="text-gray-500">Max Drawdown</div>
          <div className="font-semibold text-red-600">
            {session.maxDrawdown > 0 ? `-${session.maxDrawdown.toFixed(1)}%` : 'N/A'}
          </div>
        </div>
        <div>
          <div className="text-gray-500">Kelly Utilization</div>
          <div className="font-semibold">
            {(session.kellyUtilization * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Session Info */}
      <div className="bg-blue-50 rounded-lg p-3">
        <div className="flex justify-between items-center text-sm">
          <div>
            <span className="text-blue-800 font-medium">Session Started:</span>
            <span className="ml-2 text-blue-700">
              {new Date(session.startTime).toLocaleString()}
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <div>
              <span className="text-blue-800">Markets Analyzed:</span>
              <span className="ml-1 font-medium">{session.marketsAnalyzed}</span>
            </div>
            <div>
              <span className="text-blue-800">News Processed:</span>
              <span className="ml-1 font-medium">{session.newsProcessed}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}