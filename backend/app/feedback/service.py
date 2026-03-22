from app.dependencies import supabase_admin
from app.feedback.schemas import FeedbackCreate


def send_feedback(recruiter_id: str, data: FeedbackCreate) -> dict:
    """Store feedback from recruiter to candidate."""
    feedback_data = {
        "candidate_id": data.candidate_id,
        "recruiter_id": recruiter_id,
        "job_id": data.job_id,
        "type": data.type,
        "message": data.message,
        "sent_via_email": False,
    }
    result = supabase_admin.table("feedback").insert(feedback_data).execute()
    return {"message": "Feedback sent", "feedback": result.data[0]}


def get_candidate_feedback(candidate_id: str) -> list:
    """Get all feedback for a candidate."""
    result = supabase_admin.table("feedback").select("*").eq(
        "candidate_id", candidate_id
    ).order("created_at", desc=True).execute()
    return result.data


def update_application_status(application_id: str, status: str, recruiter_id: str) -> dict:
    """Update application status (accept/reject/shortlist)."""
    if status not in ("pending", "shortlisted", "accepted", "rejected"):
        raise Exception("Invalid status. Must be: pending, shortlisted, accepted, or rejected")

    result = supabase_admin.table("job_applications").update(
        {"status": status}
    ).eq("id", application_id).execute()

    if not result.data:
        raise Exception("Application not found")

    application = result.data[0]

    # Auto-generate feedback on rejection
    if status == "rejected":
        send_feedback(recruiter_id, FeedbackCreate(
            candidate_id=application["candidate_id"],
            job_id=application["job_id"],
            type="rejection",
            message="Unfortunately, your application was not selected for this position. We encourage you to review your skill gaps and apply again in the future.",
        ))

    # Auto-generate feedback on acceptance
    if status == "accepted":
        send_feedback(recruiter_id, FeedbackCreate(
            candidate_id=application["candidate_id"],
            job_id=application["job_id"],
            type="selection",
            message="Congratulations! Your application has been selected. The recruiter will contact you soon with next steps.",
        ))

    return {"message": f"Application {status}", "application": application}


def get_job_applications(job_id: str) -> list:
    """Get all applications for a job with candidate info."""
    apps = supabase_admin.table("job_applications").select("*").eq(
        "job_id", job_id
    ).order("applied_at", desc=True).execute()

    results = []
    for app in apps.data:
        profile = supabase_admin.table("profiles").select("*").eq(
            "id", app["candidate_id"]
        ).single().execute()
        results.append({
            **app,
            "candidate_name": profile.data.get("full_name", "Unknown"),
            "candidate_email": profile.data.get("email", ""),
        })

    return results
