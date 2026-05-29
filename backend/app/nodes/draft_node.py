from __future__ import annotations

from app.clients.ollama_client import OllamaClient


class DraftNode:
    def __init__(self) -> None:
        self.ollama = OllamaClient()

    def run(self, state):
        prompt = self._build_prompt(state)
        try:
            state.draft_reply = self.ollama.generate(prompt)
            state.metadata["draft_source"] = "ollama"
        except Exception as exc:
            state.draft_reply = self._fallback_reply(state, exc)
            state.metadata["draft_source"] = "rule_based_fallback"
        return state

    def _build_prompt(self, state) -> str:
        return f"""
You are a banking customer support assistant. Write one concise and safe reply.
Do not expose account data. Ask for missing information when required.

Customer message: {state.message}
Intent: {state.intent}
Confidence: {state.confidence:.2f}
Priority: {state.priority}
Policy: {state.policy}
Validation: {state.validation}
Missing information: {', '.join(state.missing_information) if state.missing_information else 'none'}
Next recommended action: {state.next_recommended_action}
""".strip()

    def _fallback_reply(self, state, exc: Exception) -> str:
        if state.missing_information:
            missing = ", ".join(state.missing_information)
            return (
                "I can help with this request, but I need the following information first: "
                f"{missing}. For security, please do not share sensitive credentials in chat."
            )
        if state.intent == "card_lost":
            return "I can help report a lost card. The recommended action is to freeze the card and verify your identity with card support."
        if state.intent == "check_balance":
            return "I can help check the balance after authentication is completed."
        return f"I can help route this request. Ollama was unavailable, so a fallback reply was used. Details: {exc}"
