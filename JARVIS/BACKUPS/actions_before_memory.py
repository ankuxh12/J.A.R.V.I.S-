
import re
import shutil
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus
from system_monitor import (
    get_cpu_usage,
    get_ram_usage,
    get_battery_status,
    get_disk_usage,
    get_system_status
)


# ==========================================
# JARVIS NATURAL LANGUAGE ACTIONS
# ==========================================

def clean_command(command):
    """Normalize a spoken command."""
    command = command.lower().strip()
    command = re.sub(r"[?!.,]+", " ", command)
    command = re.sub(r"\s+", " ", command).strip()

    # Remove common conversational prefixes
    prefixes = [
        r"^(?:hey |okay |ok )?jarvis\b[\s,]*",
        r"^(?:please |kindly )+",
        r"^(?:can you|could you|would you)\s+",
        r"^(?:please |kindly )+",
    ]

    for _ in range(3):
        previous = command
        for pattern in prefixes:
            command = re.sub(pattern, "", command).strip()
        if command == previous:
            break

    # Remove polite endings
    command = re.sub(
        r"\s+(?:please|for me|right now)$",
        "",
        command
    ).strip()

    return command


# ==========================================
# WINDOWS VOLUME CONTROL
# ==========================================

def control_volume(action):
    try:
        from pycaw.pycaw import AudioUtilities

        volume = AudioUtilities.GetSpeakers().EndpointVolume

        if action == "up":
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(
                min(1.0, current + 0.10), None
            )
            return "Increasing the volume, sir."

        if action == "down":
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(
                max(0.0, current - 0.10), None
            )
            return "Lowering the volume, sir."

        if action == "mute":
            volume.SetMute(1, None)
            return "Audio muted, sir."

        if action == "unmute":
            volume.SetMute(0, None)
            return "Audio unmuted, sir."

    except Exception as error:
        print("Volume error:", error)
        return "I couldn't adjust the volume, sir."

    return None


# ==========================================
# SEARCH GOOGLE OR YOUTUBE
# ==========================================

def search_web(command):
    """
    Understand:
    search iron man in google
    google iron man
    find python tutorials on google
    look up artificial intelligence
    search iron man on youtube
    play iron man trailer on youtube
    """

    google_patterns = [
        r"^(?:search|find|look up|lookup)\s+(.+?)\s+(?:in|on|using)\s+google$",
        r"^google\s+(.+)$",
        r"^(?:search|find|look up|lookup)\s+google\s+for\s+(.+)$",
        r"^(?:search for|look up|lookup)\s+(.+)$",
    ]

    youtube_patterns = [
        r"^(?:search|find|play|look up|lookup)\s+(.+?)\s+(?:in|on|using)\s+youtube$",
        r"^(?:search|find|play)\s+youtube\s+for\s+(.+)$",
        r"^youtube\s+(.+)$",
    ]

    # YouTube first
    for pattern in youtube_patterns:
        match = re.fullmatch(pattern, command)

        if match:
            query = match.group(1).strip()

            if not query:
                return "What should I search on YouTube, sir?"

            url = (
                "https://www.youtube.com/results?search_query="
                + quote_plus(query)
            )

            webbrowser.open(url)
            return f"Searching YouTube for {query}, sir."

    # Google
    for pattern in google_patterns:
        match = re.fullmatch(pattern, command)

        if match:
            query = match.group(1).strip()

            if not query:
                return "What should I search for, sir?"

            url = (
                "https://www.google.com/search?q="
                + quote_plus(query)
            )

            webbrowser.open(url)
            return f"Searching Google for {query}, sir."

    return None


# ==========================================
# OPEN WINDOWS APPLICATIONS
# ==========================================

def open_application(command):
    """
    Only approved applications are allowed.
    No arbitrary shell commands.
    """

    match = re.fullmatch(
        r"(?:open|launch|start|run)\s+(.+)",
        command
    )

    if not match:
        return None

    app = match.group(1).strip()
    app = re.sub(r"^(?:the|my)\s+", "", app)

    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
    }

    if app in websites:
        webbrowser.open(websites[app])
        return f"Opening {app}, sir."

    applications = {
        "notepad": ("notepad.exe", "Notepad"),
        "calculator": ("calc.exe", "Calculator"),
        "calc": ("calc.exe", "Calculator"),
        "file explorer": ("explorer.exe", "File Explorer"),
        "explorer": ("explorer.exe", "File Explorer"),
        "files": ("explorer.exe", "File Explorer"),
        "paint": ("mspaint.exe", "Paint"),
        "task manager": ("taskmgr.exe", "Task Manager"),
    }

    if app in applications:
        executable, name = applications[app]

        try:
            subprocess.Popen([executable])
            return f"Opening {name}, sir."
        except OSError as error:
            print("Application error:", error)
            return f"I couldn't open {name}, sir."

    if app in ("chrome", "google chrome"):
        chrome = shutil.which("chrome")

        if not chrome:
            return (
                "Chrome wasn't found in the system path, sir."
            )

        try:
            subprocess.Popen([chrome])
            return "Opening Google Chrome, sir."
        except OSError as error:
            print("Chrome error:", error)
            return "I couldn't open Chrome, sir."

    if app in (
        "vs code",
        "visual studio code",
        "visual studio",
        "code"
    ):
        code = shutil.which("code")

        if not code:
            return (
                "VS Code wasn't found in the system path, sir."
            )

        try:
            subprocess.Popen([code])
            return "Opening Visual Studio Code, sir."
        except OSError as error:
            print("VS Code error:", error)
            return "I couldn't open VS Code, sir."

    # Unknown apps go to Ollama instead of being executed.
    return None


