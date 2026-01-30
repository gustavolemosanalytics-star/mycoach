import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { nutritionAPI } from '../services/api';
import {
    Utensils,
    Flame,
    Zap,
    MessageSquare,
    Plus,
    ChevronRight,
    TrendingUp,
    Droplets
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import './Nutrition.css';

export default function Nutrition() {
    const navigate = useNavigate();
    const [summary, setSummary] = useState(null);
    const [profile, setProfile] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadNutritionData();
    }, []);

    const loadNutritionData = async () => {
        try {
            const [profRes, sumRes] = await Promise.all([
                nutritionAPI.getProfile().catch(() => ({ data: null })),
                nutritionAPI.getDailySummary(format(new Date(), 'yyyy-MM-dd')).catch(() => ({ data: null }))
            ]);

            if (!profRes.data) {
                navigate('/nutrition/anamnesis');
                return;
            }

            setProfile(profRes.data);
            setSummary(sumRes.data);
        } catch (err) {
            console.error('Error loading nutrition data:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const calculatePercent = (current, target) => {
        if (!target) return 0;
        return Math.min(Math.round((current / target) * 100), 100);
    };

    if (isLoading) return <div className="loading-screen"><div className="loading-spinner"></div></div>;

    return (
        <div className="nutrition-page">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Nutrição Neural 🍎</h1>
                    <p className="page-subtitle">Seu combustível para a performance de hoje</p>
                </div>
                <div className="header-actions">
                    <Link to="/nutrition/chat" className="btn btn-primary ai-btn">
                        <MessageSquare size={18} /> Copiloto IA
                    </Link>
                </div>
            </header>

            <div className="nutrition-grid">
                {/* Calorias Principal */}
                <div className="card calorie-main-card">
                    <div className="calorie-balance">
                        <div className="balance-item">
                            <span className="balance-value">{summary?.target_calories || 0}</span>
                            <span className="balance-label">Meta</span>
                        </div>
                        <div className="balance-operator">-</div>
                        <div className="balance-item">
                            <span className="balance-value">{summary?.total_calories || 0}</span>
                            <span className="balance-label">Ingerido</span>
                        </div>
                        <div className="balance-operator">+</div>
                        <div className="balance-item text-primary">
                            <span className="balance-value">0</span>
                            <span className="balance-label">Exercício</span>
                        </div>
                        <div className="balance-operator">=</div>
                        <div className="balance-item remaining">
                            <span className="balance-value">
                                {(summary?.target_calories || 0) - (summary?.total_calories || 0)}
                            </span>
                            <span className="balance-label">Restante</span>
                        </div>
                    </div>
                    <div className="calorie-progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${calculatePercent(summary?.total_calories, summary?.target_calories)}%` }}
                        ></div>
                    </div>
                </div>

                {/* Macros Rings */}
                <div className="card macros-card">
                    <h3 className="card-title">Distribuição de Macros</h3>
                    <div className="macros-rings-container">
                        <MacroRing
                            label="Proteína"
                            current={summary?.total_protein || 0}
                            target={summary?.target_protein || 1}
                            color="#ef4444"
                            unit="g"
                        />
                        <MacroRing
                            label="Carbo"
                            current={summary?.total_carbs || 0}
                            target={summary?.target_carbs || 1}
                            color="#3b82f6"
                            unit="g"
                        />
                        <MacroRing
                            label="Gordura"
                            current={summary?.total_fat || 0}
                            target={summary?.target_fat || 1}
                            color="#eab308"
                            unit="g"
                        />
                    </div>
                </div>

                {/* Daily Meals */}
                <div className="card meals-card">
                    <div className="card-header">
                        <h3 className="card-title">Diário Alimentar</h3>
                        <button className="btn btn-ghost btn-sm">
                            <Plus size={16} /> Registrar
                        </button>
                    </div>
                    <div className="meals-list">
                        {summary?.meals.length > 0 ? (
                            summary.meals.map((meal, i) => (
                                <div key={meal.id} className="meal-item">
                                    <div className="meal-icon"><Utensils size={18} /></div>
                                    <div className="meal-info">
                                        <span className="meal-name">{meal.name}</span>
                                        <span className="meal-time">{format(new Date(meal.created_at), 'HH:mm')}</span>
                                    </div>
                                    <div className="meal-macros">
                                        <span>P: {Math.round(meal.protein)}g</span>
                                        <span>C: {Math.round(meal.carbs)}g</span>
                                        <span>G: {Math.round(meal.fat)}g</span>
                                    </div>
                                    <div className="meal-calories">
                                        {meal.calories} <small>kcal</small>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="empty-state">
                                <p>Nenhuma refeição registrada hoje.</p>
                                <button className="btn btn-secondary btn-sm" onClick={() => navigate('/nutrition/chat')}>
                                    Perguntar sugestão à IA
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Quick Actions / Integration */}
                <div className="quick-actions-grid">
                    <div className="card action-card hydration">
                        <div className="action-icon"><Droplets size={24} /></div>
                        <div className="action-content">
                            <span className="action-title">Hidratação</span>
                            <span className="action-desc">2.5L / 3.5L atingidos</span>
                        </div>
                        <button className="btn btn-circle"><Plus size={20} /></button>
                    </div>
                    <div className="card action-card workout-fuel">
                        <div className="action-icon"><Zap size={24} /></div>
                        <div className="action-content">
                            <span className="action-title">Fueling de Treino</span>
                            <span className="action-desc">Sugestão baseada no seu próximo treino</span>
                        </div>
                        <ChevronRight size={20} />
                    </div>
                </div>
            </div>
        </div>
    );
}

function MacroRing({ label, current, target, color, unit }) {
    const percent = Math.min(Math.round((current / target) * 100), 100);
    const radius = 35;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percent / 100) * circumference;

    return (
        <div className="macro-ring-item">
            <div className="ring-svg-wrapper">
                <svg width="80" height="80">
                    <circle
                        className="ring-bg"
                        cx="40" cy="40" r={radius}
                        strokeWidth="6"
                        fill="transparent"
                        stroke="#f3f4f6"
                    />
                    <circle
                        className="ring-fill"
                        cx="40" cy="40" r={radius}
                        strokeWidth="6"
                        fill="transparent"
                        stroke={color}
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                    />
                </svg>
                <div className="ring-content">
                    <span className="ring-percent">{percent}%</span>
                </div>
            </div>
            <span className="macro-label">{label}</span>
            <span className="macro-values">{Math.round(current)}{unit} / {target}{unit}</span>
        </div>
    );
}
