import re
from pathlib import Path

import pytest

from radar_ingest.seed import load_companies

STRIPE = {"name": "Stripe", "slug": "stripe", "ats": "greenhouse", "token": "stripe"}


def company(**fields: str | None) -> str:
    """One [[company]] table: Stripe, with fields replaced; None drops a field."""
    lines = [f'{key} = "{value}"' for key, value in (STRIPE | fields).items() if value is not None]
    return "[[company]]\n" + "\n".join(lines) + "\n"


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "companies.toml"
    path.write_text(text)
    return path


def test_valid_file(tmp_path: Path) -> None:
    text = company(hq_country="US") + company(name="Acme", slug="acme", ats="lever", token="acme")
    companies = load_companies(write(tmp_path, text))

    assert companies[0] == STRIPE | {"hq_country": "US"}
    assert companies[1]["slug"] == "acme"
    assert companies[1]["hq_country"] is None


@pytest.mark.parametrize(
    ("text", "error"),
    [
        ("", "no [[company]] entries"),
        (company(token=None), "(stripe): missing token"),
        (company(ats="workday"), "ats must be one of"),
        (company() + company(token="stripe-ca"), "duplicate slug"),
        (company() + company(slug="stripe-2"), "duplicate greenhouse token"),
        (company(hq_country="usa"), "two capital letters"),
    ],
    ids=["empty", "no token", "bad ats", "dup slug", "dup board", "bad country"],
)
def test_invalid_file(tmp_path: Path, text: str, error: str) -> None:
    with pytest.raises(ValueError, match=re.escape(error)):
        load_companies(write(tmp_path, text))
