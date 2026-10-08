# src/delay.py

import random

# Delay bounds in seconds
MIN_DELAY = 0.5
MAX_DELAY = 3.0

# Adjust these factors to control the relationship between length and delay
deLAY_FACTOR = 0.1
MIN_LENGTH = 10


def calculate_reply_delay(reply_length: int, random_seed: int = None) -> float:
    """Calculate human-like delay based on reply length.

    Args:
        reply_length: Length of the reply text
        random_seed: Optional seed for deterministic testing

    Returns:
        float: Delay in seconds
    """
    if random_seed is not None:
        random.seed(random_seed)

    # Calculate base delay based on length
    length_factor = max(0, (reply_length - MIN_LENGTH) * deLAY_FACTOR)
    base_delay = MIN_DELAY + length_factor

    # Add some randomness
    delay = base_delay * random.uniform(0.9, 1.1)

    # Clamp to bounds
    return max(MIN_DELAY, min(MAX_DELAY, delay))
