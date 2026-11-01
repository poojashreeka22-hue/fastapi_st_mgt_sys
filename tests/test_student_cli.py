from typing import Any
import pytest
from unittest.mock import MagicMock
from client.student_cli import (
    validate_student_id,
    validate_name,
    validate_age,
    validate_email,
    validate_course,
    validate_student_inputs,
    format_student,
    format_student_table,
    add_student,
    view_all_students,
    search_student,
    update_student,
    delete_student,
)

# -------------------------------------------------------------
# 1. validate_student_id: 10 valid + 15 invalid = 25 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid",
    [1, 2, 5, 10, 42, 99, 100, 250, 500, 1000],
    ids=[f"valid_sid_{i}" for i in range(1, 11)],
)
def test_cli_validate_student_id_valid(sid: Any):
    ok, err = validate_student_id(sid)
    assert ok is True
    assert err is None


@pytest.mark.parametrize(
    "sid",
    [
        0, -1, -5, -99, "0", "-1", "-100",
        "abc", "12.34", "", " ", None, [], {}, "id_101"
    ],
    ids=[f"invalid_sid_{i}" for i in range(1, 16)],
)
def test_cli_validate_student_id_invalid(sid: Any):
    ok, err = validate_student_id(sid)
    assert ok is False
    assert err is not None


# -------------------------------------------------------------
# 2. validate_name: 10 valid + 10 invalid = 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "name",
    [
        "Alice Smith", "Bob Jones", "C", "Alexander the Great", "Dr. Jane Doe",
        "Jean-Luc Picard", "O'Connor", "Maria Garcia-Lopez", "A" * 100, "John 3rd"
    ],
    ids=[f"valid_name_{i}" for i in range(1, 11)],
)
def test_cli_validate_name_valid(name: Any):
    ok, err = validate_name(name)
    assert ok is True
    assert err is None


@pytest.mark.parametrize(
    "name",
    [
        "", "   ", "\t", "\n", None, 123, True, [], "A" * 101, "   \n  "
    ],
    ids=[f"invalid_name_{i}" for i in range(1, 11)],
)
def test_cli_validate_name_invalid(name: Any):
    ok, err = validate_name(name)
    assert ok is False
    assert err is not None


# -------------------------------------------------------------
# 3. validate_age: 10 valid + 10 invalid = 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "age",
    [1, 5, 18, 20, 25, 30, 50, 80, 120, "21"],
    ids=[f"valid_age_{i}" for i in range(1, 11)],
)
def test_cli_validate_age_valid(age: Any):
    ok, err = validate_age(age)
    assert ok is True
    assert err is None


@pytest.mark.parametrize(
    "age",
    [0, -1, -50, 121, 150, "abc", "20.5", "", None, []],
    ids=[f"invalid_age_{i}" for i in range(1, 11)],
)
def test_cli_validate_age_invalid(age: Any):
    ok, err = validate_age(age)
    assert ok is False
    assert err is not None


# -------------------------------------------------------------
# 4. validate_email: 10 valid + 10 invalid = 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "email",
    [
        "student@example.com", "user.name@domain.co", "test+tag@school.edu",
        "first_last@work.org", "s123@sub.domain.net", "a@b.cd",
        "student.alpha@university.ac.uk", "contact@developer.io",
        "info@tech-institute.com", "valid.100@domain.org"
    ],
    ids=[f"valid_email_{i}" for i in range(1, 11)],
)
def test_cli_validate_email_valid(email: Any):
    ok, err = validate_email(email)
    assert ok is True
    assert err is None


@pytest.mark.parametrize(
    "email",
    [
        "plainaddress", "missingatsign.com", "@missinguser.com", "user@.com",
        "user@domain", "", "   ", None, 12345, "a" * 115 + "@toolongdomainname.com"
    ],
    ids=[f"invalid_email_{i}" for i in range(1, 11)],
)
def test_cli_validate_email_invalid(email: Any):
    ok, err = validate_email(email)
    assert ok is False
    assert err is not None


# -------------------------------------------------------------
# 5. validate_course: 10 valid + 10 invalid = 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "course",
    [
        "Computer Science", "Mathematics", "Physics 101", "Data Engineering",
        "Intro to AI", "Bio-Chemistry", "Software Architecture", "B",
        "Statistics & Probability", "C" * 100
    ],
    ids=[f"valid_course_{i}" for i in range(1, 11)],
)
def test_cli_validate_course_valid(course: Any):
    ok, err = validate_course(course)
    assert ok is True
    assert err is None


