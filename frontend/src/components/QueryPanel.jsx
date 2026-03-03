import { useState, useEffect, useRef } from 'react'
import { Search, Terminal, CornerDownLeft, X, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import { nlQuery, rawSqlQuery, getSuggestions } from '../utils/api'

export default function QueryPanel({ onResult, loading, setLoading }) {
  const [question, setQuestion]   = useState('')
  const [mode, setMode]           = useState('nl')    // 'nl' | 'sql'
  const [sqlInput, setSqlInput]   = useState('')
  const [suggestions, setSuggestions] = useState([])
  const inputRef = useRef(null)

  useEffect(() => {
    getSuggestions().then(r => setSuggestions(r.data.suggestions)).catch(() => {})
    inputRef.current?.focus()
  }, [])

  const handleNLSubmit = async () => {
    if (!question.trim()) return
    setLoading(true)
    try {
      const { data } = await nlQuery(question)
      onResult(data, question)
      if (data.error) toast.error(data.error)
    } catch (e) {
      const msg = e.response?.data?.detail || 'Request failed.'
      toast.error(msg)
      onResult({ error: msg, sql: '', columns: [], rows: [], chart: null, row_count: 0 }, question)
    } finally {
      setLoading(false)
    }
  }

  const handleSQLSubmit = async () => {
    if (!sqlInput.trim()) return
    setLoading(true)
    try {
      const { data } = await rawSqlQuery(sqlInput)
      onResult(data, `SQL: ${sqlInput.slice(0, 60)}...`)
      if (data.error) toast.error(data.error)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'SQL failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      mode === 'nl' ? handleNLSubmit() : handleSQLSubmit()
    }
  }

  return (
    <div className="px-6 pt-6 pb-4 border-b border-[#1e2836]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-display text-xl text-white italic">NL-SQL Analyst</h1>
          <p className="text-xs font-mono text-slate-600 mt-0.5">
            Ask questions about your data in plain English
          </p>
        </div>

        {/* Mode toggle */}
        <div className="flex items-center gap-1 panel-inner p-1">
          <button
            onClick={() => setMode('nl')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono transition-all',
              mode === 'nl'
                ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                : 'text-slate-600 hover:text-slate-400'
            )}
          >
            <Search size={11} />
            Natural Language
          </button>
          <button
            onClick={() => setMode('sql')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono transition-all',
              mode === 'sql'
                ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                : 'text-slate-600 hover:text-slate-400'
            )}
          >
            <Terminal size={11} />
            SQL Editor
          </button>
        </div>
      </div>

      {/* NL input */}
      {mode === 'nl' && (
        <>
          <div className="relative">
            <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600 pointer-events-none" />
            <input
              ref={inputRef}
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. What are the top 10 customers by revenue in 2023?"
              className="w-full bg-[#0f1319] border border-[#1e2836] hover:border-[#263244]
                         focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20
                         rounded-lg pl-10 pr-14 py-3 font-sans text-sm text-slate-200
                         placeholder:text-slate-700 outline-none transition-all duration-150"
              disabled={loading}
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
              {question && !loading && (
                <button onClick={() => setQuestion('')} className="p-1 text-slate-600 hover:text-slate-400">
                  <X size={13} />
                </button>
              )}
              <button
                onClick={handleNLSubmit}
                disabled={loading || !question.trim()}
                className="flex items-center gap-1 bg-amber-500 hover:bg-amber-400 disabled:opacity-40
                           text-ink-950 text-[11px] font-mono px-2 py-1 rounded transition-all"
              >
                {loading ? <Loader2 size={11} className="animate-spin" /> : <CornerDownLeft size={11} />}
                Run
              </button>
            </div>
          </div>

          {/* Suggestion chips */}
          {suggestions.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {suggestions.slice(0, 8).map((s, i) => (
                <button
                  key={i}
                  onClick={() => { setQuestion(s); setTimeout(handleNLSubmit, 50) }}
                  disabled={loading}
                  className="text-[11px] font-mono text-slate-600 hover:text-amber-400
                             border border-[#1e2836] hover:border-amber-500/30
                             bg-[#0f1319] hover:bg-amber-500/5 px-2.5 py-1 rounded-full
                             transition-all duration-100 truncate max-w-[260px]"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </>
      )}

      {/* SQL editor */}
      {mode === 'sql' && (
        <div>
          <div className="relative">
            <textarea
              value={sqlInput}
              onChange={e => setSqlInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="SELECT * FROM orders WHERE status = 'completed' LIMIT 10"
              rows={4}
              className="w-full bg-[#0f1319] border border-[#1e2836] hover:border-[#263244]
                         focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20
                         rounded-lg px-4 py-3 font-mono text-sm text-slate-200
                         placeholder:text-slate-700 outline-none transition-all resize-none"
              disabled={loading}
            />
          </div>
          <div className="flex items-center justify-between mt-2">
            <p className="text-[10px] font-mono text-slate-700">
              Read-only · SELECT only · Shift+Enter for newline
            </p>
            <button
              onClick={handleSQLSubmit}
              disabled={loading || !sqlInput.trim()}
              className="flex items-center gap-1.5 bg-amber-500 hover:bg-amber-400 disabled:opacity-40
                         text-ink-950 text-xs font-mono px-3 py-1.5 rounded transition-all"
            >
              {loading ? <Loader2 size={12} className="animate-spin" /> : <Terminal size={12} />}
              Execute
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
