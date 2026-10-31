import pytest

from radar_ingest.normalize.locations import Location, parse_location

US, CANADA = Location("US"), Location("CA")
SF = Location("US", "CA", "San Francisco")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # "CA" without a city before it is Canada; after a US city it is California.
        ("Remote, US | Remote, CA", [US, CANADA]),
        ("CA", [CANADA]),
        ("San Francisco, CA", [SF]),
        ("Toronto, CA", [Location("CA", "ON", "Toronto")]),
        ("Ontario, CA", [Location("CA", "ON")]),
        # Remote words and empty values name no place.
        ("Remote", []),
        ("N/A", []),
        ("Remote in Canada", [CANADA]),
        ("Remote in the US", [US]),
        ("US-Remote, Chicago", [Location("US", "IL", "Chicago")]),
        # Canadian cities and provinces by full name.
        ("Calgary, AB", [Location("CA", "AB", "Calgary")]),
        ("Montréal, QC", [Location("CA", "QC", "Montreal")]),
        ("Quebec", [Location("CA", "QC")]),
        ("British Columbia", [Location("CA", "BC")]),
        # Washington alone is the state; with DC it is the city.
        ("Washington", [Location("US", "WA")]),
        ("Washington, D.C.", [Location("US", "DC", "Washington")]),
        ("Seattle, Washington", [Location("US", "WA", "Seattle")]),
        # A lone "in" is Indiana, not a filler word.
        ("IN", [Location("US", "IN")]),
        ("Indiana", [Location("US", "IN")]),
        # Lists: every city, and a country only if no city already lies in it.
        (
            "Chicago, IL; New York, NY; San Francisco, CA",
            [Location("US", "IL", "Chicago"), Location("US", "NY", "New York"), SF],
        ),
        ("US / Canada", [US, CANADA]),
        ("London OR Dublin", [Location("GB", None, "London"), Location("IE", None, "Dublin")]),
    ],
)
def test_parse_location(text: str, expected: list[Location]) -> None:
    assert parse_location(text) == expected
