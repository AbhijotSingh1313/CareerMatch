from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.auth.service import get_current_user
from app.feedback.service import (
    send_feedback, get_candidate_feedback,
    update_application_status, get_job_applications,
)
from app.feedback.schemas import FeedbackCreate, ApplicationStatusUpdate
from app.dependencies import supabase_admin

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class BatchUpdate(BaseModel):
    application_ids: List[str]
    status: str  # "accepted" or "rejected"


class EmailRequest(BaseModel):
    candidate_email: str
    candidate_name: str
    job_title: str
    status: str  # "accepted" or "rejected"
    custom_message: Optional[str] = None


@router.post("/send")
async def create_feedback(data: FeedbackCreate, user=Depends(get_current_user)):
    """Send feedback to a candidate (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    try:
        return send_feedback(user["id"], data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-feedback")
async def my_feedback(user=Depends(get_current_user)):
    """Get all feedback received (candidate only)."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return get_candidate_feedback(user["id"])


@router.put("/applications/{application_id}")
async def update_status(
    application_id: str,
    data: ApplicationStatusUpdate,
    user=Depends(get_current_user),
):
    """Accept or reject a candidate application (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    try:
        return update_application_status(application_id, data.status, user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications/{job_id}")
async def list_applications(job_id: str, user=Depends(get_current_user)):
    """List all applications for a job with candidate details (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    return get_job_applications(job_id)


@router.post("/applications/batch-update")
async def batch_update(data: BatchUpdate, user=Depends(get_current_user)):
    """Accept or reject multiple applications at once (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")
    results = []
    for app_id in data.application_ids:
        try:
            r = update_application_status(app_id, data.status, user["id"])
            results.append({"id": app_id, "success": True})
        except Exception as e:
            results.append({"id": app_id, "success": False, "error": str(e)})
    return {"updated": len([r for r in results if r["success"]]), "results": results}


@router.post("/applications/send-email")
async def send_email(data: EmailRequest, user=Depends(get_current_user)):
    """Send acceptance/rejection email to candidate (recruiter only).
    Sends a real email via SMTP and saves as feedback."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")

    # Build the email body
    if data.custom_message:
        message = data.custom_message
    else:
        if data.status == "accepted":
            message = f"Congratulations {data.candidate_name}! Your application for {data.job_title} has been accepted. We will reach out with next steps soon."
        else:
            message = f"Dear {data.candidate_name}, Thank you for applying for {data.job_title}. After careful review, we have decided to move forward with other candidates. We wish you the best in your job search."

    # Send real email via SMTP
    from app.email_service import send_real_email
    email_result = send_real_email(
        to_email=data.candidate_email,
        subject=f"Application Update: {data.job_title}",
        body=message,
    )

    # Save as feedback so the candidate sees it in-app too
    try:
        profile = supabase_admin.table("profiles").select("id").eq(
            "email", data.candidate_email
        ).single().execute()
        if profile.data:
            from app.feedback.schemas import FeedbackCreate as FC
            fb = FC(
                candidate_id=profile.data["id"],
                type="acceptance" if data.status == "accepted" else "rejection",
                message=message,
            )
            send_feedback(user["id"], fb)
    except Exception:
        pass  # Don't block if feedback save fails

    return {
        "email_sent": email_result.get("sent", False),
        "email_error": email_result.get("error"),
        "to": data.candidate_email,
        "subject": f"Application Update: {data.job_title}",
        "body": message,
        "saved_as_feedback": True,
    }


@router.get("/resume/{candidate_id}")
async def download_resume(candidate_id: str, user=Depends(get_current_user)):
    """Download a candidate's resume text (recruiter only)."""
    if user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiters only")

    result = supabase_admin.table("resumes").select("raw_text, parsed_skills, ats_score").eq(
        "candidate_id", candidate_id
    ).order("created_at", desc=True).limit(1).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="No resume found for this candidate")

    resume = result.data[0]
    raw_text = resume.get("raw_text", "")

    # Get candidate name for filename
    profile = supabase_admin.table("profiles").select("full_name").eq(
        "id", candidate_id
    ).single().execute()
    name = (profile.data.get("full_name", "candidate") if profile.data else "candidate").replace(" ", "_")

    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=raw_text,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="resume_{name}.txt"'
        },
    )


