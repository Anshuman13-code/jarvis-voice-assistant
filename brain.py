import voice
import planner
import executor
import memory
import os
os.system("afplay ~/Desktop/JarvisProject/startup.mp3 &")

def run():
    voice.speak("Ready.")

    while True:
        text = voice.listen_wake()   # wake word gated
        if not text:
            continue

        print("User:", text)

        ctx = memory.get_context()
        plan = planner.create_plan(text, ctx)

        executor.execute(plan, text)

        memory.update(text)

if __name__ == "__main__":
    run()