
import ollama

MODEL = "llama3.2:1b"

SYSTEM_PROMPT = """
You are JARVIS, a sophisticated personal AI assistant.
Speak in a calm, intelligent and concise manner.
Use British English.
Keep answers short unless the user requests detail.
"""

def ask_jarvis(question):

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        options={
            "num_predict": 100,
            "num_ctx": 2048,
            "temperature": 0.5
        },
        keep_alive="30m"
    )

    return response["message"]["content"]
