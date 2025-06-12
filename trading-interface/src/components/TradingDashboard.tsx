'use client'

import { useState, useEffect } from 'react'
import { TradingAPI, TradingSession, MarketData } from '@/lib/trading-api'
import { SessionList } from './SessionList'
import { MarketAnalysis } from './MarketAnalysis'
import { PerformanceChart } from './PerformanceChart'
import { TradeHistory } from './TradeHistory'
import { BacktestRunner } from './BacktestRunner'
import { ForecastingInterface } from './ForecastingInterface'
import { AgentMonitor } from './AgentMonitor'

interface TradingDashboardProps {
  api: TradingAPI
}

export function TradingDashboard({ api }: TradingDashboardProps) {
  const [activeTab, setActiveTab] = useState<'forecast' | 'live' | 'backtest' | 'history' | 'monitor'>('forecast')
  const [sessions, setSessions] = useState<TradingSession[]>([])
  const [selectedSession, setSelectedSession] = useState<TradingSession | null>(null)
  const [markets, setMarkets] = useState<MarketData[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadSessions()
    loadMarkets()
  }, [])

  const loadSessions = async () => {
    try {
      setIsLoading(true)
      const sessionsData = await api.getTradingSessions()
      setSessions(sessionsData)
      if (sessionsData.length > 0) {
        setSelectedSession(sessionsData[0])
      }
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadMarkets = async () => {
    try {
      const marketsData = await api.getMarkets(20)
      setMarkets(marketsData)
    } catch (error) {
      console.error('Failed to load markets:', error)
    }
  }

  const startNewSession = async (mode: 'live' | 'backtest') => {
    try {
      setIsLoading(true)
      const config = {
        initialBalance: 1000,
        maxKellyFraction: 0.25,
        minEdge: 0.05,
        riskTolerance: 'moderate'
      }
      
      const newSession = await api.startTradingSession(mode, config)
      setSessions(prev => [newSession, ...prev])
      setSelectedSession(newSession)
    } catch (error) {
      console.error('Failed to start session:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'forecast', name: 'AI Forecasting', icon: '🔮' },
            { id: 'live', name: 'Live Trading', icon: '🔴' },
            { id: 'backtest', name: 'Backtesting', icon: '📊' },
            { id: 'history', name: 'Trade History', icon: '📈' },
            { id: 'monitor', name: 'Agent Monitor', icon: '🤖' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Sessions & Controls */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Trading Sessions</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => startNewSession('live')}
                  disabled={isLoading}
                  className="px-3 py-1 text-xs font-medium text-white bg-green-600 rounded hover:bg-green-700 disabled:opacity-50"
                >
                  Start Live
                </button>
                <button
                  onClick={() => startNewSession('backtest')}
                  disabled={isLoading}
                  className="px-3 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  Backtest
                </button>
              </div>
            </div>
            <SessionList
              sessions={sessions}
              selectedSession={selectedSession}
              onSelectSession={setSelectedSession}
              isLoading={isLoading}
            />
          </div>

          {/* Current Markets */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Markets</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {markets.slice(0, 10).map((market) => (
                <div key={market.id} className="border rounded-lg p-3 hover:bg-gray-50">
                  <div className="text-sm font-medium text-gray-900 line-clamp-2">
                    {market.question}
                  </div>
                  <div className="mt-2 flex justify-between text-xs text-gray-500">
                    <span>Prob: {(market.probability * 100).toFixed(1)}%</span>
                    <span>Vol: {market.volume.toFixed(0)}</span>
                    <span>Bettors: {market.uniqueBettorCount}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {activeTab === 'forecast' && (
            <ForecastingInterface api={api} />
          )}

          {activeTab === 'live' && (
            <>
              {selectedSession && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Session Performance
                  </h2>
                  <PerformanceChart session={selectedSession} api={api} />
                </div>
              )}
              
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Market Analysis
                </h2>
                <MarketAnalysis markets={markets} api={api} />
              </div>
            </>
          )}

          {activeTab === 'backtest' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Backtest Configuration
              </h2>
              <BacktestRunner api={api} onComplete={loadSessions} />
            </div>
          )}

          {activeTab === 'history' && selectedSession && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Trade History - {selectedSession.sessionId}
              </h2>
              <TradeHistory sessionId={selectedSession.sessionId} api={api} />
            </div>
          )}

          {activeTab === 'monitor' && (
            <AgentMonitor api={api} />
          )}
        </div>
      </div>
    </div>
  )
}