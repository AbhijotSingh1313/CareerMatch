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


def save_job(candidate_id: str, job_id: str) -> dict:
    """Bookmark a job for later."""
    existing = supabase_admin.table("saved_jobs").select("id").eq(
        "candidate_id", candidate_id
    ).eq("job_id", job_id).execute()
    if existing.data:
        return {"message": "Already saved"}
    supabase_admin.table("saved_jobs").insert({
        "candidate_id": candidate_id,
        "job_id": job_id,
    }).execute()
    return {"message": "Job saved"}


def unsave_job(candidate_id: str, job_id: str) -> dict:
    """Remove bookmark."""
    supabase_admin.table("saved_jobs").delete().eq(
        "candidate_id", candidate_id
    ).eq("job_id", job_id).execute()
    return {"message": "Job removed from saved"}


def get_saved_jobs(candidate_id: str) -> list:
    """Get list of saved job IDs."""
    result = supabase_admin.table("saved_jobs").select("job_id").eq(
        "candidate_id", candidate_id
    ).execute()
    return [row["job_id"] for row in result.data]
