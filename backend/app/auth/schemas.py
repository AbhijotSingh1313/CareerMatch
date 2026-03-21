from pydantic import BaseModel, EmailStr
from typing import Optional


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # "candidate" or "recruiter"


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
