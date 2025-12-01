import sys

# Try to import TTS libraries
try:
    import pyttsx3
    TTS_ENGINE = "pyttsx3"
except ImportError:
    try:
        from gtts import gTTS
        import os
        TTS_ENGINE = "gTTS"
    except ImportError:
        TTS_ENGINE = "MOCK"

class VoiceEngine:
    """
    The Voice Interface.
    Gives the factory a voice to announce critical alerts.
    """
    def __init__(self):
        self.engine_type = TTS_ENGINE
        print(f"🎤 Voice Engine Initialized (Backend: {self.engine_type})")
        
        if self.engine_type == "pyttsx3":
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)

    def speak(self, text):
        """
        Announces the text audibly.
        """
        print(f"🔊 [VOICE] \"{text}\"")
        
        if self.engine_type == "pyttsx3":
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️  TTS Error: {e}")
                
        elif self.engine_type == "gTTS":
            try:
                # This is a bit blocking and requires internet, used as fallback
                tts = gTTS(text=text, lang='en')
                tts.save("temp_voice.mp3")
                if sys.platform == "darwin":
                    os.system("afplay temp_voice.mp3")
                elif sys.platform == "linux":
                    os.system("mpg123 temp_voice.mp3")
                os.remove("temp_voice.mp3")
            except Exception as e:
                print(f"⚠️  TTS Error: {e}")

if __name__ == "__main__":
    voice = VoiceEngine()
    voice.speak("System Online. Welcome to Empeiria Haus.")
