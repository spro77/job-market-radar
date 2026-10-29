from radar_ingest.fetch import payload_hash

JOB = {"id": 1, "title": "Engineer", "location": {"name": "Toronto", "country": "CA"}}


def test_same_hash_for_any_key_order() -> None:
    reordered = {"location": {"country": "CA", "name": "Toronto"}, "title": "Engineer", "id": 1}
    assert payload_hash(reordered) == payload_hash(JOB)


def test_hash_changes_when_a_value_changes() -> None:
    assert payload_hash(JOB | {"title": "Senior Engineer"}) != payload_hash(JOB)
