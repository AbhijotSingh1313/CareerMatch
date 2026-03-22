import spacy
import re
from app.ai_service import ask_gemini_json

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Fallback skills list (used if AI fails)
KNOWN_SKILLS = {
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node.js", "nodejs", "express", "fastapi", "django", "flask", "spring",
    "sql", "postgresql", "mysql", "mongodb", "redis", "docker", "kubernetes",
    "aws", "azure", "gcp", "git", "linux", "html", "css", "sass",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data science", "power bi", "tableau",
    "rest api", "graphql", "microservices", "ci/cd", "agile", "scrum",
    "figma", "photoshop", "ui/ux", "swift", "kotlin", "flutter", "dart",
    "rust", "go", "golang", "c++", "c#", ".net", "ruby", "php", "laravel",
    "next.js", "nuxt.js", "tailwind", "bootstrap", "firebase", "supabase",
    "excel", "word", "communication", "leadership", "project management",
}

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.tech", "m.tech", "b.sc", "m.sc",
    "bca", "mca", "b.e", "m.e", "mba", "diploma", "degree",
]


def _fallback_analyze(text: str) -> dict:
    """Fallback analysis using regex + keyword matching if AI fails."""
    text_lower = text.lower()

    found_skills = sorted({
        skill.title() if len(skill) > 3 else skill.upper()
        for skill in KNOWN_SKILLS if skill in text_lower
    })

    education_lines = [
        line.strip() for line in text.split("\n")
        if any(kw in line.lower() for kw in EDUCATION_KEYWORDS)
    ]

    experience_entries = []
    year_pattern = re.compile(r"(20\d{2})\s*[-–—]\s*(20\d{2}|present|current)", re.IGNORECASE)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        match = year_pattern.search(line)
        if match:
            start_year = int(match.group(1))
            end_raw = match.group(2).lower()
            end_year = 2026 if end_raw in ("present", "current") else int(end_raw)
            title_line = lines[i - 1].strip() if i > 0 and len(lines[i - 1].strip()) > 3 else line.strip()
            experience_entries.append({
                "title": title_line[:100], "years": end_year - start_year,
                "start": start_year, "end": end_raw,
            })

    return {
        "skills": found_skills,
        "education": "; ".join(education_lines) if education_lines else "Not detected",
        "experience": experience_entries,
    }


def analyze_resume(text: str) -> dict:
    """
    Analyze resume text using Gemini AI.
    Falls back to regex/keyword matching if AI is unavailable.
    """
    prompt = f"""Analyze the following resume text and extract structured information.

RESUME TEXT:
{text[:4000]}

Return a JSON object with exactly these keys:
{{
    "skills": ["list of technical and soft skills found"],
    "education": "education summary as a single string",
    "experience": [
        {{"title": "job title or role", "company": "company name", "years": number_of_years, "start": start_year, "end": "end_year or present"}}
    ],
    "summary": "A 2-3 sentence professional summary of this candidate"
}}

Be thorough — extract ALL skills mentioned including programming languages, frameworks, tools, soft skills, and domain expertise."""

    result = ask_gemini_json(prompt)

    if result and "skills" in result:
        return {
            "skills": result.get("skills", []),
            "education": result.get("education", "Not detected"),
            "experience": result.get("experience", []),
            "summary": result.get("summary", ""),
        }

    # Fallback to rule-based if AI fails
    return _fallback_analyze(text)
