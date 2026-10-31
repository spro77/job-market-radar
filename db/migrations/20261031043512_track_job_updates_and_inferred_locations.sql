-- migrate:up

-- When the normalizer last wrote this row. A raw posting with a newer changed_at
-- is normalized again; the unique (source, source_id) index serves the join.
alter table jobs add column updated_at timestamptz not null default now();

-- True when the location is not in the posting but filled in by us,
-- e.g. a "Remote" job placed in the company's headquarters country.
alter table job_locations add column inferred boolean not null default false;

-- migrate:down

alter table job_locations drop column inferred;
alter table jobs drop column updated_at;
