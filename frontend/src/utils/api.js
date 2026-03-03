import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 60000,
})

export const nlQuery     = (question)  => api.post('/api/query', { question })
export const rawSqlQuery = (sql)       => api.post('/api/sql',   { sql })
export const getSchema   = ()          => api.get('/api/schema')
export const getSuggestions = ()       => api.get('/api/suggestions')
export const getHealth   = ()          => api.get('/health')

export default api
