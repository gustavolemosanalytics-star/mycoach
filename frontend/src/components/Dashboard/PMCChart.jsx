/**
 * PMC Chart Component
 * Displays CTL (Fitness), ATL (Fatigue), and TSB (Form) over time
 * Per specification - Performance Management Chart
 */
import React, { useMemo } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import './PMCChart.css';

const PMCChart = ({ data = [], targetDate }) => {
    const chartData = useMemo(() => {
        return data.map(d => ({
            ...d,
            dateFormatted: new Date(d.date).toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit'
            })
        }));
    }, [data]);

    const currentTSB = data.length > 0 ? (data[data.length - 1]?.tsb || 0) : 0;
    const currentCTL = data.length > 0 ? (data[data.length - 1]?.ctl || 0) : 0;
    const currentATL = data.length > 0 ? (data[data.length - 1]?.atl || 0) : 0;

    const getTSBStatus = (tsb) => {
        if (tsb > 25) return { text: 'Muito descansado', color: '#22c55e' };
        if (tsb > 10) return { text: 'Fresh - Boa forma', color: '#10b981' };
        if (tsb > -10) return { text: 'Neutro', color: '#f59e0b' };
        if (tsb > -20) return { text: 'Cansado', color: '#f97316' };
        return { text: 'Overreaching', color: '#ef4444' };
    };

    const status = getTSBStatus(currentTSB);

    if (data.length === 0) {
        return (
            <div className="pmc-chart-container pmc-empty">
                <h2>Performance Management Chart</h2>
                <p>Sem dados de atividades. Sincronize seu Strava para ver as métricas.</p>
            </div>
        );
    }

    return (
        <div className="pmc-chart-container">
            <div className="pmc-header">
                <h2>Performance Management Chart</h2>
                <div className="pmc-status">
                    <span className="pmc-label">Forma atual:</span>
                    <span
                        className="pmc-badge"
                        style={{ backgroundColor: status.color }}
                    >
                        TSB: {currentTSB.toFixed(0)} - {status.text}
                    </span>
                </div>
            </div>

            <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis
                        dataKey="dateFormatted"
                        stroke="#9ca3af"
                        tick={{ fill: '#9ca3af' }}
                    />
                    <YAxis
                        stroke="#9ca3af"
                        tick={{ fill: '#9ca3af' }}
                    />
                    <Tooltip
                        formatter={(value, name) => [value?.toFixed(1), name]}
                        labelFormatter={(label) => `Data: ${label}`}
                        contentStyle={{
                            backgroundColor: '#1f2937',
                            border: '1px solid #374151',
                            borderRadius: '8px',
                            color: '#f3f4f6'
                        }}
                    />
                    <Legend />

                    {/* Reference lines */}
                    <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="5 5" />
                    <ReferenceLine y={15} stroke="#22c55e" strokeDasharray="3 3" label="Race Zone" />
                    <ReferenceLine y={25} stroke="#22c55e" strokeDasharray="3 3" />

                    <Line
                        type="monotone"
                        dataKey="ctl"
                        stroke="#3b82f6"
                        name="CTL (Fitness)"
                        strokeWidth={2}
                        dot={false}
                    />
                    <Line
                        type="monotone"
                        dataKey="atl"
                        stroke="#ef4444"
                        name="ATL (Fadiga)"
                        strokeWidth={2}
                        dot={false}
                    />
                    <Line
                        type="monotone"
                        dataKey="tsb"
                        stroke="#10b981"
                        name="TSB (Forma)"
                        strokeWidth={2}
                        dot={false}
                    />
                </LineChart>
            </ResponsiveContainer>

            <div className="pmc-metrics-grid">
                <div className="pmc-metric pmc-metric-ctl">
                    <div className="pmc-metric-value">{currentCTL.toFixed(0)}</div>
                    <div className="pmc-metric-label">CTL (Fitness)</div>
                </div>
                <div className="pmc-metric pmc-metric-atl">
                    <div className="pmc-metric-value">{currentATL.toFixed(0)}</div>
                    <div className="pmc-metric-label">ATL (Fadiga)</div>
                </div>
                <div className="pmc-metric pmc-metric-tsb">
                    <div className="pmc-metric-value">{currentTSB.toFixed(0)}</div>
                    <div className="pmc-metric-label">TSB (Forma)</div>
                </div>
            </div>
        </div>
    );
};

export default PMCChart;
