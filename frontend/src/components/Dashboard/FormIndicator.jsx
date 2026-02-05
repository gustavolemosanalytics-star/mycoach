/**
 * Form Indicator Component
 * Displays current training form status (TSB)
 */
import React from 'react';
import './FormIndicator.css';

const FormIndicator = ({ ctl = 0, atl = 0, tsb = 0, status = {} }) => {
    const getFormDescription = () => {
        if (tsb > 25) return 'Você está muito descansado. Excelente momento para uma prova ou treino de qualidade.';
        if (tsb > 10) return 'Boa forma! Você está fresco e pronto para treinos de qualidade.';
        if (tsb > -10) return 'Estado neutro. Bom equilíbrio entre treino e recuperação.';
        if (tsb > -20) return 'Acumulando fadiga. Considere diminuir a intensidade.';
        return 'Atenção! Risco de overtraining. Priorize descanso e recuperação.';
    };

    return (
        <div className="form-indicator">
            <div className="form-indicator-header">
                <h3>Sua Forma Atual</h3>
                <span
                    className="form-status-badge"
                    style={{ backgroundColor: status.color || '#6b7280' }}
                >
                    {status.text || 'Sem dados'}
                </span>
            </div>

            <div className="form-indicator-tsb">
                <span className="tsb-value" style={{ color: status.color || '#6b7280' }}>
                    {tsb.toFixed(0)}
                </span>
                <span className="tsb-label">TSB</span>
            </div>

            <p className="form-description">{getFormDescription()}</p>

            <div className="form-metrics-row">
                <div className="form-metric">
                    <span className="metric-icon">💪</span>
                    <span className="metric-value ctl">{ctl.toFixed(0)}</span>
                    <span className="metric-label">Fitness (CTL)</span>
                </div>
                <div className="form-metric">
                    <span className="metric-icon">😓</span>
                    <span className="metric-value atl">{atl.toFixed(0)}</span>
                    <span className="metric-label">Fadiga (ATL)</span>
                </div>
            </div>
        </div>
    );
};

export default FormIndicator;
