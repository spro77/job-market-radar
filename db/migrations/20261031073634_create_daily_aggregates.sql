-- migrate:up

-- Precomputed numbers for the dashboards, one row per (day, metric, slice); aggregate_run
-- rewrites a day in full. One narrow table, so a new chart is a new query, not a migration:
-- metric and dimension are deliberately not limited by CHECK.
create table daily_aggregates (
  id bigint generated always as identity primary key,
  day date not null,
  metric text not null,     -- 'open_jobs', 'skill_share', 'salary_median', ...
  dimension text not null,  -- 'all', 'country', 'region', 'company', 'skill'
  key text not null,        -- 'all', 'CA', 'CA/ON', 'stripe', 'react'; salaries add currency
  country char(2) check (country in ('CA', 'US')),  -- country filter; null means both
  value numeric not null,
  sample_size integer not null check (sample_size > 0),  -- what value is computed over
  companies integer check (companies > 0),               -- companies behind value
  -- country is nullable, so a primary key cannot cover it; nulls not distinct makes
  -- (…, null) collide with (…, null) like any other value.
  unique nulls not distinct (day, metric, dimension, key, country)
);

-- migrate:down

drop table daily_aggregates;
