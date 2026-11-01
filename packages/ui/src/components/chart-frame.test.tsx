import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ChartFrame } from './chart-frame'

describe('ChartFrame', () => {
  it('renders the chart, sample and source when ready', () => {
    render(
      <ChartFrame
        title="Top skills"
        source="Greenhouse"
        updated="Oct 31"
        sampleSize={1240}
        companies={12}
      >
        <p>chart</p>
      </ChartFrame>,
    )
    expect(screen.getByRole('region', { name: 'Top skills' })).toBeInTheDocument()
    expect(screen.getByText('chart')).toBeInTheDocument()
    expect(screen.getByText('Source: Greenhouse')).toBeInTheDocument()
    expect(screen.getByText('n = 1,240 · 12 companies · Updated Oct 31')).toBeInTheDocument()
    expect(screen.queryByText('Few companies')).not.toBeInTheDocument()
  })

  it('shows a skeleton instead of the chart while loading', () => {
    render(
      <ChartFrame title="Top skills" state="loading" companies={1}>
        <p>chart</p>
      </ChartFrame>,
    )
    expect(screen.getByRole('status', { name: 'Loading chart' })).toBeInTheDocument()
    expect(screen.queryByText('chart')).not.toBeInTheDocument()
    expect(screen.queryByText('Few companies')).not.toBeInTheDocument()
  })

  it('explains an empty result', () => {
    render(<ChartFrame title="Top skills" state="empty" emptyTitle="No skills yet" />)
    expect(screen.getByText('No skills yet')).toBeInTheDocument()
  })

  it('shows an error with a retry button', () => {
    const onRetry = vi.fn()
    render(<ChartFrame title="Top skills" state="error" onRetry={onRetry} />)
    expect(screen.getByRole('alert')).toHaveTextContent('This chart didn’t load')
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }))
    expect(onRetry).toHaveBeenCalledOnce()
  })

  it.each([
    [1, true],
    [2, true],
    [3, false],
  ])('with %i companies shows the few-companies badge: %s', (companies, shown) => {
    render(<ChartFrame title="Salaries" companies={companies} />)
    expect(screen.queryByText('Few companies') !== null).toBe(shown)
  })
})
