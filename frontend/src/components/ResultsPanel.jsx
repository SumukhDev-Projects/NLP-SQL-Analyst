import { useState, useEffect } from 'react'
import { Code2, Table2, BarChart2, AlertTriangle, Clock, Rows, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import { highlightSQL } from '../utils/highlight'
import { formatValue } from '../utils/format'
import ChartView from './ChartView'

export default function ResultsPanel({ result, loading }) {
  const [tab, setTab] = useState('table')

  // Switch to chart tab if chart is available, else table
  useEffect(() => {
    if (result?.chart) setTab('chart')
    else if (result) setTab('table')
  }, [result])

  if (loading) return <LoadingState />

  if (!result) return <EmptyState />

  const hasChart = !!result.chart
  const hasRows  = result.rows?.length > 0
  const hasError = !!result.error

  return (
    <div className="animate-slide-up mt-4">
      {/* SQL display */}
      {result.sql && (
        <div className="panel mb-3 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-2 border-b border-[#1e2836] bg-[#0d1016]">
            <Code2 size={12} className="text-amber-500" />
            <span className="font-mono text-[10px] text-slate-600 uppercase tracking-wider">Generated SQL</span>
            {result.execution_ms > 0 && (
              <span className="ml-auto font-mono text-[10px] text-slate-700 flex items-center gap-1">
                <Clock size={9} />
                {result.execution_ms}ms
              </span>
            )}
          </div>
          <pre
            className="px-4 py-3 font-mono text-sm overflow-x-auto leading-relaxed"
            dangerouslySetInnerHTML={{ __html: highlightSQL(result.sql) }}
          />
        </div>
      )}

      {/* Error banner */}
      {hasError && (
        <div className="panel border-red-500/20 bg-red-500/5 px-4 py-3 mb-3 flex items-start gap-3">
          <AlertTriangle size={14} className="text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-xs font-mono text-red-400">Query Error</p>
            <p className="text-xs text-slate-400 mt-1">{result.error}</p>
          </div>
        </div>
      )}

      {/* Results area */}
      {hasRows && (
        <div className="panel overflow-hidden">
          {/* Tab bar */}
          <div className="flex items-center border-b border-[#1e2836] bg-[#0d1016]">
            <button
              onClick={() => setTab('table')}
              className={clsx(
                'flex items-center gap-1.5 px-4 py-2.5 text-[11px] font-mono uppercase tracking-wider transition-colors',
                tab === 'table'
                  ? 'text-amber-400 border-b border-amber-500'
                  : 'text-slate-600 hover:text-slate-400'
              )}
            >
              <Table2 size={11} /> Table
            </button>
            {hasChart && (
              <button
                onClick={() => setTab('chart')}
                className={clsx(
                  'flex items-center gap-1.5 px-4 py-2.5 text-[11px] font-mono uppercase tracking-wider transition-colors',
                  tab === 'chart'
                    ? 'text-amber-400 border-b border-amber-500'
                    : 'text-slate-600 hover:text-slate-400'
                )}
              >
                <BarChart2 size={11} /> Chart
              </button>
            )}

            {/* Row count */}
            <div className="ml-auto flex items-center gap-1.5 px-4">
              <Rows size={10} className="text-slate-700" />
              <span className="font-mono text-[10px] text-slate-600">
                {result.row_count.toLocaleString()} rows
                {result.truncated && ' (truncated)'}
              </span>
            </div>
          </div>

          {tab === 'table' && (
            <div className="overflow-auto max-h-[420px]">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="sticky top-0 bg-[#0f1319] border-b border-[#1e2836]">
                    <th className="w-10 px-3 py-2 text-left font-mono text-[10px] text-slate-700 border-r border-[#1e2836]">
                      #
                    </th>
                    {result.columns.map(col => (
                      <th key={col} className="px-4 py-2 text-left font-mono text-[10px] text-slate-500 uppercase tracking-wider whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((row, i) => (
                    <tr
                      key={i}
                      className="border-b border-[#1e2836]/50 hover:bg-[#131820] transition-colors"
                    >
                      <td className="px-3 py-2 font-mono text-[10px] text-slate-700 border-r border-[#1e2836]/50">
                        {i + 1}
                      </td>
                      {row.map((val, j) => (
                        <td key={j} className="px-4 py-2 font-mono text-xs text-slate-300 whitespace-nowrap">
                          {formatValue(val, result.columns[j])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === 'chart' && hasChart && (
            <div className="p-4">
              <ChartView chart={result.chart} />
            </div>
          )}
        </div>
      )}

      {/* No rows, no error */}
      {!hasError && !hasRows && result.sql && (
        <div className="panel px-6 py-10 text-center">
          <p className="font-mono text-sm text-slate-600">Query executed — no rows returned.</p>
        </div>
      )}
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center h-60 gap-4">
      <Loader2 size={24} className="text-amber-500 animate-spin" />
      <div className="text-center">
        <p className="font-mono text-sm text-slate-500">Translating to SQL...</p>
        <p className="font-mono text-[11px] text-slate-700 mt-1">Claude is thinking</p>
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-3 opacity-60">
      <div className="w-12 h-12 rounded-xl bg-[#131820] border border-[#1e2836] flex items-center justify-center">
        <BarChart2 size={20} className="text-amber-500/50" />
      </div>
      <div className="text-center">
        <p className="font-display italic text-slate-400">Ask a question to get started</p>
        <p className="font-mono text-[11px] text-slate-700 mt-1">
          Results and charts appear here
        </p>
      </div>
    </div>
  )
}
