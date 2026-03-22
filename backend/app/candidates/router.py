from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.auth.service import get_current_user
from app.candidates.service import (
    get_candidate_profile,
    update_candidate_profile,
    upload_resume,
)
from app.candidates.schemas import CandidateProfileResponse, CandidateProfileUpdate

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("/profile", response_model=CandidateProfileResponse)
async def get_profile(user=Depends(get_current_user)):
    """Get the current candidate's full profile."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return get_candidate_profile(user["id"])


@router.put("/profile", response_model=CandidateProfileResponse)
async def update_profile(data: CandidateProfileUpdate, user=Depends(get_current_user)):
    """Update candidate profile details (skills, career goal, etc.)."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    return update_candidate_profile(user["id"], data)


@router.post("/resume/upload")
async def upload_resume_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    """Upload a PDF resume for parsing and analysis."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    try:
        result = await upload_resume(user["id"], file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resume/analysis")
async def get_resume_analysis(user=Depends(get_current_user)):
    """Get the latest resume analysis results."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    from app.dependencies import supabase_admin
    result = supabase_admin.table("resumes").select("*").eq(
        "candidate_id", user["id"]
    ).order("created_at", desc=True).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="No resume analysis found. Upload a resume first.")
    return result.data[0]


@router.post("/resume/reanalyze")
async def reanalyze_saved_resume(target_role: str = "", user=Depends(get_current_user)):
    """Re-run ATS analysis on already-saved resume with optional target role."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    from app.dependencies import supabase_admin
    from app.resume.ats_checker import check_ats_compatibility

    result = supabase_admin.table("resumes").select("*").eq(
        "candidate_id", user["id"]
    ).order("created_at", desc=True).limit(1).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="No saved resume found. Upload one first.")

    resume_data = result.data[0]
    resume_text = resume_data.get("raw_text", "")
    if not resume_text:
        raise HTTPException(status_code=400, detail="Saved resume has no text content.")

    ats_result = check_ats_compatibility(resume_text, target_role)

    return {
        "analysis": {
            "skills": resume_data.get("parsed_skills", []),
            "education": resume_data.get("parsed_education", ""),
            "experience": resume_data.get("parsed_experience", []),
        },
        "ats": ats_result,
    }


@router.post("/chat")
async def chat_with_ai(body: dict, user=Depends(get_current_user)):
    """AI chatbot that has access to user's profile and resume data."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")

    message = body.get("message", "").strip()
    history = body.get("history", [])
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    from app.dependencies import supabase_admin
    from app.ai_service import ask_gemini

    # Fetch profile context
    profile = {}
    try:
        p = supabase_admin.table("profiles").select("*").eq("id", user["id"]).single().execute()
        d = supabase_admin.table("candidate_details").select("*").eq("id", user["id"]).single().execute()
        profile = {**p.data, **d.data}
    except Exception:
        pass

    # Fetch resume context
    resume_info = ""
    try:
        r = supabase_admin.table("resumes").select("*").eq(
            "candidate_id", user["id"]
        ).order("created_at", desc=True).limit(1).execute()
        if r.data:
            rd = r.data[0]
            resume_info = f"""
Resume skills: {', '.join(rd.get('parsed_skills', []))}
Education: {rd.get('parsed_education', 'N/A')}
ATS Score: {rd.get('ats_score', 'N/A')}/100
Suggestions: {'; '.join(rd.get('suggestions', [])[:3])}"""
    except Exception:
        pass

    # Build system context
    context = f"""You are CareerMatch AI, a friendly and knowledgeable career assistant.
You have access to this candidate's profile:
- Name: {profile.get('full_name', 'Unknown')}
- Skills: {', '.join(profile.get('skills', [])) or 'Not set'}
- Career Goal: {profile.get('career_goal', 'Not set')}
- Education: {profile.get('education', 'Not set')}
- Experience: {profile.get('experience_years', 0)} years
- Current Position: {profile.get('current_position', 'Not set')}
{resume_info}

Help the user with career advice, job search tips, interview prep, skill development, resume improvement, and any career-related questions. Be concise, friendly, and actionable. Keep responses under 200 words unless the user asks for detail."""

    # Build conversation with history
    conversation = f"SYSTEM: {context}\n\n"
    for msg in history[-6:]:  # Last 6 messages for context
        role = "USER" if msg.get("role") == "user" else "ASSISTANT"
        conversation += f"{role}: {msg.get('content', '')}\n"
    conversation += f"USER: {message}\nASSISTANT:"

    reply = ask_gemini(conversation)

    return {"reply": reply}

