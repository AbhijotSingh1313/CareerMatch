from pydantic import BaseModel
from typing import Optional


class RecruiterProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    industry: Optional[str] = None
    hiring_needs: Optional[str] = None


class RecruiterProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    industry: Optional[str] = None
    hiring_needs: Optional[str] = None
