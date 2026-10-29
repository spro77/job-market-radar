-- migrate:up
alter table raw_postings rename column fetched_at to changed_at;
-- Postgres 18+ names NOT NULL constraints; keep the name in step with the column.
-- Older versions have no such constraint, so the rename is conditional.
do $$
begin
  if exists (select from pg_constraint where conname = 'raw_postings_fetched_at_not_null') then
    alter table raw_postings
      rename constraint raw_postings_fetched_at_not_null to raw_postings_changed_at_not_null;
  end if;
end $$;
alter table raw_postings add column last_seen_at timestamptz not null default now();

-- migrate:down
alter table raw_postings drop column last_seen_at;
do $$
begin
  if exists (select from pg_constraint where conname = 'raw_postings_changed_at_not_null') then
    alter table raw_postings
      rename constraint raw_postings_changed_at_not_null to raw_postings_fetched_at_not_null;
  end if;
end $$;
alter table raw_postings rename column changed_at to fetched_at;
