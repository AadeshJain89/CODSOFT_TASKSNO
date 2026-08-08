from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from typing import Literal
from datetime import datetime

class StudentBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)
    enrollment_number: str = Field(min_length=1, max_length=20)
    major: str = Field(min_length=1, max_length=50)
    gpa: float | None = Field(default=None, ge=0.0, le=4.0)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower() if value else value


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    enrollment_number: str | None = Field(default=None, min_length=1, max_length=20)
    major: str | None = Field(default=None, min_length=1, max_length=50)
    gpa: float | None = Field(default=None, ge=0.0, le=4.0)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value.lower() if value else value


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class CourseBase(BaseModel):
    course_code: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None)
    credits: int = Field(ge=1, le=10)
    department: str = Field(min_length=1, max_length=50)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_code: str | None = Field(default=None, min_length=1, max_length=20)
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None)
    credits: int | None = Field(default=None, ge=1, le=10)
    department: str | None = Field(default=None, min_length=1, max_length=50)


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EnrollmentCreate(BaseModel):
    student_id: int = Field(gt=0)
    course_id: int = Field(gt=0)
    grade: str | None = Field(default=None, max_length=5)
    status: Literal["enrolled", "completed", "dropped"] = "enrolled"


class EnrollmentUpdate(BaseModel):
    grade: str | None = Field(default=None, max_length=5)
    status: Literal["enrolled", "completed", "dropped"] | None = None


class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    grade: str | None
    status: str
    enrolled_at: datetime


class EnrollmentWithCourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    grade: str | None
    status: str
    enrolled_at: datetime
    course: CourseResponse


class EnrollmentWithStudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    grade: str | None
    status: str
    enrolled_at: datetime
    student: StudentResponse


class StudentDetailResponse(StudentResponse):
    enrollments: list[EnrollmentWithCourseResponse] = []


class CourseDetailResponse(CourseResponse):
    enrollments: list[EnrollmentWithStudentResponse] = []
