import { app } from '@azure/functions'
import { db } from '../db/client.js'
import { currencyOf, endpoint } from '../http.js'
import { baseQuery } from '../schemas.js'

// Headline numbers: open jobs, remote share and the salary median. Without a country the
// totals for both countries; with one, that country's slice (salary key 'CA/CAD').
const handler = endpoint(baseQuery, async (day, { country }) => {
  const rows = await db
    .selectFrom('daily_aggregates')
    .select(['metric', 'key', 'value', 'sample_size', 'companies'])
    .where('day', '=', day)
    .where('metric', 'in', ['open_jobs', 'remote_share', 'salary_median'])
    .$call((qb) =>
      country
        ? qb
            .where('dimension', '=', 'country')
            .where((eb) => eb.or([eb('key', '=', country), eb('key', 'like', `${country}/%`)]))
        : qb.where('dimension', '=', 'all'),
    )
    .orderBy('metric')
    .orderBy('key')
    .execute()

  return rows.map((row) => ({
    metric: row.metric,
    key: row.key,
    currency: row.metric === 'salary_median' ? currencyOf(row.key) : null,
    value: row.value,
    sampleSize: row.sample_size,
    companies: row.companies,
  }))
})

app.http('overview', { methods: ['GET'], authLevel: 'anonymous', handler })
