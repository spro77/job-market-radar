import { act, renderHook } from '@testing-library/react'
import type { ReactNode } from 'react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it } from 'vitest'
import { DEFAULT_FILTERS, parseFilters, useFilters, writeFilters } from './filters.ts'

describe('parseFilters', () => {
  it('reads valid values', () => {
    const params = new URLSearchParams('country=CA&period=30d&role=frontend')
    expect(parseFilters(params)).toEqual({ country: 'CA', period: '30d', role: 'frontend' })
  })

  it('accepts a lower-case country', () => {
    expect(parseFilters(new URLSearchParams('country=us')).country).toBe('US')
  })

  it('falls back to defaults for missing or unknown values', () => {
    expect(parseFilters(new URLSearchParams())).toEqual(DEFAULT_FILTERS)
    const params = new URLSearchParams('country=XX&period=7d&role=Not%20a%20slug')
    expect(parseFilters(params)).toEqual(DEFAULT_FILTERS)
  })
})

describe('writeFilters', () => {
  it('leaves defaults out of the URL and keeps unrelated params', () => {
    const next = writeFilters(new URLSearchParams('country=CA&tab=x'), {
      ...DEFAULT_FILTERS,
      period: '12m',
    })
    expect(next.toString()).toBe('tab=x&period=12m')
  })
})

// Renders the hook inside a real data router, so history entries can be checked too.
function renderFilters(url: string) {
  let router!: ReturnType<typeof createMemoryRouter>
  const result = renderHook(() => useFilters(), {
    wrapper: ({ children }: { children: ReactNode }) => {
      router ??= createMemoryRouter([{ path: '/', element: children }], { initialEntries: [url] })
      return <RouterProvider router={router} />
    },
  })
  return { ...result, router: () => router }
}

describe('useFilters', () => {
  it('reads the filters from the URL', () => {
    const { result } = renderFilters('/?country=US&period=12m')
    expect(result.current[0]).toEqual({ country: 'US', period: '12m', role: undefined })
  })

  it('writes a change into the URL as a new history entry, merging with the rest', () => {
    const { result, router } = renderFilters('/?period=30d')
    act(() => result.current[1]({ country: 'CA' }))
    expect(router().state.location.search).toBe('?period=30d&country=CA')
    expect(result.current[0]).toEqual({ country: 'CA', period: '30d', role: undefined })

    act(() => {
      router().navigate(-1)
    })
    expect(result.current[0].country).toBeUndefined()
  })

  it('removes a filter set back to its default', () => {
    const { result, router } = renderFilters('/?country=CA')
    act(() => result.current[1]({ country: undefined }))
    expect(router().state.location.search).toBe('')
  })
})
