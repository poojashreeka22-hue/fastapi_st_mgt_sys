from contextlib import asynccontextmanager
import sqlite3
from typing import Generator, List
from fastapi import Depends, FastAPI, HTTPException, Path, status

from app.database import get_connection, init_db
from app.models import StudentCreate, StudentResponse, StudentUpdate
import app.crud as crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_connection()
    init_db(conn)
    conn.close()
    yield


app = FastAPI(
    title="Student Management System",
    description="A beginner-friendly Student Management System API",
    version="1.0.0",
    lifespan=lifespan,
)


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    student: StudentCreate, db: sqlite3.Connection = Depends(get_db)
):
    existing = crud.get_student_by_id(db, student.student_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student ID {student.student_id} already exists",
        )
    return crud.create_student(db, student)


@app.get("/students", response_model=List[StudentResponse])
def read_all_students(db: sqlite3.Connection = Depends(get_db)):
    return crud.get_all_students(db)


@app.get("/students/{student_id}", response_model=StudentResponse)
def read_student(
    student_id: int = Path(..., gt=0, description="The ID of the student to search"),
    db: sqlite3.Connection = Depends(get_db),
):
    student = crud.get_student_by_id(db, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
    return student


@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int = Path(..., gt=0, description="The ID of the student to update"),
    student_data: StudentUpdate = ...,
    db: sqlite3.Connection = Depends(get_db),
):
    existing = crud.get_student_by_id(db, student_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
    updated = crud.update_student(db, student_id, student_data)
    return updated


@app.delete("/students/{student_id}")
def delete_student(
    student_id: int = Path(..., gt=0, description="The ID of the student to delete"),
    db: sqlite3.Connection = Depends(get_db),
):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
    return {"message": f"Student with ID {student_id} successfully deleted"}
