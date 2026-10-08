# src/router.py

# Simple contact mapping for routing
CONTACT_MAPPING = {
    "Mom": "family",
    "Dad": "family",
    "Brother": "family",
    "BestFriend": "friend",
    "WorkColleague": "professional",
    "Boss": "professional"
}

def route_sender(sender_name: str) -> str:
    """Route sender to category based on mapping."""
    return CONTACT_MAPPING.get(sender_name, "unknown")
