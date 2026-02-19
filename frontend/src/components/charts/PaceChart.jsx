import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceLine } from 'recharts'
import { formatDuration, formatPace } from '../../utils/formatters'

export default function PaceChart({ data }) {
  if (!data || data.length === 0) return null

  const avgPace = data.reduce((sum, d) => sum + d.pace, 0) / data.length

  return (
    <div className="bg-[#111827] rounded-xl p-4">
      <h3 className="text-sm font-medium text-gray-400 mb-3">Pace</h3>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
            <XAxis
              dataKey="t"
              tickFormatter={(t) => formatDuration(t)}
              tick={{ fill: '#6B7280', fontSize: 10 }}
              axisLine={{ stroke: '#374151' }}
            />
            <YAxis
              reversed
              domain={['auto', 'auto']}
              tickFormatter={(v) => formatPace(v)}
              tick={{ fill: '#6B7280', fontSize: 10 }}
              axisLine={{ stroke: '#374151' }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1A2332', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
              labelFormatter={(t) => formatDuration(t)}
              formatter={(v) => [formatPace(v) + ' /km', 'Pace']}
            />
            <ReferenceLine
              y={avgPace}
              stroke="#00E5A0"
              strokeDasharray="4 4"
              strokeWidth={1}
            />
            <Line
              type="monotone"
              dataKey="pace"
              stroke="#F472B6"
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
