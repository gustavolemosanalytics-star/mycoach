import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi, profileApi } from '../services/api'

const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      loading: false,
      error: null,

      login: async (email, password) => {
        set({ loading: true, error: null })
        try {
          const { data } = await authApi.login({ email, password })
          set({ token: data.access_token, loading: false })
          await get().fetchProfile()
        } catch (err) {
          set({ error: err.response?.data?.detail || 'Erro ao fazer login', loading: false })
          throw err
        }
      },

      register: async (userData) => {
        set({ loading: true, error: null })
        try {
          const { data } = await authApi.register(userData)
          set({ token: data.access_token, loading: false })
          await get().fetchProfile()
        } catch (err) {
          set({ error: err.response?.data?.detail || 'Erro ao registrar', loading: false })
          throw err
        }
      },

      fetchProfile: async () => {
        try {
          const { data } = await profileApi.get()
          set({ user: data })
        } catch {
          // token invalid
          get().logout()
        }
      },

      updateProfile: async (profileData) => {
        const { data } = await profileApi.update(profileData)
        set({ user: data })
        return data
      },

      logout: () => {
        set({ token: null, user: null, error: null })
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'mycoach-auth',
      partialize: (state) => ({ token: state.token }),
    }
  )
)

export default useAuthStore
