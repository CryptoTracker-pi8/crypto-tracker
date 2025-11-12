import axios from 'axios'

const API_BASE_URL = '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for Telegram ID (will be set from auth context)
apiClient.interceptors.request.use((config) => {
  const telegramId = localStorage.getItem('telegram_id')
  if (telegramId) {
    config.headers['X-Telegram-ID'] = telegramId
  }
  return config
})

