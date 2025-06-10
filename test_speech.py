import speech_recognition as sr
import time

def test_microphone():
    r = sr.Recognizer()
    
    # List available microphones
    print("Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {index}: {name}")
    
    # Test microphone
    try:
        with sr.Microphone() as source:
            print("\nAdjusting for ambient noise... Please wait")
            r.adjust_for_ambient_noise(source, duration=2)
            print("Ready! Say something...")
            
            # Listen for 5 seconds
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Processing speech...")
            
            # Try to recognize
            text = r.recognize_google(audio)
            print(f"You said: '{text}'")
            return True
            
    except sr.UnknownValueError:
        print("❌ Could not understand the audio")
        return False
    except sr.RequestError as e:
        print(f"❌ Error with speech recognition service: {e}")
        return False
    except sr.WaitTimeoutError:
        print("❌ No speech detected within timeout period")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing microphone and speech recognition...")
    test_microphone()