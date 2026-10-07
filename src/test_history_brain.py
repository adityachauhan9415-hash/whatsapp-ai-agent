#!/usr/bin/env python3
"""
Clean test script to verify duplicate prevention in history brain.
"""

import chromadb
from src.history_brain import ingest_memory_pair

def test_duplicate_prevention():
    """Test that duplicate records are prevented using an ephemeral client."""

    # Create an ephemeral ChromaDB client for testing
    test_client = chromadb.EphemeralClient()

    # Define the test pair
    test_pair = {
        "timestamp": "6/28/26, 10:28:34 AM",
        "relationship": "friend",
        "contact_name": "Prateek",
        "incoming": "Thora mahnga h but sahi h sikhne ke liye",
        "reply": "Ha"
    }

    collection_name = f"whatsapp_memory_{test_pair['relationship']}"
    collection = test_client.get_or_create_collection(name=collection_name)

    # Ingest the test pair once
    ingest_memory_pair(test_pair, client=test_client)
    count1 = len(collection.get()['ids'])

    # Ingest the same test pair again
    ingest_memory_pair(test_pair, client=test_client)
    count2 = len(collection.get()['ids'])

    # Verify counts
    if count1 == 1 and count2 == 1:
        print(f"Duplicate prevention: PASS (counts: {count1} -> {count2})")
    else:
        print(f"Duplicate prevention: FAIL (Expected 1 and 1, got {count1} and {count2})")

if __name__ == "__main__":
    test_duplicate_prevention()