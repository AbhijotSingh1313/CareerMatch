from fastapi import APIRouter, Depends, HTTPException
from app.auth.service import get_current_user
from app.jobs.service import (
    create_job, get_recruiter_jobs, get_job, update_job,
    delete_job, update_job_status, get_all_open_jobs, apply_to_job,
    save_job, unsave_job, get_saved_jobs,
)
from app.jobs.schemas import JobCreate, JobUpdate, JobResponse
from typing import List

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ─── Recruiter endpoints ───

@router.post("/", response_model=JobResponse)
async def create_job_posting(data: JobCreate, user=Depends(get_current_user)):
    """Create a new job posting (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    return create_job(user["id"], data)


@router.get("/my-jobs", response_model=List[JobResponse])
async def list_my_jobs(user=Depends(get_current_user)):
    """List all jobs created by the current recruiter."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    return get_recruiter_jobs(user["id"])


@router.put("/{job_id}", response_model=JobResponse)
async def edit_job(job_id: str, data: JobUpdate, user=Depends(get_current_user)):
    """Edit a job posting (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    try:
        return update_job(job_id, user["id"], data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{job_id}")
async def remove_job(job_id: str, user=Depends(get_current_user)):
    """Delete a job posting (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    delete_job(job_id, user["id"])
    return {"message": "Job deleted successfully"}


@router.put("/{job_id}/status")
async def change_status(job_id: str, status: str, user=Depends(get_current_user)):
    """Open, close, or pause a job posting (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    try:
        return update_job_status(job_id, user["id"], status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Public / Candidate endpoints ───

@router.get("/", response_model=List[JobResponse])
async def list_open_jobs():
    """List all open job postings (public — no auth needed)."""
    return get_all_open_jobs()


@router.get("/saved")
async def list_saved(user=Depends(get_current_user)):
    """Get list of saved/bookmarked job IDs."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return get_saved_jobs(user["id"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_single_job(job_id: str):
    """Get a single job posting details (public)."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/apply")
async def apply(job_id: str, user=Depends(get_current_user)):
    """Apply to a job (candidate only)."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    try:
        return apply_to_job(job_id, user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_id}/save")
async def bookmark_job(job_id: str, user=Depends(get_current_user)):
    """Save/bookmark a job (candidate only)."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return save_job(user["id"], job_id)


@router.delete("/{job_id}/save")
async def unbookmark_job(job_id: str, user=Depends(get_current_user)):
    """Remove bookmark (candidate only)."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return unsave_job(user["id"], job_id)
