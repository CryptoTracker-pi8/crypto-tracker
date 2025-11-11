import { useEffect, useState } from 'react'

type Theme = 'light' | 'dark'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    // Инициализация из localStorage на клиенте
    if (typeof window === 'undefined') return 'dark'
    
    const stored = localStorage.getItem('theme')
    if (stored === 'light' || stored === 'dark') {
      return stored
    }
    
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    return isDark ? 'dark' : 'light'
  })

  useEffect(() => {
    // Применить тему к DOM
    if (typeof window === 'undefined') return

    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'))
  }

  return { theme, toggleTheme }
}
