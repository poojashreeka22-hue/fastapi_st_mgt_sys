import pytest
from app.models import StudentCreate
import app.crud as crud

# -------------------------------------------------------------
# 1. API POST /students valid creation: 150 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid,name,age,email,course",
    [
        (
            i,
            f"API Student {i}",
            18 + (i % 30),
            f"student_{i}@university.edu",
            f"Course {100 + (i % 50)}",
        )
        for i in range(1, 151)
    ],
    ids=[f"api_create_valid_{i}" for i in range(1, 151)],
)
def test_api_create_student_valid(client, sid, name, age, email, course):
    payload = {
        "student_id": sid,
        "name": name,
        "age": age,
        "email": email,
        "course": course,
    }
    resp = client.post("/students", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["student_id"] == sid
    assert data["name"] == name
    assert data["age"] == age
    assert data["email"] == email
    assert data["course"] == course


# -------------------------------------------------------------
# 2. Duplicate student ID conflicts (409): 50 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "dup_id",
    range(1, 51),
    ids=[f"api_create_duplicate_{i}" for i in range(1, 51)],
)
def test_api_create_student_duplicate_id(client, dup_id):
    payload = {
        "student_id": dup_id,
        "name": f"First Student {dup_id}",
        "age": 20,
        "email": f"first_{dup_id}@test.com",
        "course": "Math",
    }
    resp1 = client.post("/students", json=payload)
    assert resp1.status_code == 201

    dup_payload = {
        "student_id": dup_id,
        "name": f"Duplicate Student {dup_id}",
        "age": 22,
        "email": f"second_{dup_id}@test.com",
        "course": "Physics",
    }
    resp2 = client.post("/students", json=dup_payload)
    assert resp2.status_code == 409
    assert f"Student ID {dup_id} already exists" in resp2.json()["detail"]


# -------------------------------------------------------------
# 3. Invalid payload validations (422 Unprocessable Entity): 100 tests
# -------------------------------------------------------------
INVALID_CREATE_PAYLOADS = [
    # Missing fields
    ({"name": "No ID", "age": 20, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 1, "age": 20, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 1, "name": "No Age", "email": "a@b.com", "course": "CS"}),
    ({"student_id": 1, "name": "No Email", "age": 20, "course": "CS"}),
    ({"student_id": 1, "name": "No Course", "age": 20, "email": "a@b.com"}),
    # Invalid ID values
    ({"student_id": 0, "name": "Zero ID", "age": 20, "email": "a@b.com", "course": "CS"}),
    ({"student_id": -1, "name": "Neg ID", "age": 20, "email": "a@b.com", "course": "CS"}),
    ({"student_id": -100, "name": "Neg ID", "age": 20, "email": "a@b.com", "course": "CS"}),
    ({"student_id": "not_an_int", "name": "Str ID", "age": 20, "email": "a@b.com", "course": "CS"}),
    # Invalid name values
    ({"student_id": 10, "name": "", "age": 20, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 10, "name": "   ", "age": 20, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 10, "name": "\t", "age": 20, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 10, "name": "\n", "age": 20, "email": "a@b.com", "course": "CS"}),
    # Invalid age values
    ({"student_id": 10, "name": "Bad Age", "age": 0, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 10, "name": "Bad Age", "age": -5, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 10, "name": "Bad Age", "age": 121, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 10, "name": "Bad Age", "age": 200, "email": "a@b.com", "course": "CS"}),
    ({"student_id": 10, "name": "Bad Age", "age": "twenty", "email": "a@b.com", "course": "CS"}),
    # Invalid email values
    ({"student_id": 10, "name": "Bad Email", "age": 20, "email": "plain", "course": "CS"}),
    ({"student_id": 10, "name": "Bad Email", "age": 20, "email": "@domain.com", "course": "CS"}),
    ({"student_id": 10, "name": "Bad Email", "age": 20, "email": "user@", "course": "CS"}),
    ({"student_id": 10, "name": "Bad Email", "age": 20, "email": "", "course": "CS"}),
    ({"student_id": 10, "name": "Bad Email", "age": 20, "email": "   ", "course": "CS"}),
    # Invalid course values
    ({"student_id": 10, "name": "Bad Course", "age": 20, "email": "a@b.com", "course": ""}),
    ({"student_id": 10, "name": "Bad Course", "age": 20, "email": "a@b.com", "course": "   "}),
    ({"student_id": 10, "name": "Bad Course", "age": 20, "email": "a@b.com", "course": "\t"}),
] + [
    ({"student_id": 500 + i, "name": f"Invalid P_{i}", "age": -i, "email": "a@b.com", "course": "CS"})
    for i in range(1, 75)
]

@pytest.mark.parametrize(
    "payload",
    INVALID_CREATE_PAYLOADS,
    ids=[f"api_create_invalid_{i}" for i in range(1, 101)],
)
def test_api_create_student_invalid_payloads(client, payload):
    resp = client.post("/students", json=payload)
    assert resp.status_code == 422


# -------------------------------------------------------------
# 4. Response structure and integrity: 50 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid",
    range(1, 51),
    ids=[f"api_create_integrity_{i}" for i in range(1, 51)],
)
def test_api_create_response_integrity(client, sid):
    payload = {
        "student_id": 1000 + sid,
        "name": f"Integrity Student {sid}",
        "age": 21,
        "email": f"integrity_{sid}@domain.edu",
        "course": "Software Quality",
    }
    resp = client.post("/students", json=payload)
    assert resp.status_code == 201
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert set(body.keys()) == {"student_id", "name", "age", "email", "course"}
    assert body["student_id"] == 1000 + sid
