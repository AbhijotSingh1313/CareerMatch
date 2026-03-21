from pydantic import BaseModel
from typing import Optional, List


class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: List[str] = []
    experience_min: float = 0
    vacancies: int = 1
    ats_required: bool = False


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_min: Optional[float] = None
    vacancies: Optional[int] = None
    ats_required: Optional[bool] = None


class JobResponse(BaseModel):
    id: str
    recruiter_id: str
    title: str
    description: Optional[str] = None
    required_skills: List[str] = []
    experience_min: float = 0
    vacancies: int = 1
    status: str = "open"
    ats_required: bool = False
    created_at: Optional[str] = None
