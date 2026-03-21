import spacy
import re

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Common tech skills for matching (expandable)
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
    "elasticsearch", "kafka", "rabbitmq", "nginx", "apache",
    "excel", "word", "powerpoint", "communication", "leadership",
    "problem solving", "teamwork", "project management",
}

# Education keywords
EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.tech", "m.tech", "b.sc", "m.sc",
    "bca", "mca", "b.e", "m.e", "mba", "diploma", "certification",
    "b.s.", "m.s.", "associate", "degree",
]


def analyze_resume(text: str) -> dict:
    """
    Analyze resume text using spaCy NLP and pattern matching.
    Returns structured data: skills, education, experience.
    """
    text_lower = text.lower()
    doc = nlp(text)

    # ─── Extract Skills ───
    found_skills = []
    for skill in KNOWN_SKILLS:
        if skill in text_lower:
            found_skills.append(skill.title() if len(skill) > 3 else skill.upper())

    # Deduplicate
    found_skills = sorted(set(found_skills))

    # ─── Extract Education ───
    education_lines = []
    for line in text.split("\n"):
        line_lower = line.strip().lower()
        if any(kw in line_lower for kw in EDUCATION_KEYWORDS):
            education_lines.append(line.strip())

    education = "; ".join(education_lines) if education_lines else "Not detected"

    # ─── Extract Experience ───
    experience_entries = []
    # Pattern: look for year ranges like "2020 - 2023" or "2020 - Present"
    year_pattern = re.compile(
        r"(20\d{2})\s*[-–—]\s*(20\d{2}|present|current)",
        re.IGNORECASE,
    )
    lines = text.split("\n")
    for i, line in enumerate(lines):
        match = year_pattern.search(line)
        if match:
            start_year = int(match.group(1))
            end_raw = match.group(2).lower()
            end_year = 2026 if end_raw in ("present", "current") else int(end_raw)
            years = end_year - start_year

            # Try to grab the job title from the same or previous line
            title_line = line.strip()
            if i > 0 and len(lines[i - 1].strip()) > 3:
                title_line = lines[i - 1].strip()

            experience_entries.append({
                "title": title_line[:100],
                "years": years,
                "start": start_year,
                "end": end_raw,
            })

    return {
        "skills": found_skills,
        "education": education,
        "experience": experience_entries,
    }
