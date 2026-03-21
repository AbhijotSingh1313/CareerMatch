from pydantic import BaseModel
from typing import Optional, List


class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[str] = None
    career_goal: Optional[str] = None
    preferred_companies: Optional[List[str]] = None


class CandidateProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[str] = None
    career_goal: Optional[str] = None
    preferred_companies: Optional[List[str]] = None
