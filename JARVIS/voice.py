"""JARVIS MARK XI: multilingual speech input with adaptive noise calibration.

Drop-in replacement for voice.py (retains listen_once() -> str).
Test independently before replacing the original file.
"""

import time
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

MIC_DEVICE = 1
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.1
SILENCE_DURATION = 1.2
MAX_RECORDING = 15.0
START_TIMEOUT = 6.0
CALIBRATION_DURATION = 0.6
MIN_SILENCE_THRESHOLD = 0.006
NOISE_MULTIPLIER = 3.0
PRE_ROLL_CHUNKS = 3

print("Loading JARVIS multilingual speech recognition...")
model = WhisperModel(
    "small",  # multilingual; slower than base.en on CPU
    device="cpu",
    compute_type="int8",
    cpu_threads=2,
    num_workers=1,
)


def _rms(audio):
    return float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))


def listen_once():
    """Record one utterance and return recognized text, or an empty string."""
    print("\nJARVIS listening...")
    chunk_size = int(SAMPLE_RATE * CHUNK_DURATION)
    chunks = []
    speech_started = False
    silence_elapsed = 0.0

    try:
        with sd.InputStream(
            device=MIC_DEVICE,
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=chunk_size,
        ) as stream:
            # Calibrate from the current microphone's ambient noise.
            levels = []
            for _ in range(max(1, round(CALIBRATION_DURATION / CHUNK_DURATION))):
                data, overflowed = stream.read(chunk_size)
                if overflowed:
                    print("Warning: microphone input overflow during calibration")
                levels.append(_rms(data))

            threshold = max(MIN_SILENCE_THRESHOLD, float(np.median(levels)) * NOISE_MULTIPLIER)
            print(f"Mic threshold: {threshold:.4f}")
            started_at = time.monotonic()
            pre_roll = []

            while True:
                data, overflowed = stream.read(chunk_size)
                if overflowed:
                    print("Warning: microphone input overflow")
                audio = data[:, 0].copy()
                volume = _rms(audio)
                elapsed = time.monotonic() - started_at

                if not speech_started:
                    pre_roll.append(audio)
                    if len(pre_roll) > PRE_ROLL_CHUNKS:
                        pre_roll.pop(0)
                    if volume > threshold:
                        speech_started = True
                        chunks.extend(pre_roll)
                        pre_roll.clear()
                        silence_elapsed = 0.0
                else:
                    chunks.append(audio)
                    if volume > threshold:
                        silence_elapsed = 0.0
                    else:
                        silence_elapsed += CHUNK_DURATION

                if speech_started and silence_elapsed >= SILENCE_DURATION:
                    print("Speech finished.")
                    break
                if elapsed >= MAX_RECORDING:
                    print("Maximum recording reached.")
                    break
                if not speech_started and elapsed >= START_TIMEOUT:
                    print("No speech detected.")
                    return ""

    except sd.PortAudioError as exc:
        print(f"Microphone error: {exc}")
        return ""

    if not chunks:
        return ""

    recorded_audio = np.concatenate(chunks).astype(np.float32, copy=False)
    print("Transcribing...")
    try:
        segments, info = model.transcribe(
            recorded_audio,
            language=None,  # auto-detect Hindi/English
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
            initial_prompt=(
                "Jarvis, Chrome, YouTube, VS Code, Python, Ollama. "
    
            ),
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        print(f"Transcription error: {exc}")
        return ""

    print(f"Detected language: {info.language} ({info.language_probability:.2f})")
    print("YOU:", text)
    return text


if __name__ == "__main__":
    print("Test MARK XI smart listening")
    print("Result:", listen_once())
