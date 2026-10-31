import re
from pathlib import Path

import pytest

from radar_ingest.normalize.skills import (
    CATEGORIES,
    build_dictionary,
    extract_skills,
    load_skills,
    slugify,
)

SKILLS = load_skills()
DICTIONARY = build_dictionary(SKILLS)


def test_skills_file_follows_the_rules() -> None:
    # load_skills() already rejects duplicate terms and slugs; check the rest here.
    assert 120 <= len(SKILLS) <= 160
    assert all(skill.category in CATEGORIES for skill in SKILLS)
    assert all(skill.slug == slugify(skill.name) for skill in SKILLS)
    assert all(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", skill.slug) for skill in SKILLS)


@pytest.mark.parametrize(
    ("name", "slug"),
    [
        ("React", "react"),
        ("C++", "cpp"),
        ("C#", "csharp"),
        (".NET", "dotnet"),
        ("Node.js", "nodejs"),
        ("CI/CD", "ci-cd"),
        ("Spring Boot", "spring-boot"),
    ],
)
def test_slugify(name: str, slug: str) -> None:
    assert slugify(name) == slug


def write(tmp_path: Path, *entries: str) -> Path:
    path = tmp_path / "skills.toml"
    path.write_text("".join(f"[[skill]]\n{entry}\n" for entry in entries))
    return path


REACT = 'name = "React"\ncategory = "framework"\naliases = ["reactjs"]'


@pytest.mark.parametrize(
    ("entries", "error"),
    [
        ((), "write skills as [[skill]] entries"),
        (('name = "React"\ncategory = "frontend"',), "category must be one of"),
        ((REACT, 'name = "react"\ncategory = "framework"'), "'react' is already used by React"),
        ((REACT, 'name = "ReactJS"\ncategory = "framework"'), "'ReactJS' is already used by React"),
        ((REACT, 'name = "Preact"\ncategory = "framework"\naliases = ["REACTJS"]'), "already used"),
        (
            ('name = "Node.js"\ncategory = "platform"', 'name = "NodeJS"\ncategory = "platform"'),
            "slug",
        ),
        (
            ('name = "React"\ncategory = "framework"\naliases = "reactjs"',),
            "aliases must be a list",
        ),
        (('name = "React"\ncategory = "framework"\ntags = ["ui"]',), "unknown keys tags"),
    ],
    ids=[
        "empty",
        "bad category",
        "dup name",
        "alias as name",
        "dup alias",
        "dup slug",
        "alias str",
        "key",
    ],
)
def test_invalid_skills_file(tmp_path: Path, entries: tuple[str, ...], error: str) -> None:
    with pytest.raises(ValueError, match=re.escape(error)):
        load_skills(write(tmp_path, *entries))


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Names with dots, plus and hash signs; the longest name wins.
        (
            "Python, Go, and C++. We use Node.js and .NET.",
            {"Python", "Go", "C++", "Node.js", ".NET"},
        ),
        ("React Native apps and a Spring Boot API", {"React Native", "Spring Boot"}),
        # Word edges: no Java in JavaScript, no SQL in NoSQL or MySQL.
        ("javascript is not java", {"JavaScript", "Java"}),
        ("NoSQL and MySQL", {"MySQL"}),
        ("Experience with SQL.", {"SQL"}),  # a sentence-ending dot is fine
        # Capitalized names that are also ordinary words.
        ("Own the Go-to-market plan and go live in Q3", set()),
        ("Spring 2027 internship", set()),
        ("We are at the helm of the rest of the agile team", set()),
        ("Helm charts, REST APIs, Agile ceremonies", {"Helm", "REST", "Agile"}),
        ("SWIFT payments", set()),
        # Short all-caps aliases match only as written.
        ("AI/ML", {"Machine Learning"}),
        ("add 5 ml of water", set()),
        # Aliases, plurals and line breaks inside a name.
        ("k8s, LLMs, agentic workflows, RAG", {"Kubernetes", "LLMs", "AI Agents", "RAG"}),
        ("machine\nlearning", {"Machine Learning"}),
    ],
)
def test_extract_skills(text: str, expected: set[str]) -> None:
    assert extract_skills(text, DICTIONARY) == expected
