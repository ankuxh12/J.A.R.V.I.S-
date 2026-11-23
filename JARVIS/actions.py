import pyautogui
import re
import shutil
import subprocess
import win32gui
import win32process
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
from memory import (
    save_memory,
    get_memory,
    get_all_memories,
    delete_memory
)


# ==========================================
# JARVIS NATURAL LANGUAGE ACTIONS
# ==========================================

def normalize_hinglish(command):
    """Convert a small, explicit set of Roman-Hindi commands to existing intents.

    Unrecognized phrases pass through unchanged to the AI brain.
    """
    # Commands are matched in full to avoid accidentally executing casual speech.
    app_names = {
        "chrome": "chrome", "google chrome": "chrome",
        "calculator": "calculator", "calc": "calculator",
        "notepad": "notepad", "paint": "paint",
        "file explorer": "file explorer", "explorer": "explorer",
        "task manager": "task manager", "vs code": "vs code",
        "visual studio code": "vs code", "youtube": "youtube",
        "google": "google", "gmail": "gmail", "github": "github",
    }
    match = re.fullmatch(r"(.+?)\s+(?:kholo|khol do|open karo|chalao|chalu karo)", command)
    if match:
        app = match.group(1).strip()
        if app in app_names:
            return "open " + app_names[app]

    # "youtube par python search karo", "google pe weather dhundo"
    match = re.fullmatch(
        r"(youtube|google)\s+(?:par|pe|mein|me)\s+(.+?)\s+"
        r"(?:search karo|search kar do|dhundo|dhundho)", command
    )
    if match:
        site, query = match.groups()
        return f"search {query} on {site}"

    # "python youtube par search karo", "weather google pe search karo"
    match = re.fullmatch(
        r"(.+?)\s+(youtube|google)\s+(?:par|pe|mein|me)\s+"
        r"(?:search karo|search kar do|dhundo|dhundho)", command
    )
    if match:
        query, site = match.groups()
        return f"search {query} on {site}"

    volume_commands = {
        "volume badhao": "volume up",
        "volume badha do": "volume up",
        "awaz badhao": "volume up",
        "awaaz badhao": "volume up",
        "volume kam karo": "volume down",
        "volume ghatao": "volume down",
        "awaz kam karo": "volume down",
        "awaaz kam karo": "volume down",
        "mute karo": "mute",
        "unmute karo": "unmute",
        "awaz band karo": "mute",
        "awaaz band karo": "mute",
        "awaz chalu karo": "unmute",
        "awaaz chalu karo": "unmute",
    }
    if command in volume_commands:
        return volume_commands[command]

    status_commands = {
        "system status batao": "system status",
        "laptop ka status batao": "system status",
        "cpu usage batao": "cpu usage",
        "ram usage batao": "ram usage",
        "battery kitni hai": "battery",
        "storage kitni hai": "how much storage",
        "time batao": "tell me the time",
        "kitne baje hain": "tell me the time",
        "aaj ki date batao": "today's date",
    }
    return status_commands.get(command, command)


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

    return normalize_hinglish(command)


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

def handle_memory(command):
    # Save: "remember that my favorite superhero is Iron Man"
    match = re.fullmatch(
        r"(?:remember that|remember)\s+(.+?)\s+is\s+(.+)",
        command
    )

    if match:
        key = match.group(1).strip()
        value = match.group(2).strip()

        save_memory(key, value)
        return f"I'll remember that {key} is {value}, sir."

    # Recall: "what's my favorite superhero?"
    match = re.fullmatch(
        r"(?:what is|what's)\s+(.+)",
        command
    )

    if match:
        key = match.group(1).strip()
        key = re.sub(r"^(?:my|the)\s+", "", key)

        memories = get_all_memories()

        for saved_key, value in memories.items():
            normalized_key = re.sub(
                r"^(?:my|the)\s+", "", saved_key
            )

            if key == normalized_key:
                return f"{saved_key.capitalize()} is {value}, sir."

    # List stored memories
    if command in (
        "what do you remember about me",
        "show my memories",
        "list my memories"
    ):
        memories = get_all_memories()

        if not memories:
            return "I haven't saved any memories yet, sir."

        facts = [
            f"{key} is {value}"
            for key, value in memories.items()
        ]

        return "I remember that " + "; ".join(facts) + "."

    # Forget one fact
    match = re.fullmatch(
        r"(?:forget|delete memory about)\s+(.+)",
        command
    )

    if match:
        key = match.group(1).strip()

        if delete_memory(key):
            return f"I've forgotten {key}, sir."

        return "I couldn't find that memory, sir."

    return None

def get_active_browser():
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return None

    title = win32gui.GetWindowText(hwnd)

    if not title:
        return None

    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    import os
    import psutil

    try:
        process_name = psutil.Process(pid).name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

    if process_name == "chrome.exe":
        return {"browser": "Google Chrome", "title": title}

    if process_name == "msedge.exe":
        return {"browser": "Microsoft Edge", "title": title}

    return None


def handle_desktop_control(command):
    if command in ("scroll down", "neeche scroll karo", "scroll neeche"):
        pyautogui.scroll(-5)
        return "Scrolling down, sir."


    if command in ("scroll up", "upar scroll karo", "scroll upar"):
        pyautogui.scroll(5)
        return "Scrolling up, sir."

    
    if command in ("click", "mouse click", "click here"):
        pyautogui.click()
        return "Clicked, sir."


    if command in ("double click", "double-click"):
        pyautogui.doubleClick()
        return "Double-clicked, sir."


    if command in ("right click", "right-click"):
        pyautogui.rightClick()
        return "Right-clicked, sir."
    
    if command in (
        "which browser is open",
        "what browser am i using",
        "what page am i on",
        "which page is open",
    ):
        info = get_active_browser()

        if info is None:
            return "Sir, Chrome or Edge is not the active window."

        return (
            f"Sir, you're using {info['browser']}. "
            f"The active window is titled {info['title']}."
        )
    return None


def perform_action(command):

    command = clean_command(command)
        # Permanent memory
    result = handle_memory(command)
    result = handle_desktop_control(command)


    if result is not None:
        return result

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
