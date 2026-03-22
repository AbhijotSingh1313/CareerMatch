from app.dependencies import supabase_admin
from app.ai_service import ask_gemini_json
import traceback

# Role → expected skills mapping (expanded)
ROLE_SKILL_MAP = {
    "frontend developer": ["html", "css", "javascript", "react", "typescript", "git", "figma", "responsive design"],
    "backend developer": ["python", "sql", "postgresql", "rest api", "docker", "git", "linux", "node.js"],
    "full stack developer": [
        "html", "css", "javascript", "react", "python", "sql",
        "postgresql", "docker", "git", "rest api", "node.js",
    ],
    "web developer": ["html", "css", "javascript", "react", "git", "rest api", "node.js"],
    "data scientist": [
        "python", "pandas", "numpy", "scikit-learn", "machine learning",
        "data analysis", "sql", "tableau", "statistics",
    ],
    "data analyst": ["python", "sql", "excel", "power bi", "tableau", "data analysis", "pandas", "statistics"],
    "data engineer": ["python", "sql", "spark", "aws", "docker", "airflow", "postgresql", "etl"],
    "machine learning engineer": [
        "python", "tensorflow", "pytorch", "scikit-learn", "machine learning",
        "deep learning", "docker", "sql", "mlops",
    ],
    "ai engineer": [
        "python", "machine learning", "deep learning", "tensorflow", "pytorch",
        "nlp", "computer vision", "docker", "sql",
    ],
    "devops engineer": ["docker", "kubernetes", "linux", "aws", "ci/cd", "git", "python", "terraform"],
    "cloud engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "linux", "terraform", "ci/cd"],
    "mobile developer": ["flutter", "dart", "kotlin", "swift", "git", "firebase", "rest api"],
    "android developer": ["kotlin", "java", "android", "git", "firebase", "rest api"],
    "ios developer": ["swift", "xcode", "git", "firebase", "rest api", "ui/ux"],
    "ui/ux designer": ["figma", "photoshop", "html", "css", "ui/ux", "adobe xd"],
    "software engineer": [
        "python", "java", "javascript", "sql", "git", "docker", "rest api", "data structures",
    ],
    "cybersecurity analyst": ["linux", "python", "networking", "sql", "wireshark", "penetration testing"],
    "project manager": ["agile", "scrum", "project management", "communication", "leadership", "excel"],
    "product manager": ["agile", "data analysis", "communication", "sql", "figma", "project management"],
    "qa engineer": ["python", "selenium", "git", "sql", "testing", "ci/cd", "agile"],
    "embedded systems": ["c++", "c", "linux", "python", "rtos", "electronics"],
    "game developer": ["c++", "c#", "unity", "unreal engine", "git", "3d modeling"],
    "blockchain developer": ["solidity", "javascript", "python", "git", "web3", "smart contracts"],
}

ROLE_KEYWORDS = {
    "frontend": "frontend developer", "front-end": "frontend developer",
    "front end": "frontend developer", "react": "frontend developer",
    "backend": "backend developer", "back-end": "backend developer",
    "back end": "backend developer", "node": "backend developer",
    "full stack": "full stack developer", "fullstack": "full stack developer",
    "full-stack": "full stack developer",
    "web dev": "web developer", "web developer": "web developer",
    "data scien": "data scientist", "data analyst": "data analyst",
    "data analy": "data analyst", "data engineer": "data engineer",
    "machine learning": "machine learning engineer", "ml engineer": "machine learning engineer",
    "ai engineer": "ai engineer", "artificial intelligence": "ai engineer",
    "devops": "devops engineer", "cloud": "cloud engineer",
    "mobile": "mobile developer", "android": "android developer",
    "ios": "ios developer", "flutter": "mobile developer",
    "ui/ux": "ui/ux designer", "ux": "ui/ux designer",
    "software": "software engineer", "sde": "software engineer", "swe": "software engineer",
    "cyber": "cybersecurity analyst", "security": "cybersecurity analyst",
    "project manag": "project manager", "product manag": "product manager",
    "qa": "qa engineer", "test": "qa engineer",
    "game": "game developer", "blockchain": "blockchain developer",
    "embedded": "embedded systems",
}


def _normalize(skill: str) -> str:
    return skill.lower().strip()


def _match_role(text: str) -> str | None:
    text_lower = text.lower()
    for role_name in ROLE_SKILL_MAP:
        if role_name in text_lower or text_lower in role_name:
            return role_name
    for keyword, role in ROLE_KEYWORDS.items():
        if keyword in text_lower:
            return role
    return None


