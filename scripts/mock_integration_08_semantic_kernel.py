# Mocked end-to-end simulation of the AgentGroupChat loop from
# 08-semantic-kernel.ipynb without any network calls.
# It uses simplified mocked agents and the same parser logic to
# drive turn-taking and termination.

REVIEWER_NAME = "Concierge"
FRONTDESK_NAME = "FrontDesk"


class MockResult:
    def __init__(self, value):
        self.value = value


def termination_parser(result):
    try:
        if not result or not getattr(result, "value", None):
            return False
        return str(result.value[0]).strip().lower() == "yes"
    except Exception:
        return False


def selection_parser(result):
    try:
        if not result or not getattr(result, "value", None):
            return FRONTDESK_NAME
        val = str(result.value[0]).strip()
        val_norm = val.lower()
        if val_norm == REVIEWER_NAME.lower():
            return REVIEWER_NAME
        if val_norm == FRONTDESK_NAME.lower():
            return FRONTDESK_NAME
        return FRONTDESK_NAME
    except Exception:
        return FRONTDESK_NAME


class MockAgent:
    def __init__(self, name, instructions):
        self.name = name
        self.instructions = instructions

    def respond(self, history):
        """Generate a deterministic mock response based on the agent name and history.
        - FrontDesk: returns a short recommendation on first turn, then refines if asked.
        - Concierge: provides feedback; after seeing the same recommendation twice, says 'yes'.
        """
        if self.name == FRONTDESK_NAME:
            # If last message from reviewer contains 'refine' or is negative, refine.
            if history and len(history) >= 2 and 'refine' in history[-1]['content'].lower():
                return "Here's a refined, more local suggestion: visit the lesser-known canal district for street music."
            return "I recommend visiting the Louvre and then having coffee at a nearby cafe."  
        if self.name == REVIEWER_NAME:
            # If the front desk repeated similar content, approve; otherwise give critique.
            last_front = next((m for m in reversed(history) if m['author'] == FRONTDESK_NAME), None)
            if last_front:
                content = last_front['content'].lower()
                # naive heuristic: if 'lesser-known' or 'refined' appears, approve
                if 'lesser-known' in content or 'refined' in content or 'authentic' in content:
                    # For compatibility with the notebook's termination_parser
                    # which expects 'yes' or 'no', return 'yes' here to signal
                    # approval while the notebook might display a more verbose
                    # approval message.
                    return "yes"
                # otherwise ask for refinement
                return "Please refine to be less touristy and more authentic."
            return "No recommendation found."
        return ""


def simulate_chat(max_turns=10):
    # history as list of dicts {author: name, content: text}
    history = []

    front_agent = MockAgent(FRONTDESK_NAME, "Front desk instructions")
    reviewer_agent = MockAgent(REVIEWER_NAME, "Reviewer instructions")

    # initial user input
    user_input = "I would like to go to Paris."
    history.append({'author': 'User', 'content': user_input})
    print(f"# User: '{user_input}'")

    # control variables
    last_author = 'User'
    turn = 0

    while turn < max_turns:
        # Decide who goes next using the simple rules from the notebook
        if last_author == 'User':
            next_agent = FRONTDESK_NAME
        elif last_author == FRONTDESK_NAME:
            next_agent = REVIEWER_NAME
        else:
            next_agent = FRONTDESK_NAME

        # Simulate agent response
        agent = front_agent if next_agent == FRONTDESK_NAME else reviewer_agent
        content = agent.respond(history)
        history.append({'author': agent.name, 'content': content})
        print(f"# Agent - {agent.name}: '{content}'")

        # Check termination via the termination_parser applied to a MockResult
        # We only check the reviewer's last response for approval semantics
        if agent.name == REVIEWER_NAME:
            t_result = MockResult([content])
            is_done = termination_parser(t_result)
            if is_done:
                print("# IS COMPLETE: True")
                return 0

        last_author = agent.name
        turn += 1

    print("# IS COMPLETE: False (max turns reached)")
    return 1


if __name__ == '__main__':
    raise SystemExit(simulate_chat())
