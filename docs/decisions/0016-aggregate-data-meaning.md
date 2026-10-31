# 0016. What the aggregates mean: salary currency and remote share

Status: Accepted · 2026-10-31

## Context

`aggregate_run` turns open jobs into the numbers the dashboards show (`daily_aggregates`). Two numbers came out wrong on the first run on 2026-10-31, not because of the SQL but because of what the source data can and cannot say:

- **Salary in the wrong country.** Cohere posts one CAD range on jobs listed in both Canada and the US. Counted for every location, it produced a `US/CAD` median of 392,500 from 33 jobs at one company: a Canadian headquarters range reported as a US salary. Stripe does the reverse with USD ranges on Canadian locations.
- **Remote share inflated.** Greenhouse has no workplace field. The only type it ever reveals is `remote`, from "Remote" in the location text; onsite and hybrid stay `unknown`. With `unknown` left out of the denominator, the US remote share was 0.91.

## Decision

- **The currency ties a salary to a country.** A CAD range describes only the job's Canadian locations, a USD range only its US locations. A job in both countries with one CAD range is in the Canadian salary slices and counts as a job without a salary in the US ones. Other pairs (CAD in the US, USD in Canada, any other currency) are not counted at all. Salary keys keep the currency (`CA/ON/CAD`) so the dashboard never has to guess it.
- **Remote share is the share of all open jobs stated as remote.** `unknown` stays in the denominator. The metric reads "jobs that say remote", not "jobs that are remote".

## Alternatives considered

- **Count the salary for every location of the job.** Simple, but it puts headquarters pay into other countries' medians, as the 392,500 showed.
- **Convert currencies.** Exchange rates do not turn a Toronto range into a New York one; the range was set for one labour market. Conversion may come later for comparing countries, never for assigning salaries to them.
- **Remote share over jobs with a known workplace type.** Correct in principle, but with one source that only reveals remote it measures the parser, not the market.

## Consequences

- An absent number is preferred to a wrong one: some slices have fewer salaries, and US salaries currently come from one company (Stripe, 31 jobs). `sample_size` and `companies` show this next to every number.
- Remote share is a lower bound. It becomes more accurate as sources with a real workplace field (Ashby, Lever) grow in the mix.
- If a source ever states a range per location, the rule should use that instead of the currency.
