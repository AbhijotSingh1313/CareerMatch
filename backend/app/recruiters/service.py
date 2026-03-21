from app.dependencies import supabase_admin
from app.recruiters.schemas import RecruiterProfileUpdate


def get_recruiter_profile(user_id: str) -> dict:
    """Fetch combined profile + recruiter_details."""
    profile = supabase_admin.table("profiles").select("*").eq(
        "id", user_id
    ).single().execute()

    details = supabase_admin.table("recruiter_details").select("*").eq(
        "id", user_id
    ).single().execute()

    return {**profile.data, **details.data}


def update_recruiter_profile(user_id: str, data: RecruiterProfileUpdate) -> dict:
    """Update recruiter profile and details."""
    update_data = data.model_dump(exclude_none=True)

    # Fields that go into profiles table
    profile_fields = {"full_name", "avatar_url"}
    profile_update = {k: v for k, v in update_data.items() if k in profile_fields}
    if profile_update:
        supabase_admin.table("profiles").update(profile_update).eq(
            "id", user_id
        ).execute()

    # Fields that go into recruiter_details table
    detail_fields = {"company_name", "company_website", "industry", "hiring_needs"}
    detail_update = {k: v for k, v in update_data.items() if k in detail_fields}
    if detail_update:
        supabase_admin.table("recruiter_details").update(detail_update).eq(
            "id", user_id
        ).execute()

    return get_recruiter_profile(user_id)
