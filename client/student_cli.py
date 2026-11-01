import re
import sys
from typing import Any, Dict, List, Optional, Tuple
import requests

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def validate_student_id(val: Any) -> Tuple[bool, Optional[str]]:
    try:
        sid = int(val)
        if sid <= 0:
            return False, "Student ID must be a positive integer greater than zero."
        return True, None
    except (ValueError, TypeError):
        return False, "Student ID must be a valid integer."


def validate_name(val: Any) -> Tuple[bool, Optional[str]]:
    if not isinstance(val, str) or not val.strip():
        return False, "Name cannot be empty or blank."
    if len(val.strip()) > 100:
        return False, "Name must be at most 100 characters."
    return True, None


def validate_age(val: Any) -> Tuple[bool, Optional[str]]:
    try:
        age = int(val)
        if age < 1 or age > 120:
            return False, "Age must be between 1 and 120."
        return True, None
    except (ValueError, TypeError):
        return False, "Age must be a valid integer."


def validate_email(val: Any) -> Tuple[bool, Optional[str]]:
    if not isinstance(val, str) or not val.strip():
        return False, "Email cannot be empty or blank."
    cleaned = val.strip()
    if not EMAIL_REGEX.match(cleaned):
        return False, "Email must be a valid email address (e.g. user@example.com)."
    if len(cleaned) > 120:
        return False, "Email must be at most 120 characters."
    return True, None


def validate_course(val: Any) -> Tuple[bool, Optional[str]]:
    if not isinstance(val, str) or not val.strip():
        return False, "Course cannot be empty or blank."
    if len(val.strip()) > 100:
        return False, "Course must be at most 100 characters."
    return True, None


def validate_student_inputs(
    student_id: Any, name: Any, age: Any, email: Any, course: Any
) -> List[str]:
    errors = []
    ok, err = validate_student_id(student_id)
    if not ok and err:
        errors.append(err)
    ok, err = validate_name(name)
    if not ok and err:
        errors.append(err)
    ok, err = validate_age(age)
    if not ok and err:
        errors.append(err)
    ok, err = validate_email(email)
    if not ok and err:
        errors.append(err)
    ok, err = validate_course(course)
    if not ok and err:
        errors.append(err)
    return errors


def format_student(student: Dict[str, Any]) -> str:
    return (
        f"ID: {student.get('student_id')} | "
        f"Name: {student.get('name')} | "
        f"Age: {student.get('age')} | "
        f"Email: {student.get('email')} | "
        f"Course: {student.get('course')}"
    )


def format_student_table(students: List[Dict[str, Any]]) -> str:
    if not students:
        return "No students found."
    header = f"{'ID':<8} {'Name':<25} {'Age':<6} {'Email':<30} {'Course':<20}"
    separator = "-" * len(header)
    rows = [header, separator]
    for s in students:
        row = f"{s.get('student_id', ''):<8} {s.get('name', '')[:23]:<25} {s.get('age', ''):<6} {s.get('email', '')[:28]:<30} {s.get('course', '')[:18]:<20}"
        rows.append(row)
    return "\n".join(rows)


def add_student(
    base_url: str,
    student_id: int,
    name: str,
    age: int,
    email: str,
    course: str,
    session: Optional[requests.Session] = None,
) -> Tuple[bool, Any]:
    errors = validate_student_inputs(student_id, name, age, email, course)
    if errors:
        return False, "; ".join(errors)

    payload = {
        "student_id": int(student_id),
        "name": name.strip(),
        "age": int(age),
        "email": email.strip(),
        "course": course.strip(),
    }
    client = session or requests
    try:
        response = client.post(f"{base_url}/students", json=payload, timeout=5)
        if response.status_code == 201:
            return True, response.json()
        elif response.status_code == 409:
            return False, f"Conflict: {response.json().get('detail', 'Duplicate ID')}"
        else:
            return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Connection failed: {e}"


