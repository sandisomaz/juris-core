from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.core.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_role: str = "Legal Counsel"

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    if req.username and req.password:
        token = create_access_token({"sub": req.username, "role": "Senior Compliance Counsel"})
        return TokenResponse(access_token=token, user_role="Senior Compliance Counsel")
    raise HTTPException(status_code=401, detail="Invalid credentials")
