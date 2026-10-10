# Jarvis: Local AI Desktop Automation Assistant

A local, voice-driven autonomous system assistant built for **macOS**. It pairs local large language model (LLM) reasoning via [Ollama](https://ollama.com/) with **Coqui XTTS v2** for expressive speech synthesis and native macOS automation pipelines.

---

## ⚡ Key Architecture

```text
[ Microphone ]
      |
      v
[ Voice Pipeline (STT) ]
      |  (Wake-word gated)
      v
[ Planner Engine (Ollama: Llama 3.1) ]
      |  (Structured JSON intent generation)
      v
[ Executor & State Controller ] <----> [ Slot-Filling Context Loop ]
      |
      v
[ macOS Action Layer ]
      |  (AppleScript / osascript / CLI APIs)
      v
[ Local XTTS v2 Voice Engine ]
         (Neural speech synthesis)
```

---

## ✨ Core Features

- **Two-Pass Execution Planner:** Converts unstructured voice queries into strict, multi-step JSON execution graphs using `llama3.1:8b`.
- **Dynamic Slot Filling (`ask` step):** If an intent is missing parameters (e.g., timer length), the planner pauses execution, prompts the user via TTS, gathers speech input, and resumes with contextual memory.
- **Deep macOS System Integration:** Direct access to notifications, system appearance (Dark Mode), Wi-Fi, volume, display brightness, Calendar, Reminders, and native URL schemes via AppleScript and native CLI utilities (`pmset`, `screencapture`, `networksetup`).
- **Local Inference:** Runs LLM reasoning and expressive neural audio synthesis locally on your machine. Speech recognition may use the Google Web Speech API, depending on the configured backend.

---

## 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| Reasoning | [Ollama](https://ollama.com/) running `llama3.1:8b` |
| Speech-to-Text | `SpeechRecognition` (Google Web Speech API / local audio capture) |
| Text-to-Speech | Coqui XTTS v2 (PyTorch) via `sounddevice` |
| System Automation | macOS AppleScript (`osascript`), shell commands, and CLI utilities |
| User Interface | Tkinter HUD |

---

## 📋 Prerequisites

- **macOS** (uses native tools such as `osascript`, `open`, `pmset`)
- **Python 3.10+**
- **[Ollama](https://ollama.com/)** installed and running locally
- **Coqui XTTS v2** and its required dependencies
- **Optional utilities** for Bluetooth and brightness control:

  ```bash
  brew install blueutil brightness
  ```

---

## 🚀 Quickstart

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/Anshuman13-code/jarvis-voice-assistant.git
cd jarvis-voice-assistant

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Pull the LLM Model

Make sure Ollama is installed and running, then pull the planner model:

```bash
ollama pull llama3.1:8b
```

### 3. Configure Contacts & Settings

Update your contact mappings in `actions.py`:

```python
CONTACTS = {
    "alice": "11234567890",
    "bob": "19876543210",
}
```

### 4. Run the Assistant

```bash
python brain.py
```

Wake the assistant by saying **"Jarvis"** followed by your command.

---

## 💡 Example Voice Commands

| Category | Example Command | Handled By |
| --- | --- | --- |
| **System Control** | *"Jarvis, turn on dark mode and set volume to 40"* | `actions.change_setting` |
| **Task Automation** | *"Jarvis, time for homework"* | Multi-step plan: opens apps and sites, then prompts for a timer |
| **Productivity** | *"Jarvis, remind me to check deployment logs"* | Native Reminders app via AppleScript |
| **Communication** | *"Jarvis, whatsapp text Alice saying I am on my way"* | URL scheme + automated keystroke execution |
| **Inquiries** | *"Jarvis, explain the difference between SRAM and DRAM"* | Direct response from local Llama 3.1 |

---

## 🔒 Privacy

Jarvis performs LLM reasoning and speech synthesis **locally**. However, speech recognition through the Google Web Speech API requires sending audio to an external service, so the system is **not entirely offline** when that backend is enabled.

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
