import asyncio
from typing import AsyncGenerator, Optional
from datetime import datetime, timezone

class UserLMService:
    """
    Service for the User Language Model (UserLM).
    Simulates the "User" in the loop.
    Supports streaming responses and timeouts.
    """
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds

    async def generate_turn_stream(self, intent: str, history: list, persona: dict) -> AsyncGenerator[str, None]:
        """
        Generates a User turn, streaming the output token by token.
        """
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        # Mock response generation based on intent
        # In a real system, this would call the LLM inference endpoint
        response_text = f"Based on your intent '{intent}' and my persona '{persona.get('name', 'User')}', I need you to run a simulation."
        
        tokens = response_text.split(" ")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            for token in tokens:
                # Check timeout
                if (datetime.now(timezone.utc) - start_time).total_seconds() > self.timeout_seconds:
                    yield " [TIMEOUT]"
                    break
                
                yield token + " "
                await asyncio.sleep(0.1) # Simulate token generation latency
                
        except Exception as e:
            yield f" [ERROR: {str(e)}]"

    async def generate_turn(self, intent: str, history: list, persona: dict) -> str:
        """
        Non-streaming wrapper for generate_turn_stream.
        """
        full_response = ""
        async for token in self.generate_turn_stream(intent, history, persona):
            full_response += token
        return full_response.strip()
