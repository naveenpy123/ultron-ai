import streamlit as st
import requests
import psutil
import sqlite3
import platform
import os
import webbrowser
import subprocess
import time
import html
from datetime import datetime

# ============================================================
# ULTRON ULTRA PRO MAX
# ============================================================

APP_NAME = "ULTRON"
MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"
DATABASE = "ultron_memory.db"

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="ULTRON // Neural Command",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "NEURAL CORE"

if "scan" not in st.session_state:
    st.session_state.scan = False

# ============================================================
# DATABASE
# ============================================================

def init_database():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_memory(role, content):
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO memory(role, content, created_at)
            VALUES (?, ?, ?)
            """,
            (
                role,
                content,
                datetime.now().isoformat()
            )
        )

        conn.commit()
        conn.close()

    except Exception:
        pass


def get_memory(limit=20):
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT role, content
            FROM memory
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        result = cur.fetchall()
        conn.close()

        return list(reversed(result))

    except Exception:
        return []


init_database()

# ============================================================
# ULTRON CSS
# ============================================================

st.markdown("""
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

.stApp {
    background:
        radial-gradient(
            circle at 50% 25%,
            rgba(0,180,255,.16),
            transparent 28%
        ),
        radial-gradient(
            circle at 10% 90%,
            rgba(0,100,255,.08),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #010308 0%,
            #020912 45%,
            #000205 100%
        );

    color: #dffaff;
}

/* DIGITAL GRID */

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;

    background-image:
        linear-gradient(
            rgba(0,190,255,.035) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(0,190,255,.035) 1px,
            transparent 1px
        );

    background-size: 35px 35px;

    pointer-events: none;

    z-index: 0;
}

/* MAIN CONTAINER */

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1700px;
}

/* ==========================================================
   HEADER
   ========================================================== */

.ultron-header {
    position: relative;

    border: 1px solid rgba(0,220,255,.35);

    border-radius: 20px;

    padding: 20px 26px;

    background:
        linear-gradient(
            135deg,
            rgba(0,45,65,.72),
            rgba(2,8,15,.86)
        );

    box-shadow:
        0 0 30px rgba(0,210,255,.10),
        inset 0 0 30px rgba(0,210,255,.04);

    backdrop-filter: blur(18px);

    overflow: hidden;
}

.ultron-header:after {
    content: "";

    position: absolute;

    left: 0;
    right: 0;
    bottom: 0;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            #00eaff,
            transparent
        );

    animation: scanline 3s infinite;
}

@keyframes scanline {

    0% {
        transform: translateX(-100%);
    }

    100% {
        transform: translateX(100%);
    }

}

.logo {
    font-size: 40px;

    font-weight: 900;

    letter-spacing: 12px;

    color: #dffcff;

    text-shadow:
        0 0 10px #00eaff,
        0 0 25px rgba(0,220,255,.65);
}

.subtitle {
    margin-top: 4px;

    font-size: 10px;

    letter-spacing: 5px;

    color: #65dff5;

    opacity: .72;
}

.live {
    color: #00ffc3;

    font-weight: 800;

    letter-spacing: 2px;

    text-shadow:
        0 0 12px #00ffc3;
}

.live-dot {
    display: inline-block;

    width: 9px;
    height: 9px;

    border-radius: 50%;

    background: #00ffc3;

    box-shadow:
        0 0 8px #00ffc3,
        0 0 20px #00ffc3;

    animation: blink 1.2s infinite;
}

@keyframes blink {

    50% {
        opacity: .25;
    }

}

/* ==========================================================
   HUD PANELS
   ========================================================== */

.hud {
    background:
        linear-gradient(
            145deg,
            rgba(0,30,45,.70),
            rgba(1,7,13,.86)
        );

    border: 1px solid rgba(0,220,255,.24);

    border-radius: 18px;

    padding: 18px;

    box-shadow:
        0 0 28px rgba(0,180,255,.07),
        inset 0 0 25px rgba(0,180,255,.025);

    backdrop-filter: blur(15px);

    min-height: 205px;
}

.panel-title {
    color: #6beaff;

    font-size: 10px;

    letter-spacing: 4px;

    margin-bottom: 15px;

    text-transform: uppercase;
}

/* ==========================================================
   TELEMETRY
   ========================================================== */

.telemetry {
    display: flex;

    justify-content: space-between;

    padding: 8px 0;

    border-bottom:
        1px solid rgba(255,255,255,.05);

    font-size: 12px;
}

.value {
    color: #00eaff;

    font-weight: bold;

    text-shadow:
        0 0 8px rgba(0,220,255,.65);
}

/* ==========================================================
   REACTOR
   ========================================================== */

.reactor-area {
    display: flex;

    justify-content: center;

    align-items: center;

    min-height: 260px;
}

