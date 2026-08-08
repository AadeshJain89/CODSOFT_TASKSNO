from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select , func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import UserCreate, UserPublic, UserPrivate, UserUpdate, TaskResponse, Token

from auth import hash_password, verify_password, create_access_token, CurrentUser
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(func.lower(models.User.username) == user.username.lower()))

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist")
    
    result = await db.execute(select(models.User).where(func.lower(models.User.email) == user.email.lower()))

    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist")
    
    new_user = models.User(
        username = user.username,
        email = user.email.lower(),
        password_hash = hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.User).where(func.lower(models.User.email) == form_data.username.lower()))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if verify_password(form_data.password, user.password_hash):
        data = {"sub":str(user.id)}
        token = create_access_token(data)
        return Token(
            access_token=token,
            token_type="bearer"
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"}
    ) 

@router.get("/me", response_model=UserPrivate)
async def get_me(user: CurrentUser):
    return user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(user_id: int, user_data: UserUpdate,current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you cannot update this profile"
        )
    
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    
    if user_data.username is not None and user_data.username != user.username:
        result = await db.execute(select(models.User).where(func.lower(models.User.username) == user_data.username.lower()))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    if user_data.email is not None and user_data.email != user.email:
        result = await db.execute(select(models.User).where(func.lower(models.User.email) == user_data.email.lower()))
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist")
    
    user_update = user_data.model_dump(exclude_unset=True)

    for field, value in user_update.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int,current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you cannot delete this user"
        )

    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await db.delete(user)
    await db.commit()


