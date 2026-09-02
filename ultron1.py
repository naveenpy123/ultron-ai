#!/usr/bin/env python3

import os
import sys
import sqlite3
import subprocess
import requests
import json
import datetime
import webbrowser
import re
import shutil

# ============================================================
# ULTRON MOBILE AI
# Designed for Android + Termux + llama.cpp
# ============================================================

APP_NAME = "ULTRON MOBILE"
VERSION = "1.0"

# llama.cpp server
LLAMA_URL = "http://127.0.0.1:8080"

# SQLite memory
DB_FILE = os.path.expanduser("~/ultron_memory.db")

# ============================================================
# COLORS
# ============================================================

RESET = "\033[0m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"

# ============================================================
# DATABASE
# ============================================================

def init_database():
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_memory(role, message):
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO memory(role, message, timestamp)
        VALUES (?, ?, ?)
        """,
        (
            role,
            message,
            datetime.datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_memory(limit=12):
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, message
        FROM memory
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    conn.close()

    rows.reverse()

    return rows


def clear_memory():
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM memory")

    conn.commit()
    conn.close()


# ============================================================
# TERMINAL
# ============================================================

def clear_screen():
    os.system("clear")


def banner():

    print(CYAN + BOLD)

    print(r"""
╔══════════════════════════════════════════════╗
║                                              ║
║              U L T R O N                    ║
║          MOBILE AI ASSISTANT                ║
║                                              ║
║       LOCAL INTELLIGENCE SYSTEM              ║
║                                              ║
╚══════════════════════════════════════════════╝
""")

    print(RESET)

    print(
        DIM +
        f"Version {VERSION} | Android Mobile Edition" +
        RESET
    )

    print()


# ============================================================
# SPEAK
# ============================================================

def speak(text):

    text = str(text)

    # Android Termux TTS
    if shutil.which("termux-tts-speak"):

        try:
            subprocess.Popen(
                [
                    "termux-tts-speak",
                    text
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return

        except Exception:
            pass

    print(DIM + "[TTS unavailable]" + RESET)


# ============================================================
# LISTEN
# ============================================================

def listen():

    if shutil.which("termux-speech-to-text"):

        try:

            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True,
                text=True
            )

            text = result.stdout.strip()

            if text:
                return text

        except Exception:
            pass

    print(
        YELLOW +
        "Voice input is unavailable. Type your command." +
        RESET
    )

    return input(CYAN + "YOU > " + RESET)


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def device_info():

    print(GREEN + "\nDEVICE INFORMATION\n" + RESET)

    commands = {
        "Android": "getprop ro.build.version.release",
        "Device": "getprop ro.product.model",
        "Manufacturer": "getprop ro.product.manufacturer",
        "CPU": "getprop ro.hardware",
        "Architecture": "uname -m"
    }

    for name, command in commands.items():

        try:

            result = subprocess.check_output(
                command,
                shell=True,
                text=True
            ).strip()

            print(f"{name:15}: {result}")

        except Exception:

            print(f"{name:15}: Unknown")

    print()


# ============================================================
# TIME
# ============================================================

def show_time():

    now = datetime.datetime.now()

    response = (
        f"The current time is "
        f"{now.strftime('%I:%M %p')}."
    )

    print(GREEN + response + RESET)

    speak(response)


# ============================================================
# DATE
# ============================================================

def show_date():

    now = datetime.datetime.now()

    response = (
        f"Today is "
        f"{now.strftime('%A, %d %B %Y')}."
    )

    print(GREEN + response + RESET)

    speak(response)


# ============================================================
# CALCULATOR
# ============================================================

def calculator(expression):

    expression = expression.strip()

    # Allow only calculator characters
    if not re.fullmatch(
        r"[0-9+\-*/().% \t]+",
        expression
    ):
        return "I can only calculate basic mathematical expressions."

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return f"The answer is {result}"

    except Exception:

        return "I couldn't calculate that."


# ============================================================
# LLAMA SERVER CHECK
# ============================================================

def llama_available():

    try:

        response = requests.get(
            LLAMA_URL,
            timeout=2
        )

        return response.status_code < 500

    except Exception:

        return False


# ============================================================
# LOCAL AI
# ============================================================

def ask_ultron(prompt):

    history = get_memory(10)

    messages = [
        {
            "role": "system",
            "content": """
You are ULTRON MOBILE, a helpful personal AI assistant
running locally on an Android phone.

Be concise, intelligent and friendly.

You are running on a Vivo T4x 5G.

Do not claim to have performed actions that you did not actually perform.

