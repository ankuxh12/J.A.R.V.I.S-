import time
import sounddevice as sd
import numpy as np
from openwakeword.model import Model

from brain import ask_jarvis
from speak import speak
from voice import listen_once

MIC_DEVICE = 1

print("Initializing JARVIS...")

wake_model = Model(
    wakeword_models=["hey_jarvis"],
    inference_framework="onnx"
)

print("JARVIS SYSTEM ONLINE")

speak("All systems operational, sir.")


def wait_for_wake_word():
    print("\nSTANDBY: Say Hey Jarvis...")

    wake_model.reset()

    with sd.InputStream(
        device=MIC_DEVICE,
        samplerate=16000,
        channels=1,
        dtype="int16",
        blocksize=1280
    ) as stream:

        while True:
            audio, overflowed = stream.read(1280)
            audio = np.squeeze(audio)

            predictions = wake_model.predict(audio)

            if any(score > 0.5 for score in predictions.values()):
                print("Wake word detected!")
                return


def conversation_mode():

    speak("At your service, sir.")

    print("\nCONVERSATION MODE ACTIVE")

    while True:

        # Listen for next question
        question = listen_once()

        if not question:
            print("No speech detected. Listening again...")
            continue

        question = question.strip()

        print("YOU:", question)

        # Exit conversation mode
        exit_commands = [
            "bye",
            "bye jarvis",
            "goodbye",
            "goodbye jarvis",
            "jarvis stop listening",
            "go to sleep"
        ]

        cleaned = question.lower().strip(" .,!?'")

        if cleaned in exit_commands:

            speak("Goodbye, sir. Returning to standby mode.")
            return

        # Ask AI
       

        print("JARVIS is thinking...")

        try:
            start = time.perf_counter()

            answer = ask_jarvis(question)

            ai_time = time.perf_counter() - start
            print(f"AI thinking time: {ai_time:.2f} seconds")

            start = time.perf_counter()

            speak(answer)

            voice_time = time.perf_counter() - start
            print(f"Voice + playback time: {voice_time:.2f} seconds")

        except Exception as error:
            print("AI Error:", error)
            speak("Sorry sir, I encountered an error.")



try:
    while True:
        wait_for_wake_word()
        conversation_mode()

except KeyboardInterrupt:
    print("\nJARVIS shutting down.")
