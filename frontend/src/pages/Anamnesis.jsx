import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { nutritionAPI } from '../services/api';
import {
    User,
    Ruler,
    Calendar,
    Activity,
    Target,
    Utensils,
    ChevronRight,
    ChevronLeft,
    CheckCircle2
} from 'lucide-react';
import './Anamnesis.css';

export default function Anamnesis() {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        weight: '',
        height: '',
        age: '',
        gender: 'male',
        activity_level: 'moderate',
        goal: 'maintenance',
        restrictions: [],
        preferences: []
    });

    const activityOptions = [
        { value: 'sedentary', label: 'Sedentário', desc: 'Pouco ou nenhum exercício' },
        { value: 'light', label: 'Leve', desc: 'Exercício leve 1-3 dias/semana' },
        { value: 'moderate', label: 'Moderado', desc: 'Exercício moderado 3-5 dias/semana' },
        { value: 'active', label: 'Ativo', desc: 'Exercício intenso 6-7 dias/semana' },
        { value: 'very_active', label: 'Muito Ativo', desc: 'Atleta de elite ou trabalho braçal' },
    ];

    const goalOptions = [
        { value: 'cutting', label: 'Cutting', desc: 'Perda de gordura com preservação muscular' },
        { value: 'maintenance', label: 'Manutenção', desc: 'Manter peso e melhorar performance' },
        { value: 'bulking', label: 'Bulking', desc: 'Ganho de massa muscular (Superávit)' },
    ];

    const handleNext = () => setStep(s => s + 1);
    const handleBack = () => setStep(s => s - 1);

    const handleSubmit = async () => {
        setIsLoading(true);
        try {
            await nutritionAPI.updateProfile(formData);
            setStep(5); // Success step
        } catch (err) {
            alert('Erro ao salvar perfil nutricional');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const renderStep = () => {
        switch (step) {
            case 1:
                return (
                    <div className="anamnesis-step anim-fade-in">
                        <h2 className="step-title">Bio Inteligente</h2>
                        <p className="step-desc">Vamos começar com suas informações básicas.</p>
                        <div className="input-group-grid">
                            <div className="input-field">
                                <label><User size={16} /> Sexo</label>
                                <select
                                    value={formData.gender}
                                    onChange={e => setFormData({ ...formData, gender: e.target.value })}
                                >
                                    <option value="male">Masculino</option>
                                    <option value="female">Feminino</option>
                                </select>
                            </div>
                            <div className="input-field">
                                <label><Calendar size={16} /> Idade</label>
                                <input
                                    type="number"
                                    placeholder="Ex: 28"
                                    value={formData.age}
                                    onChange={e => setFormData({ ...formData, age: e.target.value })}
                                />
                            </div>
                            <div className="input-field">
                                <label><Ruler size={16} /> Altura (cm)</label>
                                <input
                                    type="number"
                                    placeholder="Ex: 175"
                                    value={formData.height}
                                    onChange={e => setFormData({ ...formData, height: e.target.value })}
                                />
                            </div>
                            <div className="input-field">
                                <label><Activity size={16} /> Peso Atual (kg)</label>
                                <input
                                    type="number"
                                    placeholder="Ex: 75.5"
                                    value={formData.weight}
                                    onChange={e => setFormData({ ...formData, weight: e.target.value })}
                                />
                            </div>
                        </div>
                        <button className="btn btn-primary btn-next" onClick={handleNext}>
                            Continuar <ChevronRight size={18} />
                        </button>
                    </div>
                );
            case 2:
                return (
                    <div className="anamnesis-step anim-fade-in">
                        <h2 className="step-title">Nível de Atividade</h2>
                        <p className="step-desc">Como é sua rotina semanal de exercícios?</p>
                        <div className="options-list">
                            {activityOptions.map(opt => (
                                <div
                                    key={opt.value}
                                    className={`option-card ${formData.activity_level === opt.value ? 'selected' : ''}`}
                                    onClick={() => setFormData({ ...formData, activity_level: opt.value })}
                                >
                                    <div className="option-info">
                                        <span className="option-label">{opt.label}</span>
                                        <span className="option-desc">{opt.desc}</span>
                                    </div>
                                    {formData.activity_level === opt.value && <CheckCircle2 className="text-primary" size={20} />}
                                </div>
                            ))}
                        </div>
                        <div className="footer-actions">
                            <button className="btn btn-ghost" onClick={handleBack}><ChevronLeft size={18} /> Voltar</button>
                            <button className="btn btn-primary" onClick={handleNext}>Próximo <ChevronRight size={18} /></button>
                        </div>
                    </div>
                );
            case 3:
                return (
                    <div className="anamnesis-step anim-fade-in">
                        <h2 className="step-title">Objetivo Principal</h2>
                        <p className="step-desc">O que você busca com o MyCoach Nutrition?</p>
                        <div className="options-list">
                            {goalOptions.map(opt => (
                                <div
                                    key={opt.value}
                                    className={`option-card ${formData.goal === opt.value ? 'selected' : ''}`}
                                    onClick={() => setFormData({ ...formData, goal: opt.value })}
                                >
                                    <div className="option-info">
                                        <span className="option-label">{opt.label}</span>
                                        <span className="option-desc">{opt.desc}</span>
                                    </div>
                                    {formData.goal === opt.value && <Target className="text-primary" size={20} />}
                                </div>
                            ))}
                        </div>
                        <div className="footer-actions">
                            <button className="btn btn-ghost" onClick={handleBack}><ChevronLeft size={18} /> Voltar</button>
                            <button className="btn btn-primary" onClick={handleNext}>Próximo <ChevronRight size={18} /></button>
                        </div>
                    </div>
                );
            case 4:
                return (
                    <div className="anamnesis-step anim-fade-in">
                        <h2 className="step-title">Preferências e Dieta</h2>
                        <p className="step-desc">Alguma restrição ou preferência importante?</p>
                        <div className="input-field">
                            <label><Utensils size={16} /> Restrições (ex: Vegano, Gluten-free)</label>
                            <textarea
                                placeholder="Digite aqui..."
                                className="modern-textarea"
                                rows={4}
                                onChange={e => setFormData({ ...formData, restrictions: e.target.value.split(',') })}
                            />
                        </div>
                        <div className="footer-actions">
                            <button className="btn btn-ghost" onClick={handleBack}><ChevronLeft size={18} /> Voltar</button>
                            <button className="btn btn-primary" onClick={handleSubmit} disabled={isLoading}>
                                {isLoading ? 'Calculando...' : 'Finalizar Anamnese'}
                            </button>
                        </div>
                    </div>
                );
            case 5:
                return (
                    <div className="anamnesis-step success-step anim-scale-up">
                        <div className="success-icon-wrapper">
                            <CheckCircle2 size={64} className="text-success" />
                        </div>
                        <h2 className="step-title">Tudo Pronto!</h2>
                        <p className="step-desc">Seu perfil nutricional foi criado. Nosso Motor Neural calculou seus macros ideais para o seu objetivo.</p>
                        <button className="btn btn-primary w-full" onClick={() => navigate('/nutrition')}>
                            Ver Meu Dashboard de Nutrição
                        </button>
                    </div>
                );
        }
    };

    return (
        <div className="anamnesis-page">
            <div className="anamnesis-container card">
                <div className="progress-bar-container">
                    <div className="progress-fill" style={{ width: `${(step / 4) * 100}%` }}></div>
                </div>
                {renderStep()}
            </div>
        </div>
    );
}
