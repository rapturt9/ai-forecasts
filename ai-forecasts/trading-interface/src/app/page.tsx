'use client'

import { useState, useEffect } from 'react'
import { TradingDashboard } from '@/components/TradingDashboard'
import { TradingAPI } from '@/lib/trading-api'

export default function Home() {
  const [tradingAPI, setTradingAPI] = useState<TradingAPI | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Initialize trading API
    const apiKey = process.env.NEXT_PUBLIC_MANIFOLD_API_KEY || 'demo-key'
    const api = new TradingAPI(apiKey)
    setTradingAPI(api)
    setIsLoading(false)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading Trading Interface...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🤖 AI Forecasting Trading System
              </h1>
              <span className="ml-3 px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                Enhanced Kelly Criterion
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Status: <span className="text-green-600 font-medium">Active</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {tradingAPI && <TradingDashboard api={tradingAPI} />}
      </main>
    </div>
  )
}