.reactor {

    width: 185px;

    height: 185px;

    border-radius: 50%;

    position: relative;

    display: flex;

    justify-content: center;

    align-items: center;

    border:
        2px solid #00eaff;

    background:
        radial-gradient(
            circle,
            #ffffff 0%,
            #70efff 5%,
            #009dff 15%,
            #00507a 28%,
            #001521 48%,
            #01060a 68%
        );

    box-shadow:
        0 0 15px #00eaff,
        0 0 35px rgba(0,220,255,.85),
        0 0 90px rgba(0,130,255,.45);

    animation:
        reactorPulse 2.4s infinite ease-in-out;
}

.reactor:before {

    content: "";

    position: absolute;

    width: 230px;
    height: 230px;

    border-radius: 50%;

    border:
        1px dashed rgba(0,225,255,.65);

    animation:
        rotateRing 9s linear infinite;
}

.reactor:after {

    content: "";

    position: absolute;

    width: 270px;
    height: 270px;

    border-radius: 50%;

    border:
        1px solid rgba(0,180,255,.18);

    border-top-color: #00eaff;

    animation:
        rotateRing 13s linear infinite reverse;
}

.reactor-core {

    font-size: 18px;

    font-weight: 900;

    letter-spacing: 3px;

    color: white;

    text-shadow:
        0 0 12px #00eaff;
}

@keyframes reactorPulse {

    0%, 100% {
        transform: scale(.96);
    }

    50% {
        transform: scale(1.04);
    }

}

@keyframes rotateRing {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }

}

/* ==========================================================
   RADAR
   ========================================================== */

.radar {

    width: 150px;

    height: 150px;

    margin: auto;

    border-radius: 50%;

    border:
        1px solid rgba(0,230,255,.7);

    background:
        radial-gradient(
            circle,
            transparent 15%,
            rgba(0,220,255,.04) 16%,
            transparent 17%
        );

    position: relative;

    overflow: hidden;
}

.radar:before {

    content: "";

    position: absolute;

    inset: 50% 0 auto 0;

    height: 1px;

    background: rgba(0,230,255,.4);

}

.radar:after {

    content: "";

    position: absolute;

    left: 50%;

    top: 0;

    width: 1px;

    height: 100%;

    background: rgba(0,230,255,.4);

}

.radar-sweep {

    position: absolute;

    width: 50%;

    height: 50%;

    top: 50%;

    left: 50%;

    transform-origin: 0 0;

    background:
        conic-gradient(
            from 0deg,
            transparent,
            rgba(0,230,255,.55)
        );

    animation:
        radarRotate 3s linear infinite;
}

@keyframes radarRotate {

    to {
        transform: rotate(360deg);
    }

}

/* ==========================================================
   COMMAND TERMINAL
   ========================================================== */

.command-panel {

    background:
        rgba(0,9,15,.82);

    border:
        1px solid rgba(0,220,255,.22);

    border-radius: 18px;

    padding: 20px;

    box-shadow:
        inset 0 0 30px rgba(0,220,255,.025);
}

.user-command {

    padding: 12px 15px;

    margin: 8px 0;

    border-left:
        3px solid #009dff;

    background:
        rgba(0,130,255,.08);

    border-radius: 8px;
}

.ultron-command {

    padding: 12px 15px;

    margin: 8px 0;

    border-left:
        3px solid #00ffc3;

    background:
        rgba(0,255,190,.055);

    border-radius: 8px;
}

/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {

    background:
        linear-gradient(
            135deg,
            rgba(0,100,140,.30),
            rgba(0,30,50,.55)
        );

    border:
        1px solid rgba(0,220,255,.32);

    color: #c9faff;

    border-radius: 10px;

    min-height: 42px;

    transition: .2s;
}

.stButton > button:hover {

    border-color: #00eaff;

    color: white;

    box-shadow:
        0 0 18px rgba(0,220,255,.25);

    transform: translateY(-1px);
}

/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #020b12,
            #010307
        );

    border-right:
        1px solid rgba(0,220,255,.18);
}

/* ==========================================================
   CHAT INPUT
   ========================================================== */

.stChatInput {

    border-radius: 15px;
}

.stChatInput textarea {

    background:
        rgba(0,15,25,.90);

    color: white;
}

/* ==========================================================
   FOOTER
   ========================================================== */

.footer {

    text-align: center;

    font-size: 9px;

    letter-spacing: 4px;

    color: #4bbbd0;

    opacity: .55;

    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# SYSTEM DATA
# ============================================================

cpu = psutil.cpu_percent(interval=0.05)
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage(os.path.abspath(os.sep)).percent

try:
    net = psutil.net_io_counters()

    network = (
        (net.bytes_sent + net.bytes_recv)
        / 1024 / 1024
    )

except Exception:
    network = 0

# ============================================================
# OLLAMA STATUS
# ============================================================

def ollama_online():

    try:

        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=2
        )

        return response.status_code == 200

    except Exception:

        return False


