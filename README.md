# Student Management System

A beginner-friendly Student Management System built with Python, FastAPI, SQLite, and a console client (CLI).

## Features

1. **Add a Student**: Create a student record with `student_id`, `name`, `age`, `email`, and `course`.
2. **View All Students**: Retrieve and list all registered students.
3. **Search Student by ID**: Look up an individual student by unique positive integer ID.
4. **Update Student Details**: Modify one or more fields (`name`, `age`, `email`, `course`) of an existing student.
5. **Delete a Student**: Remove a student record from the system.
6. **Input Validation**: Strict validation on IDs, names, ages (1–120), email formats, and course names.

## Project Structure

```
StudentManagementSystem/
│
├── app/
│   ├── __init__.py
│   ├── database.py       # SQLite connection and table initialization
│   ├── models.py         # Pydantic validation schemas
│   ├── crud.py           # Database CRUD operations
│   └── main.py           # FastAPI REST API application & endpoints
│
├── client/
│   ├── __init__.py
│   └── student_cli.py    # Console client with interactive menu and API helpers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures (in-memory DB and TestClient)
│   ├── test_student_cli.py       # 150 CLI operation & validation tests
│   ├── test_database.py          # 200 Database CRUD unit tests
│   ├── test_student_validation.py# 450 Pydantic model validation tests
│   ├── test_student_create.py    # 350 Student creation & duplicate tests
│   ├── test_student_read.py      # 300 Student retrieval & search tests
│   ├── test_student_update.py    # 300 Student update tests
│   └── test_student_delete.py    # 250 Student deletion tests
│
├── pyproject.toml        # uv project configuration and dependencies
├── README.md             # Documentation and usage guide
└── .gitignore            # Git ignore patterns
```

## Setup & Execution (Windows PowerShell)

### 1. Install Dependencies
```powershell
cd "$HOME\StudentManagementSystem"
uv sync --group dev --extra standard
```

### 2. Start the FastAPI Backend (Optional / Local Run)
```powershell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Run the Console CLI Client
In a new PowerShell window:
```powershell
uv run python client/student_cli.py
```

### 4. Run Automated Testing

#### Run Selected Test File:
```powershell
uv run pytest tests/test_student_cli.py -v
```

#### Run Complete Automated Test Suite (2,000 Tests):
```powershell
uv run pytest
```

## Automated Test Suite Summary

- **Total Test Cases**: Exactly 2,000 automated pytest cases across 7 test modules.
- **Identifiable Test IDs**: Every collected test case has a descriptive, unique test ID.
- **Isolation**: Tests use isolated in-memory SQLite databases (`:memory:`) to ensure fast, deterministic execution without leaving residual test data.
