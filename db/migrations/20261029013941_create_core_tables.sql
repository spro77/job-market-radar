-- migrate:up

create table companies (
  id bigint generated always as identity primary key,
  name text not null,
  slug text not null unique,
  ats text not null check (ats in ('greenhouse', 'lever', 'ashby')),
  ats_token text not null,
  hq_country char(2),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (ats, ats_token)
);

create table fetch_runs (
  id bigint generated always as identity primary key,
  company_id bigint not null references companies (id),
  started_at timestamptz not null,
  finished_at timestamptz,
  -- null while the run is in progress
  status text check (status in ('ok', 'failed')),
  jobs_seen integer,
  error text
);

create table raw_postings (
  source text not null,
  source_id text not null,
  company_id bigint not null references companies (id),
  payload jsonb not null,
  payload_hash text not null,
  fetched_at timestamptz not null default now(),
  primary key (source, source_id)
);

create table jobs (
  id bigint generated always as identity primary key,
  company_id bigint not null references companies (id),
  source text not null,
  source_id text not null,
  title text not null,
  url text,
  description_text text,
  location_raw text,
  workplace_type text not null default 'unknown'
    check (workplace_type in ('onsite', 'hybrid', 'remote', 'unknown')),
  salary_min numeric,
  salary_max numeric,
  salary_currency char(3),
  salary_period text check (salary_period in ('year', 'hour')),
  salary_source text not null default 'none'
    check (salary_source in ('structured', 'text', 'none')),
  posted_at timestamptz,
  first_seen_at timestamptz not null,
  last_seen_at timestamptz not null,
  closed_at timestamptz,
  unique (source, source_id),
  check (salary_min >= 0),
  check (salary_min <= salary_max),
  check (salary_source <> 'none' or (salary_min is null and salary_max is null))
);

create table job_locations (
  id bigint generated always as identity primary key,
  job_id bigint not null references jobs (id) on delete cascade,
  country char(2),
  region text,
  city text,
  is_primary boolean not null default false
);

create index fetch_runs_company_started_idx on fetch_runs (company_id, started_at desc);
create index jobs_company_id_idx on jobs (company_id);
create index jobs_open_last_seen_idx on jobs (last_seen_at) where closed_at is null;
create index job_locations_job_id_idx on job_locations (job_id);
create index job_locations_country_region_idx on job_locations (country, region);
-- at most one primary location per job
create unique index job_locations_one_primary_idx on job_locations (job_id) where is_primary;

-- migrate:down

drop table job_locations;
drop table jobs;
drop table raw_postings;
drop table fetch_runs;
drop table companies;
