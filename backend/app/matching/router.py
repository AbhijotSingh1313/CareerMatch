from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.auth.service import get_current_user
from app.matching.engine import (
    get_job_matches_for_candidate,
    get_candidate_matches_for_job,
    ai_compare_candidates,
    ai_shortlist_candidates,
)

router = APIRouter(prefix="/matching", tags=["Matching"])


@router.get("/jobs")
async def matched_jobs(user=Depends(get_current_user)):
    """Get AI-powered job recommendations for the current candidate, ranked by match score."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return get_job_matches_for_candidate(user["id"])


@router.get("/candidates/{job_id}")
async def matched_candidates(job_id: str, user=Depends(get_current_user)):
    """Get ranked candidates for a specific job (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    return get_candidate_matches_for_job(job_id)


@router.post("/compare/{job_id}")
async def compare_candidates(job_id: str, candidate_ids: List[str], user=Depends(get_current_user)):
    """AI-powered comparison of selected candidates for a job (recruiter only).
    Send a list of candidate IDs to get a detailed AI analysis and ranking."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    return ai_compare_candidates(job_id, candidate_ids)


@router.get("/shortlist/{job_id}")
async def shortlist(job_id: str, max_candidates: int = 5, user=Depends(get_current_user)):
    """AI-powered automatic shortlisting of top candidates for a job (recruiter only).
    Reviews all applicants and recommends the best fits."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    return ai_shortlist_candidates(job_id, max_candidates)
