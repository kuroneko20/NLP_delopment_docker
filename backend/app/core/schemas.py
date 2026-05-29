from typing import Any

from pydantic import BaseModel, Field


class RunAgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class IntentResult(BaseModel):
    intent: str
    confidence: float
    reason: str


class AgentState(BaseModel):
    message: str
    intent: str = "unknown"
    confidence: float = 0.0
    reason: str = ""
    priority: str = "normal"
    policy: str = "No specific policy retrieved."
    validation: str = "not_checked"
    draft_reply: str = ""
    missing_information: list[str] = Field(default_factory=list)
    next_recommended_action: str = "manual_review"
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunAgentResponse(BaseModel):
    message: str
    intent: str
    confidence: float
    reason: str
    priority: str
    policy: str
    validation: str
    draft_reply: str
    missing_information: list[str]
    next_recommended_action: str
