import { apiClient } from './client'

export interface PortfolioManipulations {
  id: number
  user_id: number
  name: string
  status: 'created' | 'edited'
}

export interface Investment {
  id: number
  symbol: string
  amount: string
  buy_price: string
  bought_at: string | null
}

export interface PortfolioRead {
  id: number
  user_id: number
  name: string
  investments: Investment[]
}

export interface PortfolioStats {
  total_invested: string
  current_value: string
  pnl_abs: string
  pnl_pct: string
}

export interface InvestmentCreatePayload {
  symbol: string
  amount: string
  buy_price: string
  bought_at?: string | null
}

export interface PortfolioCreatePayload {
  name: string
  flag: boolean
  new_name?: string | null
}

export const portfolioApi = {
  createPortfolio: async (name: string): Promise<PortfolioManipulations> => {
    const payload: PortfolioCreatePayload = {
      name,
      flag: true,
      new_name: null,
    }
    const response = await apiClient.post<PortfolioManipulations>('/portfolio', payload)
    return response.data
  },
  renamePortfolio: async (currentName: string, newName: string): Promise<PortfolioManipulations> => {
    const payload: PortfolioCreatePayload = {
      name: currentName,
      flag: false,
      new_name: newName,
    }
    const response = await apiClient.post<PortfolioManipulations>('/portfolio', payload)
    return response.data
  },
  getPortfolio: async (): Promise<PortfolioRead> => {
    const response = await apiClient.get<PortfolioRead>('/portfolio')
    return response.data
  },
  getStats: async (): Promise<PortfolioStats> => {
    const response = await apiClient.get<PortfolioStats>('/portfolio/stats')
    return response.data
  },
  addInvestment: async (payload: InvestmentCreatePayload): Promise<Investment> => {
    const response = await apiClient.post<Investment>('/portfolio/investments', payload)
    return response.data
  },
}
