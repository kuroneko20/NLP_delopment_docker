POLICIES = {
    "check_balance": "Balance requests require user authentication before account data is disclosed.",
    "transfer_money": "Money transfers require recipient details, amount, currency, account verification, and explicit confirmation.",
    "card_lost": "Lost-card reports are urgent. Freeze the card, verify identity, and route to card support immediately.",
    "loan_inquiry": "Loan inquiries require loan type, income range, target amount, and consent for eligibility checks.",
    "transaction_history": "Transaction history requests require a verified date range and authenticated account ownership.",
    "account_support": "Account support cases require identity verification and a concise issue description.",
    "unknown": "Unknown requests should be clarified before banking actions are performed.",
}

DEFAULT_POLICY = POLICIES["unknown"]
