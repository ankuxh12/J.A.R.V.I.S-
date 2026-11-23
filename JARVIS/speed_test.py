
import ollama
import time

MODEL = "llama3.2:1b"

for test in range(2):
    print(f"\nRunning AI speed test {test + 1}...")

    start = time.perf_counter()

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": "Say hello in one short sentence."
            }
        ],
        options={
            "num_predict": 50,
            "num_ctx": 2048
        },
        keep_alive="30m"
    )

    elapsed = time.perf_counter() - start

    print("Answer:", response["message"]["content"])
    print(f"Total time: {elapsed:.2f} seconds")

    load = response.get("load_duration", 0) / 1e9
    generation = response.get("eval_duration", 0) / 1e9
    tokens = response.get("eval_count", 0)

    print(f"Model loading: {load:.2f} seconds")
    print(f"Token generation: {generation:.2f} seconds")

    if generation > 0:
        print(f"Speed: {tokens / generation:.1f} tokens/sec")
