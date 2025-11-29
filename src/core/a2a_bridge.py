import asyncio
import json
from typing import Callable, Dict, List

class AgentMessage:
    def __init__(self, sender: str, topic: str, payload: dict):
        self.sender = sender
        self.topic = topic
        self.payload = payload

class AgentBus:
    """
    A lightweight Pub/Sub bus for Capsule-to-Capsule communication.
    Allows decentralized coordination without a central Maestro bottleneck.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[AgentMessage] = []

    async def publish(self, sender: str, topic: str, payload: dict):
        """Publish a message to a topic."""
        message = AgentMessage(sender, topic, payload)
        self._history.append(message)
        
        if topic in self._subscribers:
            for callback in self._subscribers[topic]:
                # In a real system, this would be async/parallel
                try:
                    await callback(message)
                except Exception as e:
                    print(f"Error in A2A callback for {topic}: {e}")

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

# Singleton instance
global_agent_bus = AgentBus()
