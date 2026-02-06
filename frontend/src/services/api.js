/**
 * API Service
 * Centralized API client for MyCoach backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper to handle responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
};

// Strava API
export const stravaApi = {
  getAuthUrl: () => fetch(`${API_URL}/api/strava/auth`).then(handleResponse),
  getStatus: () => fetch(`${API_URL}/api/strava/status`).then(handleResponse),
  sync: (daysBack = 30) => fetch(`${API_URL}/api/strava/sync?days_back=${daysBack}`, { method: 'POST' }).then(handleResponse),
};

// Activities API
export const activitiesApi = {
  list: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetch(`${API_URL}/api/activities${query ? '?' + query : ''}`).then(handleResponse);
  },
  get: (id) => fetch(`${API_URL}/api/activities/${id}`).then(handleResponse),
  getStats: (days = 30) => fetch(`${API_URL}/api/activities/stats/summary?days=${days}`).then(handleResponse),
};

// Metrics API
export const metricsApi = {
  getDaily: (fromDate, toDate) => {
    const params = new URLSearchParams();
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    return fetch(`${API_URL}/api/metrics/daily?${params}`).then(handleResponse);
  },
  getCurrent: () => fetch(`${API_URL}/api/metrics/current`).then(handleResponse),
  getProjection: (targetDate, taperIntensity = 0.5) =>
    fetch(`${API_URL}/api/metrics/projection?target_date=${targetDate}&taper_intensity=${taperIntensity}`).then(handleResponse),
  getWeeklySummary: (weeksBack = 4) => fetch(`${API_URL}/api/metrics/weekly-summary?weeks_back=${weeksBack}`).then(handleResponse),
};

// Athlete API
export const athleteApi = {
  getConfig: () => fetch(`${API_URL}/api/athlete/config`).then(handleResponse),
  updateConfig: (config) => fetch(`${API_URL}/api/athlete/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  }).then(handleResponse),
  logWeight: (weight, dateStr = null) => fetch(`${API_URL}/api/athlete/weight`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ weight_kg: weight, date_str: dateStr }),
  }).then(handleResponse),
  getWeightHistory: (days = 90) => fetch(`${API_URL}/api/athlete/weight-history?days=${days}`).then(handleResponse),
  getThresholds: () => fetch(`${API_URL}/api/athlete/thresholds`).then(handleResponse),
};

// Coach (AI) API
export const coachApi = {
  chat: (message, history = []) => fetch(`${API_URL}/api/coach/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  }).then(handleResponse),
  getWeeklyAnalysis: () => fetch(`${API_URL}/api/coach/weekly-analysis`).then(handleResponse),
  getNutritionSuggestion: () => fetch(`${API_URL}/api/coach/nutrition-suggestion`).then(handleResponse),
};

// Nutrition API
export const nutritionApi = {
  getScenarios: () => fetch(`${API_URL}/api/nutrition/scenarios`).then(handleResponse),
  getScenario: (code) => fetch(`${API_URL}/api/nutrition/scenario/${code}`).then(handleResponse),
};

// Export all
export default {
  strava: stravaApi,
  activities: activitiesApi,
  metrics: metricsApi,
  athlete: athleteApi,
  coach: coachApi,
  nutrition: nutritionApi,
};

// --- Legacy Exports for Compatibility ---

export const authAPI = {
  login: (credentials) => fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  }).then(handleResponse),
  register: (userData) => fetch(`${API_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  }).then(handleResponse),
};

export const workoutsAPI = {
  getAll: () => activitiesApi.list(),
  getById: (id) => activitiesApi.get(id),
};

export const wellnessAPI = {
  getLatest: () => fetch(`${API_URL}/api/wellness/latest`).then(handleResponse),
  log: (data) => fetch(`${API_URL}/api/wellness`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(handleResponse),
};

export const achievementsAPI = {
  getAll: () => fetch(`${API_URL}/api/achievements`).then(handleResponse),
};

export const usersAPI = {
  getProfile: () => athleteApi.getConfig(),
};

export const analyticsAPI = {
  getSummary: () => activitiesApi.getStats(),
  getPerformanceLoad: (days = 90) => {
    const fromDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const toDate = new Date().toISOString().split('T')[0];
    return metricsApi.getDaily(fromDate, toDate);
  },
  getHRZones: (days = 30) => fetch(`${API_URL}/api/analytics/hr-zones?days=${days}`).then(handleResponse),
};

export const groupsAPI = {
  list: () => fetch(`${API_URL}/api/groups`).then(handleResponse),
  getFeed: () => fetch(`${API_URL}/api/groups/feed`).then(handleResponse),
};

export const nutritionAPI = {
  ...nutritionApi,
  getProfile: () => fetch(`${API_URL}/api/nutrition/profile`).then(handleResponse),
  updateProfile: (data) => fetch(`${API_URL}/api/nutrition/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(handleResponse),
  getDailySummary: (date) => fetch(`${API_URL}/api/nutrition/daily-summary?date=${date}`).then(handleResponse),
  chat: (message, history) => fetch(`${API_URL}/api/nutrition/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  }).then(handleResponse),
};

export const integrationsAPI = {
  getStravaStatus: () => stravaApi.getStatus(),
};
