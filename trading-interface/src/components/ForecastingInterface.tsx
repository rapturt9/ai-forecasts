'use client'

import { useState } from 'react'
import { TradingAPI, ForecastRequest, ForecastResult } from '@/lib/trading-api'

interface ForecastingInterfaceProps {
  api: TradingAPI
}

export function ForecastingInterface({ api }: ForecastingInterfaceProps) {
  const [request, setRequest] = useState<ForecastRequest>({
    question: '',
    background: '',
    prior: undefined,
    timeHorizon: '1 year'
  })
  const [result, setResult] = useState<ForecastResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!request.question.trim()) {
      setError('Please enter a question')
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const forecast = await api.generateForecast(request)
      setResult(forecast)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate forecast')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setRequest({
      question: '',
      background: '',
      prior: undefined,
      timeHorizon: '1 year'
    })
    setResult(null)
    setError(null)
  }

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          🔮 AI Forecasting System
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Question to Forecast *
            </label>
            <textarea
              id="question"
              value={request.question}
              onChange={(e) => setRequest(prev => ({ ...prev, question: e.target.value }))}
              placeholder="e.g., Will the S&P 500 reach 6000 by the end of 2025?"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              rows={3}
              required
            />
          </div>

          <div>
            <label htmlFor="background" className="block text-sm font-medium text-gray-700 mb-2">
              Background Information (Optional)
            </label>
            <textarea
              id="background"
              value={request.background}
              onChange={(e) => setRequest(prev => ({ ...prev, background: e.target.value }))}
              placeholder="Provide any relevant context or background information..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              rows={2}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="prior" className="block text-sm font-medium text-gray-700 mb-2">
                Prior Probability (Optional)
              </label>
              <input
                id="prior"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={request.prior || ''}
                onChange={(e) => setRequest(prev => ({ 
                  ...prev, 
                  prior: e.target.value ? parseFloat(e.target.value) : undefined 
                }))}
                placeholder="0.5"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Enter a value between 0 and 1</p>
            </div>

            <div>
              <label htmlFor="timeHorizon" className="block text-sm font-medium text-gray-700 mb-2">
                Time Horizon
              </label>
              <select
                id="timeHorizon"
                value={request.timeHorizon}
                onChange={(e) => setRequest(prev => ({ ...prev, timeHorizon: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="1 month">1 Month</option>
                <option value="3 months">3 Months</option>
                <option value="6 months">6 Months</option>
                <option value="1 year">1 Year</option>
                <option value="2 years">2 Years</option>
                <option value="5 years">5 Years</option>
              </select>
            </div>
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={isLoading || !request.question.trim()}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating Forecast...
                </div>
              ) : (
                'Generate Forecast'
              )}
            </button>
            
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Reset
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Forecast Results</h3>
          
          <div className="space-y-6">
            {/* Main Prediction */}
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Probability Forecast</h4>
                <span className="text-sm text-gray-500">Confidence: {result.confidence}</span>
              </div>
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {(result.probability * 100).toFixed(1)}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${result.probability * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h5 className="font-medium text-gray-700 mb-1">Base Rate</h5>
                <p className="text-2xl font-semibold text-gray-900">
                  {(result.baseRate * 100).toFixed(1)}%
                </p>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <h5 className="font-medium text-gray-700 mb-1">Evidence Quality</h5>
                <p className="text-2xl font-semibold text-gray-900">
                  {(result.evidenceQuality * 100).toFixed(0)}%
                </p>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <h5 className="font-medium text-gray-700 mb-1">News Sources</h5>
                <p className="text-2xl font-semibold text-gray-900">
                  {result.newsSourcesCount}
                </p>
                <p className="text-sm text-gray-500">
                  {result.totalArticles} articles analyzed
                </p>
              </div>
            </div>

            {/* Reasoning */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Reasoning</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-wrap">{result.reasoning}</p>
              </div>
            </div>

            {/* Strategies */}
            {result.strategies && result.strategies.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Most Likely Strategies for Outcome</h4>
                <div className="space-y-2">
                  {result.strategies.map((strategy, index) => (
                    <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p className="text-green-800">{strategy}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Search Timeframe */}
            <div className="text-sm text-gray-500 border-t pt-4">
              <p>
                Analysis based on information from {result.searchTimeframe.start} to {result.searchTimeframe.end}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}