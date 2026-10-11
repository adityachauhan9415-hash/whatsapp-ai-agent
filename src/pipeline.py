# src/pipeline.py

from router import route_sender
from decision_engine import decide_action
from history_brain import retrieve_memory as retrieve_memories
from generator import generate_reply, MockProvider
from delay import calculate_reply_delay

class Pipeline:
    def __init__(self, provider=None):
        self.provider = provider or MockProvider()

    def process_message(self, sender: str, message: str) -> dict:
        """Process a message through the pipeline."""
        # Step 1: Route sender
        relationship = route_sender(sender)

        # Step 2: Make decision
        action = decide_action(message, "normal")

        # Step 3: Handle based on action
        if action == "ignore":
            return {"status": "ignored"}

        if action == "manual_review":
            return {"status": "manual_review_required"}

        if action == "reply":
            # Retrieve memories
            memories = retrieve_memories(
                message, relationship, 3
            )

            # Generate reply
            reply = generate_reply(
                message, relationship, memories, self.provider
            )

            # Calculate delay
            delay_seconds = calculate_reply_delay(len(reply))

            return {
                "status": "replied",
                "relationship": relationship,
                "memories": memories,
                "reply": reply,
                "delay_seconds": delay_seconds
            }

        return {"status": "unknown_action"}
