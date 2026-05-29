from app.data.policies import DEFAULT_POLICY, POLICIES


class PolicyNode:
    def run(self, state):
        state.policy = POLICIES.get(state.intent, DEFAULT_POLICY)
        return state
