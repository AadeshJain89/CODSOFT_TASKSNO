from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy import select, func, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentDetailResponse,
)

router = APIRouter()


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):

    email_check = await db.execute(
        select(models.Student).where(func.lower(models.Student.email) == student_data.email.lower())
    )
    if email_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this email already exists"
        )

    en_check = await db.execute(
        select(models.Student).where(func.lower(models.Student.enrollment_number) == student_data.enrollment_number.lower())
    )
    if en_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this enrollment number already exists"
        )

    new_student = models.Student(
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        email=student_data.email.lower(),
        enrollment_number=student_data.enrollment_number,
        major=student_data.major,
        gpa=student_data.gpa
    )

    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return new_student


@router.get("", response_model=list[StudentResponse])
async def list_students(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: str | None = Query(default=None, description="Search by name, email, enrollment number, or major"),
    major: str | None = Query(default=None, description="Filter by major"),
    sort_by: Literal["id", "first_name", "last_name", "email", "enrollment_number", "major", "gpa", "created_at"] = "id",
    order: Literal["asc", "desc"] = "asc",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = select(models.Student)

    if major:
        query = query.where(func.lower(models.Student.major) == major.lower())

    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(models.Student.first_name).like(search_pattern),
                func.lower(models.Student.last_name).like(search_pattern),
                func.lower(models.Student.email).like(search_pattern),
                func.lower(models.Student.enrollment_number).like(search_pattern),
                func.lower(models.Student.major).like(search_pattern),
            )
        )

    column = getattr(models.Student, sort_by)
    sort_func = desc(column) if order == "desc" else asc(column)
    query = query.order_by(sort_func)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{student_id}", response_model=StudentDetailResponse)
async def get_student(
    student_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    query = (
        select(models.Student)
        .where(models.Student.id == student_id)
        .options(
            selectinload(models.Student.enrollments).selectinload(models.Enrollment.course)
        )
    )
    result = await db.execute(query)
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )

    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student_full(
    student_id: int,
    student_data: StudentCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Student).where(models.Student.id == student_id))
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )

    if student_data.email.lower() != student.email:
        email_check = await db.execute(
            select(models.Student).where(func.lower(models.Student.email) == student_data.email.lower())
        )
        if email_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this email already exists"
            )
    if student_data.enrollment_number.lower() != student.enrollment_number.lower():
        en_check = await db.execute(
            select(models.Student).where(func.lower(models.Student.enrollment_number) == student_data.enrollment_number.lower())
        )
        if en_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this enrollment number already exists"
            )

    student.first_name = student_data.first_name
    student.last_name = student_data.last_name
    student.email = student_data.email.lower()
    student.enrollment_number = student_data.enrollment_number
    student.major = student_data.major
    student.gpa = student_data.gpa

    await db.commit()
    await db.refresh(student)
    return student


@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student_partial(
    student_id: int,
    student_data: StudentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Student).where(models.Student.id == student_id))
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )

    updates = student_data.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"]:
        new_email = updates["email"].lower()
        if new_email != student.email:
            email_check = await db.execute(
                select(models.Student).where(func.lower(models.Student.email) == new_email)
            )
            if email_check.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student with this email already exists"
                )
        updates["email"] = new_email

    if "enrollment_number" in updates and updates["enrollment_number"]:
        new_en = updates["enrollment_number"]
        if new_en.lower() != student.enrollment_number.lower():
            en_check = await db.execute(
                select(models.Student).where(func.lower(models.Student.enrollment_number) == new_en.lower())
            )
            if en_check.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student with this enrollment number already exists"
                )

    for field, value in updates.items():
        setattr(student, field, value)

    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Student).where(models.Student.id == student_id))
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )

    await db.delete(student)
    await db.commit()
