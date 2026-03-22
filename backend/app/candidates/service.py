from fastapi import UploadFile
from app.dependencies import supabase_admin
from app.candidates.schemas import CandidateProfileUpdate


def get_candidate_profile(user_id: str) -> dict:
    """Fetch combined profile + candidate_details for a user."""
    profile = supabase_admin.table("profiles").select("*").eq(
        "id", user_id
    ).single().execute()

    details = supabase_admin.table("candidate_details").select("*").eq(
        "id", user_id
    ).single().execute()

    merged = {**profile.data, **details.data}
    # Check if profile is complete (has at least skills and career_goal)
    merged["profile_complete"] = bool(
        merged.get("skills") and len(merged["skills"]) > 0
        and merged.get("career_goal")
    )
    return merged


def update_candidate_profile(user_id: str, data: CandidateProfileUpdate) -> dict:
    """Update candidate profile and details."""
    update_data = data.model_dump(exclude_none=True)

    # Fields that go into profiles table
    profile_fields = {"full_name", "avatar_url"}
    profile_update = {k: v for k, v in update_data.items() if k in profile_fields}
    if profile_update:
        supabase_admin.table("profiles").update(profile_update).eq(
            "id", user_id
        ).execute()

    # Fields that go into candidate_details table
    detail_fields = {"skills", "experience_years", "education", "current_position", "career_goal", "preferred_companies"}
    detail_update = {k: v for k, v in update_data.items() if k in detail_fields}
    if detail_update:
        supabase_admin.table("candidate_details").update(detail_update).eq(
            "id", user_id
        ).execute()

    return get_candidate_profile(user_id)


async def upload_resume(user_id: str, file: UploadFile) -> dict:
    """Process uploaded resume: extract text, parse with NLP, compute scores."""
    from app.resume.parser import extract_text_from_pdf
    from app.resume.analyzer import analyze_resume
    from app.resume.ats_checker import check_ats_compatibility

    # Read file bytes
    content = await file.read()

    # 1. Extract raw text from PDF
    raw_text = extract_text_from_pdf(content)

    if not raw_text.strip():
        raise Exception("Could not extract any text from the PDF. Make sure it's not a scanned image.")

    # 2. NLP analysis — extract skills, education, experience
    analysis = analyze_resume(raw_text)

    # 3. ATS compatibility check
    ats_result = check_ats_compatibility(raw_text)

    # 4. Store results in resumes table
    resume_data = {
        "candidate_id": user_id,
        "raw_text": raw_text,
        "parsed_skills": analysis["skills"],
        "parsed_education": analysis["education"],
        "parsed_experience": analysis["experience"],
        "ats_score": ats_result["score"],
        "ai_detection_score": ats_result["ai_detection_score"],
        "suggestions": ats_result["suggestions"],
    }

    supabase_admin.table("resumes").insert(resume_data).execute()

    # 5. Also update candidate_details with extracted skills
    supabase_admin.table("candidate_details").update({
        "skills": analysis["skills"],
    }).eq("id", user_id).execute()

    return {
        "message": "Resume uploaded and analyzed successfully",
        "analysis": analysis,
        "ats": ats_result,
    }
