import { apiClient } from './client'
import type { CurrencyListResponse, CurrencyPrice } from '../types/currency'

export const currenciesApi = {
  getCurrencies: async (limit: number = 50): Promise<CurrencyPrice[]> => {
    const response = await apiClient.get<CurrencyListResponse>('/currencies', {
      params: { limit },
    })
    return response.data.currencies
  },
}

