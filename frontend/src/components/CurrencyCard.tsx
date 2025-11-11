import { CurrencyPrice } from '../types/currency'
import './CurrencyCard.css'

interface CurrencyCardProps {
  currency: CurrencyPrice
  onAddToFavorites?: (symbol: string) => void
  isFavorite?: boolean
}

export function CurrencyCard({ currency, onAddToFavorites, isFavorite }: CurrencyCardProps) {
  const priceChangeClass = currency.price_change_percentage_24h
    ? currency.price_change_percentage_24h >= 0
      ? 'positive'
      : 'negative'
    : 'neutral'

  const safePrice = currency.price ?? 0
  const safeMarketCap = currency.market_cap_usd ?? 0
  const safeVolume = currency.total_volume ?? 0

  return (
    <div className="currency-card">
      <div className="currency-header">
        <div>
          <h3 className="currency-symbol">{currency.symbol}</h3>
          <p className="currency-name">{currency.name}</p>
        </div>
        {onAddToFavorites && (
          <button
            className={`favorite-btn ${isFavorite ? 'active' : ''}`}
            onClick={() => onAddToFavorites(currency.symbol)}
            aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            {isFavorite ? '★' : '☆'}
          </button>
        )}
      </div>
      <div className="currency-price">
        <span className="price">${safePrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        {currency.price_change_percentage_24h !== undefined && currency.price_change_percentage_24h !== null && (
          <span className={`price-change ${priceChangeClass}`}>
            {currency.price_change_percentage_24h >= 0 ? '+' : ''}
            {(currency.price_change_percentage_24h ?? 0).toFixed(2)}%
          </span>
        )}
      </div>
      <div className="currency-stats">
        {safeMarketCap > 0 && (
          <div className="stat">
            <span className="stat-label">Market Cap:</span>
            <span className="stat-value">
              ${(safeMarketCap / 1e9).toFixed(2)}B
            </span>
          </div>
        )}
        {safeVolume > 0 && (
          <div className="stat">
            <span className="stat-label">24h Volume:</span>
            <span className="stat-value">
              ${(safeVolume / 1e9).toFixed(2)}B
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

