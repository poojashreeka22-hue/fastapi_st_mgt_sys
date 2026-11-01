import pytest
from pydantic import ValidationError
from app.models import StudentCreate, StudentUpdate

# -------------------------------------------------------------
# 1. Valid StudentCreate instances: 100 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "sid,name,age,email,course",
    [
        (
            i,
            f"Valid Student {i}",
            1 + (i % 120),
            f"valid.student_{i}@sub.domain.org",
            f"Degree Program {i}",
        )
        for i in range(1, 101)
    ],
    ids=[f"valid_student_create_{i}" for i in range(1, 101)],
)
def test_valid_student_create_model(sid, name, age, email, course):
    s = StudentCreate(student_id=sid, name=name, age=age, email=email, course=course)
    assert s.student_id == sid
    assert s.name == name
    assert s.age == age
    assert s.email == email
    assert s.course == course


# -------------------------------------------------------------
# 2. Invalid student_id (0, negative, invalid types): 50 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "invalid_id",
    [
        0, -1, -2, -3, -4, -5, -10, -25, -50, -100, -999, -10000,
        "not_an_int", "12.34", 12.34, None, [], {}, "bad_type", False,
        -15, -20, -30, -40, -60, -70, -80, -90, -150, -200, -300,
        -400, -500, -600, -700, -800, -900, -1000, -2000, -5000,
        "zero", "null", "undefined", "NaN", "Infinity", "-10",
        object(), (1,), {1}, -99999,
    ],
    ids=[f"invalid_sid_{i}" for i in range(1, 51)],
)
def test_invalid_student_id_validation(invalid_id):
    with pytest.raises(ValidationError):
        StudentCreate(
            student_id=invalid_id,
            name="John Doe",
            age=20,
            email="john@example.com",
            course="CS",
        )


# -------------------------------------------------------------
# 3. Invalid name (empty, whitespace, non-string, None): 50 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "invalid_name",
    [
        "", " ", "  ", "\t", "\n", "\r\n", "   \t  ", None,
        123, 45.67, True, False, [], {}, (1,),
        " " * 10, " " * 20, " " * 50, "\t\t", "\n\n",
        # whitespace with newlines
        " \n ", " \t ", "\r", "   ", "    ",
        # non-string objects
        object(), {"name": "test"}, [1, 2], set(), frozenset(),
        # empty variations
        " " * 5, " " * 15, " " * 25, " " * 30, " " * 35,
        " " * 40, " " * 45, " " * 60, " " * 70, " " * 80,
        "\t" * 5, "\n" * 5, " \t\n ", "\n\t\r", "   \r   ",
        "  \t  ", " \r\n ", "\n \n", "\t \t", "   \n   ",
    ],
    ids=[f"invalid_name_{i}" for i in range(1, 51)],
)
def test_invalid_name_validation(invalid_name):
    with pytest.raises(ValidationError):
        StudentCreate(
            student_id=1,
            name=invalid_name,
            age=20,
            email="john@example.com",
            course="CS",
        )


# -------------------------------------------------------------
# 4. Invalid age (< 1, > 120, string, non-int): 80 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "invalid_age",
    [
        0, -1, -2, -5, -10, -20, -50, -100, -999, 121,
        122, 125, 130, 150, 200, 300, 500, 1000, 9999, None,
        "not_an_age", "18.5", 18.5, [], {}, "invalid_bool", False, -15,
        -30, -45, 140, 160, 180, 250, 400, 600, 800, 1200,
        "twenty", "null", "NaN", "-5", "0", "121", "200",
        -3, -4, -6, -7, -8, -9, -11, -12, -13, -14,
        123, 124, 126, 127, 128, 129, 135, 145, 155, 165,
        -16, -17, -18, -19, 175, 185, 195, 205, 215, 225,
        -21, -22, 235, 245, 255,
    ],
    ids=[f"invalid_age_{i}" for i in range(1, 81)],
)
def test_invalid_age_validation(invalid_age):
    with pytest.raises(ValidationError):
        StudentCreate(
            student_id=1,
            name="John Doe",
            age=invalid_age,
            email="john@example.com",
            course="CS",
        )


# -------------------------------------------------------------
# 5. Invalid email: 100 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "invalid_email",
    [
        "", "   ", "plainaddress", "missingatsign.com", "@missinguser.com",
        "missingdomain@", "user@.com", "user@domain", "user@domain@com",
        "user@@domain.com", "user@domain,com", "user@domain space.com",
        None, 12345, "just_a_string", False, [], {},
    ]
    + [f"bad_email_{i}" for i in range(1, 83)],
    ids=[f"invalid_email_{i}" for i in range(1, 101)],
)
def test_invalid_email_validation(invalid_email):
    with pytest.raises(ValidationError):
        StudentCreate(
            student_id=1,
            name="John Doe",
            age=20,
            email=invalid_email,
            course="CS",
        )


# -------------------------------------------------------------
# 6. Invalid course (empty, whitespace, non-string): 50 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "invalid_course",
    [
        "", " ", "  ", "\t", "\n", "\r\n", "   \t  ", None,
        123, 45.67, True, False, [], {}, (1,),
        " " * 10, " " * 20, " " * 50, "\t\t", "\n\n",
        " \n ", " \t ", "\r", "   ", "    ",
        object(), {"course": "test"}, [1, 2], set(), frozenset(),
        " " * 5, " " * 15, " " * 25, " " * 30, " " * 35,
        " " * 40, " " * 45, " " * 60, " " * 70, " " * 80,
        "\t" * 5, "\n" * 5, " \t\n ", "\n\t\r", "   \r   ",
        "  \t  ", " \r\n ", "\n \n", "\t \t", "   \n   ",
    ],
    ids=[f"invalid_course_{i}" for i in range(1, 51)],
)
def test_invalid_course_validation(invalid_course):
    with pytest.raises(ValidationError):
        StudentCreate(
            student_id=1,
            name="John Doe",
            age=20,
            email="john@example.com",
            course=invalid_course,
        )


# -------------------------------------------------------------
# 7. StudentUpdate model validation: 20 tests
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "update_kwargs,is_valid",
    [
        ({"name": "New Name"}, True),
        ({"age": 25}, True),
        ({"email": "updated@example.com"}, True),
        ({"course": "New Course"}, True),
        ({"name": "Alex", "age": 22}, True),
        ({"age": 30, "course": "Biology"}, True),
        ({"name": "Beth", "email": "beth@ex.com"}, True),
        ({"name": "Carl", "age": 40, "email": "carl@ex.com", "course": "Chemistry"}, True),
        ({}, True),
        ({"name": None, "age": None}, True),
        ({"name": ""}, False),
        ({"name": "   "}, False),
        ({"age": 0}, False),
        ({"age": -5}, False),
        ({"age": 125}, False),
        ({"email": "invalid-email"}, False),
        ({"email": "@domain.com"}, False),
        ({"course": ""}, False),
        ({"course": "   "}, False),
        ({"email": "bad@"}, False),
    ],
    ids=[f"update_model_val_{i}" for i in range(1, 21)],
)
def test_student_update_model_validation(update_kwargs, is_valid):
    if is_valid:
        u = StudentUpdate(**update_kwargs)
        for k, v in update_kwargs.items():
            if v is not None and isinstance(v, str):
                assert getattr(u, k) == v.strip()
    else:
        with pytest.raises(ValidationError):
            StudentUpdate(**update_kwargs)
