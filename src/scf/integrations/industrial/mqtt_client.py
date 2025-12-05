import json
import time
from typing import Dict, Any

class MQTTClient:
    """
    Industrial IoT Connector for MQTT.
    Publishes telemetry and subscribes to commands.
    """
    def __init__(self, broker: str, port: int = 1883, client_id: str = "sovereign_edge"):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.connected = False
        self.mock_mode = True # Default to mock for now

    def connect(self):
        if self.mock_mode:
            self.connected = True
            print(f"📡 [MOCK] Connected to MQTT Broker {self.broker}:{self.port}")
            return

    def publish(self, topic: str, payload: Dict[str, Any]):
        """
        Publish a JSON payload to a topic.
        """
        if not self.connected:
            print("⚠️ MQTT not connected. Dropping message.")
            return

        message = json.dumps(payload)
        if self.mock_mode:
            print(f"📤 [MOCK] Published to {topic}: {message}")

    def subscribe(self, topic: str):
        if self.mock_mode:
            print(f"📥 [MOCK] Subscribed to {topic}")

    def disconnect(self):
        self.connected = False
        print("📡 Disconnected from MQTT Broker")
