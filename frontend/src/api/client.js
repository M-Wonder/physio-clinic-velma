/**
 * Axios API client
 * Uses relative /api path — Vite dev server proxies it to the backend container.
 * Never hardcode localhost here — it breaks inside Docker.
 */
import axios from 'axios'
import { useAuthStore } from '../store/authStore'

// Always use relative path — Vite proxy handles forwarding to backend:8000
const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Inject JWT access token on every request
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 — attempt token refresh, then logout if that fails too
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refreshToken = useAuthStore.getState().refreshToken
        const resp = await axios.post('/api/auth/token/refresh/', {
          refresh: refreshToken,
        })
        useAuthStore.getState().setTokens(resp.data.access, refreshToken)
        original.headers.Authorization = `Bearer ${resp.data.access}`
        return api(original)
      } catch {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api