# ==========================================
# TIME AND DATE
# ==========================================

def get_time_or_date(command):

    time_phrases = [
        "what time",
        "what's the time",
        "tell me the time",
        "current time",
        "time is it",
    ]

    date_phrases = [
        "what date",
        "what's the date",
        "today's date",
        "todays date",
        "current date",
        "what day is it",
    ]

    if any(phrase in command for phrase in time_phrases):
        now = datetime.now().strftime("%I:%M %p")
        return f"The time is {now}, sir."

    if any(phrase in command for phrase in date_phrases):
        today = datetime.now().strftime("%A, %d %B %Y")
        return f"Today is {today}, sir."

    return None


# ==========================================
# NATURAL VOLUME COMMANDS
# ==========================================

def handle_volume(command):

    unmute_phrases = [
        "unmute",
        "turn sound back on",
        "turn audio back on",
    ]

    mute_phrases = [
        "mute",
        "turn off the sound",
        "silence the audio",
    ]

    volume_up_phrases = [
        "volume up",
        "increase volume",
        "increase the volume",
        "raise volume",
        "raise the volume",
        "turn up the volume",
        "make it louder",
        "louder",
    ]

    volume_down_phrases = [
        "volume down",
        "decrease volume",
        "decrease the volume",
        "lower volume",
        "lower the volume",
        "turn down the volume",
        "make it quieter",
        "quieter",
    ]

    if any(phrase in command for phrase in unmute_phrases):
        return control_volume("unmute")

    if any(phrase in command for phrase in mute_phrases):
        return control_volume("mute")

    if any(phrase in command for phrase in volume_up_phrases):
        return control_volume("up")

    if any(phrase in command for phrase in volume_down_phrases):
        return control_volume("down")

    return None


# ==========================================
# MAIN ACTION ROUTER
# ==========================================

def perform_action(command):

    command = clean_command(command)

    if not command:
        return None

    # SYSTEM STATUS
    if any(phrase in command for phrase in [
        "system status",
        "system report",
        "system health",
        "how is my laptop",
        "how's my laptop",
        "how is my computer",
        "how's my computer",
        "laptop performance",
        "check my laptop"
    ]):
        return get_system_status()

    # CPU
    if any(phrase in command for phrase in [
        "cpu usage",
        "processor usage",
        "cpu load",
        "how busy is my cpu"
    ]):
        return get_cpu_usage()

    # RAM
    if any(phrase in command for phrase in [
        "ram usage",
        "memory usage",
        "how much ram",
        "check my ram"
    ]):
        return get_ram_usage()

    # BATTERY
    if any(phrase in command for phrase in [
        "battery",
        "charging status",
        "charger connected"
    ]):
        return get_battery_status()

    # STORAGE
    if any(phrase in command for phrase in [
        "disk usage",
        "storage space",
        "drive space",
        "how much storage"
    ]):
        return get_disk_usage()

    # Check volume controls
    result = handle_volume(command)
    if result is not None:
        return result

    # Check Google / YouTube searches
    result = search_web(command)
    if result is not None:
        return result

    # Check app opening
    result = open_application(command)
    if result is not None:
        return result

    # Check time / date
    result = get_time_or_date(command)
    if result is not None:
        return result

    # Not a recognized action: let Ollama handle it.
    return None


# ==========================================
# TEST MODE
# ==========================================

if __name__ == "__main__":
    print("JARVIS Natural Command System Ready")
    print("Type 'exit' to stop.\n")

    while True:
        command = input("YOU: ").strip()

        if command.lower() == "exit":
            break

        response = perform_action(command)

        if response is None:
            print("JARVIS: Sending to AI brain.")
        else:
            print("JARVIS:", response)
