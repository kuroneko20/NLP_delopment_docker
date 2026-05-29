from app.clients.base import ExternalServiceError
from app.clients.grpc_intent_client import IntentGrpcClient
from app.core.schemas import AgentState


class IntentNode:
    def __init__(self) -> None:
        self.client = IntentGrpcClient()

    def run(self, state: AgentState) -> AgentState:
        try:
            result = self.client.classify(state.message)
            state.intent = result.intent
            state.confidence = result.confidence
            state.reason = result.reason
            state.metadata["intent_source"] = "grpc"
        except ExternalServiceError as exc:
            state.intent = "unknown"
            state.confidence = 0.0
            state.reason = f"Intent service unavailable: {exc}"
            state.metadata["intent_source"] = "backend_fallback_unknown"
        return state
