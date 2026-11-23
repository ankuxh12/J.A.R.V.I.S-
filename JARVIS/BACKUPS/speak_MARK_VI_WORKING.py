
import sounddevice as sd
import wave
import numpy as np
import time

from scipy.io import wavfile
from piper import PiperVoice

MODEL = "models/jarvis/jarvis-high.onnx"
OUTPUT = "jarvis_response.wav"

# HUD audio-reactive callback
audio_level_callback = None

print("Loading JARVIS voice...")
voice = PiperVoice.load(MODEL)
print("JARVIS voice ready!")


def update_audio_level(level):
    if audio_level_callback is not None:
        try:
            audio_level_callback(float(level))
        except Exception as error:
            print("HUD audio update error:", error)


def speak(text):
    print("JARVIS:", text)

    with wave.open(OUTPUT, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    sample_rate, audio = wavfile.read(OUTPUT)

    # Convert audio to normalized float32 for analysis
    if np.issubdtype(audio.dtype, np.integer):
        max_value = float(np.iinfo(audio.dtype).max)
        audio_float = audio.astype(np.float32) / max_value
    else:
        audio_float = audio.astype(np.float32)

    # Analyze voice volume in small chunks
    chunk_size = max(1, int(sample_rate * 0.04))

    # Keep the original audio playback
    sd.play(audio, sample_rate, device=3)

    try:
        start_time = time.perf_counter()

        for start in range(0, len(audio_float), chunk_size):
            chunk = audio_float[start:start + chunk_size]

            if len(chunk) == 0:
                continue

            # RMS = actual voice energy
            rms = float(np.sqrt(np.mean(chunk * chunk)))

            # Boost visual response
            level = min(1.0, rms * 8.0)

            update_audio_level(level)

            # Synchronize animation with playback time
            target_time = (start + len(chunk)) / sample_rate
            elapsed = time.perf_counter() - start_time
            remaining = target_time - elapsed

            if remaining > 0:
                time.sleep(remaining)

        sd.wait()

    finally:
        # Reset HUD when speaking ends
        update_audio_level(0.0)
