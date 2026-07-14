from pathlib import Path

from src.db import (
    add_application,
    delete_application,
    get_application,
    init_db,
    list_applications,
    update_application,
)


def test_crud_round_trip(tmp_path: Path):
    db = tmp_path / "test.db"
    init_db(db)
    new_id = add_application(db, {"company": "Test Oy", "role": "Python Intern", "status": "Saved"})
    row = get_application(db, new_id)
    assert row is not None
    assert row["company"] == "Test Oy"

    update_application(db, new_id, {"status": "Applied", "match_score": 77})
    updated = get_application(db, new_id)
    assert updated["status"] == "Applied"
    assert updated["match_score"] == 77

    frame = list_applications(db, statuses=["Applied"])
    assert len(frame) == 1

    delete_application(db, new_id)
    assert get_application(db, new_id) is None


def test_company_and_role_are_required(tmp_path: Path):
    db = tmp_path / "test.db"
    init_db(db)
    try:
        add_application(db, {"company": "", "role": "Developer"})
    except ValueError as exc:
        assert "required" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")
