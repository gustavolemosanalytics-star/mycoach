/**
 * Settings Page
 * Athlete configuration, Strava connection, thresholds
 */
import React, { useState, useEffect } from 'react';
import StravaConnect from '../components/Settings/StravaConnect';
import { athleteApi } from '../services/api';
import './Settings.css';

const Settings = () => {
    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            const data = await athleteApi.getConfig();
            setConfig(data);
        } catch (error) {
            console.error('Error loading config:', error);
        }
        setLoading(false);
    };

    const handleChange = (field, value) => {
        setConfig(prev => ({ ...prev, [field]: value }));
    };

    const handleSave = async () => {
        setSaving(true);
        setMessage(null);
        try {
            await athleteApi.updateConfig(config);
            setMessage({ type: 'success', text: 'Configurações salvas com sucesso!' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Erro ao salvar: ' + error.message });
        }
        setSaving(false);
    };

    const formatPace = (seconds) => {
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min}:${sec.toString().padStart(2, '0')}`;
    };

    if (loading) {
        return <div className="settings-page loading">Carregando...</div>;
    }

    return (
        <div className="settings-page">
            <h1>Configurações</h1>

            <div className="settings-grid">
                {/* Strava Connection */}
                <div className="settings-section">
                    <StravaConnect />
                </div>

                {/* Athlete Profile */}
                <div className="settings-section">
                    <h2>Perfil do Atleta</h2>
                    <div className="form-grid">
                        <div className="form-field">
                            <label>Nome</label>
                            <input
                                type="text"
                                value={config?.name || ''}
                                onChange={(e) => handleChange('name', e.target.value)}
                                placeholder="Seu nome"
                            />
                        </div>
                        <div className="form-field">
                            <label>Peso Atual (kg)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={config?.weight_kg || ''}
                                onChange={(e) => handleChange('weight_kg', parseFloat(e.target.value))}
                            />
                        </div>
                        <div className="form-field">
                            <label>Peso Meta (kg)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={config?.target_weight_kg || ''}
                                onChange={(e) => handleChange('target_weight_kg', parseFloat(e.target.value))}
                            />
                        </div>
                        <div className="form-field">
                            <label>Altura (cm)</label>
                            <input
                                type="number"
                                value={config?.height_cm || ''}
                                onChange={(e) => handleChange('height_cm', parseInt(e.target.value))}
                            />
                        </div>
                    </div>
                </div>

                {/* Training Thresholds */}
                <div className="settings-section">
                    <h2>Limiares de Treino</h2>
                    <div className="thresholds-grid">
                        <div className="threshold-card bike">
                            <span className="threshold-icon">🚴</span>
                            <h3>Bike</h3>
                            <div className="form-field">
                                <label>FTP (watts)</label>
                                <input
                                    type="number"
                                    value={config?.ftp_watts || ''}
                                    onChange={(e) => handleChange('ftp_watts', parseInt(e.target.value))}
                                />
                            </div>
                        </div>

                        <div className="threshold-card run">
                            <span className="threshold-icon">🏃</span>
                            <h3>Corrida</h3>
                            <div className="form-field">
                                <label>Pace Limiar (seg/km)</label>
                                <input
                                    type="number"
                                    value={config?.run_threshold_pace_sec || ''}
                                    onChange={(e) => handleChange('run_threshold_pace_sec', parseInt(e.target.value))}
                                />
                                <span className="threshold-preview">
                                    {config?.run_threshold_pace_sec && formatPace(config.run_threshold_pace_sec)}/km
                                </span>
                            </div>
                            <div className="form-field">
                                <label>LTHR (bpm)</label>
                                <input
                                    type="number"
                                    value={config?.run_lthr || ''}
                                    onChange={(e) => handleChange('run_lthr', parseInt(e.target.value))}
                                />
                            </div>
                        </div>

                        <div className="threshold-card swim">
                            <span className="threshold-icon">🏊</span>
                            <h3>Natação</h3>
                            <div className="form-field">
                                <label>CSS (seg/100m)</label>
                                <input
                                    type="number"
                                    value={config?.css_pace_sec || ''}
                                    onChange={(e) => handleChange('css_pace_sec', parseInt(e.target.value))}
                                />
                                <span className="threshold-preview">
                                    {config?.css_pace_sec && formatPace(config.css_pace_sec)}/100m
                                </span>
                            </div>
                        </div>

                        <div className="threshold-card hr">
                            <span className="threshold-icon">❤️</span>
                            <h3>Frequência Cardíaca</h3>
                            <div className="form-field">
                                <label>FC Máxima (bpm)</label>
                                <input
                                    type="number"
                                    value={config?.fc_max || ''}
                                    onChange={(e) => handleChange('fc_max', parseInt(e.target.value))}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Nutrition Goals */}
                <div className="settings-section">
                    <h2>Metas de Nutrição</h2>
                    <div className="form-grid">
                        <div className="form-field">
                            <label>TDEE (kcal/dia)</label>
                            <input
                                type="number"
                                value={config?.tdee_kcal || ''}
                                onChange={(e) => handleChange('tdee_kcal', parseInt(e.target.value))}
                            />
                        </div>
                        <div className="form-field">
                            <label>Déficit Alvo (%)</label>
                            <input
                                type="number"
                                step="0.01"
                                value={(config?.target_deficit_pct * 100) || ''}
                                onChange={(e) => handleChange('target_deficit_pct', parseFloat(e.target.value) / 100)}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {message && (
                <div className={`settings-message ${message.type}`}>
                    {message.text}
                </div>
            )}

            <div className="settings-actions">
                <button
                    className="save-button"
                    onClick={handleSave}
                    disabled={saving}
                >
                    {saving ? 'Salvando...' : 'Salvar Configurações'}
                </button>
            </div>
        </div>
    );
};

export default Settings;
