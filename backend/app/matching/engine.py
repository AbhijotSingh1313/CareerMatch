from app.dependencies import supabase_admin
from app.ai_service import ask_gemini_json


def _normalize(skill: str) -> str:
    return skill.lower().strip().replace(".", "").replace("-", " ")


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def _experience_score(candidate_years: float, required_min: float) -> float:
    if required_min == 0:
        return 1.0
    if candidate_years >= required_min:
        return min(1.0, 0.8 + 0.2 * (candidate_years / required_min))
    return max(0.0, candidate_years / required_min)


def _goal_match(career_goal: str, job_title: str) -> float:
    if not career_goal or not job_title:
        return 0.0
    goal_words = set(career_goal.lower().split()) - {"a", "an", "the", "and", "or", "of", "in", "at", "for", "to"}
    title_words = set(job_title.lower().split()) - {"a", "an", "the", "and", "or", "of", "in", "at", "for", "to"}
    return _jaccard_similarity(goal_words, title_words)


def compute_match_score(candidate: dict, job: dict) -> dict:
    """Compute weighted match score between candidate and job."""
    candidate_skills = {_normalize(s) for s in (candidate.get("skills") or [])}
    job_skills = {_normalize(s) for s in (job.get("required_skills") or [])}

    skill_score = _jaccard_similarity(candidate_skills, job_skills)
    exp_score = _experience_score(candidate.get("experience_years") or 0, job.get("experience_min") or 0)
    goal_score = _goal_match(candidate.get("career_goal") or "", job.get("title") or "")
    edu_score = 0.5

    total = (0.40 * skill_score + 0.25 * exp_score + 0.20 * goal_score + 0.15 * edu_score)

    return {
        "score": round(total * 100, 1),
        "explanation": {
            "skill_match": round(skill_score * 100, 1),
            "experience_match": round(exp_score * 100, 1),
            "goal_match": round(goal_score * 100, 1),
            "education_match": round(edu_score * 100, 1),
            "matched_skills": sorted(list(candidate_skills & job_skills)),
            "missing_skills": sorted(list(job_skills - candidate_skills)),
        },
    }


def get_job_matches_for_candidate(candidate_id: str) -> list:
    """Find and rank all open jobs for a candidate with AI-powered insights."""
    details = supabase_admin.table("candidate_details").select("*").eq("id", candidate_id).single().execute()
    candidate = details.data
    jobs = supabase_admin.table("jobs").select("*").eq("status", "open").execute()

    results = []
    for job in jobs.data:
        match = compute_match_score(candidate, job)
        results.append({"job": job, "score": match["score"], "explanation": match["explanation"]})

    results.sort(key=lambda x: x["score"], reverse=True)

    # AI-powered insight for top 3 matches
    if results[:3]:
        top_jobs_info = [
            f"- {r['job']['title']} (score: {r['score']}%, matched: {r['explanation']['matched_skills']}, missing: {r['explanation']['missing_skills']})"
            for r in results[:3]
        ]
        candidate_info = f"Skills: {candidate.get('skills', [])}, Goal: {candidate.get('career_goal', 'N/A')}, Experience: {candidate.get('experience_years', 0)} years"

        prompt = f"""You are a career advisor. A candidate has these details:
{candidate_info}

Their top 3 job matches are:
{chr(10).join(top_jobs_info)}

For each job, write a 1-sentence personalized explanation of WHY they match and WHAT they should focus on to improve their chances. Return a JSON array of 3 strings."""

        ai_insights = ask_gemini_json(prompt)
        if isinstance(ai_insights, list):
            for i, insight in enumerate(ai_insights[:3]):
                if i < len(results):
                    results[i]["ai_insight"] = insight

    return results


