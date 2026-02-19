import { create } from 'zustand'
import { plansApi } from '../services/api'

const usePlanStore = create((set) => ({
  currentWeek: null,
  plan: null,
  races: [],
  loading: false,
  generating: false,
  error: null,

  fetchCurrentWeek: async () => {
    set({ loading: true })
    try {
      const { data } = await plansApi.getCurrentWeek()
      set({ currentWeek: data, loading: false })
    } catch (err) {
      set({ error: err.response?.data?.detail, loading: false })
    }
  },

  fetchRaces: async () => {
    try {
      const { data } = await plansApi.getRaces()
      set({ races: data })
    } catch {
      // ignore
    }
  },

  createRace: async (raceData) => {
    const { data } = await plansApi.createRace(raceData)
    set((s) => ({ races: [...s.races, data] }))
    return data
  },

  generatePlan: async (raceId) => {
    set({ generating: true })
    try {
      const { data } = await plansApi.generatePlan({ race_id: raceId })
      set({ plan: data, generating: false })
      return data
    } catch (err) {
      set({ generating: false })
      throw err
    }
  },

  generateWeekSessions: async (weekId) => {
    set({ generating: true })
    try {
      const { data } = await plansApi.generateWeekSessions(weekId)
      set({ generating: false })
      return data
    } catch (err) {
      set({ generating: false })
      throw err
    }
  },

  analyzeWeek: async (weekId) => {
    set({ generating: true })
    try {
      const { data } = await plansApi.analyzeWeek(weekId)
      set({ generating: false })
      return data
    } catch (err) {
      set({ generating: false })
      throw err
    }
  },
}))

export default usePlanStore
