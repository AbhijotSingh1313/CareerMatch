from fastapi import APIRouter, Depends, HTTPException
from app.auth.service import get_current_user
from app.skills.gap_analyzer import analyze_skill_gaps
from app.skills.course_recommender import recommend_courses

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/gaps")
async def skill_gaps(target_role: str = "", user=Depends(get_current_user)):
    """Get skill gap analysis for the current candidate against a target role."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return analyze_skill_gaps(user["id"], target_role)


@router.get("/courses")
async def courses(user=Depends(get_current_user)):
    """Get course recommendations based on skill gaps."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return recommend_courses(user["id"])


@router.get("/career-path")
async def career_path(user=Depends(get_current_user)):
    """Generate AI-powered career progress path."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    from app.skills.career_path import generate_career_path
    return generate_career_path(user["id"])
