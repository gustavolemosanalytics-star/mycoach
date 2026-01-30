import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { workoutsAPI } from '../services/api';
import {
    Plus,
    Upload,
    Activity,
    Clock,
    ChevronRight,
    Search,
    Filter,
    Calendar,
    Zap
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import './Workouts.css';

export default function Workouts() {
    const navigate = useNavigate();
    const [workouts, setWorkouts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isUploading, setIsUploading] = useState(false);

    useEffect(() => {
        loadWorkouts();
    }, []);

    const loadWorkouts = async () => {
        try {
            const response = await workoutsAPI.list();
            setWorkouts(response.data.workouts);
        } catch (err) {
            console.error('Error loading workouts:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsUploading(true);
        try {
            const response = await workoutsAPI.uploadTCX(file);
            alert('Treino importado com sucesso!');
            loadWorkouts();
            navigate(`/workouts/${response.data.id}`);
        } catch (err) {
            alert('Erro ao importar arquivo TCX. Verifique o formato.');
        } finally {
            setIsUploading(false);
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

    return (
        <div className="workouts-page">
            <header className="page-header">
                <div className="header-content">
                    <h1 className="page-title">Meus Treinos</h1>
                    <p className="page-subtitle">Acompanhe sua evolução e histórico</p>
                </div>
                <div className="header-actions">
                    <label className={`btn btn-secondary ${isUploading ? 'loading' : ''}`}>
                        <Upload size={18} /> {isUploading ? 'Importando...' : 'Importar TCX'}
                        <input
                            type="file"
                            accept=".tcx"
                            onChange={handleFileUpload}
                            disabled={isUploading}
                            hidden
                        />
                    </label>
                    <button className="btn btn-primary">
                        <Plus size={18} /> Novo Treino
                    </button>
                </div>
            </header>

            <div className="workouts-filter-bar card">
                <div className="search-box">
                    <Search size={18} />
                    <input type="text" placeholder="Buscar por nome do treino..." />
                </div>
                <div className="filters">
                    <button className="btn btn-ghost btn-sm">
                        <Calendar size={16} /> Mês Atual
                    </button>
                    <button className="btn btn-ghost btn-sm">
                        <Filter size={16} /> Todos os Esportes
                    </button>
                </div>
            </div>

            <div className="workouts-list">
                {isLoading ? (
                    <div className="loading-state">Carregando seus treinos...</div>
                ) : workouts.length > 0 ? (
                    workouts.map((workout) => (
                        <Link
                            to={`/workouts/${workout.id}`}
                            key={workout.id}
                            className="card workout-list-item"
                        >
                            <div className={`workout-icon-bg ${workout.sport_type}`}>
                                {getSportIcon(workout.sport_type)}
                            </div>
                            <div className="workout-main-info">
                                <span className="workout-item-name">{workout.name}</span>
                                <span className="workout-item-date">
                                    {format(new Date(workout.start_date), "d 'de' MMMM", { locale: ptBR })}
                                </span>
                            </div>
                            <div className="workout-item-stats">
                                <div className="item-stat">
                                    <span className="stat-label">Distância</span>
                                    <span className="stat-value">{workout.distance_km} km</span>
                                </div>
                                <div className="item-stat">
                                    <span className="stat-label">Tempo</span>
                                    <span className="stat-value">{workout.duration_formatted}</span>
                                </div>
                                <div className="item-stat">
                                    <span className="stat-label">Pace</span>
                                    <span className="stat-value">{workout.pace_formatted} /km</span>
                                </div>
                            </div>
                            {workout.highlights?.length > 0 && (
                                <div className="workout-item-badge">
                                    <Zap size={14} /> AI
                                </div>
                            )}
                            <ChevronRight size={20} className="arrow-icon" />
                        </Link>
                    ))
                ) : (
                    <div className="card empty-state">
                        <h3>Nenhum treino encontrado</h3>
                        <p>Comece a treinar e registre sua primeira atividade!</p>
                    </div>
                )}
            </div>
        </div>
    );
}
