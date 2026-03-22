import google.generativeai as genai
from app.config import GEMINI_API_KEY
import json
import re

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# JSON-specific model with forced JSON output
json_model = genai.GenerativeModel(
    "gemini-2.0-flash",
    generation_config={"response_mime_type": "application/json"},
)


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "AI response unavailable due to rate limits."

def get_fallback_json(prompt: str) -> dict | list | None:
    """Provides mock JSON data when the Gemini API fails."""
    prompt_lower = prompt.lower()
    
    # Career Path
    if "milestones" in prompt_lower and "career path" in prompt_lower:
        return {
            "current_stage": "Starting Out",
            "next_milestones": [
                {"title": "Learn Fundamentals", "description": "Master the basics of the field.", "status": "in_progress"},
                {"title": "Build Projects", "description": "Create a portfolio of work.", "status": "not_started"},
                {"title": "Apply for Jobs", "description": "Start interviewing.", "status": "not_started"}
            ],
            "estimated_timeline": "6-12 months"
        }
        
    # Gap Analyzer
    if "skill breakdown" in prompt_lower and ("beginner" in prompt_lower or "intermediate" in prompt_lower):
        return {
            "breakdown": [
                {"skill": "JavaScript", "level": "intermediate", "years_experience": 2},
                {"skill": "React", "level": "beginner", "years_experience": 1}
            ],
            "missing_skills": ["TypeScript", "Node.js"],
            "strengths": ["Quick learner", "Frontend basics"]
        }
        
    # Course Recommender
    if "course recommendations" in prompt_lower or "recommend 3-5 specific" in prompt_lower:
        return [
            {
                "title": "Complete 2024 Web Development Bootcamp",
                "provider": "Udemy",
                "difficulty": "Beginner",
                "is_free": False,
                "reason": "Covers all the fundamentals you are missing.",
                "link": "https://www.udemy.com/course/the-complete-web-development-bootcamp/"
            },
            {
                "title": "CS50's Web Programming",
                "provider": "Harvard (EdX)",
                "difficulty": "Intermediate",
                "is_free": True,
                "reason": "Great for learning deeper computer science concepts.",
                "link": "https://learning.edx.org/course/course-v1:HarvardX+CS50W+Web"
            }
        ]
        
    # ATS Checker
    if "ats score" in prompt_lower and "formatting" in prompt_lower:
        return {
            "score": 75,
            "overall_feedback": "Resume is decent but missing some key terms.",
            "formatting": {"score": 80, "feedback": "Good structure, but use more bullet points."},
            "impact": {"score": 70, "feedback": "Add more metrics to your achievements."},
            "keywords": {"score": 75, "feedback": "Missing a few critical skills from the job description."},
            "keywords_found": ["React", "JavaScript", "HTML"],
            "keywords_missing": ["TypeScript", "Redux", "AWS"],
            "actionable_suggestions": ["Rewrite bullet points to start with action verbs", "Include more technical keywords"]
        }
        
    # Resume Analyzer
    if "extract the following fields from the resume" in prompt_lower:
        return {
            "summary": "Experienced software engineer with a passion for building scalable web applications.",
            "skills": ["JavaScript", "Python", "React", "Node.js", "SQL"],
            "experience": [
                {"role": "Frontend Developer", "company": "Tech Corp", "duration": "2020 - Present", "description": "Built web apps."}
            ],
            "education": [
                {"degree": "B.S. Computer Science", "institution": "State University", "year": "2019"}
            ]
        }
        
    # Matching Engine - Insights list (compare multiple)
    if "compare these candidates" in prompt_lower or ("analyze how well" in prompt_lower and "scores from 0-100" in prompt_lower):
        # We need a list of match insights per candidate
        # The prompt usually contains candidate IDs
        # To make it safe, return a generic list
        return {
            "insights": "Candidates seem generally qualified based on a basic keyword match (AI rate limited)."
        }
        
    # Single Match Profile
    if "score from 0-100" in prompt_lower and "missing_skills" in prompt_lower:
        return {
            "score": 85,
            "reasoning": "Strong match based on core skills, but missing some advanced qualifications.",
            "matching_skills": ["Python", "React"],
            "missing_skills": ["AWS", "Docker"],
            "recommendation": "Shortlist"
        }
        
    # AI Compare (list of candidate evaluations)
    if "rank them" in prompt_lower and "reasoning" in prompt_lower:
        return [
            {
                "candidate_id": "fallback-id",
                "rank": 1,
                "score": 90,
                "reasoning": "Appears to be a strong fit (AI analysis limited).",
                "strengths": ["General experience"],
                "weaknesses": ["None specified"],
                "recommendation": "Hire"
            }
        ]
        
    # Default fallback
    return {"message": "AI analysis unavailable due to rate limits."}

def ask_gemini_json(prompt: str) -> dict | list | None:
    """Send a prompt to Gemini and parse the JSON response.
    Uses Gemini's native JSON mode for reliable structured output.
    Returns fallback mock data if the API limit is reached."""
    try:
        response = json_model.generate_content(prompt)
        text = response.text.strip()
        print(f"[Gemini JSON] Got {len(text)} chars response")
        return json.loads(text)
    except Exception as e:
        print(f"Gemini API error in ask_gemini_json: {e}")
        print("[Gemini] Returning fallback JSON data...")
        return get_fallback_json(prompt)

