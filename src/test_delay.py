# src/test_delay.py
from delay import calculate_reply_delay
import random

# Save original random seed
original_seed = random.seed()

# Test short reply delay
def test_short_reply_delay():
    delay = calculate_reply_delay(10, random_seed=42)
    assert 0.5 <= delay <= 3.0
    print(f"Short reply delay: {delay:.2f} seconds")

# Test long reply delay
def test_long_reply_delay():
    delay = calculate_reply_delay(100, random_seed=42)
    assert 0.5 <= delay <= 3.0
    print(f"Long reply delay: {delay:.2f} seconds")

# Test ignore/manual_review should not generate delay
def test_ignore_no_delay():
    # This is handled in pipeline tests
    pass

# Restore original random seed
random.seed(original_seed)

if __name__ == "__main__":
    test_short_reply_delay()
    test_long_reply_delay()