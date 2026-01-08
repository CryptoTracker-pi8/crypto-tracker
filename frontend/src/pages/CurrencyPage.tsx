import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Line as LineChart } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import type { CurrencyPrice } from '../types/currency'
import { currenciesApi } from '../api/currencies'
import './CurrencyPage.css'

// Плагин для кроссхера (пунктирные линии при наведении)
const crosshairPlugin = {
  id: 'crosshair',
  afterDatasetsDraw(chart: any) {
    if (!chart.tooltip?._active || chart.tooltip._active.length === 0) {
      return
    }

    const ctx = chart.ctx
    const activeDataPoint = chart.tooltip._active[0]
    const x = activeDataPoint.element.x
    const topY = chart.scales.y.top
    const bottomY = chart.scales.y.bottom

    // Вертикальная пунктирная линия
    ctx.save()
    ctx.strokeStyle = 'rgba(74, 222, 128, 0.4)'
    ctx.lineWidth = 2
    ctx.setLineDash([5, 5])
    ctx.beginPath()
    ctx.moveTo(x, topY)
    ctx.lineTo(x, bottomY)
    ctx.stroke()
    ctx.restore()

    // Горизонтальная пунктирная линия
    ctx.save()
    ctx.strokeStyle = 'rgba(74, 222, 128, 0.4)'
    ctx.lineWidth = 2
    ctx.setLineDash([5, 5])
    ctx.beginPath()
    ctx.moveTo(chart.scales.x.left, activeDataPoint.element.y)
    ctx.lineTo(chart.scales.x.right, activeDataPoint.element.y)
    ctx.stroke()
    ctx.restore()
  },
}

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler, crosshairPlugin as any)

