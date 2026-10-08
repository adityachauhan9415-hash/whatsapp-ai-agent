# src/decision_engine.py

# Simple rule-based decision engine
def decide_action(message_text: str, message_type: str) -> str:
    """Decide action based on message content and type."""

    # Ignore rules
    if not message_text or message_text.strip() == "":
        return "ignore"

    if message_type in ["system", "call", "media_placeholder"]:
        return "ignore"

    # Manual review rules
    sensitive_keywords = [
        "bank", "otp", "password", "legal", "lawyer", "medical",
        "emergency", "threat", "kill", "money", "transfer", "pay"
    ]

    text_lower = message_text.lower()
    for keyword in sensitive_keywords:
        if keyword in text_lower:
            return "manual_review"

    # Default to reply for casual conversation
    return "reply"
