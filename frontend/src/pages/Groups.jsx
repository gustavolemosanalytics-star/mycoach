import { useState, useEffect } from 'react';
import { groupsAPI } from '../services/api';
import {
    Users,
    MessageSquare,
    TrendingUp,
    Plus,
    Search,
    ChevronRight,
    MapPin,
    Zap
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import './Groups.css';

export default function Groups() {
    const [groups, setGroups] = useState([]);
    const [feed, setFeed] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('feed'); // 'feed' or 'groups'

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [groupsRes, feedRes] = await Promise.all([
                groupsAPI.list(),
                groupsAPI.getFeed()
            ]);
            setGroups(groupsRes.data);
            setFeed(feedRes.data);
        } catch (err) {
            console.error('Error loading community data:', err);
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) return <div className="loading-screen"><div className="loading-spinner"></div></div>;

    return (
        <div className="groups-page">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Comunidade MyCoach 🤝</h1>
                    <p className="page-subtitle">Conecte-se, motive e evolua com outros atletas</p>
                </div>
                <div className="header-actions">
                    <button className="btn btn-primary">
                        <Plus size={18} /> Criar Grupo
                    </button>
                </div>
            </header>

            <div className="community-tabs">
                <button
                    className={`tab-btn ${activeTab === 'feed' ? 'active' : ''}`}
                    onClick={() => setActiveTab('feed')}
                >
                    Feed Global
                </button>
                <button
                    className={`tab-btn ${activeTab === 'groups' ? 'active' : ''}`}
                    onClick={() => setActiveTab('groups')}
                >
                    Seus Grupos
                </button>
            </div>

            <div className="community-content">
                {activeTab === 'feed' ? (
                    <div className="social-feed">
                        {feed.map((item, i) => (
                            <div key={i} className="card feed-item">
                                <div className="feed-header">
                                    <div className="user-avatar">{item.user.name.charAt(0)}</div>
                                    <div className="feed-user-info">
                                        <span className="user-name">{item.user.name}</span>
                                        <span className="post-time">{format(new Date(item.created_at), "d 'de' MMM 'às' HH:mm", { locale: ptBR })}</span>
                                    </div>
                                    {item.workout.highlights && (
                                        <div className="ai-badge-sm">
                                            <Zap size={12} /> AI
                                        </div>
                                    )}
                                </div>
                                <div className="feed-body">
                                    <div className="workout-snippet">
                                        <div className="snippet-icon">{getSportEmoji(item.workout.sport_type)}</div>
                                        <div className="snippet-content">
                                            <span className="workout-name">{item.workout.name}</span>
                                            <div className="workout-metrics-row">
                                                <span>{item.workout.distance_km} km</span>
                                                <span className="dot">•</span>
                                                <span>{item.workout.duration}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="feed-actions">
                                    <button className="btn btn-ghost btn-sm">👏 Kudos</button>
                                    <button className="btn btn-ghost btn-sm">💬 Comentar</button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="groups-grid">
                        <div className="search-groups card">
                            <Search size={18} />
                            <input type="text" placeholder="Procurar novos grupos..." />
                        </div>
                        {groups.map((group) => (
                            <div key={group.id} className="card group-card">
                                <div className="group-banner"></div>
                                <div className="group-info">
                                    <h3 className="group-name">{group.name}</h3>
                                    <p className="group-desc">{group.description || 'Um grupo de apaixonados por performance.'}</p>
                                    <div className="group-stats">
                                        <span><Users size={14} /> 24 membros</span>
                                        <span><TrendingUp size={14} /> Ativo</span>
                                    </div>
                                    <button className="btn btn-secondary btn-full">Entrar no Grupo</button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function getSportEmoji(sport) {
    const icons = { run: '🏃', ride: '🚴', swim: '🏊', strength: '💪' };
    return icons[sport] || '🏋️';
}
