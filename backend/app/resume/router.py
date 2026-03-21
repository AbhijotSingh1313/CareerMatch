from fastapi import APIRouter, Depends, HTTPException
from app.auth.service import get_current_user

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.get("/analysis")
async def get_analysis(user=Depends(get_current_user)):
    """Get latest resume analysis (convenience alias)."""
    if user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidates only")
    from app.dependencies import supabase_admin
    result = supabase_admin.table("resumes").select("*").eq(
        "candidate_id", user["id"]
    ).order("created_at", desc=True).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="No resume found. Upload one first.")
    return result.data[0]
