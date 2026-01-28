import { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import {
    SmilePlus,
    Battery,
    Moon,
    Brain,
    Activity,
    Scale,
    Droplets,
    Save,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
import { wellnessAPI } from '../services/api';
import './Wellness.css';

const MOODS = [
    { value: 1, emoji: '😢', label: 'Muito mal' },
    { value: 2, emoji: '😔', label: 'Mal' },
    { value: 3, emoji: '😐', label: 'Normal' },
    { value: 4, emoji: '😊', label: 'Bem' },
    { value: 5, emoji: '🤩', label: 'Ótimo' }
];

export default function Wellness() {
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [formData, setFormData] = useState({
        mood: null,
        energy_level: null,
        motivation: null,
        sleep_start: '',
        sleep_end: '',
        sleep_quality: null,
        muscle_soreness: null,
        fatigue_level: null,
        stress_level: null,
        resting_heart_rate: '',
        weight: '',
        water_intake: '',
        notes: ''
    });
    const [isSaving, setIsSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState('');
    const [trends, setTrends] = useState(null);

    useEffect(() => {
        loadWellnessData();
    }, [selectedDate]);

    useEffect(() => {
        loadTrends();
    }, []);

    const loadWellnessData = async () => {
        try {
            const dateStr = format(selectedDate, 'yyyy-MM-dd');
            const response = await wellnessAPI.getByDate(dateStr);
            if (response.data) {
                setFormData({
                    mood: response.data.mood,
                    energy_level: response.data.energy_level,
                    motivation: response.data.motivation,
                    sleep_start: response.data.sleep_start || '',
                    sleep_end: response.data.sleep_end || '',
                    sleep_quality: response.data.sleep_quality,
                    muscle_soreness: response.data.muscle_soreness,
                    fatigue_level: response.data.fatigue_level,
                    stress_level: response.data.stress_level,
                    resting_heart_rate: response.data.resting_heart_rate || '',
                    weight: response.data.weight || '',
                    water_intake: response.data.water_intake || '',
                    notes: response.data.notes || ''
                });
            } else {
                setFormData({
                    mood: null,
                    energy_level: null,
                    motivation: null,
                    sleep_start: '',
                    sleep_end: '',
                    sleep_quality: null,
                    muscle_soreness: null,
                    fatigue_level: null,
                    stress_level: null,
                    resting_heart_rate: '',
                    weight: '',
                    water_intake: '',
                    notes: ''
                });
            }
        } catch (error) {
            // Entry doesn't exist for this date
            setFormData({
                mood: null,
                energy_level: null,
                motivation: null,
                sleep_start: '',
                sleep_end: '',
                sleep_quality: null,
                muscle_soreness: null,
                fatigue_level: null,
                stress_level: null,
                resting_heart_rate: '',
                weight: '',
                water_intake: '',
                notes: ''
            });
        }
    };

    const loadTrends = async () => {
        try {
            const response = await wellnessAPI.getTrends(30);
            setTrends(response.data);
        } catch (error) {
            console.error('Error loading trends:', error);
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        setSaveMessage('');

        try {
            await wellnessAPI.create({
                date: format(selectedDate, 'yyyy-MM-dd'),
                ...formData,
                resting_heart_rate: formData.resting_heart_rate ? parseInt(formData.resting_heart_rate) : null,
                weight: formData.weight ? parseFloat(formData.weight) : null,
                water_intake: formData.water_intake ? parseFloat(formData.water_intake) : null
            });
            setSaveMessage('Salvo com sucesso! ✓');
            loadTrends();
        } catch (error) {
            setSaveMessage('Erro ao salvar');
        } finally {
            setIsSaving(false);
            setTimeout(() => setSaveMessage(''), 3000);
        }
    };

    const handleMoodSelect = (value) => {
        setFormData({ ...formData, mood: value });
    };

    const handleScaleSelect = (field, value) => {
        setFormData({ ...formData, [field]: formData[field] === value ? null : value });
    };

    const navigateDate = (days) => {
        setSelectedDate(prev => {
            const newDate = new Date(prev);
            newDate.setDate(prev.getDate() + days);
            return newDate > new Date() ? new Date() : newDate;
        });
    };

    const isToday = format(selectedDate, 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd');

    return (
        <div className="wellness-page">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Bem-estar</h1>
                    <p className="page-subtitle">Registre como você está se sentindo</p>
                </div>
            </header>

            {/* Date Navigator */}
            <div className="date-navigator">
                <button className="btn btn-ghost" onClick={() => navigateDate(-1)}>
                    <ChevronLeft size={20} />
                </button>
                <span className="current-date">
                    {isToday ? 'Hoje' : format(selectedDate, "EEEE, d 'de' MMMM", { locale: ptBR })}
                </span>
                <button
                    className="btn btn-ghost"
                    onClick={() => navigateDate(1)}
                    disabled={isToday}
                >
                    <ChevronRight size={20} />
                </button>
            </div>

            <div className="wellness-grid">
                {/* Mood Section */}
                <div className="card wellness-section">
                    <div className="section-header">
                        <SmilePlus size={20} />
                        <h3>Como você está se sentindo?</h3>
                    </div>
                    <div className="mood-selector">
                        {MOODS.map(({ value, emoji, label }) => (
                            <button
                                key={value}
                                className={`mood-option ${formData.mood === value ? 'selected' : ''}`}
                                onClick={() => handleMoodSelect(value)}
                            >
                                <span className="emoji">{emoji}</span>
                                <span className="label">{label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Energy & Motivation */}
                <div className="card wellness-section">
                    <div className="section-header">
                        <Battery size={20} />
                        <h3>Energia e Motivação</h3>
                    </div>

                    <div className="scale-group">
                        <label>Nível de Energia</label>
                        <div className="scale-buttons">
                            {[1, 2, 3, 4, 5].map((val) => (
                                <button
                                    key={val}
                                    className={`scale-btn ${formData.energy_level === val ? 'selected' : ''}`}
                                    onClick={() => handleScaleSelect('energy_level', val)}
                                >
                                    {val}
                                </button>
                            ))}
                        </div>
                        <div className="scale-labels">
                            <span>Exausto</span>
                            <span>Energizado</span>
                        </div>
                    </div>

                    <div className="scale-group">
                        <label>Motivação</label>
                        <div className="scale-buttons">
                            {[1, 2, 3, 4, 5].map((val) => (
                                <button
                                    key={val}
                                    className={`scale-btn ${formData.motivation === val ? 'selected' : ''}`}
                                    onClick={() => handleScaleSelect('motivation', val)}
                                >
                                    {val}
                                </button>
                            ))}
                        </div>
                        <div className="scale-labels">
                            <span>Sem motivação</span>
                            <span>Super motivado</span>
                        </div>
                    </div>
                </div>

                {/* Sleep */}
                <div className="card wellness-section">
                    <div className="section-header">
                        <Moon size={20} />
                        <h3>Sono</h3>
                    </div>

                    <div className="time-inputs">
                        <div className="input-group">
                            <label className="input-label">Hora de dormir</label>
                            <input
                                type="time"
                                className="input"
                                value={formData.sleep_start}
                                onChange={(e) => setFormData({ ...formData, sleep_start: e.target.value })}
                            />
                        </div>
                        <div className="input-group">
                            <label className="input-label">Hora de acordar</label>
                            <input
                                type="time"
                                className="input"
                                value={formData.sleep_end}
                                onChange={(e) => setFormData({ ...formData, sleep_end: e.target.value })}
                            />
                        </div>
                    </div>

                    <div className="scale-group">
                        <label>Qualidade do Sono</label>
                        <div className="scale-buttons">
                            {[1, 2, 3, 4, 5].map((val) => (
                                <button
                                    key={val}
                                    className={`scale-btn ${formData.sleep_quality === val ? 'selected' : ''}`}
                                    onClick={() => handleScaleSelect('sleep_quality', val)}
                                >
                                    {val}
                                </button>
                            ))}
                        </div>
                        <div className="scale-labels">
                            <span>Péssimo</span>
                            <span>Excelente</span>
                        </div>
                    </div>
                </div>

                {/* Physical State */}
                <div className="card wellness-section">
                    <div className="section-header">
                        <Activity size={20} />
                        <h3>Estado Físico</h3>
                    </div>

                    <div className="scale-group">
                        <label>Dor Muscular</label>
                        <div className="scale-buttons">
                            {[1, 2, 3, 4, 5].map((val) => (
                                <button
                                    key={val}
                                    className={`scale-btn ${formData.muscle_soreness === val ? 'selected' : ''}`}
                                    onClick={() => handleScaleSelect('muscle_soreness', val)}
                                >
                                    {val}
                                </button>
                            ))}
                        </div>
                        <div className="scale-labels">
                            <span>Nenhuma</span>
                            <span>Muita</span>
                        </div>
                    </div>

                    <div className="scale-group">
                        <label>Nível de Fadiga</label>
                        <div className="scale-buttons">
                            {[1, 2, 3, 4, 5].map((val) => (
                                <button
                                    key={val}
                                    className={`scale-btn ${formData.fatigue_level === val ? 'selected' : ''}`}
                                    onClick={() => handleScaleSelect('fatigue_level', val)}
                                >
                                    {val}
                                </button>
                            ))}
                        </div>
                        <div className="scale-labels">
                            <span>Descansado</span>
                            <span>Muito cansado</span>
                        </div>
                    </div>
                </div>

                {/* Stress */}
                <div className="card wellness-section">
                    <div className="section-header">
                        <Brain size={20} />
                        <h3>Estresse</h3>
                    </div>

                    <div className="scale-group">
                        <label>Nível de Estresse</label>
                        <div className="scale-buttons">
                            {[1, 2, 3, 4, 5].map((val) => (
                                <button
                                    key={val}
                                    className={`scale-btn ${formData.stress_level === val ? 'selected' : ''}`}
                                    onClick={() => handleScaleSelect('stress_level', val)}
                                >
                                    {val}
                                </button>
                            ))}
                        </div>
                        <div className="scale-labels">
                            <span>Relaxado</span>
                            <span>Muito estressado</span>
                        </div>
                    </div>
                </div>

                {/* Metrics */}
                <div className="card wellness-section">
                    <div className="section-header">
                        <Scale size={20} />
                        <h3>Métricas</h3>
                    </div>

                    <div className="metrics-grid">
                        <div className="input-group">
                            <label className="input-label">FC em Repouso (bpm)</label>
                            <input
                                type="number"
                                className="input"
                                placeholder="Ex: 55"
                                value={formData.resting_heart_rate}
                                onChange={(e) => setFormData({ ...formData, resting_heart_rate: e.target.value })}
                            />
                        </div>
                        <div className="input-group">
                            <label className="input-label">Peso (kg)</label>
                            <input
                                type="number"
                                step="0.1"
                                className="input"
                                placeholder="Ex: 70.5"
                                value={formData.weight}
                                onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                            />
                        </div>
                        <div className="input-group">
                            <label className="input-label">Água (litros)</label>
                            <input
                                type="number"
                                step="0.1"
                                className="input"
                                placeholder="Ex: 2.5"
                                value={formData.water_intake}
                                onChange={(e) => setFormData({ ...formData, water_intake: e.target.value })}
                            />
                        </div>
                    </div>
                </div>

                {/* Notes */}
                <div className="card wellness-section notes-section">
                    <div className="section-header">
                        <h3>Notas</h3>
                    </div>
                    <textarea
                        className="input notes-input"
                        placeholder="Como foi seu dia? Algo importante para registrar?"
                        value={formData.notes}
                        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    />
                </div>

                {/* Trends */}
                {trends && (
                    <div className="card wellness-section trends-section">
                        <div className="section-header">
                            <h3>Tendências (últimos 30 dias)</h3>
                        </div>
                        <div className="trends-grid">
                            <div className="trend-item">
                                <span className="trend-label">Humor Médio</span>
                                <span className="trend-value">{trends.avg_mood?.toFixed(1) || '--'}/5</span>
                            </div>
                            <div className="trend-item">
                                <span className="trend-label">Energia Média</span>
                                <span className="trend-value">{trends.avg_energy?.toFixed(1) || '--'}/5</span>
                            </div>
                            <div className="trend-item">
                                <span className="trend-label">Sono Médio</span>
                                <span className="trend-value">{trends.avg_sleep_hours?.toFixed(1) || '--'}h</span>
                            </div>
                            <div className="trend-item">
                                <span className="trend-label">Tendência</span>
                                <span className={`trend-value ${trends.trend_direction}`}>
                                    {trends.trend_direction === 'improving' && '📈 Melhorando'}
                                    {trends.trend_direction === 'declining' && '📉 Declinando'}
                                    {trends.trend_direction === 'stable' && '➡️ Estável'}
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Save Button */}
            <div className="save-bar">
                <button
                    className="btn btn-primary btn-lg"
                    onClick={handleSave}
                    disabled={isSaving}
                >
                    <Save size={20} />
                    {isSaving ? 'Salvando...' : 'Salvar'}
                </button>
                {saveMessage && (
                    <span className={`save-message ${saveMessage.includes('Erro') ? 'error' : 'success'}`}>
                        {saveMessage}
                    </span>
                )}
            </div>
        </div>
    );
}
