from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])

class AuthRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    user_id: int | None = None
    message: str


@router.post("/signup", response_model=AuthResponse)
def signup(body: AuthRequest):
    user = create_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email already exists")

    return AuthResponse(success=True, user_id=user["id"], message="Account created")


@router.post("/login", response_model=AuthResponse)
def login(body: AuthRequest):
    user = authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return AuthResponse(success=True, user_id=user["id"], message="Login successful")
