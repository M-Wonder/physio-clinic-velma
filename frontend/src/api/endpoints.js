/**
 * All API endpoint functions.
 */
import api from './client'

// Auth
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me/'),
  updateMe: (data) => api.patch('/auth/me/', data),
}

// Services
export const servicesAPI = {
  list: () => api.get('/services/'),
  get: (slug) => api.get(`/services/${slug}/`),
}

// Doctors
export const doctorsAPI = {
  list: (params) => api.get('/auth/doctors/', { params }),
  get: (id) => api.get(`/auth/doctors/${id}/`),
  availability: (doctorId, date) => api.get(`/appointments/slots/`, { params: { doctor_id: doctorId, date } }),
}

// Appointments
export const appointmentsAPI = {
  list: (params) => api.get('/appointments/', { params }),
  book: (data) => api.post('/appointments/book/', data),
  cancel: (id, data) => api.post(`/appointments/${id}/cancel/`, data),
  reschedule: (id, data) => api.post(`/appointments/${id}/reschedule/`, data),
  get: (id) => api.get(`/appointments/${id}/`),
}

// Treatment Records
export const treatmentsAPI = {
  list: (params) => api.get('/treatments/', { params }),
  get: (id) => api.get(`/treatments/${id}/`),
  create: (data) => api.post('/treatments/', data),
  update: (id, data) => api.patch(`/treatments/${id}/`, data),
  uploadFile: (id, formData) => api.post(`/treatments/${id}/upload_file/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

// Notifications
export const notificationsAPI = {
  getPreferences: () => api.get('/notifications/preferences/'),
  updatePreferences: (data) => api.patch('/notifications/preferences/', data),
  getLogs: () => api.get('/notifications/logs/'),
}

// Patient profile
export const patientAPI = {
  getProfile: () => api.get('/auth/patients/me/'),
  updateProfile: (data) => api.patch('/auth/patients/me/', data),
  exportData: () => api.get('/auth/patients/export_data/'),
  requestDeletion: () => api.post('/auth/patients/request_data_deletion/'),
}

// Walk-ins
export const walkinAPI = {
  list: () => api.get('/appointments/walkins/'),
  create: (data) => api.post('/appointments/walkins/', data),
  update: (id, data) => api.patch(`/appointments/walkins/${id}/`, data),
}
