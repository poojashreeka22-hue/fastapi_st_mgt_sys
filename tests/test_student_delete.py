import pytest

# -------------------------------------------------------------
# 1. API DELETE /students/{student_id} success: 100 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid",
    range(1, 101),
    ids=[f"api_delete_success_{i}" for i in range(1, 101)],
)
def test_api_delete_student_success(client, db_conn, sid):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (sid, f"To Delete {sid}", 20, f"del_{sid}@test.com", "Math"),
    )
    db_conn.commit()

    resp = client.delete(f"/students/{sid}")
    assert resp.status_code == 200
    assert "successfully deleted" in resp.json()["message"]


# -------------------------------------------------------------
# 2. Verify deleted student is gone: 50 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid",
    range(1, 51),
    ids=[f"api_delete_verify_gone_{i}" for i in range(1, 51)],
)
def test_api_delete_verify_gone(client, db_conn, sid):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (500 + sid, f"Delete Gone {sid}", 21, f"delgone_{sid}@test.com", "Physics"),
    )
    db_conn.commit()

    del_resp = client.delete(f"/students/{500 + sid}")
    assert del_resp.status_code == 200

    # Querying the deleted student must return 404
    get_resp = client.get(f"/students/{500 + sid}")
    assert get_resp.status_code == 404


# -------------------------------------------------------------
# 3. API DELETE /students/{student_id} not found (404): 50 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "missing_id",
    [9000 + i for i in range(1, 51)],
    ids=[f"api_delete_not_found_{i}" for i in range(1, 51)],
)
def test_api_delete_student_not_found(client, missing_id):
    resp = client.delete(f"/students/{missing_id}")
    assert resp.status_code == 404
    assert f"Student with ID {missing_id} not found" in resp.json()["detail"]


# -------------------------------------------------------------
# 4. API DELETE /students/{student_id} invalid ID (422): 50 tests
# -------------------------------------------------------------
INVALID_DELETE_IDS = [
    0, -1, -2, -3, -4, -5, -10, -20, -50, -100,
    "abc", "12.34", "null", "undefined", "zero",
    "-10", "-99", "id_1", "student_1", "bad",
] + [f"invalid_del_id_{i}" for i in range(1, 31)]

@pytest.mark.parametrize(
    "invalid_sid",
    INVALID_DELETE_IDS,
    ids=[f"api_delete_invalid_id_{i}" for i in range(1, 51)],
)
def test_api_delete_invalid_id(client, invalid_sid):
    resp = client.delete(f"/students/{invalid_sid}")
    assert resp.status_code == 422
