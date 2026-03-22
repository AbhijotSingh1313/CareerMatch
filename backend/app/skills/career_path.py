from app.dependencies import supabase_admin
from app.ai_service import ask_gemini_json
import traceback


def generate_career_path(candidate_id: str) -> dict:
    """Generate a comprehensive career progress path using AI."""
    # Gather all candidate data
    details = supabase_admin.table("candidate_details").select("*").eq(
        "id", candidate_id
    ).single().execute()
    candidate = details.data

    profile = supabase_admin.table("profiles").select("*").eq(
        "id", candidate_id
    ).single().execute()

    # Get resume data
    resume_data = {}
    try:
        resume_result = supabase_admin.table("resumes").select("*").eq(
            "candidate_id", candidate_id
        ).order("created_at", desc=True).limit(1).execute()
        if resume_result.data:
            resume_data = resume_result.data[0]
    except Exception:
        pass

    # Get job applications
    applications = []
    try:
        app_result = supabase_admin.table("applications").select("*, jobs(title, company)").eq(
            "candidate_id", candidate_id
        ).execute()
        applications = app_result.data or []
    except Exception:
        pass

    skills = candidate.get("skills") or []
    career_goal = candidate.get("career_goal") or ""
    current_position = candidate.get("current_position") or ""
    experience = candidate.get("experience") or []
    education = candidate.get("education") or ""

    resume_skills = resume_data.get("parsed_skills", [])
    resume_education = resume_data.get("parsed_education", "")

    apps_summary = []
    for app in applications[:10]:
        job = app.get("jobs", {}) or {}
        apps_summary.append({
            "title": job.get("title", "Unknown"),
            "company": job.get("company", "Unknown"),
            "status": app.get("status", "pending"),
        })

    # Build AI prompt
    prompt = f"""You are an expert career advisor. Based on the candidate's complete profile, generate a detailed career progress path.

CANDIDATE DATA:
- Current Position: {current_position or "Not specified"}
- Career Goal: {career_goal or "Not specified"}
- Skills: {", ".join(skills) if skills else "None listed"}
- Resume Skills: {", ".join(resume_skills) if resume_skills else "None"}
- Education: {education or resume_education or "Not specified"}
- Experience: {experience if experience else "None listed"}
- Job Applications: {apps_summary if apps_summary else "None yet"}

Return a JSON object with this EXACT structure:
{{
    "overall_progress": 45,
    "current_stage": "Building Foundation",
    "career_goal": "{career_goal or "Software Engineer"}",
    "milestones": [
        {{
            "title": "Profile Setup",
            "status": "completed",
            "icon": "📋",
            "description": "Created profile and listed skills",
            "progress": 100
        }},
        {{
            "title": "Resume Optimization",
            "status": "completed",
            "icon": "📄",
            "description": "Uploaded and analyzed resume",
            "progress": 80
        }},
        {{
            "title": "Skill Development",
            "status": "in_progress",
            "icon": "🎯",
            "description": "Working on closing skill gaps",
            "progress": 60
        }},
        {{
            "title": "Job Applications",
            "status": "in_progress",
            "icon": "💼",
            "description": "Applied to relevant positions",
            "progress": 30
        }},
        {{
            "title": "Interview Ready",
            "status": "not_started",
            "icon": "🎤",
            "description": "Prepare for interviews",
            "progress": 0
        }},
        {{
            "title": "Career Goal Achieved",
            "status": "not_started",
            "icon": "🏆",
            "description": "Land target role",
            "progress": 0
        }}
    ],
    "next_steps": [
        "Step 1 to take next",
        "Step 2 to take next",
        "Step 3 to take next"
    ],
    "strengths": ["Strength 1", "Strength 2"],
    "areas_to_improve": ["Area 1", "Area 2"],
    "estimated_timeline": "3-6 months to reach goal",
    "career_insights": "A 2-3 sentence personalized insight about their career trajectory"
}}

Rules:
- overall_progress: 0-100 based on how close they are to their career goal
- milestones: 5-7 career milestones. Status can be "completed", "in_progress", or "not_started". Progress is 0-100.
- Base progress scores on ACTUAL data: profile completeness, resume quality, skills listed, jobs applied
- If they have no career goal, suggest one based on their skills
- Be realistic and specific with next_steps based on their actual profile
- estimated_timeline: realistic estimate to reach their career goal"""

    try:
        result = ask_gemini_json(prompt)
        if isinstance(result, dict) and "milestones" in result:
            return result
    except Exception as e:
        print(f"Career path AI error: {e}")
        traceback.print_exc()

    # Fallback
    return _fallback_career_path(candidate, resume_data, applications)


def _fallback_career_path(candidate: dict, resume_data: dict, applications: list) -> dict:
    """Generate basic career path without AI."""
    skills = candidate.get("skills") or []
    career_goal = candidate.get("career_goal") or "Software Engineer"
    has_resume = bool(resume_data.get("raw_text"))
    app_count = len(applications)

    profile_progress = 100 if skills and career_goal else (50 if skills else 20)
    resume_progress = 80 if has_resume else 0
    skill_progress = min(len(skills) * 10, 100) if skills else 0
    app_progress = min(app_count * 20, 100)

    overall = round((profile_progress + resume_progress + skill_progress + app_progress) / 4)

    milestones = [
        {"title": "Profile Setup", "status": "completed" if profile_progress >= 80 else "in_progress",
         "icon": "📋", "description": "Create profile and list your skills", "progress": profile_progress},
        {"title": "Resume Optimization", "status": "completed" if has_resume else "not_started",
         "icon": "📄", "description": "Upload and optimize your resume", "progress": resume_progress},
        {"title": "Skill Development", "status": "in_progress" if skills else "not_started",
         "icon": "🎯", "description": "Build skills matching your target role", "progress": skill_progress},
        {"title": "Job Applications", "status": "in_progress" if app_count > 0 else "not_started",
         "icon": "💼", "description": f"Applied to {app_count} positions", "progress": app_progress},
        {"title": "Interview Ready", "status": "not_started",
         "icon": "🎤", "description": "Prepare for technical interviews", "progress": 0},
        {"title": f"Become {career_goal}", "status": "not_started",
         "icon": "🏆", "description": f"Land your dream role as {career_goal}", "progress": 0},
    ]

    return {
        "overall_progress": overall,
        "current_stage": "Building Foundation" if overall < 40 else "Growing" if overall < 70 else "Almost There",
        "career_goal": career_goal,
        "milestones": milestones,
        "next_steps": [
            "Complete your skill analysis to identify gaps",
            "Apply to more positions matching your profile",
            "Take recommended courses to close skill gaps",
        ],
        "strengths": [s.title() for s in skills[:3]] if skills else ["Getting Started"],
        "areas_to_improve": ["Add more skills", "Upload resume"] if not has_resume else ["Apply to more jobs"],
        "estimated_timeline": "3-6 months",
        "career_insights": f"You're making progress toward becoming a {career_goal}. Keep building your skills and applying to relevant positions.",
    }
