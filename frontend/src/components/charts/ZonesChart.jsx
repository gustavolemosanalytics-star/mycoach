export default function ZonesChart({ zones, colors, labels, title }) {
  if (!zones || zones.length === 0) return null

  const total = zones.reduce((sum, z) => sum + (z.time_seconds || z.pct || 0), 0)
  if (total === 0) return null

  return (
    <div className="bg-[#111827] rounded-xl p-4">
      <h3 className="text-sm font-medium text-gray-400 mb-3">{title}</h3>
      <div className="space-y-2">
        {zones.map((zone, i) => {
          const pct = zone.pct != null ? zone.pct : total > 0 ? Math.round((zone.time_seconds / total) * 100) : 0
          return (
            <div key={i} className="flex items-center gap-3">
              <span className="text-xs text-gray-500 w-24 truncate">{labels[i] || `Z${i + 1}`}</span>
              <div className="flex-1 h-4 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: colors[i] || '#6B7280',
                  }}
                />
              </div>
              <span className="text-xs font-mono text-gray-400 w-10 text-right">{pct}%</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
