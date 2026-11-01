import sqlite3
from typing import Any, Dict, List, Optional
from app.models import StudentCreate, StudentUpdate


def get_all_students(db: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = db.cursor()
    cursor.execute(
        "SELECT student_id, name, age, email, course FROM students ORDER BY student_id ASC"
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_student_by_id(db: sqlite3.Connection, student_id: int) -> Optional[Dict[str, Any]]:
    cursor = db.cursor()
    cursor.execute(
        "SELECT student_id, name, age, email, course FROM students WHERE student_id = ?",
        (student_id,),
    )
    row = cursor.fetchone()
    if row is not None:
        return dict(row)
    return None


def create_student(db: sqlite3.Connection, student: StudentCreate) -> Dict[str, Any]:
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO students (student_id, name, age, email, course)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            student.student_id,
            student.name,
            student.age,
            student.email,
            student.course,
        ),
    )
    db.commit()
    return dict(get_student_by_id(db, student.student_id))  # type: ignore[arg-type]


def update_student(
    db: sqlite3.Connection, student_id: int, student_data: StudentUpdate
) -> Optional[Dict[str, Any]]:
    existing = get_student_by_id(db, student_id)
    if existing is None:
        return None

    updated_name = (
        student_data.name if student_data.name is not None else existing["name"]
    )
    updated_age = (
        student_data.age if student_data.age is not None else existing["age"]
    )
    updated_email = (
        student_data.email if student_data.email is not None else existing["email"]
    )
    updated_course = (
        student_data.course if student_data.course is not None else existing["course"]
    )

    cursor = db.cursor()
    # INTENTIONAL BUG: Passing existing["email"] instead of updated_email
    # causing email updates to fail.
    cursor.execute(
        """
        UPDATE students
        SET name = ?, age = ?, email = ?, course = ?
        WHERE student_id = ?
        """,
        (updated_name, updated_age, existing["email"], updated_course, student_id),
    )
    db.commit()
    return get_student_by_id(db, student_id)


def delete_student(db: sqlite3.Connection, student_id: int) -> bool:
    existing = get_student_by_id(db, student_id)
    if existing is None:
        return False
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    db.commit()
    return True
