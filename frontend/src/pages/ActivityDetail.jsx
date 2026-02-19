import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Heart, Zap, Timer, TrendingUp, Footprints, Sparkles, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react'
import useActivityStore from '../stores/activityStore'
import { formatDistance, formatDuration, formatPace, scoreColor, scoreBg } from '../utils/formatters'
import { SPORT_COLORS, SPORT_LABELS, HR_ZONE_COLORS, HR_ZONE_LABELS } from '../utils/constants'
import HRChart from '../components/charts/HRChart'
import PaceChart from '../components/charts/PaceChart'
import ZonesChart from '../components/charts/ZonesChart'
import LapsTable from '../components/charts/LapsTable'

export default function ActivityDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { currentActivity: act, loading, fetchActivity } = useActivityStore()

  useEffect(() => {
    fetchActivity(id)
  }, [id])

  if (loading || !act) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-[#00E5A0]" size={32} />
      </div>
    )
  }

  const sportColor = SPORT_COLORS[act.sport] || '#6B7280'

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-white">
          <ArrowLeft size={20} />
        </button>
        <div className="flex-1">
          <h1 className="text-lg font-bold text-white">{act.title}</h1>
          <p className="text-sm text-gray-500">
            {act.start_time && new Date(act.start_time).toLocaleDateString('pt-BR')}
          </p>
        </div>
        <div
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: sportColor }}
        />
      </div>

      {/* Score */}
      {act.ai_score != null && (
        <div className={`bg-gradient-to-br ${scoreBg(act.ai_score)} rounded-2xl p-5 text-center`}>
          <p className="text-4xl font-mono font-bold text-white">{act.ai_score}</p>
          <p className="text-sm text-white/80">Score</p>
        </div>
      )}

      {/* Main metrics */}
      <div className="grid grid-cols-3 gap-3">
        <MetricCard icon={<TrendingUp size={14} />} value={formatDistance(act.total_distance_meters)} label="Distância" />
        <MetricCard icon={<Timer size={14} />} value={formatDuration(act.total_timer_seconds)} label="Duração" />
        <MetricCard icon={<Footprints size={14} />} value={formatPace(act.avg_pace_min_km)} label="Pace" />
      </div>

      <div className="grid grid-cols-3 gap-3">
        <MetricCard icon={<Heart size={14} className="text-red-400" />} value={act.avg_hr || '—'} label="FC Média" />
        <MetricCard icon={<Heart size={14} className="text-red-500" />} value={act.max_hr || '—'} label="FC Máx" />
        <MetricCard icon={<Zap size={14} className="text-yellow-400" />} value={act.tss || '—'} label="TSS" />
      </div>

      {/* Advanced metrics if available */}
      {(act.normalized_power || act.avg_cadence || act.total_ascent_m) && (
        <div className="grid grid-cols-3 gap-3">
          {act.normalized_power && <MetricCard value={`${act.normalized_power}W`} label="NP" />}
          {act.avg_cadence && <MetricCard value={act.avg_cadence} label="Cadência" />}
          {act.total_ascent_m && <MetricCard value={`${act.total_ascent_m}m`} label="D+" />}
        </div>
      )}

      {/* HR Chart */}
      {act.hr_stream && <HRChart data={act.hr_stream} />}

      {/* Pace Chart */}
      {act.pace_stream && <PaceChart data={act.pace_stream} />}

      {/* HR Zones */}
      {act.hr_zones && <ZonesChart zones={act.hr_zones} colors={HR_ZONE_COLORS} labels={HR_ZONE_LABELS} title="Zonas de FC" />}

      {/* Laps */}
      {act.laps_data && <LapsTable laps={act.laps_data} />}

      {/* AI Analysis */}
      {act.ai_analysis && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-[#00E5A0]" />
            <h2 className="text-sm font-medium text-[#00E5A0]">Análise do Coach</h2>
          </div>

          {act.ai_analysis.summary && (
            <div className="bg-[#111827] rounded-xl p-4">
              <p className="text-sm text-gray-300">{act.ai_analysis.summary}</p>
            </div>
          )}

          {act.ai_analysis.execution_analysis && (
            <div className="bg-[#111827] rounded-xl p-4">
              <p className="text-xs text-gray-500 mb-1">Execução</p>
              <p className="text-sm text-gray-300">{act.ai_analysis.execution_analysis}</p>
            </div>
          )}

          {act.ai_analysis.highlights?.length > 0 && (
            <div className="bg-[#111827] rounded-xl p-4">
              <p className="text-xs font-medium text-emerald-400 mb-2">Destaques</p>
              <ul className="space-y-1">
                {act.ai_analysis.highlights.map((h, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckCircle2 size={14} className="text-emerald-400 mt-0.5 shrink-0" />
                    <span className="text-sm text-gray-300">{h}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {act.ai_analysis.warnings?.length > 0 && (
            <div className="bg-[#111827] rounded-xl p-4">
              <p className="text-xs font-medium text-amber-400 mb-2">Atenção</p>
              <ul className="space-y-1">
                {act.ai_analysis.warnings.map((w, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <AlertTriangle size={14} className="text-amber-400 mt-0.5 shrink-0" />
                    <span className="text-sm text-gray-300">{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {act.ai_analysis.recommendations?.length > 0 && (
            <div className="bg-[#111827] rounded-xl p-4">
              <p className="text-xs font-medium text-blue-400 mb-2">Recomendações</p>
              <ul className="space-y-1">
                {act.ai_analysis.recommendations.map((r, i) => (
                  <li key={i} className="text-sm text-gray-300">• {r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function MetricCard({ icon, value, label }) {
  return (
    <div className="bg-[#111827] rounded-xl p-3 text-center">
      {icon && <div className="flex justify-center mb-1 text-gray-400">{icon}</div>}
      <p className="text-sm font-mono font-bold text-white">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  )
}
