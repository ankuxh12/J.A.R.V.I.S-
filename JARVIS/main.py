from speak import stop_speaking
import time
import sounddevice as sd
import numpy as np
from openwakeword.model import Model
from actions import perform_action

from brain import ask_jarvis
from speak import speak
from voice import listen_once


state_callback = None
conversation_callback = None
def update_conversation(speaker, text):
    if conversation_callback is not None:
        conversation_callback(str(speaker), str(text))

def update_state(state):
    if state_callback is not None:
        state_callback(state)


MIC_DEVICE = 1

print("Initializing JARVIS...")

wake_model = Model(
    wakeword_models=["hey_jarvis"],
    inference_framework="onnx"
)

print("JARVIS SYSTEM ONLINE")

def main():
    speak("All systems operational, sir.")

    try:
        while True:
            wait_for_wake_word()
            conversation_mode()

    except KeyboardInterrupt:
        print("\nJARVIS shutting down.")



def wait_for_wake_word(stop_requested=lambda: False):

    print("\nSTANDBY: Say Hey Jarvis...")

    wake_model.reset()

    with sd.InputStream(
        device=MIC_DEVICE,
        samplerate=16000,
        channels=1,
        dtype="int16",
        blocksize=1280
    ) as stream:

        while not stop_requested():

            audio, overflowed = stream.read(1280)
            audio = np.squeeze(audio)

            predictions = wake_model.predict(audio)

            if any(
                score > 0.5
                for score in predictions.values()
            ):
                print("Wake word detected!")
                return True

    return False

def test_voice_interruption():
    import threading

    def play_test():
        speak(
            "Sir, this is a test of my advanced voice "
            "interruption system. I shall continue speaking "
            "until you interrupt me."
        )

    speaker = threading.Thread(target=play_test)
    speaker.start()

    input("Press ENTER to interrupt JARVIS...")
    stop_speaking()
    speaker.join()

def conversation_mode(stop_requested=lambda: False):
    update_state("SPEAKING")
    speak("At your service, sir.")

    print("\nCONVERSATION MODE ACTIVE")

    while not stop_requested():

        # Listen for next question
        update_state("LISTENING")
        question = listen_once()

        # Shutdown request aayi toh conversation stop
        if stop_requested():
            return

        if not question:
            print("No speech detected. Listening again...")
            continue
        
        question = question.strip()

        print("YOU:", question)
        update_conversation("YOU", question)

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
            update_conversation("JARVIS", "Goodbye, sir. Returning to standby mode.")
            update_state("SPEAKING")
            
            speak("Goodbye, sir. Returning to standby mode.")
            return

        # Ask AI
       

        print("JARVIS is thinking...")
        update_state("THINKING")
        try:
            start = time.perf_counter()

            # Check whether this is a laptop-control command
            action_response = perform_action(question)

            if action_response is not None:
                answer = action_response
            else:
                answer = ask_jarvis(question)

            update_conversation("JARVIS", answer)
            update_state("SPEAKING")
            speak(answer)

            ai_time = time.perf_counter() - start
            print(f"AI thinking time: {ai_time:.2f} seconds")

            start = time.perf_counter()
            voice_time = time.perf_counter() - start
            print(f"Voice + playback time: {voice_time:.2f} seconds")

        except Exception as error:
            print("AI Error:", error)

            if stop_requested():
                return

            update_state("SPEAKING")
            speak("Sorry sir, I encountered an error.")



def main():
    try:
        while True:
            wait_for_wake_word()
            conversation_mode()

    except KeyboardInterrupt:
        print("\nJARVIS shutting down.")


if __name__ == "__main__":
    main()
