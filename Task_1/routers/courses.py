from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy import select, func, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseDetailResponse,
)

router = APIRouter()


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    code_check = await db.execute(
        select(models.Course).where(func.lower(models.Course.course_code) == course_data.course_code.lower())
    )
    if code_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this course code already exists"
        )

    new_course = models.Course(
        course_code=course_data.course_code,
        title=course_data.title,
        description=course_data.description,
        credits=course_data.credits,
        department=course_data.department
    )

    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)
    return new_course


@router.get("", response_model=list[CourseResponse])
async def list_courses(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: str | None = Query(default=None, description="Search by course code, title, description, or department"),
    department: str | None = Query(default=None, description="Filter by department"),
    sort_by: Literal["id", "course_code", "title", "credits", "department", "created_at"] = "id",
    order: Literal["asc", "desc"] = "asc",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = select(models.Course)

    if department:
        query = query.where(func.lower(models.Course.department) == department.lower())

    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(models.Course.course_code).like(search_pattern),
                func.lower(models.Course.title).like(search_pattern),
                func.lower(models.Course.description).like(search_pattern),
                func.lower(models.Course.department).like(search_pattern),
            )
        )

    column = getattr(models.Course, sort_by)
    sort_func = desc(column) if order == "desc" else asc(column)
    query = query.order_by(sort_func)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    query = (
        select(models.Course)
        .where(models.Course.id == course_id)
        .options(
            selectinload(models.Course.enrollments).selectinload(models.Enrollment.student)
        )
    )
    result = await db.execute(query)
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )

    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course_full(
    course_id: int,
    course_data: CourseCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Course).where(models.Course.id == course_id))
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )

    if course_data.course_code.lower() != course.course_code.lower():
        code_check = await db.execute(
            select(models.Course).where(func.lower(models.Course.course_code) == course_data.course_code.lower())
        )
        if code_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course with this course code already exists"
            )

    course.course_code = course_data.course_code
    course.title = course_data.title
    course.description = course_data.description
    course.credits = course_data.credits
    course.department = course_data.department

    await db.commit()
    await db.refresh(course)
    return course


@router.patch("/{course_id}", response_model=CourseResponse)
async def update_course_partial(
    course_id: int,
    course_data: CourseUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Course).where(models.Course.id == course_id))
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )

    updates = course_data.model_dump(exclude_unset=True)

    if "course_code" in updates and updates["course_code"]:
        new_code = updates["course_code"]
        if new_code.lower() != course.course_code.lower():
            code_check = await db.execute(
                select(models.Course).where(func.lower(models.Course.course_code) == new_code.lower())
            )
            if code_check.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course with this course code already exists"
                )

    for field, value in updates.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Course).where(models.Course.id == course_id))
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )

    await db.delete(course)
    await db.commit()
