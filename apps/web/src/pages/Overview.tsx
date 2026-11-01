import { Badge, FEW_COMPANIES, KpiCard } from '@radar/ui'
import { useQuery } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { metaQuery, type OverviewRow, overviewQuery } from '../lib/api.ts'
import { useFilters } from '../lib/filters.ts'
import { integer, salaryParts, shortDay } from '../lib/format.ts'
import { TopSkills } from './TopSkills.tsx'

const COUNTRY_NAMES = { CA: 'Canada', US: 'US' }

/** Headline numbers for the current country filter, then the top skills. */
export function Overview() {
  const [{ country }] = useFilters()
  const overview = useQuery(overviewQuery(country))
  const meta = useQuery(metaQuery(country))

  const rows = overview.data?.data ?? []
  const find = (metric: OverviewRow['metric']) => rows.find((r) => r.metric === metric)
  const openJobs = find('open_jobs')
  const remote = find('remote_share')
  // CAD describes Canadian jobs and USD US ones (ADR 0016); without a country, one card each.
  const salaries = rows.filter((r) => r.metric === 'salary_median')
  const stats = meta.data?.data[0]
  const updated = shortDay(overview.data?.day)
  const pending = overview.isPending || meta.isPending
  const dash = pending ? '…' : '–'

  return (
    <main className="mx-auto flex max-w-336 flex-col gap-6 px-4 pt-8 pb-12 md:px-12">
      <div className="flex flex-col gap-2">
        <p className="m-0 text-xs font-medium tracking-[0.04em] text-accent uppercase">
          Tech roles · {country ? COUNTRY_NAMES[country] : 'Canada + US'}
        </p>
        <h1 className="m-0 font-display text-[40px] leading-11 font-semibold tracking-[-0.015em]">
          Market overview
        </h1>
        <p className="m-0 text-[15px] leading-[22px] text-ink-muted">
          {stats
            ? `${integer(stats.openJobs)} open jobs at ${stats.companies} companies, from public career pages.`
            : 'Open jobs from public career pages.'}
          {updated && ` Updated ${updated}; changes appear once there are days to compare.`}
        </p>
      </div>

      {(overview.isError || meta.isError) && (
        <p role="alert" className="m-0 text-sm text-negative">
          The headline numbers didn’t load. Try again in a minute.
        </p>
      )}

      <div
        className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-6"
        aria-busy={pending}
      >
        <KpiCard
          label="Open jobs · today"
          value={openJobs ? integer(openJobs.value) : dash}
          color="chart-1"
        />
        <KpiCard
          label="Remote share"
          value={remote ? Math.round(remote.value * 100) : dash}
          unit={remote && '%'}
          footnote="Stated as remote; many postings don’t say."
        />
        {salaries.length > 0 ? (
          salaries.map((s) => (
            <KpiCard
              key={s.key}
              label={`Median salary · ${s.currency}`}
              {...salaryParts(s.value, s.currency ?? '')}
              footnote={<Sample n={s.sampleSize} companies={s.companies} what="posted salaries" />}
            />
          ))
        ) : (
          <KpiCard
            label="Median salary"
            value={dash}
            footnote={pending ? undefined : 'No posted salaries.'}
          />
        )}
        <KpiCard label="Companies hiring" value={stats ? integer(stats.companies) : dash} />
      </div>

      <TopSkills country={country} updated={updated} />
    </main>
  )
}

/** "91 posted salaries · 3 companies", with a warning when one employer can set the number. */
function Sample({ n, companies, what }: { n: number; companies: number; what: string }): ReactNode {
  return (
    <span className="inline-flex flex-wrap items-center gap-2">
      <span className="font-mono tabular-nums">
        {integer(n)} {what} · {companies} {companies === 1 ? 'company' : 'companies'}
      </span>
      {companies < FEW_COMPANIES && <Badge tone="warning">Few companies</Badge>}
    </span>
  )
}
