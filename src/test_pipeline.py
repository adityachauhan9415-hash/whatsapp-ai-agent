# src/test_pipeline.py
from pipeline import Pipeline
from generator import MockProvider

# Test data
pipeline = Pipeline()

# Test A: Casual friend message
def test_casual_friend():
    result = pipeline.process_message("BestFriend", "kal miloge?")
    assert result["status"] == "replied"
    assert result["relationship"] == "friend"
    assert len(result["memories"]) == 3
    assert "Mock reply" in result["reply"]
    print("Casual friend test passed!")

# Test B: Empty message
def test_empty_message():
    result = pipeline.process_message("Unknown", "")
    assert result["status"] == "ignored"
    print("Empty message test passed!")

# Test C: Sensitive message
def test_sensitive_message():
    result = pipeline.process_message("Unknown", "I need an OTP for my bank account")
    assert result["status"] == "manual_review_required"
    print("Sensitive message test passed!")

# Test D: Casual family message
def test_casual_family():
    result = pipeline.process_message("Mom", "kal miloge?")
    assert result["status"] == "replied"
    assert result["relationship"] == "family"
    print("Casual family test passed!")

if __name__ == "__main__":
    test_casual_friend()
    test_empty_message()
    test_sensitive_message()
    test_casual_family()