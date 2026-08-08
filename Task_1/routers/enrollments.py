from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas import (
    EnrollmentCreate,
    EnrollmentUpdate,
    EnrollmentResponse,
)

router = APIRouter()


@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):

    student_check = await db.execute(
        select(models.Student).where(models.Student.id == enrollment_data.student_id)
    )
    if not student_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {enrollment_data.student_id} not found"
        )

    course_check = await db.execute(
        select(models.Course).where(models.Course.id == enrollment_data.course_id)
    )
    if not course_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {enrollment_data.course_id} not found"
        )

    duplicate_check = await db.execute(
        select(models.Enrollment).where(
            models.Enrollment.student_id == enrollment_data.student_id,
            models.Enrollment.course_id == enrollment_data.course_id,
        )
    )
    if duplicate_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already enrolled in this course"
        )

    new_enrollment = models.Enrollment(
        student_id=enrollment_data.student_id,
        course_id=enrollment_data.course_id,
        grade=enrollment_data.grade,
        status=enrollment_data.status
    )

    db.add(new_enrollment)
    await db.commit()
    await db.refresh(new_enrollment)
    return new_enrollment


@router.get("", response_model=list[EnrollmentResponse])
async def list_enrollments(
    db: Annotated[AsyncSession, Depends(get_db)],
    student_id: int | None = Query(default=None, description="Filter by student ID"),
    course_id: int | None = Query(default=None, description="Filter by course ID"),
    enrollment_status: Literal["enrolled", "completed", "dropped"] | None = Query(default=None, alias="status", description="Filter by status"),
    sort_by: Literal["id", "enrolled_at", "status", "grade"] = "id",
    order: Literal["asc", "desc"] = "asc",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = select(models.Enrollment)

    if student_id is not None:
        query = query.where(models.Enrollment.student_id == student_id)
    if course_id is not None:
        query = query.where(models.Enrollment.course_id == course_id)
    if enrollment_status is not None:
        query = query.where(models.Enrollment.status == enrollment_status)

    column = getattr(models.Enrollment, sort_by)
    sort_func = desc(column) if order == "desc" else asc(column)
    query = query.order_by(sort_func)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Enrollment).where(models.Enrollment.id == enrollment_id)
    )
    enrollment = result.scalars().first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found"
        )

    return enrollment


@router.patch("/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(
    enrollment_id: int,
    enrollment_data: EnrollmentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Enrollment).where(models.Enrollment.id == enrollment_id)
    )
    enrollment = result.scalars().first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found"
        )

    updates = enrollment_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(enrollment, field, value)

    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Enrollment).where(models.Enrollment.id == enrollment_id)
    )
    enrollment = result.scalars().first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found"
        )

    await db.delete(enrollment)
    await db.commit()
