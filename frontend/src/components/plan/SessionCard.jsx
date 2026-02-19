import { useNavigate } from 'react-router-dom'
import { CheckCircle2, Circle, Clock } from 'lucide-react'
import { SPORT_COLORS, SPORT_LABELS, INTENSITY_COLORS, INTENSITY_LABELS } from '../../utils/constants'
import { formatDuration, formatWeekday, formatDateShort } from '../../utils/formatters'

export default function SessionCard({ session }) {
  const navigate = useNavigate()
  const sportColor = SPORT_COLORS[session.sport] || '#6B7280'
  const intensityColor = INTENSITY_COLORS[session.intensity] || '#6B7280'
  const completed = !!session.activity_id
  const isToday = session.date && new Date(session.date).toDateString() === new Date().toDateString()

  return (
    <button
      onClick={() => completed && session.activity_id ? navigate(`/activity/${session.activity_id}`) : undefined}
      className={`w-full flex items-center gap-3 p-3 rounded-xl transition-colors ${
        isToday ? 'bg-[#111827] border border-[#00E5A0]/30' : 'bg-[#111827]'
      } ${completed ? 'hover:bg-[#1A2332] cursor-pointer' : 'cursor-default'}`}
    >
      {/* Sport indicator */}
      <div
        className="w-1 h-12 rounded-full shrink-0"
        style={{ backgroundColor: sportColor }}
      />

      {/* Info */}
      <div className="flex-1 text-left min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white truncate">
            {session.title || SPORT_LABELS[session.sport] || session.sport}
          </span>
          {session.intensity && (
            <span
              className="text-[10px] font-medium px-1.5 py-0.5 rounded shrink-0"
              style={{ backgroundColor: intensityColor + '20', color: intensityColor }}
            >
              {INTENSITY_LABELS[session.intensity] || session.intensity}
            </span>
          )}
        </div>
        {session.description && (
          <p className="text-xs text-gray-500 truncate">{session.description}</p>
        )}
        <div className="flex items-center gap-3 mt-0.5">
          {session.date && (
            <span className="text-xs text-gray-600">
              {formatWeekday(session.date)} {formatDateShort(session.date)}
            </span>
          )}
          {session.planned_duration_minutes && (
            <span className="flex items-center gap-1 text-xs text-gray-600">
              <Clock size={10} />
              {session.planned_duration_minutes}min
            </span>
          )}
        </div>
      </div>

      {/* Status */}
      {completed ? (
        <CheckCircle2 size={20} className="text-[#00E5A0] shrink-0" />
      ) : (
        <Circle size={20} className="text-gray-700 shrink-0" />
      )}
    </button>
  )
}
