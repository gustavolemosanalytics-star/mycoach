import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react';
import './Auth.css';

export default function Register() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        sport_focus: 'triathlon'
    });
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('As senhas não coincidem');
            return;
        }

        if (formData.password.length < 6) {
            setError('A senha deve ter pelo menos 6 caracteres');
            return;
        }

        setIsLoading(true);

        try {
            await register({
                name: formData.name,
                email: formData.email,
                password: formData.password,
                sport_focus: formData.sport_focus
            });
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || 'Erro ao criar conta');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-header">
                    <div className="auth-logo">🏃</div>
                    <h1>Criar Conta</h1>
                    <p>Junte-se à comunidade MyCoach</p>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                    {error && <div className="auth-error">{error}</div>}

                    <div className="input-group">
                        <label className="input-label">Nome</label>
                        <div className="input-with-icon">
                            <User className="input-icon" size={18} />
                            <input
                                type="text"
                                name="name"
                                className="input"
                                placeholder="Seu nome"
                                value={formData.name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label className="input-label">Email</label>
                        <div className="input-with-icon">
                            <Mail className="input-icon" size={18} />
                            <input
                                type="email"
                                name="email"
                                className="input"
                                placeholder="seu@email.com"
                                value={formData.email}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label className="input-label">Foco Esportivo</label>
                        <select
                            name="sport_focus"
                            className="input"
                            value={formData.sport_focus}
                            onChange={handleChange}
                        >
                            <option value="triathlon">Triathlon</option>
                            <option value="marathon">Maratona</option>
                            <option value="ultra">Ultramaratona</option>
                            <option value="cycling">Ciclismo</option>
                            <option value="swimming">Natação</option>
                        </select>
                    </div>

                    <div className="input-group">
                        <label className="input-label">Senha</label>
                        <div className="input-with-icon">
                            <Lock className="input-icon" size={18} />
                            <input
                                type={showPassword ? 'text' : 'password'}
                                name="password"
                                className="input"
                                placeholder="••••••••"
                                value={formData.password}
                                onChange={handleChange}
                                required
                            />
                            <button
                                type="button"
                                className="input-toggle"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                    </div>

                    <div className="input-group">
                        <label className="input-label">Confirmar Senha</label>
                        <div className="input-with-icon">
                            <Lock className="input-icon" size={18} />
                            <input
                                type="password"
                                name="confirmPassword"
                                className="input"
                                placeholder="••••••••"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
                        {isLoading ? 'Criando conta...' : 'Criar Conta'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>Já tem uma conta? <Link to="/login">Entrar</Link></p>
                </div>
            </div>

            <div className="auth-decoration">
                <div className="decoration-content">
                    <h2>Bem-vindo ao MyCoach</h2>
                    <p>Comece sua jornada para se tornar um atleta melhor.</p>
                    <div className="decoration-stats">
                        <div className="stat">
                            <span className="stat-number">10K+</span>
                            <span className="stat-label">Atletas</span>
                        </div>
                        <div className="stat">
                            <span className="stat-number">1M+</span>
                            <span className="stat-label">Treinos</span>
                        </div>
                        <div className="stat">
                            <span className="stat-number">500K</span>
                            <span className="stat-label">KM corridos</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
