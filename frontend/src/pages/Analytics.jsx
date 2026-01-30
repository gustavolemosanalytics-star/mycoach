import { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar, Cell, Legend
} from 'recharts';
import { TrendingUp, Activity, Zap, Info } from 'lucide-react';
import './Analytics.css';

export default function Analytics() {
    const [performanceData, setPerformanceData] = useState([]);
    const [hrDistribution, setHrDistribution] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [perfRes, hrRes] = await Promise.all([
                analyticsAPI.getPerformanceLoad(90),
                analyticsAPI.getHRZones(30)
            ]);
            setPerformanceData(perfRes.data);
            setHrDistribution(hrRes.data);
        } catch (err) {
            console.error('Error loading analytics:', err);
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) return <div className="loading-screen"><div className="loading-spinner"></div></div>;

    const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#7c3aed'];

    return (
        <div className="analytics-page">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Laboratório de Performance 📈</h1>
                    <p className="page-subtitle">Análise profunda da sua evolução atlética</p>
                </div>
            </header>

            <div className="analytics-grid">
                {/* Performance Load Chart */}
                <div className="card full-width chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Carga de Treinamento (CTL/ATL)</h3>
                        <div className="info-badge">
                            <Info size={14} /> Entenda o gráfico
                        </div>
                    </div>
                    <div className="chart-wrapper" style={{ height: '400px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={performanceData}>
                                <defs>
                                    <linearGradient id="colorCtl" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis
                                    dataKey="date"
                                    tickFormatter={(str) => new Date(str).toLocaleDateString()}
                                    fontSize={12}
                                />
                                <YAxis fontSize={12} />
                                <Tooltip
                                    labelFormatter={(str) => new Date(str).toLocaleDateString()}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                />
                                <Legend verticalAlign="top" height={36} />
                                <Area
                                    type="monotone"
                                    dataKey="ctl"
                                    name="Fitness (CTL)"
                                    stroke="#3b82f6"
                                    fillOpacity={1}
                                    fill="url(#colorCtl)"
                                    strokeWidth={3}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="atl"
                                    name="Fadiga (ATL)"
                                    stroke="#ef4444"
                                    strokeWidth={2}
                                    dot={false}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* HR Zones Distribution */}
                <div className="card chart-card">
                    <h3 className="card-title">Distribuição de Zonas de Intensidade</h3>
                    <div className="chart-wrapper" style={{ height: '300px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={hrDistribution} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                                <XAxis type="number" hide />
                                <YAxis dataKey="zone" type="category" fontSize={12} width={120} />
                                <Tooltip cursor={{ fill: 'transparent' }} />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                    {hrDistribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Insights Summary */}
                <div className="card analytics-summary-card">
                    <h3 className="card-title">Análise do Período</h3>
                    <div className="insights-list">
                        <div className="analytics-insight-item">
                            <div className="insight-icon fitness"><TrendingUp size={20} /></div>
                            <div className="insight-content">
                                <span className="insight-label">Status de Fitness</span>
                                <span className="insight-value text-primary">Em Evolução (+12% vs mês anterior)</span>
                            </div>
                        </div>
                        <div className="analytics-insight-item">
                            <div className="insight-icon fatigue"><Activity size={20} /></div>
                            <div className="insight-content">
                                <span className="insight-label">Gerenciamento de Fadiga</span>
                                <span className="insight-value text-error">Risco Moderado (TSB: -15)</span>
                            </div>
                        </div>
                        <div className="analytics-insight-item">
                            <div className="insight-icon zap"><Zap size={20} /></div>
                            <div className="insight-content">
                                <span className="insight-label">Aerobic Base</span>
                                <span className="insight-value text-success">65% do tempo em Z2</span>
                            </div>
                        </div>
                    </div>
                    <button className="btn btn-primary btn-full" style={{ marginTop: 'var(--space-6)' }}>
                        Gerar Relatório IA Detalhado
                    </button>
                </div>
            </div>
        </div>
    );
}
