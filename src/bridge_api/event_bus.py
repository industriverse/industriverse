import asyncio
from typing import List, Callable, Awaitable

class GlobalEventBus:
    _subscribers: List[Callable[[dict], Awaitable[None]]] = []

    @classmethod
    async def publish(cls, event: dict):
        # Create a copy of the list to avoid modification during iteration
        for sub in list(cls._subscribers):
            try:
                await sub(event)
            except Exception as e:
                print(f"Error in subscriber: {e}")

    @classmethod
    def subscribe(cls, callback: Callable[[dict], Awaitable[None]]):
        cls._subscribers.append(callback)
        
    @classmethod
    def unsubscribe(cls, callback: Callable[[dict], Awaitable[None]]):
        if callback in cls._subscribers:
            cls._subscribers.remove(callback)
