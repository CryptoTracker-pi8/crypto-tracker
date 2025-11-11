import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { HomePage } from './pages/HomePage'
import { CurrencyPage } from './pages/CurrencyPage'
import { useTheme } from './hooks/useTheme'
import { Moon, Sun } from 'lucide-react'
import './App.css'

function App() {
  const { theme, toggleTheme } = useTheme()

  return (
    <BrowserRouter>
      <div className="app">
        <nav className="app-nav">
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
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App

