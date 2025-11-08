export interface CurrencyPrice {
  symbol: string
  name: string
  price_usd: number
  price_change_24h?: number
  market_cap?: number
  volume_24h?: number
}

export interface CurrencyListResponse {
  currencies: CurrencyPrice[]
}

