"""The skill dictionary (skills.toml) and finding its skills in job text.

All names and aliases go into one compiled regex, longest first, so "Spring Boot" wins over
"Spring" and one pass over the text finds everything.
"""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

SKILLS_FILE = Path(__file__).resolve().parents[3] / "skills.toml"

CATEGORIES = (
    "language",
    "framework",
    "library",
    "cloud",
    "database",
    "tool",
    "platform",
    "practice",
)
KEYS = {"name", "category", "aliases", "case_sensitive"}

# \b fails around names like C++, .NET and Node.js, so the edges are explicit: no word
# character, dot, plus or hash before; none after either, but a sentence-ending dot is fine.
BEFORE = r"(?<![\w.+#])"
AFTER = r"(?![\w+#]|\.\w)"
# Phrases where a capitalized skill name is an ordinary word: "Go-to-market", "Spring 2027".
FALSE_FRIENDS = re.compile(
    r"\bGo(?=[\s-]+(?:to|live|deep|beyond|further)\b)"
    r"|\bSpring(?=\s+(?:\d{4}|semester|term|internship|break)\b)"
)


@dataclass(frozen=True)
class Skill:
    name: str
    slug: str
    category: str
    aliases: tuple[str, ...] = ()
    case_sensitive: bool = False  # applies to the name only


@dataclass(frozen=True)
class Dictionary:
    pattern: re.Pattern[str]
    exact: dict[str, str]  # case-sensitive term -> skill name
    folded: dict[str, str]  # lowercased term -> skill name


def slugify(name: str) -> str:
    """URL id from a name: "C++" -> "cpp", ".NET" -> "dotnet", "CI/CD" -> "ci-cd"."""
    s = name.lower().replace("++", "pp").replace("#", "sharp").replace(".net", "dotnet")
    return re.sub(r"[^a-z0-9]+", "-", s.replace(".", "")).strip("-")


def is_exact(term: str, skill: Skill) -> bool:
    """Short all-caps terms (ML, SQL, RAG) and case_sensitive names match only as written."""
    if skill.case_sensitive and term == skill.name:
        return True
    return len(term) <= 5 and term == term.upper() and any(c.isalpha() for c in term)


def load_skills(path: Path = SKILLS_FILE) -> list[Skill]:
    """Read and validate the skills file. Errors name the entry by number and name."""
    with path.open("rb") as f:
        entries = tomllib.load(f).get("skill")
    if not entries or not isinstance(entries, list):
        raise ValueError(f"{path.name}: write skills as [[skill]] entries")

    skills: list[Skill] = []
    owners: dict[str, str] = {}  # lowercased term -> skill that uses it
    slugs: dict[str, str] = {}
    for number, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"{path.name}: skill #{number} is not a table")
        name = entry.get("name")
        where = f"{path.name}: skill #{number} ({name or 'no name'})"

        unknown = sorted(set(entry) - KEYS)
        if unknown:
            raise ValueError(f"{where}: unknown keys {', '.join(unknown)}")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{where}: name must be a non-empty string")
        if entry.get("category") not in CATEGORIES:
            raise ValueError(f"{where}: category must be one of {', '.join(CATEGORIES)}")
        aliases = entry.get("aliases", [])
        if not isinstance(aliases, list) or not all(isinstance(a, str) and a for a in aliases):
            raise ValueError(f'{where}: aliases must be a list of strings, like ["a", "b"]')
        if not isinstance(entry.get("case_sensitive", False), bool):
            raise ValueError(f"{where}: case_sensitive must be true or false")

        # Names and aliases share one namespace, case-insensitively: a term means one skill.
        for term in (name, *aliases):
            if term.lower() in owners:
                raise ValueError(f"{where}: {term!r} is already used by {owners[term.lower()]}")
            owners[term.lower()] = name
        slug = slugify(name)
        if slug in slugs:
            raise ValueError(f"{where}: slug {slug!r} is already used by {slugs[slug]}")
        slugs[slug] = name

        skills.append(
            Skill(name, slug, entry["category"], tuple(aliases), entry.get("case_sensitive", False))
        )
    return skills


def build_dictionary(skills: list[Skill]) -> Dictionary:
    exact: dict[str, str] = {}
    folded: dict[str, str] = {}
    for skill in skills:
        for term in (skill.name, *skill.aliases):
            if is_exact(term, skill):
                exact[term] = skill.name
            else:
                folded[term.lower()] = skill.name

    def alternative(term: str, case_sensitive: bool) -> str:
        body = re.escape(term).replace(r"\ ", r"\s+")  # a line break inside a name still matches
        return body if case_sensitive else f"(?i:{body})"

    terms = [(t, True) for t in exact] + [(t, False) for t in folded]
    terms.sort(
        key=lambda t: len(t[0]), reverse=True
    )  # longest first: "React Native" before "React"
    pattern = re.compile(BEFORE + "(?:" + "|".join(alternative(*t) for t in terms) + ")" + AFTER)
    return Dictionary(pattern, exact, folded)


def extract_skills(text: str, dictionary: Dictionary) -> set[str]:
    """Names of the dictionary skills mentioned in text."""
    found = set()
    for match in dictionary.pattern.finditer(FALSE_FRIENDS.sub(" ", text)):
        term = " ".join(match.group(0).split())
        name = dictionary.exact.get(term) or dictionary.folded.get(term.lower())
        if name:
            found.add(name)
    return found
