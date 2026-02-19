import { Outlet } from 'react-router-dom'
import BottomNav from './BottomNav'
import DesktopSidebar from './DesktopSidebar'

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-[#0A0E17]">
      {/* Desktop sidebar */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:flex lg:w-64 lg:flex-col">
        <DesktopSidebar />
      </aside>

      {/* Main content */}
      <main className="lg:pl-64 pb-20 lg:pb-0">
        <div className="mx-auto max-w-lg lg:max-w-2xl px-4 py-6">
          <Outlet />
        </div>
      </main>

      {/* Mobile bottom nav */}
      <nav className="lg:hidden fixed bottom-0 inset-x-0 z-50">
        <BottomNav />
      </nav>
    </div>
  )
}
