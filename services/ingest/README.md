# radar-ingest

Fetches public job boards (Greenhouse, Lever, Ashby) into PostgreSQL. Reads `DATABASE_URL` from the environment or from the `.env` file in the repository root.

```bash
uv sync                                  # install Python 3.12 and dependencies
uv run python -m radar_ingest.check      # print the server version and table row counts
uv run ruff check && uv run ruff format  # lint and format
uv run pytest                            # tests
```
