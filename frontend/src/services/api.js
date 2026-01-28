import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
          const { access_token, refresh_token: newRefreshToken } = response.data;
          
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefreshToken);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => 
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
  register: (data) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

// Users API
export const usersAPI = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me', data),
  getStats: () => api.get('/users/me/stats'),
};

// Workouts API
export const workoutsAPI = {
  list: (params) => api.get('/workouts', { params }),
  get: (id) => api.get(`/workouts/${id}`),
  create: (data) => api.post('/workouts', data),
  update: (id, data) => api.put(`/workouts/${id}`, data),
  delete: (id) => api.delete(`/workouts/${id}`),
  getSummary: (days) => api.get('/workouts/summary', { params: { days } }),
  getWeekly: () => api.get('/workouts/weekly'),
};

// Wellness API
export const wellnessAPI = {
  list: (params) => api.get('/wellness', { params }),
  getToday: () => api.get('/wellness/today'),
  getByDate: (date) => api.get(`/wellness/${date}`),
  create: (data) => api.post('/wellness', data),
  update: (date, data) => api.put(`/wellness/${date}`, data),
  getTrends: (days) => api.get('/wellness/trends', { params: { days } }),
};

// Achievements API
export const achievementsAPI = {
  listAll: () => api.get('/achievements'),
  getMine: () => api.get('/achievements/me'),
  getStats: () => api.get('/achievements/me/stats'),
  getProgress: () => api.get('/achievements/me/progress'),
};

// Integrations API
export const integrationsAPI = {
  getStatus: () => api.get('/integrations/status'),
  stravaConnect: () => api.get('/integrations/strava/connect'),
  stravaDisconnect: () => api.delete('/integrations/strava/disconnect'),
  stravaSync: () => api.post('/integrations/strava/sync'),
};

export default api;
