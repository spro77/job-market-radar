import { app } from '@azure/functions'
import { db } from '../db/client.js'
import { endpoint } from '../http.js'
import { baseQuery } from '../schemas.js'

// For the "Updated Oct 31 · 602 jobs at 4 companies" line. data has one item, or none when
// the day has no rows.
const handler = endpoint(baseQuery, async (day, { country }) => {
  const row = await db
    .selectFrom('daily_aggregates')
    .select(['value', 'companies'])
    .where('day', '=', day)
    .where('metric', '=', 'open_jobs')
    .where('dimension', '=', country ? 'country' : 'all')
    .where('key', '=', country ?? 'all')
    .executeTakeFirst()

  return row ? [{ openJobs: row.value, companies: row.companies }] : []
})

app.http('meta', { methods: ['GET'], authLevel: 'anonymous', handler })
