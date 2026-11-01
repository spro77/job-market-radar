import { BarChart, ChartFrame, Tabs, TabsContent, TabsList, TabsTrigger } from '@radar/ui'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { skillsQuery } from '../lib/api.ts'
import type { Country } from '../lib/filters.ts'
import { percent } from '../lib/format.ts'

type Measure = 'jobs' | 'companies'

const SUBTITLES: Record<Measure, string> = {
  jobs: 'Share of open jobs that mention each skill',
  companies: 'Share of hiring companies with at least one job that mentions it',
}

/**
 * Top skills by share of jobs, or by share of companies (skill_share / skill_companies), so a
 * skill carried by one large employer shows as such (ADR 0015). The measure is a view choice,
 * not a filter, so it stays out of the URL.
 */
export function TopSkills({
  country,
  updated,
}: {
  country: Country | undefined
  updated?: string
}) {
  const [measure, setMeasure] = useState<Measure>('jobs')
  const skills = useQuery(skillsQuery(country, 10))
  const rows = skills.data?.data ?? []
  const first = rows[0]

  const byJobs = rows.map((r) => ({ label: r.name, value: r.share * 100 }))
  const byCompanies = rows
    .map((r) => ({ label: r.name, value: (r.companyShare ?? 0) * 100 }))
    .sort((a, b) => b.value - a.value)

  const state = skills.isPending
    ? 'loading'
    : skills.isError
      ? 'error'
      : rows.length
        ? 'ready'
        : 'empty'

  return (
    <Tabs value={measure} onValueChange={(v) => setMeasure(v as Measure)}>
      <ChartFrame
        title="Top skills today"
        subtitle={SUBTITLES[measure]}
        actions={
          <TabsList aria-label="Measure">
            <TabsTrigger value="jobs">By jobs</TabsTrigger>
            <TabsTrigger value="companies">By companies</TabsTrigger>
          </TabsList>
        }
        source="Greenhouse, Ashby"
        updated={updated}
        sampleSize={
          measure === 'jobs' ? first?.sampleSize : (first?.companySampleSize ?? undefined)
        }
        companies={first?.companySampleSize ?? undefined}
        state={state}
        onRetry={() => skills.refetch()}
      >
        <TabsContent value="jobs">
          <BarChart
            data={byJobs}
            color="chart-1"
            format={percent}
            labelWidth={140}
            label="Share of open jobs by skill"
          />
        </TabsContent>
        <TabsContent value="companies">
          <BarChart
            data={byCompanies}
            color="chart-2"
            format={percent}
            max={100}
            labelWidth={140}
            label="Share of companies by skill"
          />
        </TabsContent>
      </ChartFrame>
    </Tabs>
  )
}