ai_online = ollama_online()

# ============================================================
# HEADER
# ============================================================

status = "ONLINE" if ai_online else "OFFLINE"

st.markdown(
    f"""
    <div class="ultron-header">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

            <div>

                <div class="logo">
                    ULTRON
                </div>

                <div class="subtitle">
                    AUTONOMOUS NEURAL COMMAND SYSTEM
                </div>

            </div>

            <div>

                <span class="live-dot"></span>

                <span class="live">
                    CORE {status}
                </span>

            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ◈ ULTRON CONTROL")

    st.markdown("---")

    st.session_state.mode = st.selectbox(
        "NEURAL MODE",
        [
            "NEURAL CORE",
            "CODING",
            "RESEARCH",
            "VISION",
            "SYSTEM",
            "AUTOMATION"
        ]
    )

    st.markdown("### SYSTEM MODULES")

    enable_memory = st.toggle(
        "🧠 Neural Memory",
        value=True
    )

    enable_vision = st.toggle(
        "👁 Vision System",
        value=False
    )

    enable_voice = st.toggle(
        "🎙 Voice Interface",
        value=False
    )

    enable_web = st.toggle(
        "🌐 Internet Access",
        value=True
    )

    enable_automation = st.toggle(
        "⚙ Automation",
        value=True
    )

    st.markdown("---")

    st.markdown("### CORE")

    st.write(
        f"Model: `{MODEL}`"
    )

    st.write(
        f"Platform: `{platform.system()}`"
    )

    st.write(
        f"Python: `{platform.python_version()}`"
    )

    st.markdown("---")

    if st.button(
        "🗑 PURGE CHAT",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

# ============================================================
# MAIN HUD
# ============================================================

left, center, right = st.columns(
    [1, 1.45, 1]
)

# ============================================================
# LEFT TELEMETRY
# ============================================================

with left:

    st.markdown(
        f"""
        <div class="hud">

            <div class="panel-title">
                SYSTEM TELEMETRY
            </div>

            <div class="telemetry">
                <span>CPU LOAD</span>
                <span class="value">{cpu:.0f}%</span>
            </div>

            <div class="telemetry">
                <span>MEMORY</span>
                <span class="value">{ram:.0f}%</span>
            </div>

            <div class="telemetry">
                <span>STORAGE</span>
                <span class="value">{disk:.0f}%</span>
            </div>

            <div class="telemetry">
                <span>NETWORK</span>
                <span class="value">{network:.1f} MB</span>
            </div>

            <div class="telemetry">
                <span>AI ENGINE</span>
                <span class="value">
                    {"READY" if ai_online else "OFFLINE"}
                </span>
            </div>

            <div class="telemetry">
                <span>NEURAL MODE</span>
                <span class="value">
                    {st.session_state.mode}
                </span>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# CENTER REACTOR
# ============================================================

with center:

    st.markdown(
        """
        <div class="hud">

            <div class="panel-title"
                 style="text-align:center;">

                ULTRON NEURAL REACTOR

            </div>

            <div class="reactor-area">

                <div class="reactor">

                    <div class="reactor-core">
                        ULTRON
                    </div>

                </div>

            </div>

            <div style="
                text-align:center;
                color:#63eaff;
                font-size:10px;
                letter-spacing:4px;
            ">

                NEURAL PROCESSOR ACTIVE

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# RIGHT RADAR
# ============================================================

with right:

    st.markdown(
        """
        <div class="hud">

            <div class="panel-title">
                THREAT / SIGNAL SCANNER
            </div>

            <div class="radar">

                <div class="radar-sweep"></div>

            </div>

            <br>

            <div class="telemetry">
                <span>SIGNAL</span>
                <span class="value">LOCKED</span>
            </div>

            <div class="telemetry">
                <span>SCAN</span>
                <span class="value">ACTIVE</span>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# VISION
# ============================================================

if enable_vision:

    st.markdown("### 👁 VISION MATRIX")

    camera = st.camera_input(
        "ULTRON CAMERA",
        label_visibility="collapsed"
    )

    if camera:

        st.image(
            camera,
            caption="ULTRON VISION FEED",
            use_container_width=True
        )

# ============================================================
# COMMAND TERMINAL
# ============================================================

st.markdown("### ◈ NEURAL COMMAND TERMINAL")

st.markdown(
    '<div class="command-panel">',
    unsafe_allow_html=True
)

if not st.session_state.messages:

    st.markdown(
        """
        <div class="ultron-command">

        <b>ULTRON</b><br><br>

        Neural core initialized.<br>
        All primary command systems are standing by.<br><br>

        <span style="color:#00eaff">
        Awaiting operator command...
        </span>

        </div>
        """,
        unsafe_allow_html=True
    )

else:

    for message in st.session_state.messages:

        content = html.escape(
            message["content"]
        )

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="user-command">

                    <b>OPERATOR</b><br>

                    {content}

                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="ultron-command">

                    <b>ULTRON</b><br>

                    {content}

                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)

# ============================================================
# COMMAND ENGINE
# ============================================================

def execute_command(command):

    cmd = command.lower().strip()

    # SEARCH

    if cmd.startswith("search ") and enable_web:

        query = command[7:].strip()

        webbrowser.open(
            "https://www.google.com/search?q="
            + query.replace(" ", "+")
        )

        return "Web search initiated."

    # WEBSITE

    if cmd.startswith("open website ") and enable_web:

        site = command[13:].strip()

        if not site.startswith("http"):
            site = "https://" + site

        webbrowser.open(site)

        return f"Opening {site}"

    # SYSTEM

    if cmd in [
        "system status",
        "system information",
        "check system"
    ]:

        return (
            f"System telemetry: "
            f"CPU {cpu:.1f}%, "
            f"RAM {ram:.1f}%, "
            f"Storage {disk:.1f}%."
        )

    # TIME

    if cmd == "time":

        return (
            "Current system time is "
            + datetime.now().strftime("%H:%M:%S")
        )

    # DATE

    if cmd == "date":

        return (
            "Current system date is "
            + datetime.now().strftime("%d %B %Y")
        )

    # CALCULATOR

    if cmd == "open calculator" and enable_automation:

        try:

            if platform.system() == "Windows":

                subprocess.Popen(
                    ["calc.exe"]
                )

            elif platform.system() == "Linux":

                subprocess.Popen(
                    ["gnome-calculator"]
                )

            return "Calculator launch command executed."

        except Exception:

            return "Calculator could not be launched."

    return None

# ============================================================
# OLLAMA
# ============================================================

def ask_ollama(prompt):

    history = []

    if enable_memory:

        history = get_memory(12)

    messages = [
        {
            "role": "system",
            "content": f"""
You are ULTRON, a futuristic advanced AI assistant.

Current operating mode:
{st.session_state.mode}

Your responsibilities:
- Answer technical questions.
- Help with programming.
- Analyze information.
- Explain concepts clearly.
- Assist with planning.
- Provide useful and accurate responses.

Be concise but intelligent.

Never claim an action happened unless the application actually performed it.
"""
        }
    ]

    for role, content in history:

        if role in ["user", "assistant"]:

            messages.append(
                {
                    "role": role,
                    "content": content
                }
            )

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.35,
                    "num_ctx": 4096
                }
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]

    except requests.exceptions.ConnectionError:

        return (
            "⚠ ULTRON CORE OFFLINE.\n\n"
            "Ollama is not reachable. "
            "Start Ollama and try again."
        )

    except Exception as error:

        return (
            "⚠ ULTRON ENGINE ERROR:\n"
            + str(error)
        )

