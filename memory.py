import json, os

FILE = "memory.json"

def load():
    if not os.path.exists(FILE):
        return {"history":[]}
    with open(FILE,"r") as f:
        return json.load(f)

def save(data):
    with open(FILE,"w") as f:
        json.dump(data,f)

def update(text):
    data = load()
    data["history"].append(text)
    data["history"] = data["history"][-20:]
    save(data)

def get_context():
    return load()