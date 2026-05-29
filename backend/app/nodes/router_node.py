ROUTES = {
    "check_balance": "authenticate_and_show_balance",
    "transfer_money": "collect_transfer_details_and_verify",
    "card_lost": "freeze_card_and_escalate_to_card_support",
    "loan_inquiry": "collect_loan_profile_and_route_to_loan_team",
    "transaction_history": "authenticate_and_fetch_transactions",
    "account_support": "route_to_account_support",
    "unknown": "ask_clarifying_question",
}


class RouterNode:
    def run(self, state):
        if state.validation == "needs_more_information":
            state.next_recommended_action = "collect_missing_information"
        else:
            state.next_recommended_action = ROUTES.get(state.intent, ROUTES["unknown"])
        return state
