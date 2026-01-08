import { useEffect, useState } from 'react'
import { portfolioApi } from '../api/portfolio'
import './PortfolioCreatePage.css'

export function PortfolioCreatePage() {
  const [name, setName] = useState('')
  const [telegramId, setTelegramId] = useState(() => localStorage.getItem('telegram_id') ?? '')
  const [loading, setLoading] = useState(false)
  const [loadingPortfolio, setLoadingPortfolio] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [portfolio, setPortfolio] = useState<{ name: string; investments: Array<{ id: number; symbol: string; amount: string; buy_price: string }> } | null>(null)
  const [stats, setStats] = useState<{ total_invested: string; current_value: string; pnl_abs: string; pnl_pct: string } | null>(null)
  const [holdingSymbol, setHoldingSymbol] = useState('')
  const [holdingAmount, setHoldingAmount] = useState('')
  const [holdingBuyPrice, setHoldingBuyPrice] = useState('')
  const [holdingDate, setHoldingDate] = useState('')
  const [holdingLoading, setHoldingLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    const devTelegramId = import.meta.env.DEV ? (import.meta.env.VITE_DEV_TELEGRAM_ID as string | undefined) : undefined
    if (!telegramId.trim() && devTelegramId) {
      localStorage.setItem('telegram_id', devTelegramId)
      setTelegramId(devTelegramId)
    }
    if (!telegramId.trim() && !devTelegramId) {
      return
    }
    localStorage.setItem('telegram_id', telegramId.trim())
    loadPortfolio()
  }, [telegramId])

  const loadPortfolio = async () => {
    try {
      setLoadingPortfolio(true)
      setError(null)
      const [portfolioData, statsData] = await Promise.all([
        portfolioApi.getPortfolio(),
        portfolioApi.getStats(),
      ])
      setPortfolio({
        name: portfolioData.name,
        investments: portfolioData.investments.map((inv) => ({
          id: inv.id,
          symbol: inv.symbol,
          amount: inv.amount,
          buy_price: inv.buy_price,
        })),
      })
      setName('')
      setStats({
        total_invested: statsData.total_invested,
        current_value: statsData.current_value,
        pnl_abs: statsData.pnl_abs,
        pnl_pct: statsData.pnl_pct,
      })
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ??
        err?.message ??
        'Failed to load portfolio.'
      setError(message)
    } finally {
      setLoadingPortfolio(false)
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    if (!name.trim()) {
      setError('Portfolio name is required.')
      return
    }

    if (!telegramId.trim()) {
      setError('Telegram ID is required. Set it once in localStorage or via VITE_DEV_TELEGRAM_ID.')
      return
    }

    localStorage.setItem('telegram_id', telegramId.trim())

    try {
      setLoading(true)
      if (portfolio) {
        const result = await portfolioApi.renamePortfolio(portfolio.name, name.trim())
        setSuccess(`Portfolio renamed to "${result.name}".`)
      } else {
        const result = await portfolioApi.createPortfolio(name.trim())
        setSuccess(`Portfolio "${result.name}" ${result.status}.`)
      }
      await loadPortfolio()
      setShowCreateModal(false)
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ??
        err?.message ??
        'Failed to create portfolio.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddHolding = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    if (!telegramId.trim()) {
      setError('Telegram ID is required. Set it once in localStorage or via VITE_DEV_TELEGRAM_ID.')
      return
    }

    if (!holdingSymbol.trim() || !holdingAmount.trim() || !holdingBuyPrice.trim()) {
      setError('Symbol, amount, and buy price are required.')
      return
    }

    localStorage.setItem('telegram_id', telegramId.trim())

    try {
      setHoldingLoading(true)
      await portfolioApi.addInvestment({
        symbol: holdingSymbol.trim().toUpperCase(),
        amount: holdingAmount.trim(),
        buy_price: holdingBuyPrice.trim(),
        bought_at: holdingDate ? new Date(holdingDate).toISOString() : null,
      })
      setSuccess('Holding added.')
      setHoldingSymbol('')
      setHoldingAmount('')
      setHoldingBuyPrice('')
      setHoldingDate('')
      await loadPortfolio()
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ??
        err?.message ??
        'Failed to add holding.'
      setError(message)
    } finally {
      setHoldingLoading(false)
    }
  }

  const formatMoney = (value: string) => {
    const numberValue = Number(value)
    if (Number.isNaN(numberValue)) {
      return value
    }
    return numberValue.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  return (
    <div className="portfolio-create-page">
      <header className="portfolio-header">
        <h1>Create Portfolio</h1>
        <p>Save your holdings and track P&L in one place.</p>
      </header>

      <section className="portfolio-overview">
        <div className="overview-header">
          <div className="overview-title">
            <h2>Existing Portfolio</h2>
            <div className="portfolio-switcher">
              {portfolio ? (
                <button type="button" className="switcher-pill active">
                  {portfolio.name}
                </button>
              ) : (
                <span className="switcher-placeholder">No portfolio</span>
              )}
            </div>
          </div>
          <div className="overview-actions">
            <button
              type="button"
              className="outline-btn"
              onClick={() => setShowCreateModal(true)}
            >
              {portfolio ? 'Rename portfolio' : 'Create portfolio'}
            </button>
            <button
              type="button"
              className="outline-btn"
              onClick={loadPortfolio}
              disabled={loadingPortfolio}
            >
              {loadingPortfolio ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>

        {loadingPortfolio && <div className="overview-loading">Loading portfolio...</div>}
        {!loadingPortfolio && portfolio && stats && (
          <>
            <div className="overview-card">
              <div>
                <span className="overview-label">Name</span>
                <span className="overview-value">{portfolio.name}</span>
              </div>
              <div>
                <span className="overview-label">Investments</span>
                <span className="overview-value">{portfolio.investments.length}</span>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stats-card">
                <span className="overview-label">Total invested</span>
                <span className="overview-value">${formatMoney(stats.total_invested)}</span>
              </div>
              <div className="stats-card">
                <span className="overview-label">Current value</span>
                <span className="overview-value">${formatMoney(stats.current_value)}</span>
              </div>
              <div className="stats-card">
                <span className="overview-label">P&L</span>
                <span className="overview-value">${formatMoney(stats.pnl_abs)}</span>
                <span className={`pnl-pill ${Number(stats.pnl_pct) >= 0 ? 'positive' : 'negative'}`}>
                  {Number(stats.pnl_pct) >= 0 ? '+' : ''}
                  {formatMoney(stats.pnl_pct)}%
                </span>
              </div>
            </div>

            <div className="investments">
              <h3>Holdings</h3>
              {portfolio.investments.length === 0 ? (
                <div className="overview-empty">No investments yet.</div>
              ) : (
                <div className="investments-list">
                  {portfolio.investments.map((investment) => (
                    <div key={investment.id} className="investment-row">
                      <div>
                        <span className="overview-label">Symbol</span>
                        <span className="overview-value">{investment.symbol}</span>
                      </div>
                      <div>
                        <span className="overview-label">Amount</span>
                        <span className="overview-value">{investment.amount}</span>
                      </div>
                      <div>
                        <span className="overview-label">Buy price</span>
                        <span className="overview-value">${formatMoney(investment.buy_price)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
        {!loadingPortfolio && !portfolio && (
          <div className="overview-empty">No portfolio found. Create one below.</div>
        )}
      </section>

      <section className="portfolio-actions">
        <div className="action-card">
          <h2>Add holding</h2>
          <form className="portfolio-form compact" onSubmit={handleAddHolding}>
            <label className="form-label">
              Symbol
              <input
                type="text"
                className="form-input"
                placeholder="BTC"
                value={holdingSymbol}
                onChange={(event) => setHoldingSymbol(event.target.value)}
              />
            </label>

            <label className="form-label">
              Amount
              <input
                type="number"
                step="any"
                min="0"
                className="form-input"
                placeholder="0.1"
                value={holdingAmount}
                onChange={(event) => setHoldingAmount(event.target.value)}
              />
            </label>

            <label className="form-label">
              Buy price (USD)
              <input
                type="number"
                step="any"
                min="0"
                className="form-input"
                placeholder="30000"
                value={holdingBuyPrice}
                onChange={(event) => setHoldingBuyPrice(event.target.value)}
              />
            </label>

            <label className="form-label">
              Bought at
              <input
                type="date"
                className="form-input"
                value={holdingDate}
                onChange={(event) => setHoldingDate(event.target.value)}
              />
            </label>

            <button className="submit-btn" type="submit" disabled={holdingLoading}>
              {holdingLoading ? 'Adding...' : 'Add holding'}
            </button>
          </form>
        </div>
      </section>

      {showCreateModal && (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-card">
            <div className="modal-header">
              <h2>Create portfolio</h2>
              <button
                type="button"
                className="modal-close"
                onClick={() => setShowCreateModal(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            <form className="portfolio-form compact" onSubmit={handleSubmit}>
              <label className="form-label">
                Portfolio name
                <input
                  type="text"
                  className="form-input"
                  placeholder={portfolio ? 'New portfolio name' : 'My Portfolio'}
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                />
              </label>

              {error && <div className="form-error">{error}</div>}
              {success && <div className="form-success">{success}</div>}

              <button className="submit-btn" type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create portfolio'}
              </button>
            </form>
          </div>
        </div>
      )}

    </div>
  )
}
