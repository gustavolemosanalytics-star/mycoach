/**
 * Strava Connect Component
 * Handles Strava OAuth flow and sync
 */
import React, { useState, useEffect } from 'react';
import './StravaConnect.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const StravaConnect = () => {
    const [status, setStatus] = useState({ connected: false, loading: true });
    const [syncing, setSyncing] = useState(false);
    const [syncResult, setSyncResult] = useState(null);

    useEffect(() => {
        checkStatus();
    }, []);

    const checkStatus = async () => {
        try {
            const response = await fetch(`${API_URL}/api/strava/status`);
            const data = await response.json();
            setStatus({ ...data, loading: false });
        } catch (error) {
            console.error('Error checking Strava status:', error);
            setStatus({ connected: false, loading: false, error: true });
        }
    };

    const handleConnect = async () => {
        try {
            const response = await fetch(`${API_URL}/api/strava/auth`);
            const data = await response.json();
            window.location.href = data.url;
        } catch (error) {
            console.error('Error getting auth URL:', error);
        }
    };

    const handleSync = async () => {
        setSyncing(true);
        setSyncResult(null);
        try {
            const response = await fetch(`${API_URL}/api/strava/sync?days_back=30`, {
                method: 'POST'
            });
            const data = await response.json();
            setSyncResult({
                success: true,
                count: data.synced_activities,
                activities: data.activities || []
            });
        } catch (error) {
            console.error('Error syncing:', error);
            setSyncResult({ success: false, error: error.message });
        }
        setSyncing(false);
    };

    if (status.loading) {
        return (
            <div className="strava-connect loading">
                <div className="loading-spinner"></div>
                <p>Verificando conexão...</p>
            </div>
        );
    }

    return (
        <div className="strava-connect">
            <div className="strava-header">
                <div className="strava-logo">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
                        <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066l-2.084 4.116z" />
                        <path d="M7.355 0L0 13.828h4.128l3.227-6.387 3.227 6.387h4.128L7.355 0z" opacity=".4" />
                    </svg>
                </div>
                <h3>Strava</h3>
                <span className={`status-badge ${status.connected ? 'connected' : 'disconnected'}`}>
                    {status.connected ? 'Conectado' : 'Desconectado'}
                </span>
            </div>

            {status.connected ? (
                <div className="strava-connected">
                    <p className="connected-info">
                        <span className="check-icon">✓</span>
                        Sua conta Strava está conectada
                    </p>

                    <button
                        className="sync-button"
                        onClick={handleSync}
                        disabled={syncing}
                    >
                        {syncing ? (
                            <>
                                <span className="spinner"></span>
                                Sincronizando...
                            </>
                        ) : (
                            <>
                                <span className="sync-icon">🔄</span>
                                Sincronizar Atividades
                            </>
                        )}
                    </button>

                    {syncResult && (
                        <div className={`sync-result ${syncResult.success ? 'success' : 'error'}`}>
                            {syncResult.success ? (
                                <>
                                    <strong>{syncResult.count}</strong> atividades sincronizadas
                                    {syncResult.activities?.length > 0 && (
                                        <ul className="synced-list">
                                            {syncResult.activities.slice(0, 5).map((act, i) => (
                                                <li key={i}>
                                                    {act.date}: {act.name} ({act.sport}) - TSS: {act.tss?.toFixed(0)}
                                                </li>
                                            ))}
                                        </ul>
                                    )}
                                </>
                            ) : (
                                <span>Erro: {syncResult.error}</span>
                            )}
                        </div>
                    )}
                </div>
            ) : (
                <div className="strava-disconnected">
                    <p>Conecte sua conta Strava para sincronizar suas atividades automaticamente.</p>
                    <button className="connect-button" onClick={handleConnect}>
                        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                            <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066l-2.084 4.116z" />
                            <path d="M7.355 0L0 13.828h4.128l3.227-6.387 3.227 6.387h4.128L7.355 0z" opacity=".6" />
                        </svg>
                        Conectar com Strava
                    </button>
                </div>
            )}
        </div>
    );
};

export default StravaConnect;
