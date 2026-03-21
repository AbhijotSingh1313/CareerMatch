from fastapi import APIRouter, HTTPException, Depends
from app.auth.service import sign_up, sign_in, get_current_user
from app.auth.schemas import SignUpRequest, SignInRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse)
async def signup(request: SignUpRequest):
    """Register a new user (candidate or recruiter)."""
    try:
        user = sign_up(request.email, request.password, request.full_name, request.role)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(request: SignInRequest):
    """Login and receive JWT access token."""
    try:
        session = sign_in(request.email, request.password)
        return session
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    """Get current authenticated user's profile. Requires Bearer token."""
    return user
