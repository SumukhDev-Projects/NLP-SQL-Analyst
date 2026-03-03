import { useState, useEffect } from 'react'
import {
  Database, ChevronLeft, ChevronRight, Table2,
  Clock, Circle, ChevronDown, ChevronRight as ChevronRightSm,
} from 'lucide-react'
import { getSchema } from '../utils/api'
import clsx from 'clsx'

const TYPE_COLOR = {
  INTEGER: 'text-blue-400',
  REAL:    'text-amber-400',
  TEXT:    'text-emerald-400',
  NUMERIC: 'text-amber-400',
}

export default function Sidebar({ open, onToggle, history, onHistorySelect, apiStatus }) {
  const [schema, setSchema]     = useState(null)
  const [tab, setTab]           = useState('schema') // 'schema' | 'history'
  const [expanded, setExpanded] = useState({})

  useEffect(() => {
    if (open) {
      getSchema().then(r => setSchema(r.data)).catch(() => {})
    }
  }, [open])

  const toggleTable = (t) => setExpanded(p => ({ ...p, [t]: !p[t] }))

  const statusColor = apiStatus === 'ok' ? 'fill-emerald-500 text-emerald-500' : 'fill-red-500 text-red-500'

  return (
    <aside
      className={clsx(
        'flex-shrink-0 flex flex-col bg-[#0f1319] border-r border-[#1e2836] transition-all duration-200',
        open ? 'w-64' : 'w-10'
      )}
    >
      {/* Toggle */}
      <button
        onClick={onToggle}
        className="flex items-center justify-between px-3 py-4 border-b border-[#1e2836] hover:bg-[#131820] transition-colors"
      >
        {open && (
          <div className="flex items-center gap-2">
            <Database size={14} className="text-amber-400" />
            <span className="font-mono text-xs text-slate-400 uppercase tracking-wider">Explorer</span>
          </div>
        )}
        {open
          ? <ChevronLeft size={14} className="text-slate-600" />
          : <ChevronRight size={14} className="text-slate-600 mx-auto" />
        }
      </button>

      {open && (
        <>
          {/* Tabs */}
          <div className="flex border-b border-[#1e2836]">
            {['schema', 'history'].map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={clsx(
                  'flex-1 py-2 text-[11px] font-mono uppercase tracking-wider transition-colors',
                  tab === t
                    ? 'text-amber-400 border-b border-amber-500'
                    : 'text-slate-600 hover:text-slate-400'
                )}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto py-2">

            {/* Schema tab */}
            {tab === 'schema' && (
              schema
                ? Object.entries(schema.tables).map(([tbl, cols]) => (
                    <div key={tbl} className="mb-1">
                      <button
                        onClick={() => toggleTable(tbl)}
                        className="w-full flex items-center gap-2 px-3 py-1.5 hover:bg-[#131820] transition-colors text-left"
                      >
                        {expanded[tbl]
                          ? <ChevronDown size={11} className="text-slate-600 flex-shrink-0" />
                          : <ChevronRightSm size={11} className="text-slate-600 flex-shrink-0" />
                        }
                        <Table2 size={11} className="text-amber-400 flex-shrink-0" />
                        <span className="font-mono text-xs text-slate-300 truncate">{tbl}</span>
                        <span className="ml-auto font-mono text-[10px] text-slate-600">
                          {schema.row_counts?.[tbl]?.toLocaleString()}
                        </span>
                      </button>

                      {expanded[tbl] && (
                        <div className="pl-8 pb-1">
                          {cols.map(col => (
                            <div key={col.name} className="flex items-center gap-2 py-0.5 px-2">
                              {col.pk && (
                                <span className="text-[9px] text-amber-500 font-mono">PK</span>
                              )}
                              <span className="font-mono text-[11px] text-slate-400 truncate flex-1">
                                {col.name}
                              </span>
                              <span className={clsx('font-mono text-[10px]', TYPE_COLOR[col.type] || 'text-slate-600')}>
                                {col.type}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                : <p className="px-4 py-3 text-[11px] font-mono text-slate-600">Loading schema...</p>
            )}

            {/* History tab */}
            {tab === 'history' && (
              history.length === 0
                ? <p className="px-4 py-3 text-[11px] font-mono text-slate-600">No queries yet.</p>
                : history.map((item, i) => (
                    <button
                      key={i}
                      onClick={() => onHistorySelect(item)}
                      className="w-full text-left px-3 py-2 hover:bg-[#131820] transition-colors border-b border-[#1e2836]/50 last:border-0"
                    >
                      <p className="text-[11px] text-slate-400 font-sans truncate">{item.question}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Clock size={9} className="text-slate-600" />
                        <span className="text-[10px] font-mono text-slate-600">
                          {new Date(item.ts).toLocaleTimeString()} · {item.row_count} rows
                        </span>
                      </div>
                    </button>
                  ))
            )}
          </div>

          {/* Status */}
          <div className="px-3 py-3 border-t border-[#1e2836] flex items-center gap-2">
            <Circle size={6} className={statusColor} />
            <span className="font-mono text-[10px] text-slate-600">
              {apiStatus === 'ok' ? 'backend connected' : 'backend offline'}
            </span>
          </div>
        </>
      )}
    </aside>
  )
}
