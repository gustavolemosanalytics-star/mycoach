import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Heart,
    Settings,
    LogOut,
    Link as LinkIcon,
    TrendingUp,
    Activity,
    Utensils,
    Award,
    Users
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './Sidebar.css';

const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/workouts', icon: Activity, label: 'Treinos' },
    { path: '/community', icon: Users, label: 'Comunidade' }, // Added Comunidade link
    { path: '/wellness', icon: Heart, label: 'Bem-estar' },
    { path: '/nutrition', icon: Utensils, label: 'Nutrição' },
    { path: '/achievements', icon: Award, label: 'Conquistas' },
    { path: '/analytics', icon: TrendingUp, label: 'Analytics' }, // Analytics link moved and kept
    { path: '/integrations', icon: LinkIcon, label: 'Integrações' },
    { path: '/settings', icon: Settings, label: 'Configurações' },
];

export default function Sidebar() {
    const { user, logout } = useAuth();

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="logo">
                    <span className="logo-icon">🏃</span>
                    <span className="logo-text">MyCoach</span>
                </div>
            </div>

            <div className="sidebar-user">
                <div className="avatar">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="user-info">
                    <span className="user-name">{user?.name || 'Atleta'}</span>
                    <span className="user-level">Level {user?.level || 1}</span>
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

            <div className="sidebar-footer">
                <button className="nav-item logout" onClick={logout}>
                    <LogOut size={20} />
                    <span>Sair</span>
                </button>
            </div>
        </aside>
    );
}
