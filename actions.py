import os
import threading
import time
import subprocess
import voice
import re
import sys
import requests

# -------- ACTION DISPATCH --------

def run(action, step):
    ACTIONS = {
        "open_app": open_app,
        "open_site": open_site,
        "focus_mode": focus_mode,
        "timer": set_timer,
        "volume": set_volume,
        "brightness": set_brightness,
        "battery": battery_status,
        "screenshot": screenshot,
        "sleep": sleep_system,
        "empty_trash": empty_trash,
        "music": play_music,
        "message": open_messaging,
        "whatsapp": whatsapp_action,
        "stream": open_streaming,
        "setting": change_setting,
        "add_reminder": add_reminder,
        "add_event": add_event
    }

    fn = ACTIONS.get(action)
    if fn:
        fn(step)
    else:
        print("Unknown action:", action)


# -------- SYSTEM AUTOMATION --------

def add_reminder(step):
    task = step.get("target", "New Task").replace('"', '\\"')
    
    script = f"""
    osascript -e '
    tell application "Reminders"
        if not (exists list "Reminders") then
            make new list with properties {{name:"Reminders"}}
        end if
        tell list "Reminders"
            make new reminder with properties {{name:"{task}"}}
        end tell
    end tell'
    """
    os.system(script)
    voice.speak(f"I've added {task} to your reminders.")

def add_event(step):
    event_name = step.get("target", "New Event").replace('"', '\\"')
    
    script = f"""
    osascript -e '
    set today to current date
    tell application "Calendar"
        tell calendar 1
            make new event at end with properties {{summary:"{event_name}", start date:today, allday event:true}}
        end tell
    end tell'
    """
    os.system(script)
    voice.speak(f"I've scheduled {event_name} for today.")

def change_setting(step):
    target = step.get("target", "").lower()
    state = step.get("value", "").lower()

    if "dark mode" in target or "theme" in target:
        if state == "on":
            os.system("osascript -e 'tell app \"System Events\" to tell appearance preferences to set dark mode to true'")
            voice.speak("Dark mode enabled.")
        elif state == "off":
            os.system("osascript -e 'tell app \"System Events\" to tell appearance preferences to set dark mode to false'")
            voice.speak("Light mode enabled.")
        else:
            os.system("osascript -e 'tell app \"System Events\" to tell appearance preferences to set dark mode to not dark mode'")
            voice.speak("Switched system theme.")

    elif "wifi" in target or "wi-fi" in target:
        power = "on" if state == "on" else "off"
        os.system(f"networksetup -setairportpower en0 {power}")
        voice.speak(f"Wi-Fi turned {power}.")

    elif "bluetooth" in target:
        power = "1" if state == "on" else "0"
        os.system(f"blueutil -p {power}")
        txt = "on" if state == "on" else "off"
        voice.speak(f"Bluetooth turned {txt}.")
        
    elif "volume" in target:
        level = step.get("value", "50")
        os.system(f"osascript -e 'set volume output volume {level}'")
        voice.speak(f"Volume set to {level} percent.")
    else:
        voice.speak("I don't have access to that setting yet.")


# -------- CORE --------

def open_app(step):
    os.system(f"open -a '{step.get('target')}'")

def open_site(step):
    url = step.get("target")
    if "http" not in url:
        url = "https://" + url
    os.system(f"open '{url}'")


# -------- PRODUCTIVITY --------

def focus_mode(step):
    voice.speak("Focus mode on.")
    os.system("osascript -e 'tell application \"System Events\" to key code 144'")

def set_timer(step):
    raw_target = str(step.get("target", "10"))
    match = re.search(r'\d+', raw_target)
    mins = int(match.group()) if match else 10

    voice.speak(f"Setting a timer for {mins} minutes.")

    ui_script = f"""
import tkinter as tk
import os

root = tk.Tk()
root.title('Jarvis')
root.geometry('220x80')
root.attributes('-topmost', True) 
root.configure(bg='#1c1c1e') 

time_left = {mins} * 60

label = tk.Label(root, text='', font=('Menlo', 40, 'bold'), fg='#0a84ff', bg='#1c1c1e')
label.pack(expand=True)

def update():
    global time_left
    if time_left > 0:
        m, s = divmod(time_left, 60)
        label.config(text=f'{{m:02d}}:{{s:02d}}')
        time_left -= 1
        root.after(1000, update)
    else:
        label.config(text='00:00', fg='#ff453a')
        os.system('osascript -e \\'display notification "Time is up!" with title "Jarvis Timer" sound name "Glass"\\'')
        root.after(4000, root.destroy)

update()
root.mainloop()
"""
    
    with open("jarvis_timer_ui.py", "w") as f:
        f.write(ui_script)
        
    subprocess.Popen([sys.executable, "jarvis_timer_ui.py"])
    
    def timer_voice():
        time.sleep(mins * 60)
        voice.speak(f"Your {mins} minute timer is up.")

    threading.Thread(target=timer_voice, daemon=True).start()