@pytest.mark.parametrize(
    "course",
    [
        "", "   ", "\t", "\n", None, 999, False, [], {}, "C" * 101
    ],
    ids=[f"invalid_course_{i}" for i in range(1, 11)],
)
def test_cli_validate_course_invalid(course: Any):
    ok, err = validate_course(course)
    assert ok is False
    assert err is not None


# -------------------------------------------------------------
# 6. validate_student_inputs: 10 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "inputs,expected_err_count",
    [
        ((1, "John", 20, "john@example.com", "CS"), 0),
        ((0, "John", 20, "john@example.com", "CS"), 1),
        ((-1, "", 20, "john@example.com", "CS"), 2),
        ((-1, "", -5, "john@example.com", "CS"), 3),
        ((-1, "", -5, "bad_email", "CS"), 4),
        ((-1, "", -5, "bad_email", ""), 5),
        ((10, "Valid Name", 150, "john@example.com", "Physics"), 1),
        ((10, "Valid Name", 25, "no_at_domain.com", "Physics"), 1),
        ((10, "   ", 25, "john@example.com", "Physics"), 1),
        ((10, "Valid Name", 25, "john@example.com", "   "), 1),
    ],
    ids=[f"validate_combo_{i}" for i in range(1, 11)],
)
def test_cli_validate_inputs_combo(inputs, expected_err_count):
    sid, name, age, email, course = inputs
    errs = validate_student_inputs(sid, name, age, email, course)
    assert len(errs) == expected_err_count


# -------------------------------------------------------------
# 7. format_student: 10 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "student_dict",
    [
        {"student_id": 1, "name": "Alice", "age": 20, "email": "a@ex.com", "course": "CS"},
        {"student_id": 2, "name": "Bob", "age": 22, "email": "b@ex.com", "course": "Math"},
        {"student_id": 3, "name": "Charlie", "age": 21, "email": "c@ex.com", "course": "Physics"},
        {"student_id": 4, "name": "Diana", "age": 23, "email": "d@ex.com", "course": "Bio"},
        {"student_id": 5, "name": "Evan", "age": 19, "email": "e@ex.com", "course": "Chemistry"},
        {"student_id": 6, "name": "Fiona", "age": 24, "email": "f@ex.com", "course": "History"},
        {"student_id": 7, "name": "George", "age": 26, "email": "g@ex.com", "course": "Art"},
        {"student_id": 8, "name": "Hannah", "age": 20, "email": "h@ex.com", "course": "Law"},
        {"student_id": 9, "name": "Ian", "age": 22, "email": "i@ex.com", "course": "Medicine"},
        {"student_id": 10, "name": "Julia", "age": 25, "email": "j@ex.com", "course": "Music"},
    ],
    ids=[f"format_student_{i}" for i in range(1, 11)],
)
def test_cli_format_student(student_dict):
    output = format_student(student_dict)
    assert f"ID: {student_dict['student_id']}" in output
    assert student_dict["name"] in output
    assert str(student_dict["age"]) in output
    assert student_dict["email"] in output
    assert student_dict["course"] in output


# -------------------------------------------------------------
# 8. format_student_table: 5 tests
# -------------------------------------------------------------
def test_cli_format_table_empty():
    assert format_student_table([]) == "No students found."


def test_cli_format_table_single():
    res = format_student_table([{"student_id": 1, "name": "Alice", "age": 20, "email": "a@ex.com", "course": "CS"}])
    assert "ID" in res
    assert "Alice" in res


def test_cli_format_table_multiple():
    stus = [
        {"student_id": 1, "name": "Alice", "age": 20, "email": "a@ex.com", "course": "CS"},
        {"student_id": 2, "name": "Bob", "age": 22, "email": "b@ex.com", "course": "Math"},
    ]
    res = format_student_table(stus)
    assert "Alice" in res
    assert "Bob" in res


def test_cli_format_table_contains_headers():
    res = format_student_table([{"student_id": 1, "name": "A", "age": 20, "email": "a@e.com", "course": "C"}])
    assert "Name" in res
    assert "Age" in res
    assert "Email" in res
    assert "Course" in res


def test_cli_format_table_multiline():
    stus = [{"student_id": i, "name": f"Student {i}", "age": 20, "email": f"s{i}@ex.com", "course": "CS"} for i in range(3)]
    res = format_student_table(stus)
    lines = res.splitlines()
    assert len(lines) == 5  # header + separator + 3 rows


