import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
})

export interface Log {
  id: number
  timestamp: string
  provider: string
  endpoint: string
  model: string
  prompt: string | null
  response: string | null
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  status_code: number
  media_path: string | null
  error: string | null
}

export interface Stats {
  total_requests: number
  provider_counts: Record<string, number>
  model_counts: Record<string, number>
  providers_config: Record<string, { type: string }>
}

export interface ProviderConfig {
  type: string
  api_key?: string
  base_url?: string
  [key: string]: any
}

export const getStats = () => api.get<Stats>('/api/stats').then(res => res.data)
export const getLogs = (params: any) => api.get<Log[]>('/api/logs', { params }).then(res => res.data)
export const getLogDetail = (id: number) => api.get<Log>(`/api/logs/${id}`).then(res => res.data)
export const deleteLog = (id: number) => api.delete(`/api/logs/${id}`).then(res => res.data)
export const clearLogs = (params: any) => api.delete('/api/logs', { params }).then(res => res.data)
export const getProviders = () => api.get<Record<string, ProviderConfig>>('/api/providers').then(res => res.data)
export const getHealth = () => api.get<{ status: string, providers: Record<string, string> }>('/api/health').then(res => res.data)
export const getConfig = () => api.get<any>('/api/config').then(res => res.data)
export const updateConfig = (config: any) => api.post('/api/config', config).then(res => res.data)
export const getAllModels = () => api.get<Record<string, any>>('/api/models').then(res => res.data)

export default api