def view_all_students(
    base_url: str, session: Optional[requests.Session] = None
) -> Tuple[bool, Any]:
    client = session or requests
    try:
        response = client.get(f"{base_url}/students", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Connection failed: {e}"


def search_student(
    base_url: str, student_id: int, session: Optional[requests.Session] = None
) -> Tuple[bool, Any]:
    ok, err = validate_student_id(student_id)
    if not ok:
        return False, err

    client = session or requests
    try:
        response = client.get(f"{base_url}/students/{student_id}", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 404:
            return False, f"Not found: Student ID {student_id} does not exist"
        return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Connection failed: {e}"


def update_student(
    base_url: str,
    student_id: int,
    name: Optional[str] = None,
    age: Optional[int] = None,
    email: Optional[str] = None,
    course: Optional[str] = None,
    session: Optional[requests.Session] = None,
) -> Tuple[bool, Any]:
    ok, err = validate_student_id(student_id)
    if not ok:
        return False, err

    payload: Dict[str, Any] = {}
    if name is not None:
        ok, err = validate_name(name)
        if not ok:
            return False, err
        payload["name"] = name.strip()

    if age is not None:
        ok, err = validate_age(age)
        if not ok:
            return False, err
        payload["age"] = int(age)

    if email is not None:
        ok, err = validate_email(email)
        if not ok:
            return False, err
        payload["email"] = email.strip()

    if course is not None:
        ok, err = validate_course(course)
        if not ok:
            return False, err
        payload["course"] = course.strip()

    if not payload:
        return False, "No update fields provided."

    client = session or requests
    try:
        response = client.put(
            f"{base_url}/students/{student_id}", json=payload, timeout=5
        )
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 404:
            return False, f"Not found: Student ID {student_id} does not exist"
        return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Connection failed: {e}"


def delete_student(
    base_url: str, student_id: int, session: Optional[requests.Session] = None
) -> Tuple[bool, Any]:
    ok, err = validate_student_id(student_id)
    if not ok:
        return False, err

    client = session or requests
    try:
        response = client.delete(f"{base_url}/students/{student_id}", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 404:
            return False, f"Not found: Student ID {student_id} does not exist"
        return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Connection failed: {e}"


def display_menu():
    print("\n=== Student Management System ===")
    print("1. Add a student")
    print("2. View all students")
    print("3. Search for a student by ID")
    print("4. Update student details")
    print("5. Delete a student")
    print("6. Exit")


def main():
    base_url = DEFAULT_BASE_URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    while True:
        display_menu()
        choice = input("Enter choice (1-6): ").strip()
        if choice == "1":
            try:
                sid = int(input("Enter Student ID: ").strip())
                name = input("Enter Name: ").strip()
                age = int(input("Enter Age: ").strip())
                email = input("Enter Email: ").strip()
                course = input("Enter Course: ").strip()
                ok, res = add_student(base_url, sid, name, age, email, course)
                if ok:
                    print(f"Success! Added student: {format_student(res)}")
                else:
                    print(f"Failed to add student: {res}")
            except ValueError:
                print("Invalid input. ID and Age must be numbers.")
        elif choice == "2":
            ok, res = view_all_students(base_url)
            if ok:
                print("\n" + format_student_table(res))
            else:
                print(f"Failed to retrieve students: {res}")
        elif choice == "3":
            try:
                sid = int(input("Enter Student ID to search: ").strip())
                ok, res = search_student(base_url, sid)
                if ok:
                    print(f"\nFound student: {format_student(res)}")
                else:
                    print(f"Search failed: {res}")
            except ValueError:
                print("Invalid Student ID.")
        elif choice == "4":
            try:
                sid = int(input("Enter Student ID to update: ").strip())
                print("Leave field blank to keep unchanged:")
                name = input("New Name: ").strip() or None
                age_raw = input("New Age: ").strip()
                age = int(age_raw) if age_raw else None
                email = input("New Email: ").strip() or None
                course = input("New Course: ").strip() or None
                ok, res = update_student(base_url, sid, name, age, email, course)
                if ok:
                    print(f"Student updated successfully: {format_student(res)}")
                else:
                    print(f"Update failed: {res}")
            except ValueError:
                print("Invalid input.")
        elif choice == "5":
            try:
                sid = int(input("Enter Student ID to delete: ").strip())
                ok, res = delete_student(base_url, sid)
                if ok:
                    print(f"Success: {res.get('message', 'Student deleted')}")
                else:
                    print(f"Delete failed: {res}")
            except ValueError:
                print("Invalid Student ID.")
        elif choice == "6":
            print("Exiting Student Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
