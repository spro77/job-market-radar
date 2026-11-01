/** Short number for axes and bars: 1240 → "1.2k", 18000 → "18k". */
export function formatNumber(n: number) {
  if (Number.isNaN(n)) return '–'
  const a = Math.abs(n)
  if (a >= 1e6) return `${(n / 1e6).toFixed(a % 1e6 ? 1 : 0)}M`
  if (a >= 1e3) return `${(n / 1e3).toFixed(a % 1e3 ? 1 : 0)}k`
  return String(Math.round(n * 10) / 10)
}

/** A round axis maximum at or above v: 1, 2, 2.5, 5 or 10 times a power of ten. */
export function niceMax(v: number) {
  if (!(v > 0)) return 1
  const e = 10 ** Math.floor(Math.log10(v))
  const f = v / e
  return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * e
}
