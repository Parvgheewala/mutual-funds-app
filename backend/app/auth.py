from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginData):
    if data.username == "admin" and data.password == "1234":
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
