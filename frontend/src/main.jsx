import React from 'react'
import ReactDOM from 'react-dom/client'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
    <Toaster
      position="bottom-right"
      toastOptions={{
        style: {
          background: '#131820',
          color: '#cbd5e1',
          border: '1px solid #1e2836',
          fontFamily: '"IBM Plex Mono", monospace',
          fontSize: '0.8rem',
        },
        success: { iconTheme: { primary: '#f59e0b', secondary: '#080a0f' } },
        error:   { iconTheme: { primary: '#f87171', secondary: '#080a0f' } },
      }}
    />
  </React.StrictMode>
)
