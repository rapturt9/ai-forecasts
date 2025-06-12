'use client'

import { TradingSession } from '@/lib/trading-api'

interface SessionListProps {
  sessions: TradingSession[]
  selectedSession: TradingSession | null
  onSelectSession: (session: TradingSession) => void
  isLoading: boolean
}

export function SessionList({ sessions, selectedSession, onSelectSession, isLoading }: SessionListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  if (sessions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="text-4xl mb-2">📊</div>
        <p>No trading sessions yet</p>
        <p className="text-sm">Start a new session to begin trading</p>
      </div>
    )
  }

  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {sessions.map((session) => (
        <div
          key={session.sessionId}
          onClick={() => onSelectSession(session)}
          className={`p-3 rounded-lg border cursor-pointer transition-colors ${
            selectedSession?.sessionId === session.sessionId
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
          }`}
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  session.mode === 'live' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {session.mode}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(session.startTime).toLocaleDateString()}
                </span>
              </div>
              
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-500">Balance:</span>
                  <span className="ml-1 font-medium">
                    {session.currentBalance.toFixed(0)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">P&L:</span>
                  <span className={`ml-1 font-medium ${
                    session.totalProfit >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {session.totalProfit >= 0 ? '+' : ''}{session.totalProfit.toFixed(1)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Trades:</span>
                  <span className="ml-1 font-medium">{session.totalTrades}</span>
                </div>
                <div>
                  <span className="text-gray-500">Win Rate:</span>
                  <span className="ml-1 font-medium">
                    {session.totalTrades > 0 
                      ? ((session.winningTrades / session.totalTrades) * 100).toFixed(0)
                      : 0}%
                  </span>
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <div className={`text-sm font-semibold ${
                session.totalProfit >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {((session.totalProfit / session.initialBalance) * 100).toFixed(1)}%
              </div>
              {session.sharpeRatio > 0 && (
                <div className="text-xs text-gray-500">
                  Sharpe: {session.sharpeRatio.toFixed(2)}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}