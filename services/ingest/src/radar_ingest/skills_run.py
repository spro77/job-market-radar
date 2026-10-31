"""Sync skills.toml into the skills table, then tag jobs with dictionary skills.

Only jobs updated since their last extraction are processed, unless the dictionary changed
(then every job is, since any job may gain or lose a skill) or --all is given.
Everything runs in one transaction.
Run with: uv run python -m radar_ingest.skills_run [--all]
"""

import argparse

from psycopg import Cursor

from radar_ingest.db import connect
from radar_ingest.normalize.skills import Skill, build_dictionary, extract_skills, load_skills

METHOD = "dictionary"

UPSERT_SKILL = """
    insert into skills (name, slug, category, aliases) values (%s, %s, %s, %s)
    on conflict (slug) do update set
      name = excluded.name, category = excluded.category, aliases = excluded.aliases
"""
# Skills dropped from the file: their tags go first, then the skills.
DELETE_REMOVED_TAGS = """
    delete from job_skills
    where skill_id in (select id from skills where slug <> all(%s))
"""
DELETE_REMOVED_SKILLS = "delete from skills where slug <> all(%s)"

SELECT_JOBS = """
    select id, title, coalesce(description_text, '')
    from jobs
    where %s or skills_extracted_at is null or updated_at > skills_extracted_at
"""


def sync_skills(cur: Cursor, skills: list[Skill]) -> bool:
    """Make the skills table match the file. Returns True if anything changed."""
    wanted = {s.slug: (s.name, s.category, list(s.aliases)) for s in skills}
    rows = cur.execute("select slug, name, category, aliases from skills").fetchall()
    if {slug: (name, category, aliases) for slug, name, category, aliases in rows} == wanted:
        return False
    cur.executemany(UPSERT_SKILL, [(name, slug, *rest) for slug, (name, *rest) in wanted.items()])
    cur.execute(DELETE_REMOVED_TAGS, (list(wanted),))
    cur.execute(DELETE_REMOVED_SKILLS, (list(wanted),))
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--all", action="store_true", help="extract skills for every job")
    args = parser.parse_args()

    skills = load_skills()
    dictionary = build_dictionary(skills)
    with connect() as conn, conn.cursor() as cur:
        dictionary_changed = sync_skills(cur, skills)
        skill_ids = dict(cur.execute("select name, id from skills").fetchall())
        jobs = cur.execute(SELECT_JOBS, (args.all or dictionary_changed,)).fetchall()

        job_ids = [job_id for job_id, _, _ in jobs]
        tags = [
            (job_id, skill_ids[name], METHOD)
            for job_id, title, description in jobs
            for name in sorted(extract_skills(f"{title}\n{description}", dictionary))
        ]
        cur.execute(
            "delete from job_skills where job_id = any(%s) and method = %s", (job_ids, METHOD)
        )
        cur.executemany(
            "insert into job_skills (job_id, skill_id, method) values (%s, %s, %s)", tags
        )
        cur.execute("update jobs set skills_extracted_at = now() where id = any(%s)", (job_ids,))

    print(
        f"dictionary {'changed' if dictionary_changed else 'unchanged'} ({len(skills)} skills), "
        f"jobs {len(jobs)}, tags {len(tags)}"
    )


if __name__ == "__main__":
    main()
