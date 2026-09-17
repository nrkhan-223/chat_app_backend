"""
Authentication API endpoints.
Handles user registration, login, profile retrieval, and updates.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import get_session
from models import User
from schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserPublic,
    UserUpdate,
)
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    session: AsyncSession = Depends(get_session),
):
    """Create a new user account."""
    # Check if email already exists
    result = await session.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    # Create new user
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    session.add(new_user)
    await session.flush()
    await session.refresh(new_user)

    return UserPublic.model_validate(new_user)


@router.post("/token", response_model=TokenResponse)
async def login(
    data: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate user and return JWT token."""
    # Find user by email
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(user.id)

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserPublic)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get the current authenticated user's profile."""
    return UserPublic.model_validate(current_user)


@router.put("/profile", response_model=UserPublic)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update the current user's profile (bio, name, custom status, phone, avatar)."""
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    session.add(current_user)
    await session.flush()
    await session.refresh(current_user)

    return UserPublic.model_validate(current_user)
