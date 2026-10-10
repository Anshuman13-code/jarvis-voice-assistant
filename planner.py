import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

# -------- CLEAN JSON EXTRACTION --------

def extract_json(text):
    """
    Extract valid JSON even if model adds extra text.
    """
    try:
        return json.loads(text)
    except:
        # try to extract JSON block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return None

# -------- MAIN PLANNER --------

def create_plan(text, context=""):
    prompt = f"""
You are Jarvis, an intelligent system assistant.

Your job is to convert the user's request into an execution plan.

STRICT RULES:
- Output ONLY valid JSON
- No explanation, no extra text
- Always use provided actions only
- NEVER use "ask" to repeat the user's question. "ask" is ONLY for requesting missing parameters for a task (e.g., "How many minutes?").
- If the user wants to search for something, construct the search URL directly in 'open_site'. DO NOT use 'ask'.
  - YouTube searches: "https://www.youtube.com/results?search_query=your+search+term"
  - Google searches: "https://www.google.com/search?q=your+search+term"

BEHAVIOR:
- Questions (Facts, News, Sports, Math, General Info) → type = "answer"
- System Tasks (Apps, Sites, Media, Settings) → type = "task"
- Missing task parameters → include "ask"

AVAILABLE ACTIONS:
open_app, open_site, focus_mode, timer, setting,
add_reminder, add_event, whatsapp,
volume, brightness, battery,
screenshot, sleep, empty_trash,
music, message, stream, ask

FORMAT:
{{
  "type": "task" | "answer",
  "steps": [
    {{"action": "action_name", "target": "item", "value": "state_or_text", "mode": "optional_call_type"}}
  ]
}}

EXAMPLES:

User: "which IPL teams are playing today"
→ {{
  "type": "answer",
  "steps": []
}}

User: "time for homework"
→ {{
  "type": "task",
  "steps": [
    {{"action": "open_app", "target": "WhatsApp"}},
    {{"action": "open_site", "target": "gemini.google.com"}},
    {{"action": "open_app", "target": "Spotify"}},
    {{"action": "ask", "question": "How long should I set the timer for?"}}
  ]
}}

User: "search systolic arrays in youtube"
→ {{
  "type": "task",
  "steps": [
    {{"action": "open_site", "target": "https://www.youtube.com/results?search_query=systolic+arrays"}}
  ]
}}

User: "turn on dark mode"
→ {{
  "type": "task",
  "steps": [
    {{"action": "setting", "target": "dark mode", "value": "on"}}
  ]
}}

User: "remind me to check the vivado logs"
→ {{
  "type": "task",
  "steps": [
    {{"action": "add_reminder", "target": "check the vivado logs"}}
  ]
}}

User: "whatsapp text Shuvam saying I will be 10 minutes late"
→ {{
  "type": "task",
  "steps": [
    {{"action": "whatsapp", "target": "shuvam", "value": "I will be 10 minutes late", "mode": "text"}}
  ]
}}

User: "video call Dr. Dey on whatsapp"
→ {{
  "type": "task",
  "steps": [
    {{"action": "whatsapp", "target": "dr. dey", "mode": "video"}}
  ]
}}

CONTEXT:
{context}

USER:
"{text}"
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 300 
                }
            },
            timeout=15
        )

        raw_output = response.json().get("response", "").strip()
        print("\n[PLANNER RAW OUTPUT]\n", raw_output)

        plan = extract_json(raw_output)

        if plan:
            return plan

        # fallback if parsing fails
        return {
            "type": "answer",
            "steps": [],
            "fallback_text": text
        }

    except Exception as e:
        print("Planner Error:", e)

        return {
            "type": "answer",
            "steps": [],
            "fallback_text": text
        }