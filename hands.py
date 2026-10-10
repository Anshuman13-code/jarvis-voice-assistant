import os

def execute_command(intent_dict):
    intent = intent_dict.get('intent')
    target = intent_dict.get('target', '')
    query = intent_dict.get('query', '')

    print(f"\n>>> EXECUTION: {intent.upper()} <<<")

    try:
        if intent == 'open_app':
            os.system(f"open -a '{target}'")

        elif intent == 'open_site':
            url = target if 'http' in target else f"https://{target}"
            os.system(f"open '{url}'")

        elif intent == 'system_control':
            t = target.lower()

            if 'screenshot' in t:
                os.system("screencapture -t jpg ~/Desktop/Jarvis_Shot.jpg")

            elif 'sleep' in t:
                os.system("pmset sleepnow")

            elif 'trash' in t:
                confirm = input("⚠️ Confirm delete trash? (yes/no): ")
                if confirm.lower() == "yes":
                    os.system("rm -rf ~/.Trash/*")

        elif intent == 'search':
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            os.system(f"open '{search_url}'")

        else:
            print("Unknown intent.")

    except Exception as e:
        print(f"Execution Error: {e}")