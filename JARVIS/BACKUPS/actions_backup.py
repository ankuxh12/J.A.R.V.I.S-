
import subprocess
import webbrowser
from datetime import datetime


def perform_action(command):
    command = command.lower().strip()

    # OPEN CHROME
    if "open chrome" in command or "open google chrome" in command:
        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "", "chrome"]
            )
            return "Opening Google Chrome, sir."
        except Exception as e:
            print("Chrome error:", e)
            return "I couldn't open Chrome, sir."

    # OPEN NOTEPAD
    elif "open notepad" in command:
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad, sir."

    # OPEN CALCULATOR
    elif "open calculator" in command:
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator, sir."

    # OPEN YOUTUBE
    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube, sir."

    # OPEN GOOGLE
    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        return "Opening Google, sir."

    # CURRENT TIME
    elif "what time" in command or "current time" in command:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}, sir."

    # CURRENT DATE
    elif "what date" in command or "today's date" in command:
        today = datetime.now().strftime("%A, %d %B %Y")
        return f"Today is {today}, sir."

    # Not a laptop-control command
    return None


if __name__ == "__main__":
    while True:
        command = input("Command: ")

        if command.lower() == "exit":
            break

        result = perform_action(command)
        print(result)
