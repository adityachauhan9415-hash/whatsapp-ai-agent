# src/test_router_decision.py
from router import route_sender
from decision_engine import decide_action

def test_router():
    assert route_sender("Mom") == "family"
    assert route_sender("BestFriend") == "friend"
    assert route_sender("UnknownNumber") == "unknown"
    print("Router tests passed!")

def test_decision():
    # Ignore
    assert decide_action("", "normal") == "ignore"
    assert decide_action("hello", "system") == "ignore"

    # Reply
    assert decide_action("kal miloge?", "normal") == "reply"

    # Manual review
    assert decide_action("I need an OTP", "normal") == "manual_review"
    assert decide_action("Medical emergency", "normal") == "manual_review"
    print("Decision tests passed!")

if __name__ == "__main__":
    test_router()
    test_decision()
