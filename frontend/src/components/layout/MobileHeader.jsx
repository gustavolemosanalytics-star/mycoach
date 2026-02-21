import { Activity, Menu } from 'lucide-react'
import useAuthStore from '../../stores/authStore'

export default function MobileHeader({ onMenuOpen }) {
  const user = useAuthStore((s) => s.user)

  return (
    <header className="sticky top-0 z-30 bg-[#0A0E17]/90 backdrop-blur-md border-b border-gray-800/50">
      <div className="flex items-center justify-between px-4 h-14">
        {/* Hamburger */}
        <button
          onClick={onMenuOpen}
          className="p-2 -ml-2 rounded-xl text-gray-400 active:text-white active:bg-gray-800 transition-colors"
        >
          <Menu size={22} />
        </button>

        {/* Logo */}
        <div className="flex items-center gap-2">
          <Activity className="text-[#00E5A0]" size={20} />
          <span className="text-base font-bold text-white">My Coach</span>
        </div>

        {/* Avatar */}
        <button className="w-8 h-8 rounded-full bg-[#1A2332] flex items-center justify-center border border-gray-700">
          <span className="text-xs font-bold text-[#00E5A0]">
            {(user?.full_name || 'A').charAt(0).toUpperCase()}
          </span>
        </button>
      </div>
    </header>
  )
}
