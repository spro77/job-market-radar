import type { ReactNode } from 'react'
import { cn } from '../lib/cn'
import { Badge } from './badge'
import { Button } from './button'

/** Fewer companies than this and one employer can set the picture (ADR 0015). */
export const FEW_COMPANIES = 3

export interface ChartFrameProps {
  /** The question or finding: "Median salary by province". */
  title: ReactNode
  /** Scope: "Share of open jobs that mention each skill". */
  subtitle?: ReactNode
  /** Small ghost buttons or a toggle, top right. */
  actions?: ReactNode
  /** Data source line: "Greenhouse, Ashby". */
  source?: string
  /** Freshness: "Oct 31". */
  updated?: string
  /** Jobs (or companies) behind the numbers, shown in the footer. */
  sampleSize?: number
  /** Companies behind the numbers; below FEW_COMPANIES a warning badge says so. */
  companies?: number
  state?: 'ready' | 'loading' | 'empty' | 'error'
  emptyTitle?: string
  emptyHint?: string
  errorHint?: string
  onRetry?: () => void
  className?: string
  children?: ReactNode
}

/** The card every chart sits in: title, the chart, its sample and source, and its states. */
export function ChartFrame(props: ChartFrameProps) {
  const { title, subtitle, actions, source, updated, sampleSize, companies } = props
  const state = props.state ?? 'ready'
  const fewCompanies = state === 'ready' && companies != null && companies < FEW_COMPANIES
  const sample = [
    sampleSize != null && `n = ${sampleSize.toLocaleString('en-US')}`,
    companies != null && `${companies} ${companies === 1 ? 'company' : 'companies'}`,
  ].filter(Boolean)

  return (
    <section
      className={cn(
        'flex min-w-0 flex-col gap-4 rounded-lg border border-border bg-surface p-5',
        props.className,
      )}
      aria-label={typeof title === 'string' ? title : undefined}
    >
      <header className="flex items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="m-0 font-text text-base font-semibold text-ink">{title}</h3>
            {fewCompanies && <Badge tone="warning">Few companies</Badge>}
          </div>
          {subtitle && (
            <p className="mt-0.5 mb-0 font-text text-[13px] text-ink-muted">{subtitle}</p>
          )}
        </div>
        {actions && <div className="flex flex-none gap-2">{actions}</div>}
      </header>

      <div className="relative min-h-30 min-w-0">
        <FrameBody {...props} state={state} />
      </div>

      {(source || updated || sample.length > 0) && (
        <footer className="flex flex-wrap justify-between gap-x-4 gap-y-1 border-t border-border pt-3 font-text text-[11.5px] text-ink-muted">
          <span>{source ? `Source: ${source}` : ''}</span>
          <span className="font-mono tabular-nums">
            {[...sample, updated && `Updated ${updated}`].filter(Boolean).join(' · ')}
          </span>
        </footer>
      )}
    </section>
  )
}

function FrameBody({
  state,
  children,
  emptyTitle,
  emptyHint,
  errorHint,
  onRetry,
}: ChartFrameProps) {
  const box =
    'flex min-h-45 flex-col items-center justify-center gap-2 text-center font-text text-[13px] text-ink-muted'
  if (state === 'loading') {
    return (
      <div
        className={cn(box, 'items-stretch justify-end gap-3')}
        aria-busy="true"
        aria-label="Loading chart"
        role="status"
      >
        {['w-full', 'w-[82%]', 'w-[64%]', 'w-[40%]'].map((w) => (
          <span key={w} className={cn('skeleton h-3.5 rounded-sm', w)} />
        ))}
      </div>
    )
  }
  if (state === 'empty') {
    return (
      <div className={box}>
        <strong className="font-semibold text-ink">
          {emptyTitle ?? 'No postings match these filters'}
        </strong>
        <span>{emptyHint ?? 'Widen the date range or clear a filter.'}</span>
      </div>
    )
  }
  if (state === 'error') {
    return (
      <div className={box} role="alert">
        <strong className="font-semibold text-negative">This chart didn’t load</strong>
        <span>{errorHint ?? 'The data service didn’t respond. Try again in a minute.'}</span>
        {onRetry && (
          <Button size="sm" onClick={onRetry}>
            Try again
          </Button>
        )}
      </div>
    )
  }
  return <>{children}</>
}
