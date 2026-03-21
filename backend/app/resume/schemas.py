from pydantic import BaseModel
from typing import Optional, List


class ResumeAnalysisResponse(BaseModel):
    id: str
    candidate_id: str
    parsed_skills: List[str] = []
    parsed_education: Optional[str] = None
    parsed_experience: Optional[list] = None
    ats_score: Optional[float] = None
    ai_detection_score: Optional[float] = None
    suggestions: Optional[list] = None
    created_at: Optional[str] = None
