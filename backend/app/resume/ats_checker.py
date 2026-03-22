import re
from app.ai_service import ask_gemini_json


def _count_action_verbs(text_lower):
    verbs = {"developed", "designed", "implemented", "managed", "led", "built", "created",
             "analyzed", "improved", "optimized", "deployed", "tested", "maintained",
             "coordinated", "delivered", "launched", "automated", "collaborated",
             "achieved", "reduced", "increased", "streamlined", "architected", "configured",
             "mentored", "organized", "researched", "resolved", "integrated", "facilitated"}
    return sum(1 for v in verbs if v in text_lower)


def _count_metrics(text):
    """Count quantifiable metrics (numbers, percentages, dollar amounts)."""
    patterns = [
        r"\d+%", r"\$[\d,]+", r"\d+\+?\s*(users|clients|customers|employees|team)",
        r"(increased|reduced|improved|grew|saved).{0,30}\d+",
    ]
    return sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)


def _fallback_ats_check(text: str, target_role: str = "") -> dict:
    """Detailed heuristic ATS check based on actual resume content."""
    suggestions = []
    score = 100
    text_lower = text.lower()
    words = text.split()
    lines = text.split("\n")
    word_count = len(words)

    if word_count < 100:
        score -= 20
        suggestions.append(f"Resume is very short ({word_count} words). Aim for 300-600 words for a strong resume.")
    elif word_count < 200:
        score -= 10
        suggestions.append(f"Resume has {word_count} words. Consider adding more detail to reach 300-600 words.")
    elif word_count > 1200:
        score -= 5
        suggestions.append(f"Resume is quite long ({word_count} words). Consider trimming to under 800 words.")

    has_email = bool(re.search(r"[\w.-]+@[\w.-]+\.\w+", text))
    has_phone = bool(re.search(r"[\+]?[\d\s\-().]{7,15}", text))
    has_linkedin = "linkedin" in text_lower
    if not has_email:
        score -= 10
        suggestions.append("No email address detected. Add a professional email at the top.")
    if not has_phone:
        score -= 5
        suggestions.append("No phone number detected. Include a contact number.")
    if not has_linkedin:
        suggestions.append("Consider adding your LinkedIn profile URL.")

    section_map = {
        "experience": ["experience", "work history", "employment", "professional experience"],
        "education": ["education", "academic", "qualification", "degree"],
        "skills": ["skills", "technical skills", "competencies", "technologies"],
        "summary": ["summary", "objective", "profile", "about me", "professional summary"],
        "projects": ["projects", "portfolio", "personal projects"],
    }
    found_sections = {}
    for section, keywords in section_map.items():
        found_sections[section] = any(kw in text_lower for kw in keywords)

    missing_sections = [s for s, found in found_sections.items() if not found and s != "projects"]
    if missing_sections:
        score -= len(missing_sections) * 5
        suggestions.append(f"Missing sections: {', '.join(s.title() for s in missing_sections)}. ATS systems expect these.")

    verb_count = _count_action_verbs(text_lower)
    if verb_count < 3:
        score -= 10
        suggestions.append("Use more action verbs (developed, implemented, managed, optimized) to describe achievements.")
    elif verb_count < 6:
        score -= 5
        suggestions.append("Add more action verbs to strengthen your experience descriptions.")

    metric_count = _count_metrics(text)
    if metric_count == 0:
        score -= 10
        suggestions.append("Add quantifiable achievements (e.g., 'Reduced load time by 40%', 'Managed team of 8').")
    elif metric_count < 3:
        score -= 5
        suggestions.append("Consider adding more measurable results to your experience entries.")

    formatting_issues = []
    if any(len(line.strip()) > 150 for line in lines):
        formatting_issues.append("Some lines are very long — use bullet points for readability.")
    if text.count("\t") > 5:
        formatting_issues.append("Excessive tabs detected — ATS may misparse tabular layouts.")

    score = max(score, 0)
    if not suggestions:
        suggestions.append("Your resume looks well-structured!")

    return {
        "ats_score": score,
        "ai_detection_score": 0,
        "formatting_issues": formatting_issues,
        "keyword_analysis": {"strong_keywords": [], "missing_keywords": []},
        "suggestions": suggestions,
        "overall_assessment": f"ATS Score: {score}/100. {word_count} words, {verb_count} action verbs, {metric_count} quantified metrics.",
        "role_fit": {},
    }


def check_ats_compatibility(text: str, target_role: str = "") -> dict:
    """
    AI-powered ATS compatibility check with general + target-role analysis.
    """
    role_instruction = ""
    if target_role:
        role_instruction = f"""
Also analyze how well this resume fits the target role of "{target_role}".
Include a "role_fit" section in your response:
{{
    "role_fit": {{
        "target_role": "{target_role}",
        "fit_score": <number 0-100, how well this resume matches the target role>,
        "matching_keywords": ["keywords in the resume that match the target role"],
        "missing_keywords": ["important keywords for the target role that are missing"],
        "role_suggestions": ["2-3 specific suggestions to improve fit for this role"]
    }}
}}"""

    prompt = f"""You are an expert ATS (Applicant Tracking System) analyst and resume reviewer.

Analyze this resume text and evaluate it:

RESUME TEXT:
{text[:4000]}

Return a JSON object with exactly these keys:
{{
    "ats_score": <number 0-100, how ATS-compatible this resume is>,
    "ai_detection_score": <number 0-100, likelihood this resume was AI-generated. 0=definitely human, 100=definitely AI>,
    "formatting_issues": ["list of formatting problems that would confuse ATS parsers"],
    "keyword_analysis": {{
        "strong_keywords": ["keywords that are well-placed and relevant"],
        "missing_keywords": ["important keywords that should be added"]
    }},
    "suggestions": ["list of 5-6 specific, actionable improvement suggestions"],
    "overall_assessment": "A 2-3 sentence summary of the resume quality",
    "section_scores": {{
        "contact_info": <0-100>,
        "experience": <0-100>,
        "education": <0-100>,
        "skills": <0-100>,
        "formatting": <0-100>
    }}{', "role_fit": {{...}}' if target_role else ''}
}}
{role_instruction}

Be specific in your suggestions — give concrete, actionable advice based on what you see in the resume."""

    result = ask_gemini_json(prompt)

    if result and "ats_score" in result:
        return {
            "ats_score": result.get("ats_score", 50),
            "ai_detection_score": result.get("ai_detection_score", 0),
            "formatting_issues": result.get("formatting_issues", []),
            "keyword_analysis": result.get("keyword_analysis", {}),
            "suggestions": result.get("suggestions", []),
            "overall_assessment": result.get("overall_assessment", ""),
            "section_scores": result.get("section_scores", {}),
            "role_fit": result.get("role_fit", {}),
        }

    # Also handle old key name "score"
    if result and "score" in result:
        return {
            "ats_score": result.get("score", 50),
            "ai_detection_score": result.get("ai_detection_score", 0),
            "formatting_issues": result.get("formatting_issues", []),
            "keyword_analysis": result.get("keyword_analysis", {}),
            "suggestions": result.get("suggestions", []),
            "overall_assessment": result.get("overall_assessment", ""),
            "section_scores": result.get("section_scores", {}),
            "role_fit": result.get("role_fit", {}),
        }

    return _fallback_ats_check(text, target_role)
