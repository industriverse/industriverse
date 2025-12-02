from src.integrations.voice_engine import VoiceEngine

class VoiceOfTheMachine:
    """
    Product 10: Voice of the Machine
    Auditory Intelligence.
    """
    def __init__(self):
        self.name = "Voice of the Machine"
        self.engine = VoiceEngine()

    def get_status(self):
        return {
            "product": self.name,
            "status": "LISTENING",
            "mode": "TTS/STT"
        }

    def speak(self, text):
        print(f"[{self.name}] Speaking: {text}")
        self.engine.speak(text)
        return True
