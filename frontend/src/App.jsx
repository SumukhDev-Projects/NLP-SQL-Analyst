import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import QueryPanel from './components/QueryPanel'
import ResultsPanel from './components/ResultsPanel'
import { getHealth } from './utils/api'

export default function App() {
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [history, setHistory]     = useState([])
  const [apiStatus, setApiStatus] = useState('checking')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    getHealth()
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('offline'))
    const t = setInterval(() => {
      getHealth().then(() => setApiStatus('ok')).catch(() => setApiStatus('offline'))
    }, 20000)
    return () => clearInterval(t)
  }, [])

  const handleResult = (res, question) => {
    setResult(res)
    if (!res.error) {
      setHistory(prev => [
        { question, sql: res.sql, row_count: res.row_count, ts: Date.now() },
        ...prev.slice(0, 19),
      ])
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#080a0f]">
      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(p => !p)}
        history={history}
        onHistorySelect={(item) => {
          setResult({ sql: item.sql, columns: [], rows: [], chart: null, error: null, row_count: item.row_count })
        }}
        apiStatus={apiStatus}
      />

      {/* Main */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <QueryPanel
          onResult={handleResult}
          loading={loading}
          setLoading={setLoading}
        />
        <div className="flex-1 overflow-y-auto px-6 pb-6">
          <ResultsPanel result={result} loading={loading} />
        </div>
      </main>
    </div>
  )
}
