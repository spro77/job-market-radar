import { queryOptions } from '@tanstack/react-query'
import type { Country } from './filters.ts'

// Types mirror apps/api's responses: every endpoint answers { day, country, data }.

export interface Payload<T> {
  /** The aggregates' day, YYYY-MM-DD; null when there are none yet. */
  day: string | null
  country: Country | null
  data: T[]
}

export interface OverviewRow {
  metric: 'open_jobs' | 'remote_share' | 'salary_median'
  key: string
  currency: string | null
  value: number
  sampleSize: number
  companies: number
}

export interface SkillRow {
  slug: string
  name: string
  category: string
  share: number
  sampleSize: number
  companies: number
  companyShare: number | null
  companySampleSize: number | null
}

export interface MetaRow {
  openJobs: number
  companies: number
}

const API_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:7071/api').replace(/\/$/, '')

async function get<T>(path: string, params: Record<string, string | number | undefined>) {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) query.set(key, String(value))
  }
  const response = await fetch(`${API_URL}/${path}?${query}`)
  if (!response.ok) throw new Error(`GET /${path} answered ${response.status}`)
  return (await response.json()) as Payload<T>
}

export const overviewQuery = (country?: Country) =>
  queryOptions({
    queryKey: ['overview', country ?? 'all'],
    queryFn: () => get<OverviewRow>('overview', { country }),
  })

export const skillsQuery = (country?: Country, limit = 10) =>
  queryOptions({
    queryKey: ['skills', country ?? 'all', limit],
    queryFn: () => get<SkillRow>('skills', { country, limit }),
  })

export const metaQuery = (country?: Country) =>
  queryOptions({
    queryKey: ['meta', country ?? 'all'],
    queryFn: () => get<MetaRow>('meta', { country }),
  })
