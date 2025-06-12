/**
 * Trading API integration for Manifold Markets
 */

export interface MarketData {
  id: string
  question: string
  probability: number
  volume: number
  uniqueBettorCount: number
  closeTime?: number
  isResolved: boolean
  outcomeType: string
}

export interface TradingDecision {
  marketId: string
  action: string
  outcome: string
  amount: number
  confidence: number
  strategyType: string
  reasoning: string
  riskAssessment: string
  expectedReturn: number
  timeSensitivity: string
  marketConditions: any
  supportingEvidence: string[]
  contrarianFactors: string[]
}

export interface TradingSession {
  sessionId: string
  mode: 'backtest' | 'live'
  startTime: Date
  endTime?: Date
  initialBalance: number
  currentBalance: number
  totalTrades: number
  winningTrades: number
  totalProfit: number
  maxDrawdown: number
  sharpeRatio: number
  kellyUtilization: number
  marketsAnalyzed: number
  newsProcessed: number
}

export interface ForecastRequest {
  question: string
  background?: string
  prior?: number
  timeHorizon?: string
}

export interface ForecastResult {
  question: string
  probability: number
  confidence: string
  reasoning: string
  baseRate: number
  evidenceQuality: number
  strategies: string[]
  newsSourcesCount: number
  totalArticles: number
  searchTimeframe: {
    start: string
    end: string
  }
}

export class TradingAPI {
  private baseUrl: string
  private apiKey: string

  constructor(apiKey: string, baseUrl = '/api') {
    this.apiKey = apiKey
    this.baseUrl = baseUrl
  }

  async getMarkets(limit = 50): Promise<MarketData[]> {
    const response = await fetch(`${this.baseUrl}/markets?limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch markets: ${response.statusText}`)
    }
    
    return response.json()
  }

  async analyzeMarket(marketId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/analyze/${marketId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to analyze market: ${response.statusText}`)
    }
    
    return response.json()
  }

  async makeTradingDecision(marketId: string): Promise<TradingDecision> {
    const response = await fetch(`${this.baseUrl}/trade/${marketId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to make trading decision: ${response.statusText}`)
    }
    
    return response.json()
  }

  async startTradingSession(mode: 'backtest' | 'live', config: any): Promise<TradingSession> {
    const response = await fetch(`${this.baseUrl}/session/start`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ mode, config })
    })
    
    if (!response.ok) {
      throw new Error(`Failed to start trading session: ${response.statusText}`)
    }
    
    return response.json()
  }

  async getTradingSessions(): Promise<TradingSession[]> {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch trading sessions: ${response.statusText}`)
    }
    
    return response.json()
  }

  async getSessionTrades(sessionId: string): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/session/${sessionId}/trades`, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch session trades: ${response.statusText}`)
    }
    
    return response.json()
  }

  async getSessionAnalyses(sessionId: string): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/session/${sessionId}/analyses`, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch session analyses: ${response.statusText}`)
    }
    
    return response.json()
  }

  async runBacktest(config: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/backtest`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    
    if (!response.ok) {
      throw new Error(`Failed to run backtest: ${response.statusText}`)
    }
    
    return response.json()
  }

  async generateForecast(request: ForecastRequest): Promise<ForecastResult> {
    const response = await fetch(`${this.baseUrl}/forecast`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    })
    
    if (!response.ok) {
      throw new Error(`Failed to generate forecast: ${response.statusText}`)
    }
    
    return response.json()
  }
}