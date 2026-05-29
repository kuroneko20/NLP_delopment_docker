URGENT_KEYWORDS = {"lost", "stolen", "fraud", "urgent", "blocked", "freeze", "hack", "unauthorized"}
HIGH_INTENTS = {"card_lost", "transfer_money"}
MEDIUM_INTENTS = {"loan_inquiry", "transaction_history", "account_support"}


class PriorityNode:
    def run(self, state):
        message = state.message.lower()
        if state.intent in HIGH_INTENTS or any(keyword in message for keyword in URGENT_KEYWORDS):
            state.priority = "high"
        elif state.intent in MEDIUM_INTENTS:
            state.priority = "medium"
        else:
            state.priority = "normal"
        return state
