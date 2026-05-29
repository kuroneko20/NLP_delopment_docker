from __future__ import annotations

from clients.ollama_client import OllamaIntentClient
from core.schemas import IntentPrediction
from data.policies import SUPPORTED_INTENTS

KEYWORD_RULES = [
    ("card_lost", ["lost card", "stolen card", "block card", "freeze card", "card stolen", "mất thẻ", "khóa thẻ"]),
    ("transfer_money", ["transfer", "send money", "wire", "chuyển tiền", "send $", "pay to"]),
    ("check_balance", ["balance", "how much", "account balance", "số dư", "kiểm tra số dư"]),
    ("transaction_history", ["transaction", "history", "statement", "recent payments", "lịch sử", "sao kê"]),
    ("loan_inquiry", ["loan", "borrow", "mortgage", "interest rate", "vay", "khoản vay"]),
    ("account_support", ["account", "login", "password", "support", "profile", "tài khoản", "đăng nhập"]),
]


class IntentNode:
    def __init__(self) -> None:
        self.ollama_client = OllamaIntentClient()

    def classify(self, message: str) -> IntentPrediction:
        try:
            model_result = self.ollama_client.classify(message)
            if model_result:
                prediction = IntentPrediction(**model_result)
                if prediction.intent in SUPPORTED_INTENTS:
                    prediction.reason = prediction.reason or "Intent classified by Ollama."
                    return prediction
        except Exception:
            model_result = None

        return self.rule_based_classify(message)

    def rule_based_classify(self, message: str) -> IntentPrediction:
        normalized = message.lower()
        for intent, keywords in KEYWORD_RULES:
            if any(keyword in normalized for keyword in keywords):
                return IntentPrediction(
                    intent=intent,
                    confidence=0.82,
                    reason="Rule-based fallback matched banking keywords.",
                )
        return IntentPrediction(
            intent="unknown",
            confidence=0.35,
            reason="Rule-based fallback could not match a supported banking intent.",
        )
