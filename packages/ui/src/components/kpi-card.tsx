import type { ReactNode } from 'react'
import { cn } from '../lib/cn'
import { Delta } from './delta'
import { Sparkline } from './sparkline'

export interface KpiCardProps {
  /** What and over which window: "Open jobs · today". */
  label: ReactNode
  /** Pre-formatted headline value: "18,420", "$124". */
  value: ReactNode
  unit?: ReactNode
  /** Percent change; undefined while there is nothing to compare with. */
  delta?: number
  deltaLabel?: ReactNode
  /** When true a negative delta reads as good. */
  invertDelta?: boolean
  /** Values for the sparkline, oldest first. */
  trend?: number[]
  /** Chart token for the sparkline. */
  color?: string
  /** One quiet line under the value: sample size, a caveat. Not in the design system yet. */
  footnote?: ReactNode
  className?: string
}

/** One headline number with its change and a short trend, in the top row of a page. */
export function KpiCard(props: KpiCardProps) {
  const { label, value, unit, delta, deltaLabel, invertDelta, trend, color, footnote } = props
  return (
    <div
      className={cn(
        'flex min-w-0 flex-col gap-2 rounded-lg border border-border bg-surface p-5',
        props.className,
      )}
    >
      <div className="font-text text-xs font-medium uppercase tracking-[0.04em] text-ink-muted">
        {label}
      </div>
      <div className="flex items-end justify-between gap-4">
        <div className="font-mono text-4xl font-medium tracking-[-0.02em] text-ink tabular-nums">
          {value}
          {unit && <span className="ml-1 text-base tracking-normal text-ink-muted">{unit}</span>}
        </div>
        {trend && <Sparkline values={trend} color={color} />}
      </div>
      <Delta value={delta} label={deltaLabel} invert={invertDelta} />
      {footnote && <div className="font-text text-[13px] text-ink-muted">{footnote}</div>}
    </div>
  )
}
