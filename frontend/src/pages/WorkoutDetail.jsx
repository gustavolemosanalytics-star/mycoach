import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
    workoutsAPI,
    integrationsAPI,
    authAPI,
    usersAPI
} from '../services/api';
import {
    ChevronLeft,
    Clock,
    Activity,
    Flame,
    Zap,
    TrendingUp,
    Map as MapIcon,
    Trash2,
    Share2,
    Calendar,
    Sparkles
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import './WorkoutDetail.css';

import { MapContainer, TileLayer, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in Leaflet + React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function MapBounds({ points }) {
    const map = useMap();
    useEffect(() => {
        if (points && points.length > 0) {
            const bounds = L.latLngBounds(points);
            map.fitBounds(bounds, { padding: [20, 20] });
        }
    }, [points, map]);
    return null;
}

export default function WorkoutDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [workout, setWorkout] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadWorkout();
    }, [id]);

    const loadWorkout = async () => {
        try {
            const response = await workoutsAPI.get(id);
            setWorkout(response.data);
        } catch (err) {
            setError('Erro ao carregar o treino');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async () => {
        if (window.confirm('Tem certeza que deseja excluir este treino?')) {
            try {
                await workoutsAPI.delete(id);
                navigate('/workouts');
            } catch (err) {
                alert('Erro ao excluir o treino');
            }
        }
    };

    const getSportIcon = (sport) => {
        const icons = {
            run: '🏃',
            ride: '🚴',
            swim: '🏊',
            strength: '💪',
            walk: '🚶',
            yoga: '🧘'
        };
        return icons[sport] || '🏋️';
    };

    if (isLoading) return <div className="loading-screen"><div className="loading-spinner"></div></div>;
    if (error) return <div className="error-screen"><p>{error}</p><Link to="/workouts" className="btn btn-primary">Voltar</Link></div>;
    if (!workout) return null;

    const aiInsight = workout.highlights?.find(h => h.type === 'ai_insight');
    const regularHighlights = workout.highlights?.filter(h => h.type !== 'ai_insight') || [];
    const trackPoints = workout.track_points?.filter(p => p.lat && p.lng).map(p => [p.lat, p.lng]) || [];

    return (
        <div className="workout-detail-page">
            <header className="page-header">
                <div className="header-left">
                    <Link to="/workouts" className="btn btn-ghost">
                        <ChevronLeft size={20} />
                    </Link>
                    <div>
                        <div className="workout-badge-type">
                            <span className={`badge badge-${workout.sport_type}`}>
                                {getSportIcon(workout.sport_type)} {workout.sport_type.toUpperCase()}
                            </span>
                            <span className="workout-source">via {workout.source}</span>
                        </div>
                        <h1 className="page-title">{workout.name}</h1>
                        <p className="page-subtitle">
                            <Calendar size={14} /> {format(new Date(workout.start_date), "d 'de' MMMM 'às' HH:mm", { locale: ptBR })}
                        </p>
                    </div>
                </div>
                <div className="header-actions">
                    <button className="btn btn-ghost"><Share2 size={20} /></button>
                    <button className="btn btn-ghost text-error" onClick={handleDelete}><Trash2 size={20} /></button>
                </div>
            </header>

            <div className="workout-content-grid">
                {/* Main Stats */}
                <div className="card stats-main-card">
                    <div className="stats-row">
                        <div className="stat-item">
                            <span className="stat-label">Distância</span>
                            <span className="stat-value">{workout.distance_km} <small>km</small></span>
                        </div>
                        <div className="stat-item border-left">
                            <span className="stat-label">Duração</span>
                            <span className="stat-value">{workout.duration_formatted}</span>
                        </div>
                        <div className="stat-item border-left">
                            <span className="stat-label">Pace Médio</span>
                            <span className="stat-value">{workout.pace_formatted} <small>/km</small></span>
                        </div>
                    </div>
                </div>

                {/* AI Insight Section */}
                {aiInsight && (
                    <div className="card ai-highlight-card">
                        <div className="card-header">
                            <h3 className="card-title ai-title">
                                <Sparkles size={18} className="ai-icon-sparkle" /> MyCoach Insights
                            </h3>
                        </div>
                        <div className="ai-content">
                            <p className="ai-message">"{aiInsight.message}"</p>
                            {aiInsight.technical && (
                                <div className="ai-technical">
                                    <span className="ai-label">Análise Técnica:</span>
                                    <p>{aiInsight.technical}</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Real Map Section */}
                {trackPoints.length > 0 && (
                    <div className="card map-card">
                        <div className="card-header">
                            <h3 className="card-title"><MapIcon size={18} /> Mapa do Percurso</h3>
                        </div>
                        <div className="map-container-wrapper" style={{ height: '400px', borderRadius: 'var(--radius)', overflow: 'hidden', marginTop: 'var(--space-4)' }}>
                            <MapContainer
                                center={trackPoints[0]}
                                zoom={13}
                                style={{ height: '100%', width: '100%' }}
                                scrollWheelZoom={false}
                            >
                                <TileLayer
                                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
                                />
                                <Polyline
                                    positions={trackPoints}
                                    pathOptions={{ color: 'var(--primary-600)', weight: 4 }}
                                />
                                <MapBounds points={trackPoints} />
                            </MapContainer>
                        </div>
                    </div>
                )}

                {/* Regular Highlights */}
                {regularHighlights.length > 0 && (
                    <div className="card highlights-card">
                        <h3 className="card-title">Destaques</h3>
                        <div className="highlights-list">
                            {regularHighlights.map((h, i) => (
                                <div key={i} className="highlight-item">
                                    <span className="highlight-icon">{h.icon}</span>
                                    <span className="highlight-text">{h.message}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Secondary Stats */}
                <div className="card secondary-stats-card">
                    <h3 className="card-title">Métricas Detalhadas</h3>
                    <div className="details-grid">
                        {workout.avg_heart_rate && (
                            <div className="detail-item">
                                <Activity size={18} />
                                <div>
                                    <span className="detail-label">FC Média</span>
                                    <span className="detail-value">{Math.round(workout.avg_heart_rate)} bpm</span>
                                </div>
                            </div>
                        )}
                        {workout.max_heart_rate && (
                            <div className="detail-item">
                                <TrendingUp size={18} />
                                <div>
                                    <span className="detail-label">FC Máxima</span>
                                    <span className="detail-value">{workout.max_heart_rate} bpm</span>
                                </div>
                            </div>
                        )}
                        {workout.calories && (
                            <div className="detail-item">
                                <Flame size={18} />
                                <div>
                                    <span className="detail-label">Calorias</span>
                                    <span className="detail-value">{workout.calories} kcal</span>
                                </div>
                            </div>
                        )}
                        {workout.elevation_gain && (
                            <div className="detail-item">
                                <TrendingUp size={18} className="rotate-45" />
                                <div>
                                    <span className="detail-label">Ganho de Elevação</span>
                                    <span className="detail-value">{workout.elevation_gain}m</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Description */}
                {workout.description && (
                    <div className="card description-card">
                        <h3 className="card-title">Notas</h3>
                        <p className="workout-description-text">{workout.description}</p>
                    </div>
                )}
            </div>
        </div>
    );
}
