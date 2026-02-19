import { useLocation, useNavigate } from 'react-router-dom'
import { Calendar, Plus, User } from 'lucide-react'

const tabs = [
  { path: '/', icon: Calendar, label: 'Plano' },
  { path: '/add', icon: Plus, label: 'Adicionar' },
  { path: '/profile', icon: User, label: 'Perfil' },
]

export default function BottomNav() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <div className="bg-[#111827] border-t border-gray-800 px-6 py-2 flex justify-around items-center">
      {tabs.map(({ path, icon: Icon, label }) => {
        const active = location.pathname === path
        return (
          <button
            key={path}
            onClick={() => navigate(path)}
            className={`flex flex-col items-center gap-1 py-2 px-4 rounded-xl transition-colors ${
              active ? 'text-[#00E5A0]' : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {path === '/add' ? (
              <div className={`p-2 rounded-full ${active ? 'bg-[#00E5A0] text-[#0A0E17]' : 'bg-gray-800 text-gray-400'}`}>
                <Icon size={20} />
              </div>
            ) : (
              <Icon size={20} />
            )}
            <span className="text-xs font-medium">{label}</span>
          </button>
        )
      })}
    </div>
  )
}
