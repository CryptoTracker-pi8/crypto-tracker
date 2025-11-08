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
        <span className="price">${currency.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        {currency.price_change_percentage_24h !== undefined && (
          <span className={`price-change ${priceChangeClass}`}>
            {currency.price_change_percentage_24h >= 0 ? '+' : ''}
            {currency.price_change_percentage_24h.toFixed(2)}%
          </span>
        )}
      </div>
      <div className="currency-stats">
        {currency.market_cap_usd && (
          <div className="stat">
            <span className="stat-label">Market Cap:</span>
            <span className="stat-value">
              ${(currency.market_cap_usd / 1e9).toFixed(2)}B
            </span>
          </div>
        )}
        {currency.total_volume && (
          <div className="stat">
            <span className="stat-label">24h Volume:</span>
            <span className="stat-value">
              ${(currency.total_volume / 1e9).toFixed(2)}B
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

