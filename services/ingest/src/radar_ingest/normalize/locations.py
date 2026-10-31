"""Turn free-text job locations into countries, regions and cities with simple rules."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    country: str  # ISO 3166-1 alpha-2
    region: str | None = None  # US state or Canadian province code
    city: str | None = None


def _city(country: str, region: str | None, city: str, *aliases: str) -> dict[str, Location]:
    location = Location(country, region, city)
    return dict.fromkeys((city.lower(), *aliases), location)


CITIES: dict[str, Location] = {
    **_city("US", "CA", "San Francisco", "sf"),
    **_city("US", "CA", "South San Francisco"),
    **_city("US", "NY", "New York", "new york city", "nyc", "ny"),
    **_city("US", "WA", "Seattle", "sea"),
    **_city("US", "IL", "Chicago", "chi"),
    **_city("US", "GA", "Atlanta", "atl"),
    **_city("US", "TX", "Austin"),
    **_city("US", "MA", "Boston"),
    **_city("US", "CO", "Denver"),
    **_city("US", "CA", "Palo Alto"),
    **_city("US", "CA", "San Jose"),
    **_city("US", "CA", "Los Angeles"),
    **_city("US", "OR", "Portland"),
    # Plain "washington" is the state (REGION_NAMES); only "washington dc" and "dc" are the city.
    **dict.fromkeys(("washington dc", "dc"), Location("US", "DC", "Washington")),
    **_city("CA", "ON", "Toronto", "tor"),
    **_city("CA", "ON", "Ottawa"),
    **_city("CA", "ON", "Waterloo"),
    **_city("CA", "ON", "Kitchener"),
    **_city("CA", "ON", "Mississauga"),
    **_city("CA", "QC", "Montreal", "montréal"),
    **_city("CA", "QC", "Quebec City", "québec city"),
    **_city("CA", "AB", "Calgary"),
    **_city("CA", "AB", "Edmonton"),
    **_city("CA", "MB", "Winnipeg"),
    **_city("CA", "NS", "Halifax"),
    **_city("CA", "BC", "Vancouver"),
    **_city("GB", None, "London"),
    **_city("IE", None, "Dublin"),
    **_city("IN", None, "Bengaluru", "bangalore"),
    **_city("SG", None, "Singapore"),
    **_city("MX", None, "Mexico City", "cdmx"),
    **_city("AU", None, "Sydney"),
    **_city("AU", None, "Melbourne"),
    **_city("JP", None, "Tokyo"),
    **_city("TW", None, "Taipei", "taipei city"),
    **_city("TH", None, "Bangkok"),
    **_city("NZ", None, "Auckland"),
    **_city("BR", None, "Sao Paulo"),
    **_city("ES", None, "Barcelona"),
    **_city("ES", None, "Madrid"),
    **_city("FR", None, "Paris"),
    **_city("DE", None, "Berlin"),
    **_city("DE", None, "Munich"),
    **_city("NL", None, "Amsterdam"),
    **_city("SE", None, "Stockholm"),
    **_city("RO", None, "Bucharest"),
    **_city("PL", None, "Warsaw"),
    **_city("LU", None, "Luxembourg"),
}

COUNTRIES: dict[str, str] = {
    alias: code
    for code, aliases in {
        "US": ("us", "usa", "united states"),
        "CA": ("canada",),
        "GB": ("uk", "united kingdom"),
        "IE": ("ireland",),
        "IN": ("india",),
        "MX": ("mexico", "mx"),
        "AU": ("australia",),
        "JP": ("japan",),
        "TW": ("taiwan",),
        "TH": ("thailand",),
        "BR": ("brazil",),
        "ES": ("spain",),
        "FR": ("france",),
        "DE": ("germany",),
        "SE": ("sweden",),
        "RO": ("romania",),
        "PL": ("poland",),
        "BE": ("belgium",),
        "IL": ("israel",),
    }.items()
    for alias in aliases
}

US_STATES = set(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH "
    "NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()
)
CA_PROVINCES = set("AB BC MB NB NL NS NT NU ON PE QC SK YT".split())
REGION_NAMES: dict[str, Location] = {
    name: Location(country, region)
    for country, regions in {
        "CA": {
            "AB": ("alberta",),
            "BC": ("british columbia",),
            "MB": ("manitoba",),
            "NB": ("new brunswick",),
            # "Newfoundland and Labrador" is split at "and" into two parts.
            "NL": ("newfoundland", "labrador"),
            "NS": ("nova scotia",),
            "NT": ("northwest territories",),
            "NU": ("nunavut",),
            "ON": ("ontario",),
            "PE": ("prince edward island",),
            "QC": ("quebec", "québec"),
            "SK": ("saskatchewan",),
            "YT": ("yukon",),
        },
        # The states with the most tech postings; "new york" stays the city.
        "US": {
            "CA": ("california",),
            "TX": ("texas",),
            "WA": ("washington",),
            "MA": ("massachusetts",),
            "IL": ("illinois",),
            "CO": ("colorado",),
            "GA": ("georgia",),
            "FL": ("florida",),
            "NC": ("north carolina",),
            "VA": ("virginia",),
            "PA": ("pennsylvania",),
            "NJ": ("new jersey",),
            "OR": ("oregon",),
            "AZ": ("arizona",),
            "IN": ("indiana",),
        },
    }.items()
    for region, names in regions.items()
    for name in names
}

# Strings that name no place. "remote" alone says how, not where: the company's country
# may fill it in later, but it is not an unrecognized location.
NO_LOCATION = {"", "n/a", "na", "location", "remote"}
# Lists use ; , | / & : ( ) "or" "and"; prefixes like "US-NYC" use a dash.
SEPARATORS = re.compile(r"[;,|/&:()]|\s+or\s+|\s+and\s+|\s*-\s*")
# Words that say how, not where. A lone "in" stays: it is Indiana.
NOISE = re.compile(r"\b(remote|rem|hybrid|hq|in the|from the)\b")
LEADING_IN = re.compile(r"^in\s+")  # "Remote in Canada" -> "canada"


def split_parts(text: str) -> list[str]:
    """Lowercase pieces of a location string, without remote/hybrid words."""
    text = text.lower().replace(".", "").replace("new-york", "new york").strip()
    text = re.sub(r"\bwashington,?\s+dc\b", "washington dc", text)
    if text in NO_LOCATION:
        return []
    parts = (" ".join(NOISE.sub(" ", part).split()) for part in SEPARATORS.split(text))
    return [LEADING_IN.sub("", part) for part in parts if part]


def follows_city(previous: str | None) -> bool:
    """True if the part before is a city name, known or not (unknown text is most likely a city)."""
    return previous is not None and (previous in CITIES or resolve(previous) is None)


def resolve(part: str, previous: str | None = None) -> list[Location] | None:
    """What one piece can mean: a city, a country or a region; None if unknown.

    A region code can mean more than one place, so the result is a list of options,
    most likely first. "CA" is California only right after a city ("San Francisco, CA");
    alone or after a country ("Remote, US | Remote, CA") it is Canada.
    """
    if part in CITIES:
        return [CITIES[part]]
    if part in COUNTRIES:
        return [Location(COUNTRIES[part])]
    if part in REGION_NAMES:
        return [REGION_NAMES[part]]
    code = part.upper()
    if code == "CA":
        california, canada = Location("US", "CA"), Location("CA")
        return [california, canada] if follows_city(previous) else [canada, california]
    options = [Location("US", code)] if code in US_STATES else []
    if code in CA_PROVINCES:
        options.append(Location("CA", code))
    return options or None


def covers(place: Location, area: Location) -> bool:
    """True if place lies inside area: Seattle is inside WA and inside US."""
    return (
        place != area
        and area.city is None
        and place.country == area.country
        and area.region in (None, place.region)
    )


def parse_location(text: str) -> list[Location]:
    """Cities, plus any country or region that none of the cities already falls in."""
    parts = split_parts(text)
    found = [
        options
        for i, part in enumerate(parts)
        if (options := resolve(part, parts[i - 1] if i else None))
    ]
    places = [options[0] for options in found if options[0].city]
    for options in found:
        if options[0].city is None and not any(covers(p, o) for p in places for o in options):
            places.append(options[0])
    places = [p for p in places if not any(covers(other, p) for other in places)]
    return list(dict.fromkeys(places))  # drop duplicates, keep order
