from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    candidate_id: str
    job_id: str
    type: str = "general"  # "rejection", "selection", "general"
    message: str


class ApplicationStatusUpdate(BaseModel):
    status: str  # "pending", "shortlisted", "accepted", "rejected"
