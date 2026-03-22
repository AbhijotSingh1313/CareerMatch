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
