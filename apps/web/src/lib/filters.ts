import { useCallback, useMemo } from 'react'
import { useSearchParams } from 'react-router'

// The global filters live in the URL (/skills?country=CA&period=30d), so a view can be shared
// by link and the back button undoes a filter change. Components never keep them in state.

export const COUNTRIES = ['CA', 'US'] as const
export const PERIODS = ['30d', '90d', '12m'] as const

export type Country = (typeof COUNTRIES)[number]
export type Period = (typeof PERIODS)[number]

export interface Filters {
  /** undefined = both countries. */
  country: Country | undefined
  period: Period
  /** A role family slug; undefined = all roles. */
  role: string | undefined
}

export const DEFAULT_FILTERS: Filters = { country: undefined, period: '90d', role: undefined }

const oneOf = <T extends string>(values: readonly T[], value: string | null): T | undefined =>
  values.find((v) => v === value)

/** Reads filters from a query string; an unknown value falls back to its default. */
export function parseFilters(params: URLSearchParams): Filters {
  const role = params.get('role')
  return {
    country: oneOf(COUNTRIES, params.get('country')?.toUpperCase() ?? null),
    period: oneOf(PERIODS, params.get('period')) ?? DEFAULT_FILTERS.period,
    role: role && /^[a-z0-9-]{1,40}$/.test(role) ? role : undefined,
  }
}

/** Writes filters into params, leaving defaults out so the plain URL stays plain. */
export function writeFilters(params: URLSearchParams, filters: Filters): URLSearchParams {
  const next = new URLSearchParams(params)
  for (const key of ['country', 'period', 'role'] as const) {
    const value = filters[key]
    if (value === undefined || value === DEFAULT_FILTERS[key]) next.delete(key)
    else next.set(key, value)
  }
  return next
}

/** The current filters and a setter that merges a change into the URL as a new history entry. */
export function useFilters() {
  const [params, setParams] = useSearchParams()
  const filters = useMemo(() => parseFilters(params), [params])
  const setFilters = useCallback(
    (change: Partial<Filters>) =>
      setParams((current) => writeFilters(current, { ...parseFilters(current), ...change })),
    [setParams],
  )
  return [filters, setFilters] as const
}
