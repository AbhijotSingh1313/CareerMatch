from fastapi import Depends, HTTPException
from app.auth.service import get_current_user


def require_role(required_role: str):
    """
    Dependency that checks if the authenticated user has the required role.
    
    Usage in a route:
        @router.get("/something")
        async def something(user=Depends(require_role("recruiter"))):
            ...
    """
    async def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {required_role}",
            )
        return user
    return role_checker
