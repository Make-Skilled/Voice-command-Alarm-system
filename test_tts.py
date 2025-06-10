import pyttsx3
import threading

def test_tts():
    try:
        print("Initializing text-to-speech...")
        engine = pyttsx3.init()
        
        # List available voices
        voices = engine.getProperty('voices')
        print(f"Available voices: {len(voices)}")
        for i, voice in enumerate(voices):
            print(f"  {i}: {voice.name} - {voice.id}")
        
        # Set properties
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        if voices:
            engine.setProperty('voice', voices[0].id)
        
        print("Speaking test message...")
        engine.say("Hello! Text to speech is working correctly.")
        engine.runAndWait()
        
        print("✅ Text-to-speech test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech error: {e}")
        return False

if __name__ == "__main__":
    test_tts()