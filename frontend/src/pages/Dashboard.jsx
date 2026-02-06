import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
    Activity,
    Flame,
    Clock,
    TrendingUp,
    ChevronRight,
    Heart,
    Zap,
    Award
} from 'lucide-react';
import { workoutsAPI, wellnessAPI, achievementsAPI, usersAPI } from '../services/api';
import { format, formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar
} from 'recharts';
import './Dashboard.css';

export default function Dashboard() {
    const [stats, setStats] = useState(null);
    const [weeklyData, setWeeklyData] = useState(null);
    const [recentWorkouts, setRecentWorkouts] = useState([]);
    const [wellness, setWellness] = useState(null);
    const [gamification, setGamification] = useState(null);
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const [statsRes, weeklyRes, workoutsRes, wellnessRes, gamRes, aiRes] = await Promise.all([
                usersAPI.getStats(),
                workoutsAPI.getWeekly(),
                workoutsAPI.list({ per_page: 5 }),
                wellnessAPI.getToday().catch(() => ({ data: null })),
                achievementsAPI.getStats(),
                integrationsAPI.getWeeklyAnalysis().catch(() => ({ data: null }))
            ]);

            setStats(statsRes.data);
            setWeeklyData(weeklyRes.data);
            setRecentWorkouts(workoutsRes.data.workouts);
            setWellness(wellnessRes.data);
            setGamification(gamRes.data);
            setAiAnalysis(aiRes.data);
        } catch (error) {
            console.error('Error loading dashboard:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getSportIcon = (sport) => {
        const icons = {
            run: '🏃',
            ride: '🚴',
            swim: '🏊',
            strength: '💪',
            default: '🏋️'
        };
        return icons[sport] || icons.default;
    };

    const getMoodEmoji = (mood) => {
        const moods = ['😢', '😔', '😐', '😊', '🤩'];
        return moods[mood - 1] || '😐';
    };

    if (isLoading) {
        return (
            <div className="dashboard-loading">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Olá, Gustavo! 👋</h1>
                    <p className="page-subtitle">Veja como está seu progresso esta semana</p>
                </div>
                <Link to="/workouts/new" className="btn btn-primary">
                    + Novo Treino
                </Link>
            </header>

            {/* AI Analysis Section */}
            {aiAnalysis && (
                <div className="card ai-analysis-card">
                    <div className="card-header">
                        <h3 className="card-title ai-title">
                            <Zap size={18} className="ai-icon-zap" /> Análise do MyCoach
                        </h3>
                        <span className={`status-badge ${aiAnalysis.status}`}>
                            {aiAnalysis.status === 'improving' ? '🚀 Evoluindo' :
                                aiAnalysis.status === 'fatigued' ? '⚠️ Fadiga' : '✅ Estável'}
                        </span>
                    </div>
                    <div className="ai-analysis-content">
                        <p className="ai-summary">{aiAnalysis.summary}</p>
                        <div className="ai-recommendation">
                            <span className="ai-label">Recomendação:</span>
                            <p>{aiAnalysis.recommendation}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon blue">
                        <Activity size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-value">{stats?.total_workouts || 0}</span>
                        <span className="stat-label">Treinos esta semana</span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon orange">
                        <Flame size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-value">{stats?.total_calories?.toLocaleString() || 0}</span>
                        <span className="stat-label">Calorias queimadas</span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon teal">
                        <TrendingUp size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-value">{stats?.total_distance_km?.toFixed(1) || 0} km</span>
                        <span className="stat-label">Distância total</span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon purple">
                        <Clock size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-value">{stats?.total_time_hours?.toFixed(1) || 0}h</span>
                        <span className="stat-label">Tempo de treino</span>
                    </div>
                </div>
            </div>

            <div className="dashboard-grid">
                {/* Weekly Chart */}
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Atividade Semanal</h3>
                    </div>
                    <ResponsiveContainer width="100%" height={200}>
                        <AreaChart data={weeklyData?.workouts?.slice(0, 7).reverse() || []}>
                            <defs>
                                <linearGradient id="colorDistance" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis
                                dataKey="start_date"
                                tickFormatter={(val) => format(new Date(val), 'EEE', { locale: ptBR })}
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#6b7280', fontSize: 12 }}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#6b7280', fontSize: 12 }}
                                tickFormatter={(val) => `${(val / 1000).toFixed(0)}km`}
                            />
                            <Tooltip
                                formatter={(val) => [`${(val / 1000).toFixed(1)} km`, 'Distância']}
                                labelFormatter={(val) => format(new Date(val), 'EEEE, d MMM', { locale: ptBR })}
                            />
                            <Area
                                type="monotone"
                                dataKey="distance"
                                stroke="#06b6d4"
                                strokeWidth={2}
                                fill="url(#colorDistance)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Today's Wellness */}
                <div className="card wellness-card">
                    <div className="card-header">
                        <h3 className="card-title">Bem-estar de Hoje</h3>
                        <Link to="/wellness" className="btn btn-ghost btn-sm">
                            Atualizar
                        </Link>
                    </div>
                    {wellness ? (
                        <div className="wellness-stats">
                            <div className="wellness-item">
                                <span className="wellness-emoji">{getMoodEmoji(wellness.mood)}</span>
                                <span className="wellness-label">Humor</span>
                            </div>
                            <div className="wellness-item">
                                <span className="wellness-emoji">⚡</span>
                                <span className="wellness-value">{wellness.energy_level}/5</span>
                                <span className="wellness-label">Energia</span>
                            </div>
                            <div className="wellness-item">
                                <span className="wellness-emoji">😴</span>
                                <span className="wellness-value">
                                    {wellness.sleep_duration_minutes
                                        ? `${Math.floor(wellness.sleep_duration_minutes / 60)}h${wellness.sleep_duration_minutes % 60}m`
                                        : '--'
                                    }
                                </span>
                                <span className="wellness-label">Sono</span>
                            </div>
                            {wellness.readiness_score && (
                                <div className="wellness-item readiness">
                                    <span className="readiness-score">{wellness.readiness_score.toFixed(0)}</span>
                                    <span className="wellness-label">Prontidão</span>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="wellness-empty">
                            <p>Você ainda não registrou seu bem-estar hoje</p>
                            <Link to="/wellness" className="btn btn-primary btn-sm">
                                Registrar agora
                            </Link>
                        </div>
                    )}
                </div>

                {/* Recent Workouts */}
                <div className="card workouts-card">
                    <div className="card-header">
                        <h3 className="card-title">Treinos Recentes</h3>
                        <Link to="/workouts" className="btn btn-ghost btn-sm">
                            Ver todos <ChevronRight size={16} />
                        </Link>
                    </div>
                    <div className="workouts-list">
                        {recentWorkouts.length > 0 ? (
                            recentWorkouts.map((workout) => (
                                <Link
                                    key={workout.id}
                                    to={`/workouts/${workout.id}`}
                                    className="workout-item"
                                >
                                    <div className={`workout-icon ${workout.sport_type}`}>
                                        {getSportIcon(workout.sport_type)}
                                    </div>
                                    <div className="workout-info">
                                        <span className="workout-name">{workout.name}</span>
                                        <span className="workout-meta">
                                            {formatDistanceToNow(new Date(workout.start_date), {
                                                addSuffix: true,
                                                locale: ptBR
                                            })}
                                        </span>
                                    </div>
                                    <div className="workout-metrics">
                                        <span className="workout-distance">{workout.distance_km} km</span>
                                        <span className="workout-duration">{workout.duration_formatted}</span>
                                    </div>
                                </Link>
                            ))
                        ) : (
                            <div className="workouts-empty">
                                <p>Nenhum treino registrado ainda</p>
                                <Link to="/workouts/new" className="btn btn-primary btn-sm">
                                    Adicionar treino
                                </Link>
                            </div>
                        )}
                    </div>
                </div>

                {/* Gamification */}
                <div className="card gamification-card">
                    <div className="card-header">
                        <h3 className="card-title">Seu Progresso</h3>
                    </div>
                    <div className="gamification-content">
                        <div className="level-display">
                            <div className="level-badge">
                                <Award size={32} />
                                <span className="level-number">{gamification?.level || 1}</span>
                            </div>
                            <div className="level-info">
                                <span className="level-label">Level {gamification?.level || 1}</span>
                                <span className="points">{gamification?.total_points || 0} pontos</span>
                            </div>
                        </div>

                        <div className="level-progress">
                            <div className="progress">
                                <div
                                    className="progress-bar"
                                    style={{ width: `${gamification?.level_progress || 0}%` }}
                                />
                            </div>
                            <span className="progress-label">
                                {gamification?.points_to_next_level || 500} pts para o próximo level
                            </span>
                        </div>

                        <div className="achievements-preview">
                            <span className="achievements-count">
                                🏆 {gamification?.achievements_earned || 0}/{gamification?.achievements_total || 0} conquistas
                            </span>
                            <Link to="/achievements" className="btn btn-ghost btn-sm">
                                Ver todas
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