# ============================================================
# CHAT
# ============================================================

prompt = st.chat_input(
    "ENTER COMMAND // TALK TO ULTRON..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    if enable_memory:

        save_memory(
            "user",
            prompt
        )

    result = execute_command(prompt)

    if result:

        answer = result

    else:

        with st.spinner(
            "◈ ULTRON NEURAL CORE PROCESSING..."
        ):

            answer = ask_ollama(prompt)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    if enable_memory:

        save_memory(
            "assistant",
            answer
        )

    st.rerun()

# ============================================================
# CONTROL DECK
# ============================================================

st.markdown("### ⚡ CONTROL DECK")

b1, b2, b3, b4, b5 = st.columns(5)

with b1:

    if st.button(
        "◉ NEURAL SCAN",
        use_container_width=True
    ):

        st.session_state.scan = True

        st.toast(
            "Neural scan initialized."
        )

with b2:

    if st.button(
        "🧠 MEMORY",
        use_container_width=True
    ):

        memories = get_memory(10)

        st.info(
            f"{len(memories)} memory records available."
        )

with b3:

    if st.button(
        "🌐 WEB",
        use_container_width=True
    ):

        webbrowser.open(
            "https://www.google.com"
        )

with b4:

    if st.button(
        "⚙ TELEMETRY",
        use_container_width=True
    ):

        st.info(
            f"CPU {cpu:.1f}% | "
            f"RAM {ram:.1f}% | "
            f"DISK {disk:.1f}%"
        )

with b5:

    if st.button(
        "↻ REBOOT UI",
        use_container_width=True
    ):

        st.rerun()

# ============================================================
# STATUS BAR
# ============================================================

st.markdown(
    f"""
    <div class="footer">

        ULTRON // NEURAL COMMAND SYSTEM
        • CORE {status}
        • MODEL {MODEL}
        • {datetime.now().strftime("%H:%M:%S")}

    </div>
    """,
    unsafe_allow_html=True
)
