import speech_recognition as sr
import threading
import sounddevice as sd
import numpy as np
import torch

from TTS.api import TTS

WAKE = "jarvis"

# 🔥 XTTS v2 (fast + expressive)
print("Loading XTTS v2 model... this might take a moment.")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

# XTTS v2 uses predefined speaker names instead of index numbers.
# "Claribel Dervla" is one of the default high-quality built-in English voices.
SPEAKER_NAME = "Claribel Dervla" 

# If you want to clone a voice, put the path to a clear 5-10 second WAV file here.
SPEAKER_WAV = None   # e.g., "my_voice.wav"

def speak(text):
    print("Jarvis:", text)

    def run():
        # 🔥 emotion via style text
        styled_text = f"{text}"

        # XTTS API requires either a speaker string OR a speaker_wav for cloning.
        if SPEAKER_WAV:
            wav = tts.tts(
                text=styled_text,
                speaker_wav=SPEAKER_WAV,
                language="en"
            )
        else:
            wav = tts.tts(
                text=styled_text,
                speaker=SPEAKER_NAME,
                language="en"
            )

        sd.play(np.array(wav), samplerate=24000)
        sd.wait()

    threading.Thread(target=run).start()


# -------- SPEECH INPUT --------

def listen():
    r = sr.Recognizer()
    r.energy_threshold = 200
    r.dynamic_energy_threshold = True
    
    # ADD THIS: Gives you 1.5 seconds of silence (for breathing/thinking) before it cuts you off
    r.pause_threshold = 1.5 

    with sr.Microphone() as source:
        print("\n🎙️ Listening...") 
        try:
            # CHANGED: Increased phrase_time_limit to 15 seconds (adjust as needed)
            # The 'timeout=6' just means it will wait 6 seconds for you to START talking.
            audio = r.listen(source, timeout=6, phrase_time_limit=15)
            print("✅ Audio captured, processing...") 
        except sr.WaitTimeoutError:
            print("⏳ Timeout (no speech detected).") 
            return None

    try:
        text = r.recognize_google(audio)
        print(f"🗣️ You said: {text}") 
        return text
    except:
        print("❌ Could not understand audio.") 
        return None
        
def listen_wake():
    text = listen()
    if text and WAKE in text.lower():
        command = text.lower().replace(WAKE, "").strip()

        if command:
            return command
        else:
            speak("Yeah?")
            return listen()
    return None