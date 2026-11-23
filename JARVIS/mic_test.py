
import sounddevice as sd
from scipy.io.wavfile import write

DEVICE = 1
RATE = 16000

print("Speak something for 5 seconds...")

audio = sd.rec(
    RATE * 5,
    samplerate=RATE,
    channels=1,
    dtype="int16",
    device=DEVICE
)

sd.wait()

write("mic_test.wav", RATE, audio)

print("Recording saved! Play mic_test.wav")
