export interface CurrencyPrice {
  symbol: string
  name: string
  price: number
  price_change_percentage_24h?: number
  market_cap_usd?: number
  total_volume?: number
}

export interface CurrencyListResponse {
  currencies: CurrencyPrice[]
}

