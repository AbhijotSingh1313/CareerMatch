from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import FRONTEND_URL
from app.auth.router import router as auth_router
from app.candidates.router import router as candidates_router
from app.resume.router import router as resume_router
from app.recruiters.router import router as recruiters_router
from app.jobs.router import router as jobs_router
from app.matching.router import router as matching_router
from app.skills.router import router as skills_router
from app.feedback.router import router as feedback_router

app = FastAPI(
    title="CareerMatch AI",
    description="Intelligent Resume Analyzer & Smart Job Recommendation Platform",
    version="1.0.0",
)

# ─── CORS (allow all origins in development) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register all routers ───
app.include_router(auth_router)
app.include_router(candidates_router)
app.include_router(resume_router)
app.include_router(recruiters_router)
app.include_router(jobs_router)
app.include_router(matching_router)
app.include_router(skills_router)
app.include_router(feedback_router)


@app.get("/")
def root():
    return {"message": "Welcome to CareerMatch AI API", "docs": "/docs"}