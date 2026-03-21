from app.dependencies import supabase_admin
from app.jobs.schemas import JobCreate, JobUpdate


def create_job(recruiter_id: str, data: JobCreate) -> dict:
    """Insert a new job posting."""
    job_data = data.model_dump()
    job_data["recruiter_id"] = recruiter_id
    result = supabase_admin.table("jobs").insert(job_data).execute()
    return result.data[0]


def get_recruiter_jobs(recruiter_id: str) -> list:
    """Get all jobs posted by a recruiter."""
    result = supabase_admin.table("jobs").select("*").eq(
        "recruiter_id", recruiter_id
    ).order("created_at", desc=True).execute()
    return result.data


def get_job(job_id: str) -> dict | None:
    """Get a single job by ID."""
    result = supabase_admin.table("jobs").select("*").eq("id", job_id).execute()
    return result.data[0] if result.data else None


def get_all_open_jobs() -> list:
    """Get all open jobs."""
    result = supabase_admin.table("jobs").select("*").eq(
        "status", "open"
    ).order("created_at", desc=True).execute()
    return result.data


def update_job(job_id: str, recruiter_id: str, data: JobUpdate) -> dict:
    """Update a job posting (owner only)."""
    update_data = data.model_dump(exclude_none=True)
    result = supabase_admin.table("jobs").update(update_data).eq(
        "id", job_id
    ).eq("recruiter_id", recruiter_id).execute()
    if not result.data:
        raise Exception("Job not found or not owned by you")
    return result.data[0]


def delete_job(job_id: str, recruiter_id: str):
    """Delete a job posting (owner only)."""
    supabase_admin.table("jobs").delete().eq(
        "id", job_id
    ).eq("recruiter_id", recruiter_id).execute()


def update_job_status(job_id: str, recruiter_id: str, status: str) -> dict:
    """Change job status (open/closed/paused)."""
    if status not in ("open", "closed", "paused"):
        raise Exception("Invalid status. Must be: open, closed, or paused")
    result = supabase_admin.table("jobs").update({"status": status}).eq(
        "id", job_id
    ).eq("recruiter_id", recruiter_id).execute()
    if not result.data:
        raise Exception("Job not found or not owned by you")
    return result.data[0]


def apply_to_job(job_id: str, candidate_id: str) -> dict:
    """Candidate applies to a job."""
    # Check if already applied
    existing = supabase_admin.table("job_applications").select("id").eq(
        "job_id", job_id
    ).eq("candidate_id", candidate_id).execute()
    if existing.data:
        raise Exception("You have already applied to this job")

    result = supabase_admin.table("job_applications").insert({
        "job_id": job_id,
        "candidate_id": candidate_id,
        "status": "pending",
    }).execute()
    return {"message": "Application submitted successfully", "application": result.data[0]}
