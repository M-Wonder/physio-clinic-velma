/**
 * Axios API client
 * - Local Docker: uses Vite proxy via relative /api path
 * - Render static site: uses VITE_API_URL baked in at build time
 */
import axios from 'axios'
import { useAuthStore } from '../store/authStore'

// import.meta.env.VITE_API_URL is set at BUILD time by Vite:
//   - Local: not set, falls back to '/api' (Vite proxy handles it)
//   - Render: set to 'https://your-backend.onrender.com/api' in static site env vars
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
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
        const resp = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
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