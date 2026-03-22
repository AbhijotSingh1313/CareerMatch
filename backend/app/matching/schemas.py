from pydantic import BaseModel


class MatchResult(BaseModel):
    score: float
    explanation: dict
