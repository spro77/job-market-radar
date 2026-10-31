import { z } from 'zod'

// ?country= and ?day= with nothing after them mean "not given", not an invalid value.
const optional = <T extends z.ZodType>(schema: T) =>
  z.preprocess((value) => (value === '' ? undefined : value), schema.optional())

export const baseQuery = z.object({
  country: optional(z.enum(['CA', 'US'])), // empty means both countries
  day: optional(z.iso.date()), // empty means the latest day in daily_aggregates
})

export const skillsQuery = baseQuery.extend({
  limit: z.coerce.number().int().min(1).max(100).default(20),
})

export type BaseQuery = z.output<typeof baseQuery>
