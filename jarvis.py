from vosk import Model, KaldiRecognizer, SetLogLevel
import sounddevice as sd
import numpy as np
import pyttsx3
import json
import aiml
import os
import sys
import datetime
import webbrowser
import subprocess
import time

# ============================
#   TEXT TO SPEECH
# ============================
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 185)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

# ============================
#      AIML BRAIN
# ============================
BRAIN = "brain.dump"
k = aiml.Kernel()

if os.path.exists(BRAIN):
    print("Loading brain from brain.dump...")
    k.loadBrain(BRAIN)
else:
    print("Loading AIML files...")
    k.bootstrap(learnFiles="std-startup.aiml", commands="load aiml b")
    k.saveBrain(BRAIN)

k.setPredicate("name", "Jarvis")

# ============================
#      VOSK SETUP
# ============================
SetLogLevel(-1)

if not os.path.exists("vosk_speech_engine/model"):
    speak("Vosk model missing! Place model in vosk_speech_engine/model")
    sys.exit()

model = Model("vosk_speech_engine/model")
rec = KaldiRecognizer(model, 48000)


# MICROPHONE BOOST (IMPROVES ACCURACY)
sd.default.latency = "low"
sd.default.device = 1

# ============================
#        COMMANDS
# ============================
def open_google():
    speak("Opening Google")
    try:
        os.startfile("https://google.com")
    except:
        webbrowser.open("https://google.com")

def open_youtube():
    speak("Opening YouTube")
    try:
        os.startfile("https://youtube.com")
    except:
        webbrowser.open("https://youtube.com")

def google_search(q):
    speak(f"Searching for {q}")
    try:
        os.startfile(f"https://www.google.com/search?q={q}")
    except:
        webbrowser.open(f"https://www.google.com/search?q={q}")

def tell_time():
    speak("The time is " + datetime.datetime.now().strftime("%I:%M %p"))

def tell_date():
    speak("Today is " + datetime.datetime.now().strftime("%d %B %Y"))

def open_notepad():
    speak("Opening Notepad")
    subprocess.Popen(["notepad.exe"])

def shutdown_pc():
    speak("Shutting down")
    os.system("shutdown /s /t 5")

def restart_pc():
    speak("Restarting")
    os.system("shutdown /r /t 5")

# ============================
#     COMMAND DETECTOR
# ============================
def check_cmd(text, keywords):
    return any(k in text for k in keywords)

# ============================
#   CONTINUOUS LISTENING LOOP
# ============================
speak("Jarvis activated. Listening...")

stream = sd.InputStream(samplerate=48000, channels=1, blocksize=4000)
stream.start()

while True:
    audio = stream.read(4000)[0][:, 0]
    data = (audio * 32767).astype(np.int16).tobytes()

    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        text = result.get("text", "").lower().strip()

        if not text:
            continue

        print("You:", text)

        # ======================
        # FLEXIBLE COMMANDS
        # ======================

        # GOOGLE
        if check_cmd(text, [
            "google", "googl", "gogle", "go gel",
            "open google", "open go", "open gogle"
        ]):
            open_google()
            continue

        # YOUTUBE (BIG FLEXIBILITY)
        if check_cmd(text, [
            "youtube", "you tube", "u tube", "utub", "u tub",
            "you tub", "you toob", "yt",
            "open youtube", "open you tube", "open u tube",
            "open utub", "open yt"
        ]):
            open_youtube()
            continue

        # TIME
        if check_cmd(text, ["time", "tym", "taim"]):
            tell_time()
            continue

        # DATE
        if check_cmd(text, ["date"]):
            tell_date()
            continue

        # SEARCH (GOOGLE)
        if "search" in text:
            q = text.replace("search", "").strip()
            google_search(q)
            continue

        # NOTEPAD
        if check_cmd(text, ["notepad", "open notepad"]):
            open_notepad()
            continue

        # SHUTDOWN
        if "shutdown" in text or "shut down" in text:
            shutdown_pc()
            continue

        # RESTART
        if "restart" in text:
            restart_pc()
            continue

        # EXIT
        if check_cmd(text, ["exit", "quit", "bye"]):
            speak("Goodbye sir")
            os._exit(0)

        # ======================
        #      AIML RESPONSE
        # ======================
        reply = k.respond(text)
        if reply:
            speak(reply)
        else:
            speak("I didn't understand that.")
