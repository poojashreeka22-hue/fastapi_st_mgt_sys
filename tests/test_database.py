import sqlite3
import pytest
from app.database import get_connection, init_db
from app.models import StudentCreate, StudentUpdate
import app.crud as crud

# -------------------------------------------------------------
# 1. Connection and schema initialization: 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize("i", range(1, 11), ids=[f"db_conn_param_{i}" for i in range(1, 11)])
def test_db_get_connection(i):
    conn = get_connection(":memory:")
    assert isinstance(conn, sqlite3.Connection)
    assert conn.row_factory == sqlite3.Row
    conn.close()


@pytest.mark.parametrize("i", range(1, 11), ids=[f"init_db_idempotent_{i}" for i in range(1, 11)])
def test_db_init_idempotency(db_conn, i):
    # Running init_db multiple times should not raise errors
    init_db(db_conn)
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
    row = cursor.fetchone()
    assert row is not None
    assert row["name"] == "students"


# -------------------------------------------------------------
# 2. Database CRUD - create_student: 40 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid,name,age,email,course",
    [
        (i, f"Student {i}", 18 + (i % 25), f"db_student_{i}@university.edu", f"Course {i % 10}")
        for i in range(1, 41)
    ],
    ids=[f"crud_create_student_{i}" for i in range(1, 41)],
)
def test_crud_create_student(db_conn, sid, name, age, email, course):
    student_in = StudentCreate(student_id=sid, name=name, age=age, email=email, course=course)
    created = crud.create_student(db_conn, student_in)
    assert created["student_id"] == sid
    assert created["name"] == name
    assert created["age"] == age
    assert created["email"] == email
    assert created["course"] == course


# -------------------------------------------------------------
# 3. Database CRUD - get_student_by_id: 40 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid",
    range(1, 41),
    ids=[f"crud_get_by_id_{i}" for i in range(1, 41)],
)
def test_crud_get_student_by_id(db_conn, sid):
    # Insert first
    student_in = StudentCreate(
        student_id=sid,
        name=f"Query Student {sid}",
        age=22,
        email=f"query_{sid}@test.com",
        course="Algorithms",
    )
    crud.create_student(db_conn, student_in)

    fetched = crud.get_student_by_id(db_conn, sid)
    assert fetched is not None
    assert fetched["student_id"] == sid
    assert fetched["name"] == f"Query Student {sid}"


# -------------------------------------------------------------
# 4. Database CRUD - get_all_students: 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "count",
    range(1, 21),
    ids=[f"crud_get_all_count_{i}" for i in range(1, 21)],
)
def test_crud_get_all_students_count(db_conn, count):
    for i in range(1, count + 1):
        crud.create_student(
            db_conn,
            StudentCreate(
                student_id=i,
                name=f"Bulk {i}",
                age=20,
                email=f"bulk_{i}@example.com",
                course="Math",
            ),
        )
    all_rows = crud.get_all_students(db_conn)
    assert len(all_rows) == count
    # Verify ordering by student_id
    ids = [r["student_id"] for r in all_rows]
    assert ids == sorted(ids)


# -------------------------------------------------------------
# 5. Database CRUD - update_student (name, age, course): 40 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid,new_name,new_age,new_course",
    [
        (i, f"Updated Name {i}", 20 + (i % 30), f"Updated Course {i}")
        for i in range(1, 41)
    ],
    ids=[f"crud_update_fields_{i}" for i in range(1, 41)],
)
def test_crud_update_student_fields(db_conn, sid, new_name, new_age, new_course):
    # Setup student
    crud.create_student(
        db_conn,
        StudentCreate(
            student_id=sid,
            name="Initial Name",
            age=18,
            email=f"initial_{sid}@test.com",
            course="Initial Course",
        ),
    )
    # Update name, age, course
    update_data = StudentUpdate(name=new_name, age=new_age, course=new_course)
    updated = crud.update_student(db_conn, sid, update_data)
    assert updated is not None
    assert updated["name"] == new_name
    assert updated["age"] == new_age
    assert updated["course"] == new_course
    assert updated["email"] == f"initial_{sid}@test.com"


# -------------------------------------------------------------
# 6. Database CRUD - delete_student: 40 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid",
    range(1, 41),
    ids=[f"crud_delete_student_{i}" for i in range(1, 41)],
)
def test_crud_delete_student(db_conn, sid):
    crud.create_student(
        db_conn,
        StudentCreate(
            student_id=sid,
            name=f"To Delete {sid}",
            age=25,
            email=f"del_{sid}@example.com",
            course="Physics",
        ),
    )
    # Delete
    deleted = crud.delete_student(db_conn, sid)
    assert deleted is True
    # Verify gone
    assert crud.get_student_by_id(db_conn, sid) is None
    # Delete again returns False
    assert crud.delete_student(db_conn, sid) is False
