'use client'

import { useState, useEffect } from 'react'
import { TradingAPI } from '@/lib/trading-api'

interface AgentActivity {
  timestamp: string
  type: 'market_analysis' | 'trade_execution' | 'market_selection' | 'risk_assessment'
  marketId?: string
  marketQuestion?: string
  action?: string
  reasoning?: string
  confidence?: number
  edge?: number
  positionSize?: number
  status: 'success' | 'error' | 'pending'
  details: any
}

interface AgentStatus {
  isActive: boolean
  currentBalance: number
  totalTrades: number
  winRate: number
  lastActivity: string
  marketsAnalyzed: number
  averageConfidence: number
  totalProfit: number
}

interface AgentMonitorProps {
  api: TradingAPI
}

export function AgentMonitor({ api }: AgentMonitorProps) {
  const [activities, setActivities] = useState<AgentActivity[]>([])
  const [status, setStatus] = useState<AgentStatus>({
    isActive: false,
    currentBalance: 1000,
    totalTrades: 0,
    winRate: 0,
    lastActivity: 'Never',
    marketsAnalyzed: 0,
    averageConfidence: 0,
    totalProfit: 0
  })
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [selectedActivity, setSelectedActivity] = useState<AgentActivity | null>(null)

  useEffect(() => {
    if (isMonitoring) {
      const interval = setInterval(() => {
        fetchAgentStatus()
        fetchRecentActivities()
      }, 5000) // Update every 5 seconds

      return () => clearInterval(interval)
    }
  }, [isMonitoring])

  const fetchAgentStatus = async () => {
    try {
      // Mock agent status - in production this would call the backend
      const mockStatus: AgentStatus = {
        isActive: isMonitoring,
        currentBalance: 1000 + Math.random() * 200 - 100,
        totalTrades: Math.floor(Math.random() * 50),
        winRate: 0.6 + Math.random() * 0.3,
        lastActivity: new Date().toLocaleTimeString(),
        marketsAnalyzed: Math.floor(Math.random() * 100) + 50,
        averageConfidence: 0.7 + Math.random() * 0.2,
        totalProfit: Math.random() * 100 - 50
      }
      setStatus(mockStatus)
    } catch (error) {
      console.error('Failed to fetch agent status:', error)
    }
  }

  const fetchRecentActivities = async () => {
    try {
      // Mock activities - in production this would call the backend
      const activityTypes: AgentActivity['type'][] = [
        'market_analysis', 'trade_execution', 'market_selection', 'risk_assessment'
      ]
      
      const newActivity: AgentActivity = {
        timestamp: new Date().toISOString(),
        type: activityTypes[Math.floor(Math.random() * activityTypes.length)],
        marketId: `market_${Math.random().toString(36).substr(2, 9)}`,
        marketQuestion: `Will ${['Bitcoin', 'Tesla', 'Apple', 'Google'][Math.floor(Math.random() * 4)]} ${['increase', 'decrease'][Math.floor(Math.random() * 2)]} by ${Math.floor(Math.random() * 50) + 10}% this year?`,
        action: ['BUY_YES', 'BUY_NO', 'HOLD'][Math.floor(Math.random() * 3)],
        reasoning: 'AI analysis indicates strong edge based on recent news sentiment and technical indicators.',
        confidence: 0.6 + Math.random() * 0.3,
        edge: Math.random() * 0.2,
        positionSize: Math.floor(Math.random() * 100) + 10,
        status: ['success', 'error', 'pending'][Math.floor(Math.random() * 3)] as any,
        details: {
          aiProbability: 0.3 + Math.random() * 0.4,
          marketProbability: 0.3 + Math.random() * 0.4,
          kellyFraction: Math.random() * 0.2,
          expectedValue: Math.random() * 50 - 25
        }
      }

      setActivities(prev => [newActivity, ...prev.slice(0, 49)]) // Keep last 50 activities
    } catch (error) {
      console.error('Failed to fetch activities:', error)
    }
  }

  const startMonitoring = () => {
    setIsMonitoring(true)
    fetchAgentStatus()
    fetchRecentActivities()
  }

  const stopMonitoring = () => {
    setIsMonitoring(false)
  }

  const getActivityIcon = (type: AgentActivity['type']) => {
    switch (type) {
      case 'market_analysis': return '🔍'
      case 'trade_execution': return '💰'
      case 'market_selection': return '🎯'
      case 'risk_assessment': return '⚖️'
      default: return '📊'
    }
  }

  const getStatusColor = (status: AgentActivity['status']) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-50'
      case 'error': return 'text-red-600 bg-red-50'
      case 'pending': return 'text-yellow-600 bg-yellow-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="space-y-6">
      {/* Agent Status Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            🤖 Manifold Market Agent Monitor
          </h2>
          <div className="flex space-x-2">
            {!isMonitoring ? (
              <button
                onClick={startMonitoring}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Start Monitoring
              </button>
            ) : (
              <button
                onClick={stopMonitoring}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                Stop Monitoring
              </button>
            )}
          </div>
        </div>

        {/* Status Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${status.isActive ? 'bg-green-500' : 'bg-gray-400'}`}></div>
              <span className="text-sm font-medium text-gray-700">Status</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {status.isActive ? 'Active' : 'Inactive'}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <span className="text-sm font-medium text-gray-700">Balance</span>
            <p className="text-lg font-semibold text-gray-900">
              ${status.currentBalance.toFixed(2)}
            </p>
            <p className={`text-sm ${status.totalProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {status.totalProfit >= 0 ? '+' : ''}${status.totalProfit.toFixed(2)}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <span className="text-sm font-medium text-gray-700">Win Rate</span>
            <p className="text-lg font-semibold text-gray-900">
              {(status.winRate * 100).toFixed(1)}%
            </p>
            <p className="text-sm text-gray-500">
              {status.totalTrades} trades
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <span className="text-sm font-medium text-gray-700">Confidence</span>
            <p className="text-lg font-semibold text-gray-900">
              {(status.averageConfidence * 100).toFixed(0)}%
            </p>
            <p className="text-sm text-gray-500">
              {status.marketsAnalyzed} analyzed
            </p>
          </div>
        </div>

        <div className="text-sm text-gray-500">
          Last activity: {status.lastActivity}
        </div>
      </div>

      {/* Activity Feed */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Real-time Activity Feed</h3>
        </div>
        
        <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
          {activities.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              {isMonitoring ? 'Waiting for agent activity...' : 'Start monitoring to see agent activity'}
            </div>
          ) : (
            activities.map((activity, index) => (
              <div
                key={index}
                className="p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelectedActivity(activity)}
              >
                <div className="flex items-start space-x-3">
                  <div className="text-2xl">{getActivityIcon(activity.type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 capitalize">
                        {activity.type.replace('_', ' ')}
                      </p>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(activity.status)}`}>
                          {activity.status}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(activity.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                    
                    {activity.marketQuestion && (
                      <p className="text-sm text-gray-600 mt-1 truncate">
                        {activity.marketQuestion}
                      </p>
                    )}
                    
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      {activity.action && (
                        <span>Action: <span className="font-medium">{activity.action}</span></span>
                      )}
                      {activity.confidence && (
                        <span>Confidence: <span className="font-medium">{(activity.confidence * 100).toFixed(0)}%</span></span>
                      )}
                      {activity.edge && (
                        <span>Edge: <span className="font-medium">{(activity.edge * 100).toFixed(1)}%</span></span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Activity Detail Modal */}
      {selectedActivity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Activity Details</h3>
                <button
                  onClick={() => setSelectedActivity(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">
                  {getActivityIcon(selectedActivity.type)} {selectedActivity.type.replace('_', ' ').toUpperCase()}
                </h4>
                <p className="text-sm text-gray-600">{selectedActivity.marketQuestion}</p>
              </div>

              {selectedActivity.reasoning && (
                <div>
                  <h5 className="font-medium text-gray-700 mb-1">Reasoning</h5>
                  <p className="text-sm text-gray-600">{selectedActivity.reasoning}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                {selectedActivity.confidence && (
                  <div>
                    <h5 className="font-medium text-gray-700 mb-1">Confidence</h5>
                    <p className="text-sm text-gray-900">{(selectedActivity.confidence * 100).toFixed(1)}%</p>
                  </div>
                )}
                
                {selectedActivity.edge && (
                  <div>
                    <h5 className="font-medium text-gray-700 mb-1">Edge</h5>
                    <p className="text-sm text-gray-900">{(selectedActivity.edge * 100).toFixed(2)}%</p>
                  </div>
                )}
                
                {selectedActivity.positionSize && (
                  <div>
                    <h5 className="font-medium text-gray-700 mb-1">Position Size</h5>
                    <p className="text-sm text-gray-900">${selectedActivity.positionSize}</p>
                  </div>
                )}
                
                {selectedActivity.details?.expectedValue && (
                  <div>
                    <h5 className="font-medium text-gray-700 mb-1">Expected Value</h5>
                    <p className={`text-sm ${selectedActivity.details.expectedValue >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${selectedActivity.details.expectedValue.toFixed(2)}
                    </p>
                  </div>
                )}
              </div>

              <div className="text-xs text-gray-500 border-t pt-4">
                <p>Timestamp: {new Date(selectedActivity.timestamp).toLocaleString()}</p>
                <p>Market ID: {selectedActivity.marketId}</p>
                <p>Status: {selectedActivity.status}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}