def _ai_skill_analysis(candidate_skills: list, target_role: str, experience: list, career_goal: str) -> dict | None:
    """Use Gemini AI to generate detailed skill analysis with proficiency and real job comparisons."""
    skills_str = ", ".join(candidate_skills) if candidate_skills else "none listed"
    exp_str = ", ".join(experience) if experience else "no experience listed"

    prompt = f"""You are an expert career advisor and technical recruiter. Analyze this candidate's skills.

Candidate Skills: {skills_str}
Experience: {exp_str}
Target Role: {target_role}
Career Goal: {career_goal}

Return a JSON object with this EXACT structure:
{{
  "skill_breakdown": [
    {{
      "name": "JavaScript",
      "level": "advanced",
      "years": 3,
      "score": 85
    }}
  ],
  "radar_skills": [
    {{
      "skill": "JavaScript",
      "your_level": 85,
      "required_level": 90
    }}
  ],
  "job_comparisons": [
    {{
      "position": "Senior Software Engineer at Google",
      "strengths": ["JavaScript", "React"],
      "missing": ["System Design", "Distributed Systems"]
    }},
    {{
      "position": "Frontend Lead at Meta",
      "strengths": ["React", "CSS"],
      "missing": ["TypeScript"]
    }}
  ]
}}

Rules:
- skill_breakdown: List up to 10 most relevant candidate skills with estimated proficiency level (beginner/intermediate/advanced), estimated years of experience (1-5), and a score out of 100.
- radar_skills: Pick 5-6 most relevant skills for the target role. Show candidate level vs required level (0-100). Include skills the candidate doesn't have yet (their level would be 0).
- job_comparisons: List 5 REAL companies and positions matching the target role (like "Senior Software Engineer at Google", "ML Engineer at Amazon", etc.). For each, show which candidate skills are strengths and which key skills are missing.
- Be realistic with all scores based on the candidate's listed skills and experience."""

    try:
        result = ask_gemini_json(prompt)
        if isinstance(result, dict) and "skill_breakdown" in result:
            return result
    except Exception as e:
        print(f"AI skill analysis error: {e}")
        traceback.print_exc()
    return None


def _fallback_skill_breakdown(candidate_skills: list) -> list:
    """Generate basic skill breakdown without AI."""
    breakdown = []
    for i, skill in enumerate(candidate_skills):
        breakdown.append({
            "name": skill.title(),
            "level": "intermediate",
            "years": 2,
            "score": 60 + (i * 3) % 30,
        })
    return breakdown


def _fallback_radar(candidate_skills: set, required_skills: set) -> list:
    """Generate radar chart data without AI."""
    all_skills = list(required_skills)[:6]
    radar = []
    for skill in all_skills:
        radar.append({
            "skill": skill.title(),
            "your_level": 75 if skill in candidate_skills else 0,
            "required_level": 80,
        })
    return radar


def _fallback_comparisons(target_role: str, candidate_skills: set, required_skills: set) -> list:
    """Generate basic job comparisons without AI."""
    companies = [
        ("Google", "Senior"), ("Amazon", ""), ("Microsoft", ""),
        ("Meta", "Senior"), ("Apple", "")
    ]
    strong = sorted(list(candidate_skills & required_skills))
    missing = sorted(list(required_skills - candidate_skills))
    result = []
    for company, prefix in companies:
        role_title = target_role.title()
        position = f"{prefix + ' ' if prefix else ''}{role_title} at {company}"
        result.append({
            "position": position,
            "strengths": strong[:4],
            "missing": missing[:3] if missing else ["Advanced Patterns"],
        })
    return result


def analyze_skill_gaps(candidate_id: str, target_role: str = "") -> dict:
    """Compute skill gaps with AI-powered analysis."""
    details = supabase_admin.table("candidate_details").select("*").eq(
        "id", candidate_id
    ).single().execute()
    candidate = details.data

    profile = supabase_admin.table("profiles").select("*").eq(
        "id", candidate_id
    ).single().execute()

    raw_skills = candidate.get("skills") or []
    candidate_skills = {_normalize(s) for s in raw_skills}
    career_goal = candidate.get("career_goal") or ""
    current_position = candidate.get("current_position") or ""
    experience = candidate.get("experience") or []

    role_text = target_role.strip() if target_role.strip() else career_goal
    if not role_text:
        role_text = current_position

    matched_role = _match_role(role_text) if role_text else None

    required_skills = set()
    if matched_role and matched_role in ROLE_SKILL_MAP:
        required_skills = {_normalize(s) for s in ROLE_SKILL_MAP[matched_role]}

    if not required_skills:
        matched_role = "software engineer"
        required_skills = {_normalize(s) for s in ROLE_SKILL_MAP["software engineer"]}

    missing = required_skills - candidate_skills
    strong = candidate_skills & required_skills
    extra = candidate_skills - required_skills
    readiness = round(len(strong) / len(required_skills) * 100, 1) if required_skills else 0

    # Try AI-powered analysis
    ai_data = _ai_skill_analysis(raw_skills, matched_role or "software engineer", experience, career_goal)

    if ai_data:
        skill_breakdown = ai_data.get("skill_breakdown", [])
        radar_skills = ai_data.get("radar_skills", [])
        job_comparisons = ai_data.get("job_comparisons", [])
    else:
        skill_breakdown = _fallback_skill_breakdown(raw_skills)
        radar_skills = _fallback_radar(candidate_skills, required_skills)
        job_comparisons = _fallback_comparisons(matched_role or "software engineer", candidate_skills, required_skills)

    return {
        "target_role": matched_role or "software engineer",
        "candidate_position": current_position,
        "career_goal": career_goal,
        "missing_skills": sorted(list(missing)),
        "strong_skills": sorted(list(strong)),
        "extra_skills": sorted(list(extra)),
        "readiness_percent": readiness,
        "skill_breakdown": skill_breakdown,
        "radar_skills": radar_skills,
        "job_comparisons": job_comparisons,
    }
