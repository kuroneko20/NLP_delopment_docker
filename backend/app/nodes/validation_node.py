import re


def _has_amount(message: str) -> bool:
    return bool(re.search(r"(\$|usd|vnd|eur|amount|transfer)\s*\d+|\d+\s*(usd|vnd|eur|dollars?)", message, re.I))


class ValidationNode:
    def run(self, state):
        missing = []
        text = state.message.lower()

        if state.intent == "transfer_money":
            if not _has_amount(text):
                missing.append("transfer_amount")
            if not any(token in text for token in ["to ", "recipient", "account", "beneficiary"]):
                missing.append("recipient")
            if "confirm" not in text:
                missing.append("explicit_confirmation")
        elif state.intent == "transaction_history":
            if not any(token in text for token in ["from", "to", "last", "today", "month", "week", "date"]):
                missing.append("date_range")
        elif state.intent == "loan_inquiry":
            if not any(token in text for token in ["home", "car", "personal", "business", "mortgage", "student"]):
                missing.append("loan_type")
        elif state.intent == "unknown":
            missing.append("clarified_intent")

        state.missing_information = missing
        state.validation = "valid" if not missing else "needs_more_information"
        return state