export function CurrencyPage() {
  const { symbol } = useParams<{ symbol: string }>()
  const navigate = useNavigate()
  const [currency, setCurrency] = useState<CurrencyPrice | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [days, setDays] = useState(7)
  const [history, setHistory] = useState<Array<{ timestamp: string; price: number }>>([])
  const [isDark, setIsDark] = useState(true)
  const [chartLoading, setChartLoading] = useState(false)

  // Определяем тему при загрузке и отслеживаем изменения
  useEffect(() => {
    if (typeof window === 'undefined') return

    const updateTheme = () => {
      const stored = localStorage.getItem('theme')
      const theme = stored === 'light' || stored === 'dark' ? stored : 'dark'
      setIsDark(theme === 'dark')
    }

    updateTheme()

    // Слушаем изменения в localStorage
    const handleStorageChange = () => {
      updateTheme()
    }

    window.addEventListener('storage', handleStorageChange)

    // Также слушаем пользовательские события (если используется пользовательское событие)
    const handleThemeChange = () => {
      updateTheme()
    }

    window.addEventListener('themeChange', handleThemeChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('themeChange', handleThemeChange)
    }
  }, [])

  useEffect(() => {
    if (!symbol) return
    loadCurrency()
  }, [symbol])

  useEffect(() => {
    if (!symbol) return
    loadHistory()
  }, [symbol, days])

  const loadCurrency = async () => {
    try {
      setLoading(true)
      setError(null)
      const currencyDetails = await currenciesApi.getCurrency(symbol)
      setCurrency(currencyDetails)
    } catch (err) {
      setError('Failed to load currency details')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = async () => {
    try {
      setChartLoading(true)
      const historyData = await currenciesApi.getCurrencyHistory(symbol, days)

      // Форматируем даты, показывая каждую уникальную дату
      const formattedHistory = historyData.map((point) => ({
        timestamp: new Date(point.timestamp).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        }),
        price: point.price,
      }))

      setHistory(formattedHistory)
    } catch (err) {
      console.error('Failed to load history:', err)
    } finally {
      setChartLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="currency-page">
        <div className="loading">Loading currency details...</div>
      </div>
    )
  }

  if (error || !currency) {
    return (
      <div className="currency-page">
        <button onClick={() => navigate('/')} className="back-btn">
          <ArrowLeft size={20} /> Back to currencies
        </button>
        <div className="error">{error || 'Currency not found'}</div>
      </div>
    )
  }

  const priceChangeClass = currency.price_change_percentage_24h
    ? currency.price_change_percentage_24h >= 0
      ? 'positive'
      : 'negative'
    : 'neutral'

  return (
    <div className="currency-page">
      <button onClick={() => navigate('/')} className="back-btn">
        <ArrowLeft size={20} /> Back
      </button>

      <div className="currency-details">
        <div className="currency-header">
          <div>
            <h1>{currency.name}</h1>
            <p className="symbol">{currency.symbol}</p>
          </div>
        </div>

        <div className="price-section">
          <div className="price-display">
            <span className="price">
              ${currency.price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </span>
            {currency.price_change_percentage_24h !== undefined && (
              <span className={`price-change ${priceChangeClass}`}>
                {currency.price_change_percentage_24h >= 0 ? '+' : ''}
                {currency.price_change_percentage_24h.toFixed(2)}% 24h
              </span>
            )}
          </div>
        </div>

        <div className="stats-section">
          {currency.market_cap_usd && (
            <div className="stat-item">
              <span className="label">Market Cap</span>
              <span className="value">
                ${(currency.market_cap_usd / 1e9).toFixed(2)}B
              </span>
            </div>
          )}
          {currency.total_volume && (
            <div className="stat-item">
              <span className="label">24h Volume</span>
              <span className="value">
                ${(currency.total_volume / 1e9).toFixed(2)}B
              </span>
            </div>
          )}
        </div>

        <div className="history-section">
          <div className="history-header">
            <h2>Price History</h2>
            <div className="days-selector">
              {[7, 30, 90].map((d) => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  className={`day-btn ${days === d ? 'active' : ''}`}
                >
                  {d}d
                </button>
              ))}
            </div>
          </div>

          {history.length > 0 ? (
            <div className="chart-container">
              {chartLoading && <div className="chart-loading">Loading...</div>}
              <LineChart
                data={{
                  labels: history.map((h) => h.timestamp),
                  datasets: [
                    {
                      label: `${currency.symbol} Price (USD)`,
                      data: history.map((h) => h.price),
                      borderColor: '#4ade80',
                      backgroundColor: 'rgba(74, 222, 128, 0.08)',
                      borderWidth: 3,
                      fill: true,
                      pointRadius: 0,
                      pointHoverRadius: 6,
                      pointBackgroundColor: '#4ade80',
                      pointBorderColor: '#fff',
                      pointBorderWidth: 2,
                      tension: 0.3,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  animation: {
                    duration: 0,
                  },
                  interaction: {
                    mode: 'index',
                    intersect: false,
                  },
                  plugins: {
                    legend: {
                      display: false,
                    },
                    tooltip: {
                      enabled: true,
                      backgroundColor: 'rgba(0, 0, 0, 0.85)',
                      padding: 14,
                      titleColor: '#fff',
                      bodyColor: '#4ade80',
                      borderColor: '#4ade80',
                      borderWidth: 1.5,
                      titleFont: {
                        size: 13,
                        weight: 'bold',
                      },
                      bodyFont: {
                        size: 14,
                        weight: 'normal',
                      },
                      displayColors: false,
                      callbacks: {
                        title: (context) => {
                          return context[0]?.label ?? ''
                        },
                        label: (context) => {
                          const price = context.parsed?.y ?? 0
                          return `$${price.toLocaleString('en-US', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}`
                        },
                      },
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: false,
                      grid: {
                        color: 'rgba(74, 222, 128, 0.2)',
                        lineWidth: 1,
                      },
                      ticks: {
                        color: isDark ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.8)',
                        font: {
                          size: 12,
                        },
                        padding: 10,
                        callback: (value) => {
                          if (typeof value === 'number') {
                            return `$${(value / 1000).toFixed(0)}k`
                          }
                          return value
                        },
                      },
                    },
                    x: {
                      grid: {
                        display: true,
                        color: isDark ? 'rgba(74, 222, 128, 0.1)' : 'rgba(74, 222, 128, 0.15)',
                        lineWidth: 1,
                      },
                      ticks: {
                        color: isDark ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.8)',
                        font: {
                          size: 11,
                        },
                        maxRotation: 45,
                        minRotation: 0,
                        maxTicksLimit: 10,
                      },
                    },
                  },
                }}
              />
            </div>
          ) : (
            <div className="no-data">No history data available</div>
          )}
        </div>
      </div>
    </div>
  )
}
