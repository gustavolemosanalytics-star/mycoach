import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity, Eye, EyeOff } from 'lucide-react'
import useAuthStore from '../stores/authStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, loading, error, clearError } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(email, password)
      navigate('/')
    } catch {
      // error is set in store
    }
  }

  return (
    <div className="min-h-screen bg-[#0A0E17] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <Activity className="text-[#00E5A0]" size={32} />
          <h1 className="text-2xl font-bold text-white">My Coach</h1>
        </div>

        <div className="bg-[#111827] rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-white mb-6">Entrar</h2>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => { setEmail(e.target.value); clearError() }}
                className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0] transition-colors"
                placeholder="seu@email.com"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Senha</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); clearError() }}
                  className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0] transition-colors pr-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#00E5A0] hover:bg-[#00CC8E] text-[#0A0E17] font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-4">
            Não tem conta?{' '}
            <Link to="/register" className="text-[#00E5A0] hover:underline">Registrar</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
