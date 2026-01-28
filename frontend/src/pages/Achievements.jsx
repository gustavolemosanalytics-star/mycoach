import { useState, useEffect } from 'react';
import { achievementsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Award, Lock, TrendingUp } from 'lucide-react';
import './Achievements.css';

const TIER_COLORS = {
    bronze: '#cd7f32',
    silver: '#c0c0c0',
    gold: '#ffd700',
    platinum: '#e5e4e2'
};

export default function Achievements() {
    const { user } = useAuth();
    const [allAchievements, setAllAchievements] = useState([]);
    const [userAchievements, setUserAchievements] = useState([]);
    const [stats, setStats] = useState(null);
    const [progress, setProgress] = useState([]);
    const [activeTab, setActiveTab] = useState('all');
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadAchievements();
    }, []);

    const loadAchievements = async () => {
        try {
            const [allRes, mineRes, statsRes, progressRes] = await Promise.all([
                achievementsAPI.listAll(),
                achievementsAPI.getMine(),
                achievementsAPI.getStats(),
                achievementsAPI.getProgress()
            ]);

            setAllAchievements(allRes.data);
            setUserAchievements(mineRes.data);
            setStats(statsRes.data);
            setProgress(progressRes.data);
        } catch (error) {
            console.error('Error loading achievements:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const earnedIds = new Set(userAchievements.map(ua => ua.achievement.id));

    const categories = [...new Set(allAchievements.map(a => a.category))];

    if (isLoading) {
        return (
            <div className="achievements-loading">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div className="achievements-page">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Conquistas</h1>
                    <p className="page-subtitle">Desbloqueie badges e ganhe pontos</p>
                </div>
            </header>

            {/* Stats Overview */}
            <div className="achievements-overview">
                <div className="overview-card level-card">
                    <div className="level-badge-large">
                        <Award size={48} />
                        <span className="level-number">{stats?.level || 1}</span>
                    </div>
                    <div className="level-details">
                        <h3>Level {stats?.level || 1}</h3>
                        <p>{stats?.total_points || 0} pontos totais</p>
                        <div className="level-progress-bar">
                            <div className="progress">
                                <div
                                    className="progress-bar"
                                    style={{ width: `${stats?.level_progress || 0}%` }}
                                />
                            </div>
                            <span>{stats?.points_to_next_level || 500} pts para o próximo level</span>
                        </div>
                    </div>
                </div>

                <div className="overview-stats">
                    <div className="overview-stat">
                        <span className="stat-icon">🏆</span>
                        <div>
                            <span className="stat-value">{stats?.achievements_earned || 0}</span>
                            <span className="stat-label">Conquistados</span>
                        </div>
                    </div>
                    <div className="overview-stat">
                        <span className="stat-icon">🎯</span>
                        <div>
                            <span className="stat-value">{(stats?.achievements_total || 0) - (stats?.achievements_earned || 0)}</span>
                            <span className="stat-label">Restantes</span>
                        </div>
                    </div>
                    <div className="overview-stat">
                        <span className="stat-icon">📈</span>
                        <div>
                            <span className="stat-value">{progress.length}</span>
                            <span className="stat-label">Em progresso</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="achievements-tabs">
                <button
                    className={`tab ${activeTab === 'all' ? 'active' : ''}`}
                    onClick={() => setActiveTab('all')}
                >
                    Todas
                </button>
                <button
                    className={`tab ${activeTab === 'earned' ? 'active' : ''}`}
                    onClick={() => setActiveTab('earned')}
                >
                    Conquistadas
                </button>
                <button
                    className={`tab ${activeTab === 'progress' ? 'active' : ''}`}
                    onClick={() => setActiveTab('progress')}
                >
                    Em Progresso
                </button>
            </div>

            {/* Achievements Grid */}
            {activeTab === 'progress' ? (
                <div className="progress-list">
                    {progress.length > 0 ? (
                        progress.map((p) => (
                            <div key={p.achievement.id} className="progress-card">
                                <div
                                    className="progress-icon"
                                    style={{ background: `linear-gradient(135deg, ${TIER_COLORS[p.achievement.tier]}, ${TIER_COLORS[p.achievement.tier]}88)` }}
                                >
                                    {p.achievement.icon}
                                </div>
                                <div className="progress-info">
                                    <h4>{p.achievement.title}</h4>
                                    <p>{p.achievement.description}</p>
                                    <div className="progress-bar-container">
                                        <div className="progress">
                                            <div
                                                className="progress-bar"
                                                style={{ width: `${p.percentage}%` }}
                                            />
                                        </div>
                                        <span>{p.current_progress}/{p.target}</span>
                                    </div>
                                </div>
                                <div className="progress-points">
                                    +{p.achievement.points} pts
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="empty-state">
                            <p>Nenhuma conquista em progresso ainda. Continue treinando!</p>
                        </div>
                    )}
                </div>
            ) : (
                categories.map((category) => {
                    const categoryAchievements = allAchievements.filter(a => a.category === category);
                    const filteredAchievements = activeTab === 'earned'
                        ? categoryAchievements.filter(a => earnedIds.has(a.id))
                        : categoryAchievements;

                    if (filteredAchievements.length === 0) return null;

                    return (
                        <div key={category} className="achievement-category">
                            <h3 className="category-title">
                                {category === 'general' && '🎯 Geral'}
                                {category === 'streak' && '🔥 Sequências'}
                                {category === 'distance' && '🛤️ Distância'}
                                {category === 'triathlon' && '🏊 Triathlon'}
                                {category === 'speed' && '⚡ Velocidade'}
                                {category === 'wellness' && '🧘 Bem-estar'}
                            </h3>
                            <div className="achievement-grid">
                                {filteredAchievements.map((achievement) => {
                                    const isEarned = earnedIds.has(achievement.id);
                                    return (
                                        <div
                                            key={achievement.id}
                                            className={`achievement-card ${isEarned ? 'earned' : 'locked'}`}
                                        >
                                            <div
                                                className="achievement-badge"
                                                style={{
                                                    background: isEarned
                                                        ? `linear-gradient(135deg, ${TIER_COLORS[achievement.tier]}, ${TIER_COLORS[achievement.tier]}88)`
                                                        : 'var(--gray-200)'
                                                }}
                                            >
                                                {isEarned ? achievement.icon : <Lock size={24} />}
                                            </div>
                                            <div className="achievement-content">
                                                <h4>{achievement.title}</h4>
                                                <p>{achievement.description}</p>
                                                <div className="achievement-meta">
                                                    <span className={`tier-badge ${achievement.tier}`}>
                                                        {achievement.tier}
                                                    </span>
                                                    <span className="points">+{achievement.points} pts</span>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    );
                })
            )}
        </div>
    );
}
