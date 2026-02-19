import { useLocation, useNavigate } from 'react-router-dom'
import { Calendar, Plus, User, Activity, LogOut } from 'lucide-react'
import useAuthStore from '../../stores/authStore'
import usePlanStore from '../../stores/planStore'

const navItems = [
  { path: '/', icon: Calendar, label: 'Plano Semanal' },
  { path: '/add', icon: Plus, label: 'Adicionar Treino' },
  { path: '/profile', icon: User, label: 'Perfil' },
]

export default function DesktopSidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const currentWeek = usePlanStore((s) => s.currentWeek)

  return (
    <div className="flex h-full flex-col bg-[#111827] border-r border-gray-800 px-4 py-6">
      {/* Logo */}
      <div className="flex items-center gap-2 px-2 mb-8">
        <Activity className="text-[#00E5A0]" size={28} />
        <h1 className="text-xl font-bold text-white">My Coach</h1>
      </div>

      {/* User card */}
      {user && (
        <div className="bg-[#1A2332] rounded-xl p-3 mb-6">
          <p className="text-sm font-medium text-white truncate">{user.full_name || 'Atleta'}</p>
          <p className="text-xs text-gray-400 capitalize">
            {user.modality === 'triathlon' ? 'Triatleta' : 'Corredor'}
          </p>
        </div>
      )}

      {/* Race countdown */}
      {currentWeek?.race_name && (
        <div className="bg-[#1A2332] rounded-xl p-3 mb-6">
          <p className="text-xs text-gray-400 mb-1">Prova alvo</p>
          <p className="text-sm font-medium text-white">{currentWeek.race_name}</p>
          {currentWeek.race_date && (
            <p className="text-xs text-[#00E5A0] mt-1">
              {Math.max(0, Math.ceil((new Date(currentWeek.race_date) - new Date()) / (7 * 24 * 60 * 60 * 1000)))} semanas
            </p>
          )}
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        {navItems.map(({ path, icon: Icon, label }) => {
          const active = location.pathname === path
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                active
                  ? 'bg-[#00E5A0]/10 text-[#00E5A0]'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
              }`}
            >
              <Icon size={18} />
              {label}
            </button>
          )
        })}
      </nav>

      {/* Quick stats */}
      {currentWeek && (
        <div className="bg-[#1A2332] rounded-xl p-3 mb-4 space-y-2">
          <p className="text-xs text-gray-400">Esta semana</p>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <p className="text-xs text-gray-500">Fase</p>
              <p className="text-sm font-medium text-white capitalize">{currentWeek.phase || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Sessões</p>
              <p className="text-sm font-medium text-white">
                {currentWeek.completed_sessions || 0}/{currentWeek.total_sessions || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Logout */}
      <button
        onClick={() => { logout(); navigate('/login') }}
        className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-500 hover:text-red-400 hover:bg-gray-800 transition-colors"
      >
        <LogOut size={18} />
        Sair
      </button>
    </div>
  )
}
