/**
 * Format pace from decimal minutes to MM:SS string
 * e.g. 5.5 → "5:30"
 */
export function formatPace(paceDecimal) {
  if (!paceDecimal || paceDecimal <= 0) return '--:--'
  const mins = Math.floor(paceDecimal)
  const secs = Math.round((paceDecimal - mins) * 60)
  return `${mins}:${String(secs).padStart(2, '0')}`
}

/**
 * Format seconds to H:MM:SS or MM:SS
 */
export function formatDuration(seconds) {
  if (!seconds || seconds <= 0) return '0:00'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}

/**
 * Format meters to km string
 * e.g. 10500 → "10.5 km"
 */
export function formatDistance(meters) {
  if (!meters || meters <= 0) return '0 km'
  const km = meters / 1000
  return km >= 10 ? `${km.toFixed(1)} km` : `${km.toFixed(2)} km`
}

/**
 * Format date to short Brazilian format
 * e.g. "2026-02-19T..." → "19/02"
 */
export function formatDateShort(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}`
}

/**
 * Format date to full Brazilian format
 * e.g. "2026-02-19T..." → "19/02/2026"
 */
export function formatDateFull(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`
}

/**
 * Format weekday name in Portuguese
 */
export function formatWeekday(dateStr) {
  if (!dateStr) return ''
  const days = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
  return days[new Date(dateStr).getDay()]
}

/**
 * Score to color gradient
 */
export function scoreColor(score) {
  if (!score) return 'text-gray-500'
  if (score >= 85) return 'text-emerald-400'
  if (score >= 70) return 'text-green-400'
  if (score >= 50) return 'text-yellow-400'
  if (score >= 30) return 'text-orange-400'
  return 'text-red-400'
}

/**
 * Score to background gradient
 */
export function scoreBg(score) {
  if (!score) return 'from-gray-600 to-gray-700'
  if (score >= 85) return 'from-emerald-500 to-green-500'
  if (score >= 70) return 'from-green-500 to-lime-500'
  if (score >= 50) return 'from-yellow-500 to-amber-500'
  if (score >= 30) return 'from-orange-500 to-red-500'
  return 'from-red-500 to-red-600'
}
