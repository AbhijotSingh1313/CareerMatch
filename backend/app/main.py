from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import FRONTEND_URL
from app.auth.router import router as auth_router

app = FastAPI(
    title="CareerMatch AI",
    description="Intelligent Resume Analyzer & Smart Job Recommendation Platform",
    version="1.0.0",
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register routers ───
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Welcome to CareerMatch AI API", "docs": "/docs"}