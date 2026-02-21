import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Calendar, Plus, User, Activity, LogOut, X, Trophy } from 'lucide-react'
import useAuthStore from '../../stores/authStore'
import usePlanStore from '../../stores/planStore'

const navItems = [
  { path: '/', icon: Calendar, label: 'Plano Semanal' },
  { path: '/add', icon: Plus, label: 'Adicionar Treino' },
  { path: '/profile', icon: User, label: 'Perfil' },
]

export default function MobileDrawer({ open, onClose }) {
  const location = useLocation()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const currentWeek = usePlanStore((s) => s.currentWeek)

  // Close on route change
  useEffect(() => {
    onClose()
  }, [location.pathname])

  // Lock body scroll when open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [open])

  const handleNav = (path) => {
    navigate(path)
    onClose()
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
    onClose()
  }

  const weeksToRace = currentWeek?.race_date
    ? Math.max(0, Math.ceil((new Date(currentWeek.race_date) - new Date()) / (7 * 24 * 60 * 60 * 1000)))
    : null

  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity duration-300 ${
          open ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />

      {/* Drawer panel */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-72 bg-[#111827] shadow-2xl transform transition-transform duration-300 ease-out ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between px-5 pt-5 pb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-[#00E5A0]/10 flex items-center justify-center">
                <Activity className="text-[#00E5A0]" size={20} />
              </div>
              <h1 className="text-lg font-bold text-white">My Coach</h1>
            </div>
            <button
              onClick={onClose}
              className="p-2 -mr-2 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* User card */}
          {user && (
            <div className="mx-4 mb-4 bg-[#1A2332] rounded-2xl p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#00E5A0]/20 flex items-center justify-center">
                  <span className="text-[#00E5A0] font-bold text-sm">
                    {(user.full_name || 'A').charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-white truncate">{user.full_name || 'Atleta'}</p>
                  <p className="text-xs text-gray-400 capitalize">
                    {user.modality === 'triathlon' ? '🏊 Triatleta' : '🏃 Corredor'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Race countdown */}
          {currentWeek?.race_name && (
            <div className="mx-4 mb-4 bg-gradient-to-r from-[#00E5A0]/10 to-transparent rounded-2xl p-4 border border-[#00E5A0]/20">
              <div className="flex items-center gap-2 mb-1.5">
                <Trophy size={14} className="text-[#00E5A0]" />
                <p className="text-xs font-medium text-[#00E5A0]">Prova alvo</p>
              </div>
              <p className="text-sm font-semibold text-white">{currentWeek.race_name}</p>
              {weeksToRace !== null && (
                <p className="text-xs text-gray-400 mt-1">
                  {weeksToRace === 0 ? 'Esta semana!' : `${weeksToRace} semanas restantes`}
                </p>
              )}
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 px-3 space-y-1">
            {navItems.map(({ path, icon: Icon, label }) => {
              const active = location.pathname === path
              return (
                <button
                  key={path}
                  onClick={() => handleNav(path)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    active
                      ? 'bg-[#00E5A0]/10 text-[#00E5A0]'
                      : 'text-gray-400 active:bg-gray-800 active:text-gray-200'
                  }`}
                >
                  <Icon size={20} />
                  {label}
                </button>
              )
            })}
          </nav>

          {/* Quick stats */}
          {currentWeek && (
            <div className="mx-4 mb-3 bg-[#1A2332] rounded-2xl p-4">
              <p className="text-xs font-medium text-gray-400 mb-3">Esta semana</p>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-gray-500">Fase</p>
                  <p className="text-sm font-semibold text-white capitalize">{currentWeek.phase || '—'}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-gray-500">Sessões</p>
                  <p className="text-sm font-semibold text-white">
                    {currentWeek.completed_sessions || 0}/{currentWeek.total_sessions || 0}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Logout */}
          <div className="px-3 pb-8">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-gray-500 active:text-red-400 active:bg-red-500/10 transition-colors"
            >
              <LogOut size={18} />
              Sair
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
