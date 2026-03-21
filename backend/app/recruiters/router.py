from fastapi import APIRouter, Depends, HTTPException
from app.auth.service import get_current_user
from app.recruiters.service import get_recruiter_profile, update_recruiter_profile
from app.recruiters.schemas import RecruiterProfileResponse, RecruiterProfileUpdate

router = APIRouter(prefix="/recruiters", tags=["Recruiters"])


@router.get("/profile", response_model=RecruiterProfileResponse)
async def get_profile(user=Depends(get_current_user)):
    """Get the current recruiter's full profile."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    return get_recruiter_profile(user["id"])


@router.put("/profile", response_model=RecruiterProfileResponse)
async def update_profile(data: RecruiterProfileUpdate, user=Depends(get_current_user)):
    """Update recruiter profile details (company, industry, etc.)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    return update_recruiter_profile(user["id"], data)
