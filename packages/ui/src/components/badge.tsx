import type { ReactNode } from 'react'
import { cn, tokenColor } from '../lib/cn'

export interface BadgeProps {
  tone?: 'neutral' | 'accent' | 'positive' | 'negative' | 'warning'
  /** Chart token name ("chart-3") or a CSS color, drawn as a leading dot. */
  color?: string
  /** Short trailing number, set in mono. */
  count?: ReactNode
  className?: string
  children: ReactNode
}

const tones = {
  neutral: 'border-border bg-surface-raised text-ink',
  accent: 'border-transparent bg-accent-soft text-accent',
  positive: 'border-transparent bg-positive-soft text-positive',
  negative: 'border-transparent bg-negative-soft text-negative',
  warning: 'border-transparent bg-warning-soft text-warning',
}

/** A compact pill for a skill, a posting or a data-quality state. */
export function Badge({ tone = 'neutral', color, count, className, children }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex h-6 items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 font-text text-xs font-medium',
        tones[tone],
        className,
      )}
    >
      {color && (
        <span
          className="size-2 flex-none rounded-full"
          style={{ background: tokenColor(color) }}
          aria-hidden
        />
      )}
      <span>{children}</span>
      {count != null && (
        <span className={cn('font-mono tabular-nums', tone === 'neutral' && 'text-ink-muted')}>
          {count}
        </span>
      )}
    </span>
  )
}
