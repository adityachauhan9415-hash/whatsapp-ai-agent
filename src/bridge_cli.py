# src/bridge_cli.py

import sys
import json
from pipeline import Pipeline
from generator import OllamaProvider

# Initialize pipeline
pipeline = Pipeline(provider=OllamaProvider())

# Read input from stdin or command line
if not sys.stdin.isatty():
    input_data = json.load(sys.stdin)
else:
    input_data = {
        "sender": sys.argv[1],
        "message": sys.argv[2]
    }

# Process message through pipeline
result = pipeline.process_message(input_data["sender"], input_data["message"])

# Output JSON result
print(json.dumps(result))
