import voice, actions, planner

def execute(plan, original_text):

    if plan.get("type") == "answer":
        actions.answer(original_text)
        return

    steps = plan.get("steps", [])

    for step in steps:
        action = step.get("action")

        if action == "ask":
            # Speak the missing parameter question out loud
            voice.speak(step["question"])
            reply = voice.listen()

            if reply:
                # 🧠 NEW: Give the LLM context so it knows what the reply means!
                context_memory = f"Context: You just asked the user '{step['question']}'"
                
                new_plan = planner.create_plan(reply, context=context_memory)
                execute(new_plan, reply)

            return  # ✅ stop loop to wait for the next command chain

        else:
            actions.run(action, step)