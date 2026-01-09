import { apiClient } from './client'
import type { CurrencyListResponse, CurrencyPrice } from '../types/currency'

export interface CurrencyDetailResponse {
  currency: CurrencyPrice
}

export interface CurrencyHistoryPoint {
  timestamp: string
  price: number
}

export interface CurrencyHistoryResponse {
  symbol: string
  history: CurrencyHistoryPoint[]
}

export const currenciesApi = {
  getCurrencies: async (limit: number = 250): Promise<CurrencyPrice[]> => {
    const response = await apiClient.get<CurrencyListResponse>('/currencies', {
      params: { limit },
    })
    return response.data.currencies
  },
  getCurrency: async (symbol: string): Promise<CurrencyPrice> => {
    const response = await apiClient.get<CurrencyDetailResponse>(`/currencies/${symbol}`)
    return response.data.currency
  },
  getCurrencyHistory: async (symbol: string, days: number): Promise<CurrencyHistoryPoint[]> => {
    const response = await apiClient.get<CurrencyHistoryResponse>(`/currencies/${symbol}/history`, {
      params: { days },
    })
    return response.data.history
  },
}
