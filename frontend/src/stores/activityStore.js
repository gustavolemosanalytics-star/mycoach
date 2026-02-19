import { create } from 'zustand'
import { activitiesApi } from '../services/api'

const useActivityStore = create((set) => ({
  activities: [],
  currentActivity: null,
  uploading: false,
  uploadResult: null,
  loading: false,
  error: null,

  fetchActivities: async (params = {}) => {
    set({ loading: true })
    try {
      const { data } = await activitiesApi.list(params)
      set({ activities: data, loading: false })
    } catch (err) {
      set({ error: err.response?.data?.detail, loading: false })
    }
  },

  fetchActivity: async (id) => {
    set({ loading: true })
    try {
      const { data } = await activitiesApi.get(id)
      set({ currentActivity: data, loading: false })
    } catch (err) {
      set({ error: err.response?.data?.detail, loading: false })
    }
  },

  uploadActivity: async (file, metadata = {}) => {
    set({ uploading: true, uploadResult: null, error: null })
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (metadata.feeling) formData.append('feeling', metadata.feeling)
      if (metadata.rpe) formData.append('rpe', String(metadata.rpe))
      if (metadata.notes) formData.append('notes', metadata.notes)
      if (metadata.planned_session_id) formData.append('planned_session_id', metadata.planned_session_id)

      const { data } = await activitiesApi.upload(formData)
      set({ uploading: false, uploadResult: data })
      return data
    } catch (err) {
      set({ uploading: false, error: err.response?.data?.detail || 'Erro no upload' })
      throw err
    }
  },

  deleteActivity: async (id) => {
    await activitiesApi.delete(id)
    set((s) => ({ activities: s.activities.filter((a) => a.id !== id) }))
  },

  clearUpload: () => set({ uploadResult: null, error: null }),
}))

export default useActivityStore
