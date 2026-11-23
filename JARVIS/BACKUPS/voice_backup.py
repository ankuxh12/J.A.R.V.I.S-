import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

MIC_DEVICE = 1

print("Loading JARVIS speech recognition...")
model = WhisperModel(
    "tiny.en",
    device="cpu",
    compute_type="int8",
    cpu_threads=2,
    num_workers=1
)

def listen_once():
    sample_rate = 16000
    duration = 6

    print("\nJARVIS is listening. Speak now!")

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        device=MIC_DEVICE
    )
    sd.wait()

    audio = np.squeeze(audio)

    print("Processing your voice...")
    segments, info = model.transcribe(
        audio,
        language="en",
        vad_filter=True
    )

    result = " ".join(segment.text for segment in segments).strip()
    print("You said:", result)

    return result