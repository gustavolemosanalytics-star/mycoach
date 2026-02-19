import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// JWT interceptor
api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('mycoach-auth')
  if (raw) {
    try {
      const { state } = JSON.parse(raw)
      if (state?.token) {
        config.headers.Authorization = `Bearer ${state.token}`
      }
    } catch {
      // ignore
    }
  }
  return config
})

// 401 → logout
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('mycoach-auth')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

export const profileApi = {
  get: () => api.get('/profile'),
  update: (data) => api.put('/profile', data),
}

export const activitiesApi = {
  upload: (formData) => api.post('/activities/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  }),
  list: (params) => api.get('/activities', { params }),
  get: (id) => api.get(`/activities/${id}`),
  delete: (id) => api.delete(`/activities/${id}`),
}

export const plansApi = {
  getRaces: () => api.get('/plans/races'),
  createRace: (data) => api.post('/plans/races', data),
  generatePlan: (data) => api.post('/plans/generate', data),
  generateWeekSessions: (weekId) => api.post(`/plans/weeks/${weekId}/generate`),
  getCurrentWeek: () => api.get('/plans/current-week'),
  analyzeWeek: (weekId) => api.post(`/plans/weeks/${weekId}/analyze`),
}

export default api
