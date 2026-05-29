from pydantic import BaseModel, Field


class IntentPrediction(BaseModel):
    intent: str = "unknown"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = ""
