import { formatPace, formatDuration } from '../../utils/formatters'

export default function LapsTable({ laps }) {
  if (!laps || laps.length === 0) return null

  return (
    <div className="bg-[#111827] rounded-xl p-4">
      <h3 className="text-sm font-medium text-gray-400 mb-3">Voltas</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-gray-500 border-b border-gray-800">
              <th className="text-left py-2 font-medium">#</th>
              <th className="text-right py-2 font-medium">Dist</th>
              <th className="text-right py-2 font-medium">Tempo</th>
              <th className="text-right py-2 font-medium">Pace</th>
              <th className="text-right py-2 font-medium">FC</th>
            </tr>
          </thead>
          <tbody>
            {laps.map((lap, i) => {
              const pace = lap.distance_m > 0 && lap.duration_s > 0
                ? (lap.duration_s / lap.distance_m) * 1000 / 60
                : null
              return (
                <tr key={i} className="border-b border-gray-800/50">
                  <td className="py-2 text-gray-400">{lap.lap || i + 1}</td>
                  <td className="py-2 text-right font-mono text-white">
                    {(lap.distance_m / 1000).toFixed(2)}
                  </td>
                  <td className="py-2 text-right font-mono text-white">
                    {formatDuration(lap.duration_s)}
                  </td>
                  <td className="py-2 text-right font-mono text-white">
                    {pace ? formatPace(pace) : '—'}
                  </td>
                  <td className="py-2 text-right font-mono text-white">
                    {lap.avg_hr || '—'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
