
import ollama

MODEL = "llama3.2:1b"

SYSTEM_PROMPT = """
You are JARVIS, a smart, obedient, and intelligent personal AI assistant.

INSTRUCTIONS:
- Understand and follow instructions given ONLY in English.
- Do not interpret Hindi or Hinglish commands.
- Always respond in natural, concise British English.
- Speak clearly, politely, confidently, and conversationally.
- Keep responses short unless a detailed explanation is requested.
- Prioritise the user's direct instructions and execute them accurately.
- If a command is unclear, ask a short clarification instead of guessing.
- Do not ignore, misinterpret, or unnecessarily overcomplicate commands.
- Avoid robotic responses and unnecessary formalities.
- Never respond in Hindi or Hinglish.

Your role is to assist the user efficiently, like a real personal assistant.
"""

# Conversation memory stored in RAM
conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

MAX_MESSAGES = 12


def ask_jarvis(question):
    global conversation_history

    # Add user's new message
    conversation_history.append({
        "role": "user",
        "content": question
    })

    try:
        response = ollama.chat(
            model=MODEL,
            messages=conversation_history,
            options={
                "num_predict": 100,
                "num_ctx": 4096,
                "temperature": 0.6
            },
            keep_alive="30m"
        )

        answer = response["message"]["content"]

        # Remember JARVIS's response
        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        # Keep only recent conversation messages
        if len(conversation_history) > MAX_MESSAGES + 1:
            conversation_history = [
                conversation_history[0]
            ] + conversation_history[-MAX_MESSAGES:]

        return answer

    except Exception as e:
        print("JARVIS brain error:", e)

        # Remove unanswered user message
        conversation_history.pop()

        return "I'm having trouble processing that request, sir."


def clear_memory():
    global conversation_history

    conversation_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    print("JARVIS conversation memory cleared.")


if __name__ == "__main__":
    print(ask_jarvis("My favorite programming language is Python."))
    print(ask_jarvis("What is my favorite programming language?"))
