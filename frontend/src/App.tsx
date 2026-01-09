import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { HomePage } from './pages/HomePage'
import { CurrencyPage } from './pages/CurrencyPage'
import { PortfolioCreatePage } from './pages/PortfolioCreatePage'
import { useTheme } from './hooks/useTheme'
import { Moon, Sun } from 'lucide-react'
import './App.css'

function App() {
  const { theme, toggleTheme } = useTheme()

  return (
    <BrowserRouter>
      <div className="app">
        <nav className="app-nav">
          <div className="nav-links">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/portfolio" className="nav-link">Portfolio</Link>
          </div>
          <button onClick={toggleTheme} className="theme-toggle" title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>
            {theme === 'light' ? (
              <Moon size={20} strokeWidth={2} />
            ) : (
              <Sun size={20} strokeWidth={2} />
            )}
          </button>
        </nav>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/currency/:symbol" element={<CurrencyPage />} />
          <Route path="/portfolio" element={<PortfolioCreatePage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