def get_candidate_matches_for_job(job_id: str) -> list:
    """Find and rank all candidates for a job."""
    job = supabase_admin.table("jobs").select("*").eq("id", job_id).single().execute()
    job_data = job.data
    candidates = supabase_admin.table("candidate_details").select("*").execute()

    results = []
    for candidate in candidates.data:
        profile = supabase_admin.table("profiles").select("*").eq("id", candidate["id"]).single().execute()
        match = compute_match_score(candidate, job_data)

        # Fetch latest ATS score
        resume = supabase_admin.table("resumes").select("ats_score").eq(
            "candidate_id", candidate["id"]
        ).order("created_at", desc=True).limit(1).execute()
        ats_score = resume.data[0].get("ats_score", 0) if resume.data else 0

        results.append({
            "candidate": {**profile.data, **candidate},
            "score": match["score"],
            "ats_score": ats_score,
            "explanation": match["explanation"],
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def _build_local_comparison(candidates_info: list, job_data: dict) -> dict:
    """Build a realistic comparison using local match scores when Gemini is unavailable."""
    scored = []
    for c in candidates_info:
        match = compute_match_score(
            {"skills": c["skills"], "experience_years": c["experience_years"], "career_goal": c["career_goal"]},
            job_data,
        )
        scored.append({**c, "match": match})

    scored.sort(key=lambda x: x["match"]["score"], reverse=True)

    ranking = []
    for rank_idx, c in enumerate(scored, 1):
        m = c["match"]
        exp = m["explanation"]

        # Build strengths from matched skills + experience
        strengths = []
        if exp["matched_skills"]:
            strengths.append(f"Proficient in {', '.join(exp['matched_skills'][:4])}")
        if c["experience_years"] >= (job_data.get("experience_min") or 0):
            strengths.append(f"{c['experience_years']} years of relevant experience meets requirements")
        if exp["goal_match"] > 30:
            strengths.append("Career goals align well with this role")
        if not strengths:
            strengths.append("Shows potential for growth in this role")

        # Build weaknesses from missing skills + experience gaps
        weaknesses = []
        if exp["missing_skills"]:
            weaknesses.append(f"Missing skills: {', '.join(exp['missing_skills'][:3])}")
        if c["experience_years"] < (job_data.get("experience_min") or 0):
            weaknesses.append(f"Below minimum experience requirement ({c['experience_years']} vs {job_data.get('experience_min', 0)} years)")
        if not weaknesses:
            weaknesses.append("No major gaps identified")

        # Recommendation based on score
        score = m["score"]
        if score >= 60:
            rec = "strong hire"
        elif score >= 45:
            rec = "hire"
        elif score >= 30:
            rec = "maybe"
        else:
            rec = "pass"

        skill_pct = exp["skill_match"]
        exp_pct = exp["experience_match"]
        reasoning = (
            f"{c['name']} achieves a {score}% overall fit score with {skill_pct}% skill match "
            f"and {exp_pct}% experience match. "
        )
        if rank_idx == 1:
            reasoning += "Ranked highest among the compared candidates based on comprehensive evaluation."
        else:
            reasoning += f"Ranked #{rank_idx} — could be a strong contender with additional skill development."

        ranking.append({
            "candidate_id": c["id"],
            "candidate_name": c["name"],
            "rank": rank_idx,
            "fit_score": score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": rec,
            "reasoning": reasoning,
        })

    # Build comparison summary
    names = [r["candidate_name"] for r in ranking]
    top = ranking[0]
    summary = (
        f"After evaluating {len(ranking)} candidates for the {job_data.get('title', 'open')} position, "
        f"{top['candidate_name']} emerges as the top candidate with a {top['fit_score']}% fit score. "
    )
    if len(ranking) > 1:
        summary += (
            f"The candidates were ranked based on skill alignment, experience relevance, and career goal fit. "
            f"{ranking[-1]['candidate_name']} ranked lowest at {ranking[-1]['fit_score']}% but may still be suitable with upskilling."
        )

    return {"ranking": ranking, "comparison_summary": summary}


def ai_compare_candidates(job_id: str, candidate_ids: list) -> dict:
    """AI-powered comparison of multiple candidates for a job, with local fallback."""
    try:
        job = supabase_admin.table("jobs").select("*").eq("id", job_id).single().execute()
        job_data = job.data

        candidates_info = []
        for cid in candidate_ids:
            try:
                profile = supabase_admin.table("profiles").select("*").eq("id", cid).single().execute()
                details = supabase_admin.table("candidate_details").select("*").eq("id", cid).single().execute()
                resume = supabase_admin.table("resumes").select("raw_text").eq("candidate_id", cid).order("created_at", desc=True).limit(1).execute()

                resume_snippet = resume.data[0]["raw_text"][:1000] if resume.data else "No resume"
                candidates_info.append({
                    "id": cid,
                    "name": profile.data.get("full_name", "Unknown") if profile.data else "Unknown",
                    "skills": details.data.get("skills", []) if details.data else [],
                    "experience_years": details.data.get("experience_years", 0) if details.data else 0,
                    "career_goal": details.data.get("career_goal", "") if details.data else "",
                    "resume_snippet": resume_snippet,
                })
            except Exception as e:
                print(f"Error fetching candidate {cid}: {e}")
                candidates_info.append({
                    "id": cid,
                    "name": "Unknown",
                    "skills": [],
                    "experience_years": 0,
                    "career_goal": "",
                    "resume_snippet": "No resume",
                })

        if len(candidates_info) < 2:
            return {"error": "Need at least 2 candidates to compare"}

        prompt = f"""You are a senior recruiter evaluating candidates for a "{job_data['title']}" position.

Job requirements:
- Required skills: {job_data.get('required_skills', [])}
- Minimum experience: {job_data.get('experience_min', 0)} years
- Description: {job_data.get('description', 'N/A')}

Candidates:
{chr(10).join([f'Candidate {i+1}: {c["name"]} (ID: {c["id"]}), Skills: {c["skills"]}, Experience: {c["experience_years"]} years, Goal: {c["career_goal"]}, Resume: {c["resume_snippet"][:400]}' for i, c in enumerate(candidates_info)])}

Return a JSON object with this exact structure:
{{
    "ranking": [
        {{
            "candidate_id": "the candidate id string",
            "candidate_name": "the candidate name",
            "rank": 1,
            "fit_score": 75,
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1"],
            "recommendation": "hire",
            "reasoning": "2-3 sentence explanation of ranking"
        }}
    ],
    "comparison_summary": "A paragraph comparing all candidates and explaining the final ranking"
}}

Include ALL {len(candidates_info)} candidates in the ranking array, ordered by rank. Use the actual candidate IDs and names provided above."""

        result = ask_gemini_json(prompt)
        if result and isinstance(result, dict) and "ranking" in result:
            return result

        # Fallback: generate comparison locally using match scores
        print("[Compare] Gemini unavailable, using local comparison fallback")
        return _build_local_comparison(candidates_info, job_data)

    except Exception as e:
        print(f"Compare error: {e}")
        return {"error": f"Comparison failed: {str(e)}"}


def ai_shortlist_candidates(job_id: str, max_candidates: int = 5) -> dict:
    """AI-powered automatic shortlisting of top candidates for a job."""
    # Get all candidates ranked
    ranked = get_candidate_matches_for_job(job_id)
    job = supabase_admin.table("jobs").select("*").eq("id", job_id).single().execute()

    # Take top candidates for AI analysis
    top = ranked[:min(max_candidates * 2, 10)]

    candidates_summary = []
    for r in top:
        c = r["candidate"]
        resume = supabase_admin.table("resumes").select("ats_score, parsed_skills").eq(
            "candidate_id", c["id"]
        ).order("created_at", desc=True).limit(1).execute()

        ats = resume.data[0].get("ats_score", 0) if resume.data else 0
        candidates_summary.append({
            "id": c["id"],
            "name": c.get("full_name", "Unknown"),
            "match_score": r["score"],
            "ats_score": ats,
            "skills": c.get("skills", []),
            "experience": c.get("experience_years", 0),
            "matched_skills": r["explanation"]["matched_skills"],
            "missing_skills": r["explanation"]["missing_skills"],
        })

    prompt = f"""You are a recruitment AI assistant. Based on the following candidates for "{job.data['title']}":

{chr(10).join([f"- {c['name']}: Match {c['match_score']}%, ATS {c['ats_score']}%, Skills: {c['skills']}, Experience: {c['experience']}y, Matched: {c['matched_skills']}, Missing: {c['missing_skills']}" for c in candidates_summary])}

Select the top {max_candidates} candidates to shortlist. Return a JSON object:
{{
    "shortlisted": [
        {{
            "candidate_id": "id",
            "candidate_name": "name",
            "reason": "1-2 sentence reason for shortlisting"
        }}
    ],
    "rejected": [
        {{
            "candidate_id": "id", 
            "candidate_name": "name",
            "reason": "1-2 sentence reason for not shortlisting"
        }}
    ]
}}"""

    result = ask_gemini_json(prompt)
    if result:
        return result

    # Fallback: shortlist based on match scores locally
    print("[Shortlist] Gemini unavailable, using local shortlist fallback")
    shortlisted = []
    rejected = []
    for i, c in enumerate(candidates_summary):
        entry = {
            "candidate_id": c["id"],
            "candidate_name": c["name"],
        }
        if i < max_candidates:
            matched = ", ".join(c["matched_skills"][:3]) if c["matched_skills"] else "general fit"
            entry["reason"] = (
                f"Strong overall fit with {c['match_score']}% match score and {c['ats_score']}% ATS score. "
                f"Key strengths in {matched}."
            )
            shortlisted.append(entry)
        else:
            missing = ", ".join(c["missing_skills"][:3]) if c["missing_skills"] else "overall fit"
            entry["reason"] = (
                f"Lower match score of {c['match_score']}% with gaps in {missing}. "
                f"Consider for future openings."
            )
            rejected.append(entry)
    return {"shortlisted": shortlisted, "rejected": rejected}
