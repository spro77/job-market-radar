const CURRENCY_PREFIX: Record<string, string> = { CAD: 'CA$', USD: 'US$' }

/** 171000, 'CAD' → { value: 'CA$171', unit: 'k' }: the KpiCard shows the unit smaller. */
export function salaryParts(value: number, currency: string) {
  return { value: `${CURRENCY_PREFIX[currency] ?? currency}${Math.round(value / 1000)}`, unit: 'k' }
}

/** 18.6 → '18.6%', 41.2 → '41%'. Takes a percentage, not a share. */
export const percent = (v: number) => `${v.toFixed(v >= 10 ? 0 : 1)}%`

/** 'YYYY-MM-DD' → 'Oct 31', read as a calendar day (no time zone shift). */
export function shortDay(day: string | null | undefined) {
  if (!day) return undefined
  const [y = 0, m = 1, d = 1] = day.split('-').map(Number)
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  })
}

export const integer = (n: number) => n.toLocaleString('en-US')
