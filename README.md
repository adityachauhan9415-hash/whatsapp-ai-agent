# Put Your WhatsApp on Cruise Control — Hands-Free Replies by an AI Agent using RAG

This project is an AI-powered WhatsApp automation system designed to handle conversations hands-free, providing context-aware, personalized replies.

## Architecture
1. WhatsApp Message In
2. -> Router
3. -> Decision Engine
4. -> Retrieval (History Brain)
5. -> Persona Injection (Persona Brain)
6. -> Generation
7. -> Human-like Delay
8. -> Send via Baileys

## Two-Brain Architecture
- **History Brain (Retrieval):** Manages the factual context and past conversation history, ensuring the agent remembers relevant details about interactions.
- **Persona Brain (Persona Injection):** Maintains your unique voice, tone, and preferences to ensure replies sound authentically like you.

## Roadmap
- **Week 1:** Project setup, architecture definition, and memory foundation.
- **Week 2:** Router, Decision Engine, and History/Persona retrieval implementation.
- **Week 3:** LLM generation, personality integration, and WhatsApp connectivity (Baileys).
- **Week 4:** Human-like delay, testing, and deployment.
