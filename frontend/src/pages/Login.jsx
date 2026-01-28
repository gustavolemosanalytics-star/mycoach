import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react';
import './Auth.css';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await login(email, password);
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || 'Erro ao fazer login');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-header">
                    <div className="auth-logo">🏃</div>
                    <h1>MyCoach</h1>
                    <p>Sua jornada de treino começa aqui</p>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                    {error && <div className="auth-error">{error}</div>}

                    <div className="input-group">
                        <label className="input-label">Email</label>
                        <div className="input-with-icon">
                            <Mail className="input-icon" size={18} />
                            <input
                                type="email"
                                className="input"
                                placeholder="seu@email.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label className="input-label">Senha</label>
                        <div className="input-with-icon">
                            <Lock className="input-icon" size={18} />
                            <input
                                type={showPassword ? 'text' : 'password'}
                                className="input"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
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

                    <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
                        {isLoading ? 'Entrando...' : 'Entrar'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>Não tem uma conta? <Link to="/register">Cadastre-se</Link></p>
                </div>
            </div>

            <div className="auth-decoration">
                <div className="decoration-content">
                    <h2>Treine com propósito</h2>
                    <p>Acompanhe seus treinos, monitore seu progresso e alcance seus objetivos com insights personalizados.</p>
                    <div className="decoration-features">
                        <div className="feature">
                            <span className="feature-icon">📊</span>
                            <span>Analytics avançados</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">🏆</span>
                            <span>Gamificação</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">🔗</span>
                            <span>Integração Strava/Garmin</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
