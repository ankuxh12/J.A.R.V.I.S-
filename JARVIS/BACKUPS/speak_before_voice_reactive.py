
import sounddevice as sd
import wave
from scipy.io import wavfile
from piper import PiperVoice

MODEL = "models/jarvis/jarvis-high.onnx"
OUTPUT = "jarvis_response.wav"

print("Loading JARVIS voice...")
voice = PiperVoice.load(MODEL)
print("JARVIS voice ready!")


def speak(text):
    print("JARVIS:", text)

    with wave.open(OUTPUT, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    sample_rate, audio = wavfile.read(OUTPUT)

    # Use Windows default output device
    sd.play(audio, sample_rate, device=3)
    sd.wait()
