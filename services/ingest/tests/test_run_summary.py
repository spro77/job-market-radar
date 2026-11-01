from radar_ingest.run_summary import Fetch, Summary, cell, render


def summary(*fetches: Fetch) -> Summary:
    return Summary(
        fetches=list(fetches),
        open_jobs=1602,
        new_jobs=12,
        closed_jobs=3,
        changed_postings=40,
        day="2026-11-01",
        aggregate_rows=666,
    )


def test_all_ok_has_one_table() -> None:
    text = render(summary(Fetch("acme", "ok", 10, None), Fetch("globex", "ok", 5, None)))
    assert "| 2 of 2 | 0 | 1,602 | 12 | 3 | 40 | 666 for 2026-11-01 |" in text
    assert "| Company |" not in text


def test_failed_and_missing_companies_are_listed_with_words() -> None:
    text = render(
        summary(
            Fetch("acme", "ok", 10, None),
            Fetch("globex", "failed", None, "HTTPStatusError('404 Not Found')"),
            Fetch("initech", None, None, None),
        )
    )
    assert "| 1 of 3 | 2 |" in text
    assert "| globex | ✗ failed | HTTPStatusError('404 Not Found') |" in text
    assert "| initech | – did not run |  |" in text


def test_cell_keeps_tables_intact() -> None:
    assert cell("a | b\nc") == "a \\| b c"
    assert cell("x" * 200, limit=10) == "x" * 9 + "…"
