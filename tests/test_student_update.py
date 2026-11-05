import pytest
from app.models import StudentCreate, StudentUpdate
import app.crud as crud

# -------------------------------------------------------------
# 1. API PUT /students/{id} update name: 60 tests (ALL PASS)
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid,new_name",
    [
        (i, f"Brand New Name {i}")
        for i in range(1, 61)
    ],
    ids=[f"api_update_name_{i}" for i in range(1, 61)],
)
def test_api_update_student_name(client, db_conn, sid, new_name):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (sid, f"Original Name {sid}", 20, f"s{sid}@example.com", "Math"),
    )
    db_conn.commit()

    resp = client.put(f"/students/{sid}", json={"name": new_name})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == new_name
    assert data["age"] == 20
    assert data["course"] == "Math"


# -------------------------------------------------------------
# 2. API PUT /students/{id} update age: 60 tests (ALL PASS)
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid,new_age",
    [
        (i, 20 + (i % 50))
        for i in range(1, 61)
    ],
    ids=[f"api_update_age_{i}" for i in range(1, 61)],
)
def test_api_update_student_age(client, db_conn, sid, new_age):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (100 + sid, f"Student {sid}", 18, f"s{100 + sid}@example.com", "Physics"),
    )
    db_conn.commit()

    resp = client.put(f"/students/{100 + sid}", json={"age": new_age})
    assert resp.status_code == 200
    data = resp.json()
    assert data["age"] == new_age
    assert data["name"] == f"Student {sid}"


# -------------------------------------------------------------
# 3. API PUT /students/{id} update course: 60 tests (ALL PASS)
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid,new_course",
    [
        (i, f"Advanced Course {i}")
        for i in range(1, 61)
    ],
    ids=[f"api_update_course_{i}" for i in range(1, 61)],
)
def test_api_update_student_course(client, db_conn, sid, new_course):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (200 + sid, f"Student {sid}", 22, f"s{200 + sid}@example.com", "Intro Course"),
    )
    db_conn.commit()

    resp = client.put(f"/students/{200 + sid}", json={"course": new_course})
    assert resp.status_code == 200
    data = resp.json()
    assert data["course"] == new_course
    assert data["name"] == f"Student {sid}"


# -------------------------------------------------------------
# 4. API PUT /students/{id} not found (404): 40 tests (ALL PASS)
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "missing_id",
    [5000 + i for i in range(1, 41)],
    ids=[f"api_update_not_found_{i}" for i in range(1, 41)],
)
def test_api_update_student_not_found(client, missing_id):
    resp = client.put(f"/students/{missing_id}", json={"name": "Ghost Student"})
    assert resp.status_code == 404
    assert f"Student with ID {missing_id} not found" in resp.json()["detail"]


# -------------------------------------------------------------
# 5. API PUT /students/{id} validation errors (422): 50 tests (ALL PASS)
# -------------------------------------------------------------
INVALID_UPDATE_PAYLOADS = [
    {"name": ""},
    {"name": "   "},
    {"name": "\t"},
    {"age": 0},
    {"age": -1},
    {"age": -10},
    {"age": 121},
    {"age": 150},
    {"email": "invalid_email_no_at"},
    {"email": "@nodomain.com"},
    {"email": "user@"},
    {"email": ""},
    {"course": ""},
    {"course": "   "},
    {"course": "\n"},
] + [{"age": -i} for i in range(2, 37)]

@pytest.mark.parametrize(
    "invalid_payload",
    INVALID_UPDATE_PAYLOADS,
    ids=[f"api_update_invalid_{i}" for i in range(1, 51)],
)
def test_api_update_student_invalid_values(client, db_conn, invalid_payload):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (9999, "Validation Student", 20, "val@example.com", "CS"),
    )
    db_conn.commit()

    resp = client.put("/students/9999", json=invalid_payload)
    assert resp.status_code == 422


# -------------------------------------------------------------
# 6. Database CRUD update fields (name, age, course): 24 tests (ALL PASS)
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid,new_name,new_age,new_course",
    [
        (1000 + i, f"CRUD Name {i}", 21 + (i % 20), f"CRUD Course {i}")
        for i in range(1, 25)
    ],
    ids=[f"crud_update_multi_{i}" for i in range(1, 25)],
)
def test_crud_update_multi_fields(db_conn, sid, new_name, new_age, new_course):
    crud.create_student(
        db_conn,
        StudentCreate(
            student_id=sid,
            name=f"Old Name {sid}",
            age=19,
            email=f"crud_{sid}@old.com",
            course="Old Course",
        ),
    )
    update_data = StudentUpdate(name=new_name, age=new_age, course=new_course)
    updated = crud.update_student(db_conn, sid, update_data)
    assert updated is not None
    assert updated["name"] == new_name
    assert updated["age"] == new_age
    assert updated["course"] == new_course


# -------------------------------------------------------------
# 7. Student Update Email Functionality: EXACTLY 6 TESTS
# (These 6 fail initially due to the email update bug in app/crud.py)
# -------------------------------------------------------------
def test_update_student_email_standard(client, db_conn):
    """Test updating student email to a standard new address."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (801, "Alice Standard", 20, "old_alice@example.com", "Computer Science"),
    )
    db_conn.commit()

    resp = client.put("/students/801", json={"email": "alice.new@example.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "alice.new@example.com"


def test_update_student_email_domain_change(client, db_conn):
    """Test updating student email across different academic domain."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (802, "Bob Transfer", 22, "bob@statecollege.edu", "Mathematics"),
    )
    db_conn.commit()

    resp = client.put("/students/802", json={"email": "bob@university.edu"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "bob@university.edu"


def test_update_student_email_with_subdomain(client, db_conn):
    """Test updating student email with a department subdomain."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (803, "Charlie Research", 24, "charlie@general.org", "Physics"),
    )
    db_conn.commit()

    resp = client.put("/students/803", json={"email": "charlie@cs.university.org"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "charlie@cs.university.org"


def test_update_student_email_with_plus_tag(client, db_conn):
    """Test updating student email using standard plus-addressing."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (804, "Diana Tag", 21, "diana@test.com", "Biology"),
    )
    db_conn.commit()

    resp = client.put("/students/804", json={"email": "diana+student@test.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "diana+student@test.com"


def test_update_student_email_with_dots(client, db_conn):
    """Test updating student email containing multiple dot separators."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        (805, "Evan MultiDot", 23, "evan@simple.net", "Chemistry"),
    )
    db_conn.commit()

    resp = client.put("/students/805", json={"email": "first.middle.last@domain.net"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "first.middle.last@domain.net"


def test_crud_update_student_email_direct(db_conn):
    """Test direct database layer student email update."""
    crud.create_student(
        db_conn,
        StudentCreate(
            student_id=806,
            name="Frank Direct",
            age=25,
            email="frank_old@database.io",
            course="Database Systems",
        ),
    )
    update_data = StudentUpdate(email="frank_new@database.io")
    updated = crud.update_student(db_conn, 806, update_data)
    assert updated is not None
    assert updated["email"] == "frank_new@database.io"


