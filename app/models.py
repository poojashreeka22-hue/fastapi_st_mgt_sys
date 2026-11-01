import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class StudentCreate(BaseModel):
    student_id: int = Field(..., gt=0, description="Positive integer unique student ID")
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=1, le=120)
    email: str = Field(..., min_length=3, max_length=120)
    course: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty or blank")
        return v

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        v = v.strip()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("course")
    def validate_course(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Course cannot be empty or blank")
        return v


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=120)
    email: Optional[str] = Field(None, min_length=3, max_length=120)
    course: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator("name")
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Name cannot be empty or blank")
        return v

    @field_validator("email")
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not EMAIL_REGEX.match(v):
                raise ValueError("Invalid email format")
        return v

    @field_validator("course")
    def validate_course(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Course cannot be empty or blank")
        return v


class StudentResponse(BaseModel):
    student_id: int
    name: str
    age: int
    email: str
    course: str
