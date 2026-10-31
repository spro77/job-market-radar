-- migrate:up

-- The skill dictionary; services/ingest/skills.toml is the source, skills_run syncs it here.
create table skills (
  id bigint generated always as identity primary key,
  name text not null unique,  -- canonical name: "React"
  slug text not null unique,  -- derived from name: "react"
  category text not null check (category in
    ('language', 'framework', 'library', 'cloud', 'database', 'tool', 'platform', 'practice')),
  aliases text[] not null default '{}'  -- "reactjs", "react.js"
);

-- method is part of the key, so several extractors can tag the same skill on the same job
-- and be compared against each other.
create table job_skills (
  job_id bigint not null references jobs (id) on delete cascade,
  skill_id bigint not null references skills (id),
  method text not null check (method in ('dictionary', 'ml', 'llm')),
  confidence real,
  primary key (job_id, skill_id, method)
);
create index job_skills_skill_id_idx on job_skills (skill_id);

-- When skills were last extracted; a job updated after that is extracted again.
alter table jobs add column skills_extracted_at timestamptz;

-- migrate:down

alter table jobs drop column skills_extracted_at;
drop table job_skills;
drop table skills;
