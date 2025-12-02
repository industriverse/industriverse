from typing import Dict, Callable, Any
from src.coherence.iacp_v2 import IACPMessage, IACPIntent

class IntentParser:
    """
    The Semantic Router.
    Directs messages to the correct cognitive function based on Intent.
    """
    
    def __init__(self):
        self.handlers: Dict[IACPIntent, Callable[[IACPMessage], None]] = {}
        
    def register_handler(self, intent: IACPIntent, handler: Callable[[IACPMessage], None]):
        self.handlers[intent] = handler
        
    def process(self, message: IACPMessage):
        """
        Parses and routes the message.
        """
        print(f"   📨 [PARSER] Received: {message.intent.name} (Urgency: {message.context.urgency:.2f})")
        
        # 1. Priority Check (Mock)
        if message.context.urgency > 0.8:
            print("     -> 🚨 HIGH PRIORITY INTERRUPT")
            
        # 2. Routing
        handler = self.handlers.get(message.intent)
        if handler:
            handler(message)
        else:
            print(f"     -> ⚠️ No handler for {message.intent.name}")

# --- Verification ---
if __name__ == "__main__":
    parser = IntentParser()
    
    def on_warning(msg):
        print(f"     -> HANDLING WARNING: {msg.payload}")
        
    parser.register_handler(IACPIntent.ISSUE_WARNING, on_warning)
    
    # Mock Message
    from src.coherence.iacp_v2 import IACPContext
    msg = IACPMessage(
        intent=IACPIntent.ISSUE_WARNING,
        context=IACPContext(0.9, "SECURITY"),
        payload={"msg": "TEST"}
    )
    parser.process(msg)
