/**
 * Zustand auth store — persists JWT tokens in memory + sessionStorage.
 */
import { create } from 'zustand'

export const useAuthStore = create((set, get) => ({
  user: JSON.parse(sessionStorage.getItem('user') || 'null'),
  accessToken: sessionStorage.getItem('access_token') || null,
  refreshToken: sessionStorage.getItem('refresh_token') || null,
  isAuthenticated: !!sessionStorage.getItem('access_token'),

  setAuth: (user, access, refresh) => {
    sessionStorage.setItem('user', JSON.stringify(user))
    sessionStorage.setItem('access_token', access)
    sessionStorage.setItem('refresh_token', refresh)
    set({ user, accessToken: access, refreshToken: refresh, isAuthenticated: true })
  },

  setTokens: (access, refresh) => {
    sessionStorage.setItem('access_token', access)
    if (refresh) sessionStorage.setItem('refresh_token', refresh)
    set({ accessToken: access, refreshToken: refresh || get().refreshToken })
  },

  logout: () => {
    sessionStorage.clear()
    set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false })
  },

  updateUser: (userData) => {
    const updated = { ...get().user, ...userData }
    sessionStorage.setItem('user', JSON.stringify(updated))
    set({ user: updated })
  },
}))
