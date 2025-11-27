import speech_recognition as sr
import logging
import os

logger = logging.getLogger(__name__)

class SpeechProcessor:
    """
    Handles Speech-to-Text using Google Speech Recognition (Fallback for Whisper).
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def transcribe_audio_file(self, file_path: str) -> str:
        """
        Transcribe audio file to text.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        try:
            with sr.AudioFile(file_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Could not request results from service; {e}")
            raise e
            
    def parse_intent(self, text: str) -> dict:
        """
        Simple keyword-based intent parser.
        """
        text = text.lower()
        intent = {"action": "unknown", "params": {}}
        
        if "optimize" in text or "strike" in text:
            intent["action"] = "optimize"
            if "fusion" in text:
                intent["params"]["domain"] = "fusion"
            elif "grid" in text:
                intent["params"]["domain"] = "grid"
            elif "wafer" in text:
                intent["params"]["domain"] = "wafer"
            else:
                intent["params"]["domain"] = "default"
                
        return intent
