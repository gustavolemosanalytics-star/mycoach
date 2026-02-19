import { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight, Target, Zap, Clock, TrendingUp, Sparkles, Loader2 } from 'lucide-react'
import usePlanStore from '../stores/planStore'
import SessionCard from '../components/plan/SessionCard'
import { PHASE_LABELS, PHASE_COLORS } from '../utils/constants'
import { formatDateShort } from '../utils/formatters'

export default function PlanScreen() {
  const { currentWeek, loading, generating, fetchCurrentWeek, generatePlan, fetchRaces, races } = usePlanStore()
  const [showSetup, setShowSetup] = useState(false)

  useEffect(() => {
    fetchCurrentWeek()
    fetchRaces()
  }, [])

  // No plan yet
  if (!loading && !currentWeek) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <Target className="mx-auto text-gray-600 mb-4" size={48} />
          <h2 className="text-xl font-semibold text-white mb-2">Nenhum plano ativo</h2>
          <p className="text-gray-400 text-sm mb-6">
            Crie uma prova alvo e gere sua periodização com IA
          </p>
          <button
            onClick={() => setShowSetup(true)}
            className="bg-[#00E5A0] hover:bg-[#00CC8E] text-[#0A0E17] font-semibold px-6 py-2.5 rounded-lg transition-colors"
          >
            Criar Plano
          </button>
        </div>

        {showSetup && (
          <SetupPlan
            races={races}
            generating={generating}
            onGenerate={async (raceId) => {
              await generatePlan(raceId)
              await fetchCurrentWeek()
              setShowSetup(false)
            }}
            onClose={() => setShowSetup(false)}
          />
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-[#00E5A0]" size={32} />
      </div>
    )
  }

  const week = currentWeek
  const phase = week?.phase
  const phaseColor = PHASE_COLORS[phase] || '#6B7280'
  const sessions = week?.sessions || []
  const completedCount = sessions.filter((s) => s.completed).length
  const compliance = sessions.length > 0 ? Math.round((completedCount / sessions.length) * 100) : 0

  return (
    <div className="space-y-5">
      {/* Week header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white">Semana {week?.week_number || '—'}</h1>
            {phase && (
              <span
                className="text-xs font-medium px-2 py-0.5 rounded-full"
                style={{ backgroundColor: phaseColor + '20', color: phaseColor }}
              >
                {PHASE_LABELS[phase] || phase}
              </span>
            )}
          </div>
          {week?.start_date && (
            <p className="text-sm text-gray-500">
              {formatDateShort(week.start_date)} — {formatDateShort(week.end_date)}
            </p>
          )}
        </div>

        {/* Race countdown */}
        {week?.race_name && (
          <div className="text-right">
            <p className="text-xs text-gray-500">{week.race_name}</p>
            {week.weeks_to_race != null && (
              <p className="text-sm font-mono font-bold text-[#00E5A0]">
                {week.weeks_to_race} sem
              </p>
            )}
          </div>
        )}
      </div>

      {/* Volume bar */}
      <div className="bg-[#111827] rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Volume semanal</span>
          <span className="text-sm font-mono text-white">{compliance}%</span>
        </div>
        <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${compliance}%`,
              background: `linear-gradient(90deg, #00E5A0, #00CC8E)`,
            }}
          />
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-[#111827] rounded-xl p-3 text-center">
          <Zap size={16} className="mx-auto text-yellow-400 mb-1" />
          <p className="text-lg font-mono font-bold text-white">{week?.total_tss || '—'}</p>
          <p className="text-xs text-gray-500">TSS</p>
        </div>
        <div className="bg-[#111827] rounded-xl p-3 text-center">
          <Clock size={16} className="mx-auto text-blue-400 mb-1" />
          <p className="text-lg font-mono font-bold text-white">
            {completedCount}/{sessions.length}
          </p>
          <p className="text-xs text-gray-500">Sessões</p>
        </div>
        <div className="bg-[#111827] rounded-xl p-3 text-center">
          <TrendingUp size={16} className="mx-auto text-emerald-400 mb-1" />
          <p className="text-lg font-mono font-bold text-white">{week?.weekly_score || '—'}</p>
          <p className="text-xs text-gray-500">Score</p>
        </div>
      </div>

      {/* AI weekly analysis */}
      {week?.ai_summary && (
        <div className="bg-[#111827] rounded-xl p-4 border border-[#00E5A0]/20">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-[#00E5A0]" />
            <span className="text-xs font-medium text-[#00E5A0]">Coach IA</span>
          </div>
          <p className="text-sm text-gray-300">{week.ai_summary}</p>
        </div>
      )}

      {/* Sessions list */}
      <div className="space-y-2">
        <h2 className="text-sm font-medium text-gray-400">Treinos da semana</h2>
        {sessions.length > 0 ? (
          sessions.map((session) => (
            <SessionCard key={session.id} session={session} />
          ))
        ) : (
          <div className="bg-[#111827] rounded-xl p-6 text-center">
            <p className="text-gray-500 text-sm">Nenhuma sessão gerada ainda</p>
            <button
              onClick={() => generateWeekSessions(week.week_id)}
              disabled={generating}
              className="mt-3 text-sm text-[#00E5A0] hover:underline disabled:opacity-50"
            >
              {generating ? 'Gerando...' : 'Gerar sessões com IA'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

function SetupPlan({ races, generating, onGenerate, onClose }) {
  const { createRace } = usePlanStore()
  const [selectedRace, setSelectedRace] = useState(null)
  const [creating, setCreating] = useState(false)
  const [raceForm, setRaceForm] = useState({
    name: '',
    race_type: 'half_marathon',
    race_date: '',
    priority: 'A',
  })

  const handleCreateRace = async () => {
    setCreating(true)
    try {
      const race = await createRace(raceForm)
      setSelectedRace(race.id)
      setCreating(false)
    } catch {
      setCreating(false)
    }
  }

  return (
    <div className="bg-[#111827] rounded-2xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold">Configurar Plano</h3>
        <button onClick={onClose} className="text-gray-500 text-sm">Cancelar</button>
      </div>

      {races.length > 0 && (
        <div>
          <label className="block text-sm text-gray-400 mb-2">Prova existente</label>
          <div className="space-y-2">
            {races.map((r) => (
              <button
                key={r.id}
                onClick={() => setSelectedRace(r.id)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  selectedRace === r.id
                    ? 'border-[#00E5A0] bg-[#00E5A0]/10'
                    : 'border-gray-700 bg-[#1A2332]'
                }`}
              >
                <p className="text-sm text-white font-medium">{r.name}</p>
                <p className="text-xs text-gray-500">{r.race_type} • {r.race_date}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="border-t border-gray-800 pt-4">
        <p className="text-sm text-gray-400 mb-3">Ou crie uma nova prova:</p>
        <div className="space-y-3">
          <input
            value={raceForm.name}
            onChange={(e) => setRaceForm((f) => ({ ...f, name: e.target.value }))}
            className="w-full bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
            placeholder="Nome da prova"
          />
          <div className="grid grid-cols-2 gap-2">
            <select
              value={raceForm.race_type}
              onChange={(e) => setRaceForm((f) => ({ ...f, race_type: e.target.value }))}
              className="bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
            >
              <option value="5k">5K</option>
              <option value="10k">10K</option>
              <option value="half_marathon">Meia Maratona</option>
              <option value="marathon">Maratona</option>
              <option value="sprint_tri">Sprint Tri</option>
              <option value="olympic_tri">Olympic Tri</option>
              <option value="half_ironman">Half Ironman</option>
              <option value="ironman">Ironman</option>
            </select>
            <input
              type="date"
              value={raceForm.race_date}
              onChange={(e) => setRaceForm((f) => ({ ...f, race_date: e.target.value }))}
              className="bg-[#1A2332] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#00E5A0]"
            />
          </div>
          <button
            onClick={handleCreateRace}
            disabled={creating || !raceForm.name || !raceForm.race_date}
            className="w-full bg-gray-800 hover:bg-gray-700 text-white text-sm py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {creating ? 'Criando...' : 'Criar Prova'}
          </button>
        </div>
      </div>

      {selectedRace && (
        <button
          onClick={() => onGenerate(selectedRace)}
          disabled={generating}
          className="w-full bg-[#00E5A0] hover:bg-[#00CC8E] text-[#0A0E17] font-semibold py-3 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {generating ? (
            <>
              <Loader2 className="animate-spin" size={16} />
              Gerando periodização...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Gerar Periodização com IA
            </>
          )}
        </button>
      )}
    </div>
  )
}
