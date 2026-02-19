import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Trophy, Activity, Clock, Zap, ChevronRight, Edit3, Save, X } from 'lucide-react'
import useAuthStore from '../stores/authStore'
import useActivityStore from '../stores/activityStore'
import usePlanStore from '../stores/planStore'
import { formatDistance, formatDuration, scoreColor } from '../utils/formatters'
import { SPORT_COLORS, SPORT_LABELS } from '../utils/constants'

export default function ProfileScreen() {
  const navigate = useNavigate()
  const { user, updateProfile } = useAuthStore()
  const { activities, fetchActivities } = useActivityStore()
  const { races, fetchRaces } = usePlanStore()
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({})

  useEffect(() => {
    fetchActivities({ limit: 5 })
    fetchRaces()
  }, [])

  const startEdit = () => {
    setEditForm({
      weight_kg: user?.weight_kg || '',
      height_cm: user?.height_cm || '',
      hr_max: user?.hr_max || '',
      hr_rest: user?.hr_rest || '',
      hr_threshold: user?.hr_threshold || '',
      ftp: user?.ftp || '',
      run_threshold_pace: user?.run_threshold_pace || '',
      weekly_hours_available: user?.weekly_hours_available || '',
      training_days_per_week: user?.training_days_per_week || '',
    })
    setEditing(true)
  }

  const handleSave = async () => {
    const payload = {}
    for (const [k, v] of Object.entries(editForm)) {
      payload[k] = v === '' ? null : Number(v)
    }
    await updateProfile(payload)
    setEditing(false)
  }

  // Stats
  const totalActivities = activities.length
  const totalDistance = activities.reduce((sum, a) => sum + (a.total_distance_meters || 0), 0)
  const totalTime = activities.reduce((sum, a) => sum + (a.total_timer_seconds || 0), 0)
  const avgScore = activities.length > 0
    ? Math.round(activities.reduce((sum, a) => sum + (a.ai_score || 0), 0) / activities.filter((a) => a.ai_score).length)
    : null

  return (
    <div className="space-y-5">
      {/* Athlete card */}
      <div className="bg-[#111827] rounded-2xl p-5">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-[#1A2332] flex items-center justify-center">
            <User className="text-[#00E5A0]" size={24} />
          </div>
          <div className="flex-1">
            <h1 className="text-lg font-bold text-white">{user?.full_name || 'Atleta'}</h1>
            <p className="text-sm text-gray-400 capitalize">
              {user?.modality === 'triathlon' ? 'Triatleta' : 'Corredor'} • {user?.experience_level || '—'}
            </p>
          </div>
          <button
            onClick={editing ? handleSave : startEdit}
            className="text-gray-400 hover:text-[#00E5A0] transition-colors"
          >
            {editing ? <Save size={20} /> : <Edit3 size={20} />}
          </button>
        </div>

        {/* Physical / physiological data */}
        {editing ? (
          <div className="mt-4 grid grid-cols-2 gap-3">
            {[
              { key: 'weight_kg', label: 'Peso (kg)' },
              { key: 'height_cm', label: 'Altura (cm)' },
              { key: 'hr_max', label: 'FC Máx' },
              { key: 'hr_rest', label: 'FC Rep' },
              { key: 'hr_threshold', label: 'FC Limiar' },
              { key: 'ftp', label: 'FTP (W)' },
              { key: 'run_threshold_pace', label: 'Pace Limiar' },
              { key: 'weekly_hours_available', label: 'Horas/sem' },
              { key: 'training_days_per_week', label: 'Dias/sem' },
            ].map(({ key, label }) => (
              <div key={key}>
                <label className="block text-xs text-gray-500 mb-1">{label}</label>
                <input
                  type="number"
                  value={editForm[key]}
                  onChange={(e) => setEditForm((f) => ({ ...f, [key]: e.target.value }))}
                  className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-2 py-1.5 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
                />
              </div>
            ))}
            <button
              onClick={() => setEditing(false)}
              className="col-span-2 text-sm text-gray-500 hover:text-gray-300"
            >
              Cancelar
            </button>
          </div>
        ) : (
          <div className="mt-4 grid grid-cols-3 gap-y-2 text-sm">
            {user?.weight_kg && (
              <div>
                <p className="text-xs text-gray-500">Peso</p>
                <p className="text-white font-mono">{user.weight_kg} kg</p>
              </div>
            )}
            {user?.hr_max && (
              <div>
                <p className="text-xs text-gray-500">FC Máx</p>
                <p className="text-white font-mono">{user.hr_max} bpm</p>
              </div>
            )}
            {user?.ftp && (
              <div>
                <p className="text-xs text-gray-500">FTP</p>
                <p className="text-white font-mono">{user.ftp} W</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-[#111827] rounded-xl p-4">
          <Activity size={16} className="text-[#00E5A0] mb-2" />
          <p className="text-2xl font-mono font-bold text-white">{totalActivities}</p>
          <p className="text-xs text-gray-500">Atividades</p>
        </div>
        <div className="bg-[#111827] rounded-xl p-4">
          <Zap size={16} className="text-yellow-400 mb-2" />
          <p className={`text-2xl font-mono font-bold ${scoreColor(avgScore)}`}>{avgScore || '—'}</p>
          <p className="text-xs text-gray-500">Score médio</p>
        </div>
        <div className="bg-[#111827] rounded-xl p-4">
          <Trophy size={16} className="text-amber-400 mb-2" />
          <p className="text-2xl font-mono font-bold text-white">{formatDistance(totalDistance)}</p>
          <p className="text-xs text-gray-500">Distância total</p>
        </div>
        <div className="bg-[#111827] rounded-xl p-4">
          <Clock size={16} className="text-blue-400 mb-2" />
          <p className="text-2xl font-mono font-bold text-white">{formatDuration(totalTime)}</p>
          <p className="text-xs text-gray-500">Tempo total</p>
        </div>
      </div>

      {/* Races */}
      {races.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-400 mb-2">Provas alvo</h2>
          <div className="space-y-2">
            {races.map((race) => (
              <div key={race.id} className="bg-[#111827] rounded-xl p-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white">{race.name}</p>
                  <p className="text-xs text-gray-500">{race.race_type} • {race.race_date}</p>
                </div>
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                  race.priority === 'A' ? 'bg-red-500/20 text-red-400' :
                  race.priority === 'B' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-gray-500/20 text-gray-400'
                }`}>
                  {race.priority}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent activities */}
      {activities.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-400 mb-2">Atividades recentes</h2>
          <div className="space-y-2">
            {activities.map((act) => (
              <button
                key={act.id}
                onClick={() => navigate(`/activity/${act.id}`)}
                className="w-full bg-[#111827] rounded-xl p-3 flex items-center gap-3 hover:bg-[#1A2332] transition-colors"
              >
                <div
                  className="w-1 h-8 rounded-full"
                  style={{ backgroundColor: SPORT_COLORS[act.sport] || '#6B7280' }}
                />
                <div className="flex-1 text-left">
                  <p className="text-sm text-white">{act.title || SPORT_LABELS[act.sport] || act.sport}</p>
                  <p className="text-xs text-gray-500">
                    {formatDistance(act.total_distance_meters)} • {formatDuration(act.total_timer_seconds)}
                  </p>
                </div>
                {act.ai_score != null && (
                  <span className={`text-sm font-mono font-bold ${scoreColor(act.ai_score)}`}>
                    {act.ai_score}
                  </span>
                )}
                <ChevronRight size={16} className="text-gray-600" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
