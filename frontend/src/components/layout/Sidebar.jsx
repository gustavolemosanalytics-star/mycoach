import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Heart,
    Settings,
    Link as LinkIcon,
    TrendingUp,
    Activity,
    Utensils,
    Award,
} from 'lucide-react';
import './Sidebar.css';

const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/workouts', icon: Activity, label: 'Treinos' },
    { path: '/wellness', icon: Heart, label: 'Bem-estar' },
    { path: '/nutrition', icon: Utensils, label: 'Nutrição' },
    { path: '/achievements', icon: Award, label: 'Conquistas' },
    { path: '/analytics', icon: TrendingUp, label: 'Analytics' },
    { path: '/integrations', icon: LinkIcon, label: 'Integrações' },
    { path: '/settings', icon: Settings, label: 'Configurações' },
];

export default function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="logo">
                    <span className="logo-icon">🏃</span>
                    <span className="logo-text">MyCoach</span>
                </div>
            </div>

            <div className="sidebar-user">
                <div className="avatar">G</div>
                <div className="user-info">
                    <span className="user-name">Gustavo</span>
                    <span className="user-level">Atleta</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map(({ path, icon: Icon, label }) => (
                    <NavLink
                        key={path}
                        to={path}
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                    >
                        <Icon size={20} />
                        <span>{label}</span>
                    </NavLink>
                ))}
            </nav>
        </aside>
    );
}
