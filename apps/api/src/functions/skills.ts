import { app } from '@azure/functions'
import { db } from '../db/client.js'
import { endpoint } from '../http.js'
import { skillsQuery } from '../schemas.js'

// Top skills by share of open jobs, each with its share of companies next to it, so a skill
// carried by one large employer is visible as such (ADR 0015).
const handler = endpoint(skillsQuery, async (day, { country, limit }) => {
  const rows = await db
    .selectFrom('daily_aggregates as s')
    .innerJoin('skills as k', 'k.slug', 's.key')
    .leftJoin('daily_aggregates as c', (join) =>
      join
        .onRef('c.day', '=', 's.day')
        .onRef('c.key', '=', 's.key')
        .on('c.metric', '=', 'skill_companies')
        .on('c.country', country ? '=' : 'is', country ?? null),
    )
    .select([
      's.key as slug',
      'k.name',
      'k.category',
      's.value as share',
      's.sample_size',
      's.companies',
      'c.value as companyShare',
      'c.sample_size as companySampleSize',
    ])
    .where('s.day', '=', day)
    .where('s.metric', '=', 'skill_share')
    .where('s.country', country ? '=' : 'is', country ?? null)
    .orderBy('s.value', 'desc')
    .orderBy('k.name')
    .limit(limit)
    .execute()

  return rows.map(({ sample_size, ...row }) => ({ ...row, sampleSize: sample_size }))
})

app.http('skills', { methods: ['GET'], authLevel: 'anonymous', handler })
