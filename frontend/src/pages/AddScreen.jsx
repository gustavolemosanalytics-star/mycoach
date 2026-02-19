import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileCheck, Loader2, Sparkles, AlertTriangle, CheckCircle2, X } from 'lucide-react'
import useActivityStore from '../stores/activityStore'
import { FEELING_OPTIONS } from '../utils/constants'
import { formatDistance, formatDuration, formatPace, scoreColor, scoreBg } from '../utils/formatters'

export default function AddScreen() {
  const navigate = useNavigate()
  const { uploading, uploadResult, uploadActivity, clearUpload } = useActivityStore()
  const [file, setFile] = useState(null)
  const [feeling, setFeeling] = useState(null)
  const [notes, setNotes] = useState('')
  const [dragOver, setDragOver] = useState(false)

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer?.files?.[0]
    if (f && (f.name.endsWith('.fit') || f.name.endsWith('.tcx'))) {
      setFile(f)
    }
  }, [])

  const handleFileSelect = (e) => {
    const f = e.target.files?.[0]
    if (f) setFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    try {
      await uploadActivity(file, { feeling, notes })
    } catch {
      // error in store
    }
  }

  const handleReset = () => {
    setFile(null)
    setFeeling(null)
    setNotes('')
    clearUpload()
  }

  // Show upload result
  if (uploadResult) {
    const r = uploadResult
    return (
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-bold text-white">Treino Registrado</h1>
          <button onClick={handleReset} className="text-gray-500 hover:text-gray-300">
            <X size={20} />
          </button>
        </div>

        {/* Score card */}
        {r.ai_score != null && (
          <div className={`bg-gradient-to-br ${scoreBg(r.ai_score)} rounded-2xl p-6 text-center`}>
            <p className="text-5xl font-mono font-bold text-white mb-1">{r.ai_score}</p>
            <p className="text-sm text-white/80">Score do treino</p>
          </div>
        )}

        {/* Summary stats */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-[#111827] rounded-xl p-3 text-center">
            <p className="text-sm font-mono font-bold text-white">{formatDistance(r.total_distance_meters)}</p>
            <p className="text-xs text-gray-500">Distância</p>
          </div>
          <div className="bg-[#111827] rounded-xl p-3 text-center">
            <p className="text-sm font-mono font-bold text-white">{formatDuration(r.total_timer_seconds)}</p>
            <p className="text-xs text-gray-500">Duração</p>
          </div>
          <div className="bg-[#111827] rounded-xl p-3 text-center">
            <p className="text-sm font-mono font-bold text-white">{formatPace(r.avg_pace_min_km)}</p>
            <p className="text-xs text-gray-500">Pace médio</p>
          </div>
        </div>

        {/* AI Analysis */}
        {r.ai_analysis && (
          <div className="space-y-3">
            {r.ai_analysis.summary && (
              <div className="bg-[#111827] rounded-xl p-4 border border-[#00E5A0]/20">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles size={14} className="text-[#00E5A0]" />
                  <span className="text-xs font-medium text-[#00E5A0]">Análise do Coach</span>
                </div>
                <p className="text-sm text-gray-300">{r.ai_analysis.summary}</p>
              </div>
            )}

            {r.ai_analysis.highlights?.length > 0 && (
              <div className="bg-[#111827] rounded-xl p-4">
                <p className="text-xs font-medium text-emerald-400 mb-2">Destaques</p>
                <ul className="space-y-1">
                  {r.ai_analysis.highlights.map((h, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle2 size={14} className="text-emerald-400 mt-0.5 shrink-0" />
                      <span className="text-sm text-gray-300">{h}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {r.ai_analysis.warnings?.length > 0 && (
              <div className="bg-[#111827] rounded-xl p-4">
                <p className="text-xs font-medium text-amber-400 mb-2">Atenção</p>
                <ul className="space-y-1">
                  {r.ai_analysis.warnings.map((w, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <AlertTriangle size={14} className="text-amber-400 mt-0.5 shrink-0" />
                      <span className="text-sm text-gray-300">{w}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => navigate(`/activity/${r.id}`)}
            className="flex-1 bg-[#111827] hover:bg-[#1A2332] text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            Ver detalhes
          </button>
          <button
            onClick={handleReset}
            className="flex-1 bg-[#00E5A0] hover:bg-[#00CC8E] text-[#0A0E17] font-semibold py-2.5 rounded-lg transition-colors"
          >
            Novo upload
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <h1 className="text-lg font-bold text-white">Adicionar Treino</h1>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-8 text-center transition-colors ${
          dragOver ? 'border-[#00E5A0] bg-[#00E5A0]/5' :
          file ? 'border-emerald-600 bg-emerald-500/5' :
          'border-gray-700 bg-[#111827]'
        }`}
      >
        {file ? (
          <div className="flex items-center justify-center gap-3">
            <FileCheck className="text-emerald-400" size={24} />
            <div className="text-left">
              <p className="text-sm font-medium text-white">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(0)} KB</p>
            </div>
            <button onClick={() => setFile(null)} className="text-gray-500 hover:text-red-400 ml-2">
              <X size={16} />
            </button>
          </div>
        ) : (
          <>
            <Upload className="mx-auto text-gray-600 mb-3" size={32} />
            <p className="text-sm text-gray-300 mb-1">Arraste seu arquivo .FIT ou .TCX</p>
            <p className="text-xs text-gray-500 mb-3">Prefira .FIT para dados mais completos</p>
            <label className="inline-block cursor-pointer">
              <span className="bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm px-4 py-2 rounded-lg transition-colors">
                Escolher arquivo
              </span>
              <input
                type="file"
                accept=".fit,.tcx"
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>
          </>
        )}
      </div>

      {/* Feeling selector */}
      <div>
        <label className="block text-sm text-gray-400 mb-2">Como você se sentiu?</label>
        <div className="flex gap-2">
          {FEELING_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setFeeling(feeling === opt.value ? null : opt.value)}
              className={`flex-1 flex flex-col items-center gap-1 py-3 rounded-xl border transition-colors ${
                feeling === opt.value
                  ? 'border-[#00E5A0] bg-[#00E5A0]/10'
                  : 'border-gray-700 bg-[#111827]'
              }`}
            >
              <span className="text-xl">{opt.emoji}</span>
              <span className="text-xs text-gray-400">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="block text-sm text-gray-400 mb-1">Notas (opcional)</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          className="w-full bg-[#111827] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm resize-none focus:outline-none focus:border-[#00E5A0]"
          placeholder="Como foi o treino? Alguma dor ou desconforto?"
        />
      </div>

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="w-full bg-[#00E5A0] hover:bg-[#00CC8E] text-[#0A0E17] font-semibold py-3 rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {uploading ? (
          <>
            <Loader2 className="animate-spin" size={18} />
            Analisando com IA...
          </>
        ) : (
          <>
            <Upload size={18} />
            Enviar e Analisar
          </>
        )}
      </button>
    </div>
  )
}