# -------------------------------------------------------------
# 9. API client functions with mock session: 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "status_code,response_payload,expected_ok",
    [
        (201, {"student_id": 101, "name": "Sam", "age": 21, "email": "sam@ex.com", "course": "CS"}, True),
        (409, {"detail": "Student ID 101 already exists"}, False),
        (422, {"detail": "Validation error"}, False),
        (500, "Internal Server Error", False),
    ],
    ids=[f"add_student_http_{i}" for i in range(1, 5)],
)
def test_cli_add_student_http_cases(status_code, response_payload, expected_ok):
    session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    if isinstance(response_payload, dict):
        mock_resp.json.return_value = response_payload
    else:
        mock_resp.text = str(response_payload)
    session.post.return_value = mock_resp

    ok, res = add_student("http://testserver", 101, "Sam", 21, "sam@ex.com", "CS", session=session)
    assert ok is expected_ok


def test_cli_add_student_validation_failure():
    ok, err = add_student("http://testserver", -1, "", 0, "bad", "")
    assert ok is False
    assert "positive integer" in err


def test_cli_add_student_connection_exception():
    session = MagicMock()
    session.post.side_effect = Exception("Connection refused")
    ok, err = add_student("http://testserver", 1, "Alice", 20, "a@b.com", "CS", session=session)
    assert ok is False
    assert "Connection failed" in err


@pytest.mark.parametrize(
    "status_code,response_data,expected_ok",
    [
        (200, [{"student_id": 1, "name": "Alice", "age": 20, "email": "a@ex.com", "course": "CS"}], True),
        (200, [], True),
        (500, "Internal error", False),
    ],
    ids=[f"view_all_http_{i}" for i in range(1, 4)],
)
def test_cli_view_all_students_http_cases(status_code, response_data, expected_ok):
    session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    if isinstance(response_data, list):
        mock_resp.json.return_value = response_data
    else:
        mock_resp.text = str(response_data)
    session.get.return_value = mock_resp

    ok, res = view_all_students("http://testserver", session=session)
    assert ok is expected_ok


def test_cli_view_all_connection_exception():
    session = MagicMock()
    session.get.side_effect = Exception("Network down")
    ok, err = view_all_students("http://testserver", session=session)
    assert ok is False
    assert "Connection failed" in err


@pytest.mark.parametrize(
    "sid,status_code,response_data,expected_ok",
    [
        (1, 200, {"student_id": 1, "name": "Alice", "age": 20, "email": "a@ex.com", "course": "CS"}, True),
        (999, 404, {"detail": "Student with ID 999 not found"}, False),
        (1, 500, "Server error", False),
    ],
    ids=[f"search_http_{i}" for i in range(1, 4)],
)
def test_cli_search_student_http_cases(sid, status_code, response_data, expected_ok):
    session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    if isinstance(response_data, dict):
        mock_resp.json.return_value = response_data
    else:
        mock_resp.text = str(response_data)
    session.get.return_value = mock_resp

    ok, res = search_student("http://testserver", sid, session=session)
    assert ok is expected_ok


def test_cli_search_invalid_id():
    ok, err = search_student("http://testserver", -5)
    assert ok is False
    assert "positive integer" in err


@pytest.mark.parametrize(
    "sid,kwargs,status_code,expected_ok",
    [
        (1, {"name": "Bob"}, 200, True),
        (1, {"age": 22}, 200, True),
        (99, {"name": "Ghost"}, 404, False),
    ],
    ids=[f"update_http_{i}" for i in range(1, 4)],
)
def test_cli_update_student_http_cases(sid, kwargs, status_code, expected_ok):
    session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = {"student_id": sid, **kwargs}
    session.put.return_value = mock_resp

    ok, res = update_student("http://testserver", sid, **kwargs, session=session)
    assert ok is expected_ok


def test_cli_update_no_fields():
    ok, err = update_student("http://testserver", 1)
    assert ok is False
    assert "No update fields" in err


@pytest.mark.parametrize(
    "sid,status_code,expected_ok",
    [
        (1, 200, True),
        (999, 404, False),
    ],
    ids=[f"delete_http_{i}" for i in range(1, 3)],
)
def test_cli_delete_student_http_cases(sid, status_code, expected_ok):
    session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = {"message": "done"}
    session.delete.return_value = mock_resp

    ok, res = delete_student("http://testserver", sid, session=session)
    assert ok is expected_ok
