import { Kysely, PostgresDialect } from 'kysely'
import pg from 'pg'
import type { DB } from './types.js'

// types.ts is generated with --date-parser string --numeric-parser number; make pg return
// the same at runtime. By default pg turns a date into a Date at local midnight (a day off
// west of UTC) and numeric into a string.
pg.types.setTypeParser(pg.types.builtins.DATE, (value) => value)
pg.types.setTypeParser(pg.types.builtins.NUMERIC, (value) => Number.parseFloat(value))

const connectionString = process.env.DATABASE_URL
if (!connectionString) {
  throw new Error(
    'DATABASE_URL is not set: copy local.settings.example.json to local.settings.json',
  )
}

// One pool per Functions instance, created when the module loads and reused across
// invocations. The URL must be Neon's pooled endpoint (-pooler): many instances can run at
// once, and direct connections would hit Neon's connection limit.
export const db = new Kysely<DB>({
  dialect: new PostgresDialect({
    pool: new pg.Pool({ connectionString, max: 3, idleTimeoutMillis: 30_000 }),
  }),
})
