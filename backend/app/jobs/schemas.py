from pydantic import BaseModel
from typing import Optional, List


class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: List[str] = []
    experience_min: float = 0
    vacancies: int = 1
    ats_required: bool = False
    external_link: Optional[str] = None
    job_type: Optional[str] = None          # full-time, part-time, contract, internship, freelance
    work_mode: Optional[str] = None         # onsite, remote, hybrid
    location: Optional[str] = None
    salary_range: Optional[str] = None
    requirements: Optional[str] = None      # additional requirements text
    ats_threshold: int = 30                 # ATS score below which candidates are auto-rejected


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_min: Optional[float] = None
    vacancies: Optional[int] = None
    ats_required: Optional[bool] = None
    external_link: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    requirements: Optional[str] = None
    ats_threshold: Optional[int] = None


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
    external_link: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    requirements: Optional[str] = None
    ats_threshold: int = 30
    created_at: Optional[str] = None

