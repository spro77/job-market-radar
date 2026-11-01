import { tokenColor } from '../lib/cn'

export interface SparklineProps {
  /** At least two values, oldest first; fewer render nothing. */
  values: number[]
  /** Chart token, e.g. "chart-1". */
  color?: string
  width?: number
  height?: number
}

/** A word-sized trend line, scaled to its own range. Decorative: the number sits next to it. */
export function Sparkline({ values, color, width = 112, height = 32 }: SparklineProps) {
  if (values.length < 2) return null
  const min = Math.min(...values)
  const range = Math.max(...values) - min || 1
  const points = values.map((v, i) => [
    2 + (i * (width - 4)) / (values.length - 1),
    height - 3 - ((v - min) / range) * (height - 6),
  ])
  const line = points
    .map(([x, y], i) => `${i ? 'L' : 'M'}${x?.toFixed(1)} ${y?.toFixed(1)}`)
    .join('')
  const [lastX = 0, lastY = 0] = points.at(-1) ?? []
  return (
    <svg
      className="block flex-none overflow-visible"
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
      style={{ color: tokenColor(color) }}
      aria-hidden
    >
      <path
        d={`${line}L${lastX.toFixed(1)} ${height}L2 ${height}Z`}
        fill="currentColor"
        opacity={0.14}
      />
      <path
        className="glow"
        d={line}
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <circle cx={lastX} cy={lastY} r={2.5} fill="currentColor" />
    </svg>
  )
}
