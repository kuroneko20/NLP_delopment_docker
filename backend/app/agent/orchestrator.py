from app.core.schemas import AgentState, RunAgentResponse
from app.nodes.draft_node import DraftNode
from app.nodes.intent_node import IntentNode
from app.nodes.policy_node import PolicyNode
from app.nodes.priority_node import PriorityNode
from app.nodes.router_node import RouterNode
from app.nodes.validation_node import ValidationNode


class BankingAgentOrchestrator:
    def __init__(self) -> None:
        self.nodes = [
            IntentNode(),
            PriorityNode(),
            PolicyNode(),
            ValidationNode(),
            RouterNode(),
            DraftNode(),
        ]

    def run(self, message: str) -> RunAgentResponse:
        state = AgentState(message=message)
        for node in self.nodes:
            state = node.run(state)
        return RunAgentResponse(**state.model_dump(exclude={"metadata"}))
