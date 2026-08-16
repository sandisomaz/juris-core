import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.security import hash_password, verify_password, create_access_token, get_current_user
from src.storage.db import get_db
from src.storage.models import UserDB

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = ""
    role: Optional[str] = "Legal Counsel"


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    user_role: str


class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if username or email exists
    stmt = select(UserDB).where((UserDB.username == req.username) | (UserDB.email == req.email))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    user_id = str(uuid.uuid4())
    new_user = UserDB(
        id=user_id,
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name or req.username,
        role=req.role or "Legal Counsel"
    )
    db.add(new_user)
    await db.commit()

    token = create_access_token({"sub": new_user.username, "role": new_user.role, "user_id": user_id})
    return TokenResponse(
        access_token=token,
        username=new_user.username,
        user_role=new_user.role
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(UserDB).where(UserDB.username == req.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        # Fallback for dev convenience if using default counsel credentials
        if req.username == "counsel" and (req.password == "generate_a_secure_random_key_min_32_chars" or req.password == "counsel"):
            token = create_access_token({"sub": "counsel", "role": "Senior Compliance Counsel"})
            return TokenResponse(access_token=token, username="counsel", user_role="Senior Compliance Counsel")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token({"sub": user.username, "role": user.role, "user_id": user.id})
    return TokenResponse(
        access_token=token,
        username=user.username,
        user_role=user.role
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    username = current_user.get("sub", "counsel")
    stmt = select(UserDB).where(UserDB.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return UserProfileResponse(
            id="usr-counsel-01",
            username=username,
            email="counsel@juriscore.io",
            full_name="Senior Compliance Counsel",
            role=current_user.get("role", "Legal Counsel"),
            is_active=True
        )

    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active
    )
