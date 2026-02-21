import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity } from 'lucide-react'
import useAuthStore from '../stores/authStore'

const MODALITIES = [
  { value: 'triathlon', label: 'Triatleta', desc: 'Nado, bike e corrida' },
  { value: 'running', label: 'Corredor', desc: 'Foco em corrida' },
]

const LEVELS = [
  { value: 'beginner', label: 'Iniciante' },
  { value: 'intermediate', label: 'Intermediário' },
  { value: 'advanced', label: 'Avançado' },
  { value: 'elite', label: 'Elite' },
]

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register, loading, error, clearError } = useAuthStore()
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    modality: 'running',
    experience_level: 'intermediate',
    weight_kg: '',
    height_cm: '',
    hr_max: '',
    hr_rest: '',
    weekly_hours_available: '',
    training_days_per_week: '',
  })

  const set = (key, val) => {
    setForm((f) => ({ ...f, [key]: val }))
    clearError()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      ...form,
      weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
      height_cm: form.height_cm ? Number(form.height_cm) : null,
      hr_max: form.hr_max ? Number(form.hr_max) : null,
      hr_rest: form.hr_rest ? Number(form.hr_rest) : null,
      weekly_hours_available: form.weekly_hours_available ? Number(form.weekly_hours_available) : null,
      training_days_per_week: form.training_days_per_week ? Number(form.training_days_per_week) : null,
    }
    try {
      await register(payload)
      navigate('/')
    } catch {
      // error in store
    }
  }

  return (
    <div className="min-h-screen bg-[#0A0E17] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <Activity className="text-[#00E5A0]" size={32} />
          <h1 className="text-2xl font-bold text-white">My Coach</h1>
        </div>

        <div className="bg-[#111827] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white">Registrar</h2>
            <span className="text-xs text-gray-500">Passo {step}/2</span>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {step === 1 && (
              <>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Nome completo</label>
                  <input
                    required
                    value={form.full_name}
                    onChange={(e) => set('full_name', e.target.value)}
                    className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                    placeholder="Seu nome"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1">Email</label>
                  <input
                    type="email"
                    required
                    value={form.email}
                    onChange={(e) => set('email', e.target.value)}
                    className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                    placeholder="seu@email.com"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1">Senha</label>
                  <input
                    type="password"
                    required
                    value={form.password}
                    onChange={(e) => set('password', e.target.value)}
                    className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                    placeholder="Mínimo 6 caracteres"
                    minLength={6}
                  />
                </div>

                {/* Modality */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Modalidade</label>
                  <div className="grid grid-cols-2 gap-2">
                    {MODALITIES.map((m) => (
                      <button
                        key={m.value}
                        type="button"
                        onClick={() => set('modality', m.value)}
                        className={`p-3 rounded-lg border text-left transition-colors ${
                          form.modality === m.value
                            ? 'border-[#00E5A0] bg-[#00E5A0]/10'
                            : 'border-gray-700 bg-[#1A2332]'
                        }`}
                      >
                        <p className={`text-sm font-medium ${form.modality === m.value ? 'text-[#00E5A0]' : 'text-white'}`}>
                          {m.label}
                        </p>
                        <p className="text-xs text-gray-500">{m.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1">Nível</label>
                  <select
                    value={form.experience_level}
                    onChange={(e) => set('experience_level', e.target.value)}
                    className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                  >
                    {LEVELS.map((l) => (
                      <option key={l.value} value={l.value}>{l.label}</option>
                    ))}
                  </select>
                </div>

                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="w-full bg-[#00E5A0] hover:bg-[#00CC8E] text-[#0A0E17] font-semibold py-2.5 rounded-lg transition-colors"
                >
                  Próximo
                </button>
              </>
            )}

            {step === 2 && (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Peso (kg)</label>
                    <input
                      type="number"
                      value={form.weight_kg}
                      onChange={(e) => set('weight_kg', e.target.value)}
                      className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                      placeholder="70"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Altura (cm)</label>
                    <input
                      type="number"
                      value={form.height_cm}
                      onChange={(e) => set('height_cm', e.target.value)}
                      className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                      placeholder="175"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">FC Máx</label>
                    <input
                      type="number"
                      value={form.hr_max}
                      onChange={(e) => set('hr_max', e.target.value)}
                      className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                      placeholder="185"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">FC Repouso</label>
                    <input
                      type="number"
                      value={form.hr_rest}
                      onChange={(e) => set('hr_rest', e.target.value)}
                      className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                      placeholder="50"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Horas/semana</label>
                    <input
                      type="number"
                      value={form.weekly_hours_available}
                      onChange={(e) => set('weekly_hours_available', e.target.value)}
                      className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                      placeholder="10"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Dias/semana</label>
                    <input
                      type="number"
                      value={form.training_days_per_week}
                      onChange={(e) => set('training_days_per_week', e.target.value)}
                      className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                      placeholder="6"
                      min={1}
                      max={7}
                    />
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium py-2.5 rounded-lg transition-colors"
                  >
                    Voltar
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-[#00E5A0] hover:bg-[#00CC8E] text-[#0A0E17] font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {loading ? 'Criando...' : 'Criar conta'}
                  </button>
                </div>
              </>
            )}
          </form>

          <p className="text-center text-sm text-gray-500 mt-4">
            Já tem conta?{' '}
            <Link to="/login" className="text-[#00E5A0] hover:underline">Entrar</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
