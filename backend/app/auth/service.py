from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.dependencies import supabase, supabase_admin


def sign_up(email: str, password: str, full_name: str, role: str) -> dict:
    """Register user via Supabase Auth, then create a profile row."""

    # Validate role
    if role not in ("candidate", "recruiter"):
        raise Exception("Role must be 'candidate' or 'recruiter'")

    # 1. Create auth user in Supabase
    auth_response = supabase.auth.sign_up({
        "email": email,
        "password": password,
    })

    if auth_response.user is None:
        raise Exception("Signup failed — user not created")

    user_id = auth_response.user.id

    # 2. Insert into profiles table
    supabase_admin.table("profiles").insert({
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
    }).execute()

    # 3. Insert role-specific details row
    if role == "candidate":
        supabase_admin.table("candidate_details").insert({
            "id": user_id,
        }).execute()
    elif role == "recruiter":
        supabase_admin.table("recruiter_details").insert({
            "id": user_id,
            "company_name": "Not set",
        }).execute()

    return {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
    }


def sign_in(email: str, password: str) -> dict:
    """Login via Supabase Auth and return session tokens."""
    auth_response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })

    if auth_response.session is None:
        raise Exception("Login failed — invalid credentials")

    # Fetch profile to get role
    profile = supabase_admin.table("profiles").select("*").eq(
        "id", auth_response.user.id
    ).single().execute()

    return {
        "access_token": auth_response.session.access_token,
        "refresh_token": auth_response.session.refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(auth_response.user.id),
            "email": auth_response.user.email,
            "full_name": profile.data.get("full_name", ""),
            "role": profile.data.get("role", ""),
        },
    }


security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT from Authorization header and return user profile.
    Usage: add Depends(get_current_user) to any protected route.
    """
    token = credentials.credentials

    try:
        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Fetch full profile from database
        profile = supabase_admin.table("profiles").select("*").eq(
            "id", user.id
        ).single().execute()

        return profile.data

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
