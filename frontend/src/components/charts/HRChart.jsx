import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { formatDuration } from '../../utils/formatters'

export default function HRChart({ data }) {
  if (!data || data.length === 0) return null

  return (
    <div className="bg-[#111827] rounded-xl p-4">
      <h3 className="text-sm font-medium text-gray-400 mb-3">Frequência Cardíaca</h3>
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
              domain={['auto', 'auto']}
              tick={{ fill: '#6B7280', fontSize: 10 }}
              axisLine={{ stroke: '#374151' }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1A2332', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
              labelFormatter={(t) => formatDuration(t)}
              formatter={(v) => [`${v} bpm`, 'FC']}
            />
            <Line
              type="monotone"
              dataKey="hr"
              stroke="#EF4444"
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
