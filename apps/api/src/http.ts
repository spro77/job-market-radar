import type { HttpRequest, HttpResponseInit, InvocationContext } from '@azure/functions'
import { sql } from 'kysely'
import { z } from 'zod'
import { db } from './db/client.js'
import type { BaseQuery } from './schemas.js'

// Aggregates change once a day, so browsers and the CDN may keep a response for an hour.
const CACHE = { 'Cache-Control': 'public, max-age=3600' }

type Payload<T> = { day: string | null; country: string | null; data: T[] }

/** The requested day, or the latest one in daily_aggregates; null when the table is empty. */
export async function resolveDay(query: BaseQuery): Promise<string | null> {
  if (query.day) return query.day
  const row = await db
    .selectFrom('daily_aggregates')
    .select(sql<string | null>`max(day)::text`.as('day'))
    .executeTakeFirst()
  return row?.day ?? null
}

/**
 * Wraps a GET handler: validates the query string with schema (400 with the reason if it
 * fails), resolves the day, and answers { day, country, data } with a cache header.
 */
export function endpoint<S extends z.ZodType<BaseQuery>, T>(
  schema: S,
  load: (day: string, query: z.output<S>) => Promise<T[]>,
) {
  return async (request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> => {
    const parsed = schema.safeParse(Object.fromEntries(request.query))
    if (!parsed.success) {
      return { status: 400, jsonBody: { error: z.prettifyError(parsed.error) } }
    }
    try {
      const day = await resolveDay(parsed.data)
      const body: Payload<T> = {
        day,
        country: parsed.data.country ?? null,
        data: day ? await load(day, parsed.data) : [],
      }
      return { status: 200, headers: CACHE, jsonBody: body }
    } catch (error) {
      context.error(error)
      return { status: 500, jsonBody: { error: 'Internal error' } }
    }
  }
}

/** The currency at the end of a salary key: 'CA/ON/CAD' -> 'CAD'. */
export const currencyOf = (key: string) => key.split('/').at(-1) ?? key
