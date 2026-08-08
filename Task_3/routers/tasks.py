from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import TaskCreate, TaskResponse, TaskUpdate

from auth import CurrentUser

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):  
    new_task = models.Task(
        title = task.title,
        description = task.description,
        completed = task.completed,
        priority = task.priority,
        due_date = task.due_date,
        category = task.category,
        user_id = current_user.id
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task, attribute_names=['creator'])
    return new_task

@router.get("", response_model=list[TaskResponse])
async def get_tasks(
    current_user: CurrentUser, 
    db: Annotated[AsyncSession, Depends(get_db)], 
    completed: bool | None = None,
    category: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 10
    ):

    query = (
        select(models.Task)
        .options(selectinload(models.Task.creator))
        .where(models.Task.user_id == current_user.id)
    )

    if completed is not None:
        query = query.where(models.Task.completed == completed)

    if category is not None:
        query = query.where(func.lower(models.Task.category) == category.lower())

    if search:
        query = query.where(
            or_(
                models.Task.title.ilike(f"%{search}%"),
                models.Task.description.ilike(f"%{search}%"),
                models.Task.category.ilike(f"%{search}%")
            )
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int,current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Task).options(selectinload(models.Task.creator)).where(models.Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task."
        )
    
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task_full(task_id: int, update_task: TaskCreate,current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]): 
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task."
        )
    
    task.title = update_task.title
    task.description = update_task.description
    task.completed = update_task.completed
    task.priority = update_task.priority
    task.due_date = update_task.due_date
    task.category = update_task.category
    task.user_id = current_user.id

    await db.commit()
    await db.refresh(task, attribute_names=["creator"])
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task_partial(task_id: int, update_task: TaskUpdate,current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Task).options(selectinload(models.Task.creator)).where(models.Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task."
        )
    
    update_data = update_task.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int,current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task."
        )
    await db.delete(task)
    await db.commit()