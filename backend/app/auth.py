# backend/app/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginData(BaseModel):
    username: str
    password: str

# Replace these with a real password hasher (e.g., passlib/bcrypt)
def verify_password(plain: str, hashed_or_plain: str) -> bool:
    # TODO: return pwd_context.verify(plain, hashed_or_plain)
    return plain == hashed_or_plain

@router.post("/login")
async def login(data: LoginData, db: AsyncSession = Depends(get_db)):
    # Look up the user by username
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    # Fail fast if no user or password mismatch
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Success: return a minimal, safe payload (no password)
    # Later, issue a real JWT access_token here.
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }
