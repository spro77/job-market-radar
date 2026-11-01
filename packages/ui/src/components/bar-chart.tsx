import { tokenColor } from '../lib/cn'
import { formatNumber, niceMax } from '../lib/format'

export interface BarChartProps {
  /** Already sorted, usually descending. */
  data: { label: string; value: number; color?: string }[]
  /** One color for all bars (a chart token); otherwise chart-1…8 in turn. */
  color?: string
  format?: (value: number) => string
  max?: number
  /** Label column width in px, default 120. */
  labelWidth?: number
  /** Accessible name. */
  label?: string
}

/** One measure across a handful of categories, as horizontal bars. */
export function BarChart({
  data,
  color,
  format = formatNumber,
  max,
  labelWidth = 120,
  label,
}: BarChartProps) {
  const top = max ?? niceMax(Math.max(0, ...data.map((d) => d.value)))
  return (
    <ul className="m-0 flex list-none flex-col gap-3 p-0" aria-label={label}>
      {data.map((d, i) => (
        <li
          key={d.label}
          className="grid items-center gap-3 font-text text-[13px] text-ink-muted"
          style={{ gridTemplateColumns: `${labelWidth}px 1fr 64px` }}
        >
          <span className="truncate">{d.label}</span>
          <span className="h-3 rounded-full bg-surface-sunken">
            <span
              className="glow block h-full rounded-full bg-current transition-[width] duration-400 motion-reduce:transition-none"
              style={{
                width: `${Math.max(0, (d.value / top) * 100)}%`,
                color: tokenColor(d.color ?? color, `var(--chart-${(i % 8) + 1})`),
              }}
            />
          </span>
          <span className="text-right font-mono text-ink tabular-nums">{format(d.value)}</span>
        </li>
      ))}
    </ul>
  )
}