# -------- HARDWARE/SYSTEM --------

def set_volume(step):
    level = step.get("target", "50")
    os.system(f"osascript -e 'set volume output volume {level}'")

def set_brightness(step):
    level = step.get("target", "50")
    os.system(f"brightness {level}/100") 

def battery_status(step):
    output = subprocess.getoutput("pmset -g batt")
    match = re.search(r'(\d+)%', output)
    percent = match.group(1) if match else "an unknown"
    state = "charging" if "AC Power" in output else "running on battery"
    voice.speak(f"Sir, the battery is at {percent} percent and is currently {state}.")
    
def screenshot(step):
    os.system("screencapture ~/Desktop/jarvis_shot.png")
    voice.speak("Screenshot taken.")

def sleep_system(step):
    os.system("pmset sleepnow")

def empty_trash(step):
    os.system("rm -rf ~/.Trash/*")
    voice.speak("Trash emptied.")


# -------- COMMUNICATION --------

def open_messaging(step):
    target = step.get("target", "").lower()
    if "whatsapp" in target:
        os.system("open -a 'WhatsApp'")
    elif "gmail" in target:
        os.system("open 'https://mail.google.com'")
    elif "discord" in target:
        os.system("open -a 'Discord'")

def whatsapp_action(step):
    import urllib.parse
    
    # JARVIS CONTACT BOOK
    # Add actual numbers here (Country code + Number, no + sign or spaces)
    CONTACTS = {
    "user_1": os.getenv("CONTACT_USER_1", "1234567890"),
    "user_2": os.getenv("CONTACT_USER_2", "1234567890"),
    }

    name = step.get("target", "").lower()
    message = step.get("value", "")
    mode = step.get("mode", "text").lower()

    phone = None
    for key in CONTACTS:
        if key in name:
            phone = CONTACTS[key]
            break

    if not phone:
        voice.speak(f"Sir, I don't have a phone number saved for {name}.")
        return

    if mode == "text":
        voice.speak(f"Sending your message to {name}.")
        encoded_msg = urllib.parse.quote(message)
        os.system(f"open 'whatsapp://send?phone={phone}&text={encoded_msg}'")
        time.sleep(1.5)
        os.system("osascript -e 'tell application \"System Events\" to keystroke return'")

    elif mode in ["audio", "video"]:
        voice.speak(f"Initiating a {mode} call with {name}.")
        os.system(f"open 'whatsapp://send?phone={phone}'")
        time.sleep(1.5)
        if mode == "video":
            os.system("osascript -e 'tell application \"System Events\" to keystroke \"v\" using {command down, shift down}'")
        else:
            os.system("osascript -e 'tell application \"System Events\" to keystroke \"d\" using {command down, shift down}'")

# -------- ENTERTAINMENT --------

def open_streaming(step):
    target = step.get("target", "").lower()
    if "youtube" in target:
        os.system("open 'https://youtube.com'")
    elif "twitch" in target:
        os.system("open 'https://twitch.tv'")
    elif "anime" in target:
        os.system("open 'https://zoro.to'")

def play_music(step):
    target = step.get("target", "").lower()
    if "spotify" in target:
        os.system("open -a 'Spotify'")
    else:
        os.system("open -a 'Spotify'")

def answer(text):
    import requests
    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.1:8b",
            "prompt": f"""
You are Jarvis.

Reply naturally in 1–2 short sentences.
No lists. No robotic tone.

User: {text}
""",
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": 60}
        }, timeout=5)

        reply = res.json().get("response", "").replace("\n", " ").strip()
        voice.speak(reply)
        
    except requests.exceptions.ConnectionError:
        voice.speak("I'm sorry sir, my local LLM brain is currently offline. Please start Ollama.")
    except Exception as e:
        voice.speak("I encountered an error connecting to my neural net.")
        print(f"Brain Error: {e}")