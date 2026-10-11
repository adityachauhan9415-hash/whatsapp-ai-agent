import os
from google import genai
from openai import OpenAI
from typing import List, Dict

class LLMProvider:
    def generate(self, prompt: str) -> str:
        """Generate response from LLM"""
        raise NotImplementedError

class MockProvider(LLMProvider):
    def generate(self, prompt: str) -> str:
        """Mock provider for testing"""
        return f"Mock reply for prompt: {prompt[:50]}..."

class OpenAIProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.model = 'gpt-6-luna'

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt
            )
            return response.output_text.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

class OllamaProvider(LLMProvider):
    def __init__(self):
        import requests
        self.client = requests.Session()
        self.model = 'qwen2.5:3b'
        self.url = 'http://localhost:11434/api/generate'

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.post(
                self.url,
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.7}
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()['response'].strip()
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")

class GeminiProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)
        self.primary_model = 'gemini-3.8-flash'
        self.fallback_model = 'gemini-1.5-flash'

    def generate(self, prompt: str) -> str:
        """Generate response using Gemini API with fallback for high demand"""
        models_to_try = [self.primary_model, self.fallback_model]
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                # Safely extract error code from Gemini API errors
                error_code = None
                if hasattr(e, 'args') and len(e.args) > 0 and isinstance(e.args[0], dict):
                    error_info = e.args[0].get('error')
                    if isinstance(error_info, dict):
                        error_code = error_info.get('code')

                if error_code == 503 and model == self.primary_model:
                    # Retry with fallback model on 503 error
                    continue
                raise e

def load_persona() -> str:
    """Load persona definition from config/persona.md"""
    persona_path = os.path.join(os.path.dirname(__file__), "..", "config", "persona.md")
    try:
        with open(persona_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Default casual texting style: short, friendly, and conversational."

def format_memories(memories: List[Dict]) -> str:
    """Format retrieved memories for prompt inclusion"""
    if not memories:
        return "No relevant memories found."

    formatted = []
    for i, memory in enumerate(memories, 1):
        formatted.append(f"Memory {i}:")
        formatted.append(f"Incoming: {memory['incoming']}")
        formatted.append(f"Reply: {memory['reply']}")
        distance = memory.get("distance")
        if distance is not None:
            formatted.append(f"Distance: {distance:.4f}")
    return "\n".join(formatted)

def build_prompt(incoming_text: str, relationship: str, persona: str, formatted_memories: str) -> str:
    """Build complete prompt for LLM"""
    return f"""
Persona:
{persona}

Relationship: {relationship}

Incoming message:
{incoming_text}

Relevant memories:
{formatted_memories}

Generate a reply in the specified style:
"""

def generate_reply(
    incoming_text: str,
    relationship: str,
    memories: List[Dict],
    provider: LLMProvider
) -> str:
    """Generate a reply combining incoming message, relationship, persona, and memories.

    Args:
        incoming_text: The new incoming message
        relationship: Relationship type (e.g., 'friend', 'family')
        memories: Top 3 retrieved memories from History Brain
        provider: LLM provider instance

    Returns:
        Generated reply in the specified style
    """
    persona = load_persona()
    formatted_memories = format_memories(memories)
    prompt = build_prompt(incoming_text, relationship, persona, formatted_memories)
    return provider.generate(prompt)
