"""Precision and recall of dictionary extraction against hand-labeled postings.

Labels live in tests/fixtures/skills/labeled.jsonl (see the README there). Needs no database.
Run with: uv run python -m radar_ingest.normalize.skills_eval [--verbose]
"""

import argparse
import json
from collections import Counter
from pathlib import Path

from radar_ingest.normalize.skills import SKILLS_FILE, build_dictionary, extract_skills, load_skills

LABELED_FILE = SKILLS_FILE.parent / "tests" / "fixtures" / "skills" / "labeled.jsonl"
TOP = 15


def load_labeled(path: Path = LABELED_FILE) -> list[dict]:
    # Iterate the file, not str.splitlines(): texts contain U+2028, which splitlines() breaks on.
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verbose", action="store_true", help="print the errors of every posting")
    args = parser.parse_args()

    skills = load_skills()
    names = {skill.name for skill in skills}
    dictionary = build_dictionary(skills)
    postings = load_labeled()

    true_positives = 0
    extra, missed = Counter[str](), Counter[str]()
    for posting in postings:
        expected = set(posting["skills"])
        found = extract_skills(posting["text"], dictionary)
        true_positives += len(found & expected)
        extra.update(found - expected)
        missed.update(expected - found)
        if args.verbose and found != expected:
            print(f"{posting['company']} {posting['title']!r}")
            print(f"  extra:  {sorted(found - expected)}\n  missed: {sorted(expected - found)}")

    found_total = true_positives + extra.total()
    expected_total = true_positives + missed.total()
    precision = true_positives / found_total if found_total else 0.0
    recall = true_positives / expected_total if expected_total else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    print(f"postings   {len(postings)}")
    print(f"labels     {expected_total}   found {found_total}   correct {true_positives}")
    print(f"precision  {precision:.2f}")
    print(f"recall     {recall:.2f}")
    print(f"F1         {f1:.2f}")
    print(f"\nfound but not labeled (false positives), top {TOP}:")
    for name, count in extra.most_common(TOP):
        print(f"  {count:>3}  {name}")
    print(f"\nlabeled but not found (false negatives), top {TOP}:")
    for name, count in missed.most_common(TOP):
        reason = "matching" if name in names else "not in dictionary"
        print(f"  {count:>3}  {name:<24} {reason}")


if __name__ == "__main__":
    main()
