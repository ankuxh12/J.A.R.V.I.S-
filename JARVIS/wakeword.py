
import sounddevice as sd
import numpy as np
from openwakeword.model import Model

print("Initializing JARVIS wake-word system...")

wake_model = Model(
    wakeword_models=["hey_jarvis"],
    inference_framework="onnx"
)

print("JARVIS is active.")
print("Say: Hey Jarvis")

try:
    with sd.InputStream(
        samplerate=16000,
        channels=1,
        dtype="int16",
        blocksize=1280
    ) as stream:

        while True:
            audio, overflowed = stream.read(1280)

            audio = np.squeeze(audio)

            predictions = wake_model.predict(audio)

            for name, score in predictions.items():
                if score > 0.5:
                    print("\nHEY JARVIS DETECTED!")
                    print("Wake word score:", round(float(score), 2))
                    wake_model.reset()

except KeyboardInterrupt:
    print("\nJARVIS wake-word system stopped.")
