import type { ReactNode } from 'react'
import { cn } from '../lib/cn'

export interface DeltaProps {
  /** The change; undefined (nothing to compare with yet) renders nothing. */
  value: number | undefined
  /** Default '%'. */
  unit?: string
  /** Default 1. */
  digits?: number
  /** The comparison, e.g. "vs prior 30 days". */
  label?: ReactNode
  /** When true a decrease is good: swaps the colors, never the arrow. */
  invert?: boolean
}

/** A change shown with an arrow, a sign and a color, so the direction reads without color. */
export function Delta({ value, unit = '%', digits = 1, label, invert }: DeltaProps) {
  if (value == null || Number.isNaN(value)) return null
  const up = value > 0
  const flat = value === 0
  const good = invert ? !up : up
  return (
    <span
      className={cn(
        'inline-flex items-baseline gap-1 font-mono text-[13px] font-medium tabular-nums',
        flat ? 'text-ink-muted' : good ? 'text-positive' : 'text-negative',
      )}
    >
      <span className="text-[10px]" aria-hidden>
        {flat ? '■' : up ? '▲' : '▼'}
      </span>
      <span>
        {up ? '+' : ''}
        {value.toFixed(digits)}
        {unit}
      </span>
      {label && <span className="ml-0.5 font-text font-normal text-ink-muted">{label}</span>}
    </span>
  )
}
