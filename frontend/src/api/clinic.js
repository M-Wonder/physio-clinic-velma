/**
 * Clinic identity, contact details and rates — served by the backend at
 * GET /api/clinic/ (configured with CLINIC_* env vars), so nothing is
 * hardcoded in the UI. FALLBACK is used until the response arrives (or if the
 * API is waking up), so the page never flashes empty or wrong.
 */
import { useQuery } from '@tanstack/react-query'
import api from './client'

export const FALLBACK_CLINIC = {
  name: 'Neuromotion Physiotherapy Clinic',
  tagline: 'Move Better. Feel Better.',
  phone: '',
  whatsapp: '',
  email: 'neuromotionphysio@gmail.com',
  address: 'Nairobi, Kenya',
  social_handle: 'neuromotionphysio',
  currency: 'KES',
  rates: { clinic: 4500, home: 5500 },
  cancellation_notice_hours: 24,
  booking_advance_days: 30,
}

export function useClinic() {
  const { data } = useQuery({
    queryKey: ['clinic'],
    queryFn: () => api.get('/clinic/').then((r) => r.data),
    staleTime: 60 * 60 * 1000,
    retry: 1,
  })
  return { ...FALLBACK_CLINIC, ...(data || {}) }
}
