import { useState, useEffect } from 'react'
import { CurrencyCard } from '../components/CurrencyCard'
import { currenciesApi } from '../api/currencies'
import type { CurrencyPrice } from '../types/currency'
import './HomePage.css'

export function HomePage() {
  const [allCurrencies, setAllCurrencies] = useState<CurrencyPrice[]>([])
  const [filteredCurrencies, setFilteredCurrencies] = useState<CurrencyPrice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [favorites, setFavorites] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadCurrencies()
    loadFavorites()
  }, [])

  useEffect(() => {
    filterCurrencies()
  }, [searchQuery, allCurrencies])

  const loadCurrencies = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await currenciesApi.getCurrencies(250)
      setAllCurrencies(data)
    } catch (err) {
      setError('Failed to load currencies. Please try again later.')
      console.error('Error loading currencies:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadFavorites = () => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('favorites')
      if (stored) {
        try {
          const favList = JSON.parse(stored) as string[]
          setFavorites(new Set(favList))
        } catch {
          // Ignore parse errors
        }
      }
    }
  }

  const filterCurrencies = () => {
    if (!searchQuery.trim()) {
      setFilteredCurrencies(allCurrencies)
      return
    }

    const query = searchQuery.toLowerCase().trim()
    const filtered = allCurrencies.filter(
      (currency) =>
        currency.symbol.toLowerCase() === query ||
        currency.symbol.toLowerCase().startsWith(query) ||
        currency.name.toLowerCase().includes(query)
    )
    setFilteredCurrencies(filtered)
  }

  const handleAddToFavorites = (symbol: string) => {
    const newFavorites = new Set(favorites)
    if (newFavorites.has(symbol)) {
      newFavorites.delete(symbol)
    } else {
      newFavorites.add(symbol)
    }
    setFavorites(newFavorites)
    if (typeof window !== 'undefined') {
      localStorage.setItem('favorites', JSON.stringify(Array.from(newFavorites)))
    }
  }

  if (loading) {
    return (
      <div className="home-page">
        <div className="loading">Loading currencies...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="home-page">
        <div className="error">{error}</div>
        <button onClick={loadCurrencies} className="retry-btn">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="home-page">
      <header className="page-header">
        <h1>Crypto Tracker</h1>
        <p className="subtitle">Track your favorite cryptocurrencies</p>
      </header>

      <div className="search-container">
        <input
          type="text"
          placeholder="Search by symbol or name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        <div className="search-stats">
          Showing {filteredCurrencies.length} of {allCurrencies.length} currencies
        </div>
      </div>

      <div className="currencies-grid">
        {filteredCurrencies.length === 0 ? (
          <div className="no-results">No currencies found</div>
        ) : (
          filteredCurrencies.map((currency, index) => (
            <CurrencyCard
              key={`${currency.symbol}-${index}`}
              currency={currency}
              onAddToFavorites={handleAddToFavorites}
              isFavorite={favorites.has(currency.symbol)}
            />
          ))
        )}
      </div>
    </div>
  )
}

