from typing import Any, Callable, Dict

class LogicRouter:
    """
    Routes intents and tasks to the appropriate engines within the SCF.
    """
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}

    def register(self, intent_type: str, handler: Callable) -> None:
        """
        Registers a handler for a specific intent type.
        """
        self.handlers[intent_type] = handler

    def route(self, intent: Any) -> Any:
        """
        Routes the intent to the registered handler.
        """
        intent_type = getattr(intent, 'type', 'default')
        if intent_type in self.handlers:
            return self.handlers[intent_type](intent)
        raise ValueError(f"No handler registered for intent type: {intent_type}")
