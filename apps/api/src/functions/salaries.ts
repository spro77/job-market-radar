import { app } from '@azure/functions'
import { db } from '../db/client.js'
import { currencyOf, endpoint } from '../http.js'
import { baseQuery } from '../schemas.js'

const QUARTILES = { salary_p25: 'p25', salary_median: 'median', salary_p75: 'p75' } as const

type Region = {
  region: string
  currency: string
  p25: number | null
  median: number | null
  p75: number | null
  sampleSize: number
  companies: number | null
}

// Yearly salary quartiles per region ('CA/ON'), largest samples first. The currency comes
// from the key; a currency only ever describes its own country (ADR 0016).
const handler = endpoint(baseQuery, async (day, { country }) => {
  const rows = await db
    .selectFrom('daily_aggregates')
    .select(['metric', 'key', 'value', 'sample_size', 'companies'])
    .where('day', '=', day)
    .where('dimension', '=', 'region')
    .where('metric', 'in', Object.keys(QUARTILES))
    .$if(Boolean(country), (qb) => qb.where('key', 'like', `${country}/%`))
    .execute()

  const regions = new Map<string, Region>()
  for (const row of rows) {
    const currency = currencyOf(row.key)
    const region = row.key.slice(0, -currency.length - 1)
    const entry = regions.get(row.key) ?? {
      region,
      currency,
      p25: null,
      median: null,
      p75: null,
      sampleSize: row.sample_size,
      companies: row.companies,
    }
    entry[QUARTILES[row.metric as keyof typeof QUARTILES]] = row.value
    regions.set(row.key, entry)
  }
  return [...regions.values()].sort((a, b) => b.sampleSize - a.sampleSize)
})

app.http('salaries', { methods: ['GET'], authLevel: 'anonymous', handler })
