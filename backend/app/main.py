from fastapi import FastAPI

from app.agent.orchestrator import BankingAgentOrchestrator
from app.core.schemas import RunAgentRequest, RunAgentResponse
from app.core.settings import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)
orchestrator = BankingAgentOrchestrator()


@app.get("/health")
def health() -> dict:
    return {"status": "running", "service": "backend", "version": settings.app_version}


@app.get("/config")
def config() -> dict:
    return {
        "service": settings.app_name,
        "intent_service_target": settings.intent_service_target,
        "ollama_base_url": settings.ollama_base_url,
        "intent_model_name": settings.intent_model_name,
        "grpc_timeout_seconds": settings.grpc_timeout_seconds,
        "http_timeout_seconds": settings.http_timeout_seconds,
    }


@app.post("/run-agent", response_model=RunAgentResponse)
def run_agent(payload: RunAgentRequest) -> RunAgentResponse:
    return orchestrator.run(payload.message)
