import re


def check_ats_compatibility(text: str) -> dict:
    """
    Evaluate resume text for ATS compatibility and AI detection.
    Returns score (0-100), ai_detection_score, and actionable suggestions.
    """
    suggestions = []
    score = 100  # Start at 100, deduct for issues
    lines = text.split("\n")
    words = text.split()
    text_lower = text.lower()

    # ─── 1. Length check ───
    word_count = len(words)
    if word_count < 150:
        score -= 15
        suggestions.append("Resume is too short. Aim for at least 300-600 words.")
    elif word_count < 300:
        score -= 5
        suggestions.append("Resume could be more detailed. Add more context to your experience.")
    elif word_count > 1200:
        score -= 10
        suggestions.append("Resume is very long. Try to keep it concise (1-2 pages).")

    # ─── 2. Contact info ───
    has_email = bool(re.search(r"[\w.-]+@[\w.-]+\.\w+", text))
    has_phone = bool(re.search(r"[\+]?[\d\s\-().]{7,15}", text))

    if not has_email:
        score -= 10
        suggestions.append("No email address detected. Include your email for ATS parsing.")
    if not has_phone:
        score -= 5
        suggestions.append("No phone number detected. Include a contact number.")

    # ─── 3. Section headers ───
    expected_sections = ["experience", "education", "skills", "projects", "summary"]
    found_sections = 0
    for section in expected_sections:
        if section in text_lower:
            found_sections += 1

    if found_sections < 3:
        score -= 15
        suggestions.append(
            f"Only {found_sections}/5 key sections detected. "
            "Include: Experience, Education, Skills, Projects, Summary."
        )
    elif found_sections < 4:
        score -= 5
        suggestions.append("Consider adding more clearly labeled sections for better ATS parsing.")

    # ─── 4. Bullet points / structure ───
    bullet_lines = sum(1 for line in lines if line.strip().startswith(("•", "-", "●", "▪", "*")))
    if bullet_lines < 3:
        score -= 10
        suggestions.append("Use bullet points to describe experience. ATS systems parse them better.")

    # ─── 5. Action verbs ───
    action_verbs = [
        "developed", "managed", "designed", "implemented", "led",
        "built", "created", "optimized", "analyzed", "collaborated",
        "deployed", "maintained", "architected", "reduced", "increased",
    ]
    verbs_found = sum(1 for v in action_verbs if v in text_lower)
    if verbs_found < 2:
        score -= 10
        suggestions.append("Use action verbs (e.g., 'Developed', 'Led', 'Designed') to describe achievements.")

    # ─── 6. Quantified achievements ───
    has_numbers = bool(re.search(r"\d+%|\d+\+|\$\d+|\d+ (users|customers|projects)", text_lower))
    if not has_numbers:
        score -= 5
        suggestions.append("Add quantified achievements (e.g., 'Increased efficiency by 30%').")

    # ─── AI Detection heuristic ───
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    ai_score = 0  # 0 = human, 100 = likely AI

    if len(sentences) > 5:
        # Check sentence length uniformity (AI tends to be very uniform)
        lengths = [len(s.split()) for s in sentences]
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
            if variance < 15:
                ai_score += 30

        # Check for overly generic phrases
        generic_phrases = [
            "highly motivated", "team player", "strong communication",
            "proven track record", "dynamic individual", "self-starter",
            "passionate about", "detail-oriented professional",
        ]
        generic_count = sum(1 for p in generic_phrases if p in text_lower)
        ai_score += min(generic_count * 10, 40)

        # Check for repetitive sentence starters
        starters = [s.split()[0].lower() for s in sentences if s.split()]
        if starters:
            most_common_ratio = max(starters.count(s) for s in set(starters)) / len(starters)
            if most_common_ratio > 0.4:
                ai_score += 20

    ai_score = min(ai_score, 100)
    score = max(score, 0)

    if not suggestions:
        suggestions.append("Your resume looks well-structured for ATS parsing!")

    return {
        "score": score,
        "ai_detection_score": ai_score,
        "suggestions": suggestions,
    }