When the user asks a simple question, answer directly.
"""
        }
    ]

    for role, message in history:

        messages.append(
            {
                "role": role,
                "content": message
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    payload = {
        "messages": messages,
        "temperature": 0.4,
        "stream": False
    }

    try:

        response = requests.post(
            f"{LLAMA_URL}/v1/chat/completions",
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        answer = (
            data["choices"][0]
            ["message"]
            ["content"]
            .strip()
        )

        save_memory("user", prompt)
        save_memory("assistant", answer)

        return answer

    except requests.exceptions.ConnectionError:

        return (
            "My local AI server is not running.\n\n"
            "Start llama-server first."
        )

    except Exception as error:

        return f"AI connection error: {error}"


# ============================================================
# COMMAND ENGINE
# ============================================================

def process_command(command):

    original = command

    command = command.lower().strip()

    # EXIT
    if command in [
        "exit",
        "quit",
        "shutdown",
        "goodbye"
    ]:

        print(
            CYAN +
            "\nULTRON shutting down. Goodbye.\n" +
            RESET
        )

        speak("ULTRON shutting down.")

        sys.exit(0)

    # HELP
    if command in [
        "help",
        "commands"
    ]:

        show_help()

        return

    # TIME
    if command in [
        "time",
        "what time is it"
    ]:

        show_time()

        return

    # DATE
    if command in [
        "date",
        "what is today's date",
        "today"
    ]:

        show_date()

        return

    # DEVICE
    if command in [
        "device",
        "device info",
        "phone info",
        "system info"
    ]:

        device_info()

        return

    # MEMORY
    if command in [
        "memory",
        "show memory"
    ]:

        history = get_memory(20)

        print(
            GREEN +
            "\nULTRON MEMORY\n" +
            RESET
        )

        for role, message in history:

            print(
                f"{role.upper()}: {message}"
            )

        print()

        return

    # CLEAR MEMORY
    if command in [
        "clear memory",
        "forget everything"
    ]:

        clear_memory()

        print(
            GREEN +
            "ULTRON memory cleared." +
            RESET
        )

        return

    # VOICE
    if command in [
        "voice",
        "listen",
        "voice mode"
    ]:

        print(
            CYAN +
            "Listening..." +
            RESET
        )

        spoken = listen()

        if spoken:

            print(
                WHITE +
                "YOU > " +
                spoken +
                RESET
            )

            response = process_command(spoken)

            if response:
                print(
                    GREEN +
                    "ULTRON > " +
                    response +
                    RESET
                )

                speak(response)

        return

    # CALCULATOR
    if command.startswith("calculate "):

        expression = original[10:]

        response = calculator(expression)

        print(
            GREEN +
            "ULTRON > " +
            response +
            RESET
        )

        speak(response)

        return

    # OPEN WEBSITE
    if command.startswith("open "):

        target = original[5:].strip()

        if target.startswith("http://") or \
           target.startswith("https://"):

            url = target

        else:

            url = "https://" + target

        try:

            webbrowser.open(url)

            response = f"Opening {target}."

        except Exception:

            response = "I couldn't open that website."

        print(
            GREEN +
            "ULTRON > " +
            response +
            RESET
        )

        speak(response)

        return

    # AI
    response = ask_ultron(original)

    print(
        GREEN +
        "\nULTRON > " +
        RESET +
        response +
        "\n"
    )

    # Keep speech reasonably short
    if len(response) < 600:
        speak(response)

    return response


# ============================================================
# HELP
# ============================================================

def show_help():

    print(
        CYAN +
        """
ULTRON COMMANDS
────────────────────────────────

help
time
date
device info

voice
memory
clear memory

calculate 25 * 4
open google.com

exit

Anything else is sent to
the local AI model.

────────────────────────────────
""" +
        RESET
    )


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    init_database()

    clear_screen()

    banner()

    print(
        YELLOW +
        "Checking local AI server..." +
        RESET
    )

    if llama_available():

        print(
            GREEN +
            "● LOCAL AI ONLINE" +
            RESET
        )

    else:

        print(
            RED +
            "● LOCAL AI OFFLINE" +
            RESET
        )

        print(
            DIM +
            "Start llama-server before chatting." +
            RESET
        )

    print()

    print(
        CYAN +
        "Type 'help' for commands." +
        RESET
    )

    print()

    while True:

        try:

            command = input(
                CYAN +
                "YOU > " +
                RESET
            ).strip()

            if not command:
                continue

            process_command(command)

        except KeyboardInterrupt:

            print(
                "\n" +
                YELLOW +
                "Use 'exit' to shut down ULTRON." +
                RESET
            )

        except Exception as error:

            print(
                RED +
                f"ULTRON ERROR: {error}" +
                RESET
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
