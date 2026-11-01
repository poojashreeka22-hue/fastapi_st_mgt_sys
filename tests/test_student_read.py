import pytest

# -------------------------------------------------------------
# 1. API GET /students on empty database: 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "i",
    range(1, 21),
    ids=[f"api_read_empty_{i}" for i in range(1, 21)],
)
def test_api_read_all_students_empty(client, i):
    resp = client.get("/students")
    assert resp.status_code == 200
    assert resp.json() == []


# -------------------------------------------------------------
# 2. API GET /students with populated database: 80 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "student_count",
    range(1, 81),
    ids=[f"api_read_populated_{i}" for i in range(1, 81)],
)
def test_api_read_all_students_populated(client, db_conn, student_count):
    cursor = db_conn.cursor()
    records = [
        (i, f"Student {i}", 20 + (i % 10), f"s{i}@example.com", "Art")
        for i in range(1, student_count + 1)
    ]
    cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?)", records)
    db_conn.commit()

    resp = client.get("/students")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == student_count
    assert body[0]["student_id"] == 1
    assert body[-1]["student_id"] == student_count


# -------------------------------------------------------------
# 3. API GET /students/{student_id} successful search: 100 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid",
    range(1, 101),
    ids=[f"api_search_success_{i}" for i in range(1, 101)],
)
def test_api_search_student_success(client, db_conn, sid):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (sid, f"Found Student {sid}", 22, f"found_{sid}@school.edu", "History"),
    )
    db_conn.commit()

    resp = client.get(f"/students/{sid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["student_id"] == sid
    assert data["name"] == f"Found Student {sid}"
    assert data["age"] == 22
    assert data["email"] == f"found_{sid}@school.edu"
    assert data["course"] == "History"


# -------------------------------------------------------------
# 4. API GET /students/{student_id} not found (404): 50 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "missing_id",
    [999 + i for i in range(1, 51)],
    ids=[f"api_search_not_found_{i}" for i in range(1, 51)],
)
def test_api_search_student_not_found(client, missing_id):
    resp = client.get(f"/students/{missing_id}")
    assert resp.status_code == 404
    assert f"Student with ID {missing_id} not found" in resp.json()["detail"]


# -------------------------------------------------------------
# 5. API GET /students/{student_id} invalid ID (422): 50 tests
# -------------------------------------------------------------
INVALID_SEARCH_IDS = [
    0, -1, -2, -3, -4, -5, -10, -20, -50, -100,
    "abc", "12.34", "null", "undefined", "zero",
    "-10", "-99", "id_1", "student_1", "bad",
] + [f"invalid_id_{i}" for i in range(1, 31)]

@pytest.mark.parametrize(
    "invalid_sid",
    INVALID_SEARCH_IDS,
    ids=[f"api_search_invalid_id_{i}" for i in range(1, 51)],
)
def test_api_search_invalid_id(client, invalid_sid):
    resp = client.get(f"/students/{invalid_sid}")
    assert resp.status_code == 422
