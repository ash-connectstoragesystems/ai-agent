import streamlit as st
import json
import os
import asyncio
from datetime import datetime
from telegram import Bot
from gpt4all import GPT4All

# -------------------------------
# CONFIG
# -------------------------------

BOT_TOKEN = "8739715981:AAHPojn9d8kU-uKzmk3w-I_m0CFCI2twsVA"
CHAT_ID = 8675971003

MODEL_FOLDER = r"C:\Users\ash\PyCharmMiscProject\models\mistral-7b-instruct-v0.1.Q4_K_M"
MODEL_NAME = "mistral-local.gguf"

DATA_FILE = "agent_data.json"

# -------------------------------
# LOAD DATA
# -------------------------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"tasks": [], "memory": [], "chat": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# -------------------------------
# LOAD MODEL
# -------------------------------

st.title("🚀 Ultimate AI Agent")

try:
    class FakeModel:
        def generate(self, prompt):
            return "AI response for: " + prompt


    model = FakeModel()
    st.success("AI Loaded ✅")
except Exception as e:
    st.error(e)
    st.stop()

# -------------------------------
# TELEGRAM
# -------------------------------

async def send_telegram(msg):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=msg)
    await bot.close()

# -------------------------------
# MULTI AGENTS
# -------------------------------

def decision_agent(task):
    prompt = f"Rate task 1-10 based on importance: {task}. Only number."
    res = model.generate(prompt)
    return min(int(''.join(filter(str.isdigit, res))[:2] or 0), 10)

def planner_agent(task):
    return model.generate(f"Create step-by-step plan: {task}")

def research_agent(task):
    return model.generate(f"Give insights or ideas for: {task}")

def executor_agent(task):
    # Simple real execution simulation
    if "open google" in task.lower():
        os.system("start https://www.google.com")
        return "Opened Google"
    if "create file" in task.lower():
        with open("output.txt", "w") as f:
            f.write("File created by AI")
        return "File created"
    return "No real execution"

# -------------------------------
# UI TABS
# -------------------------------

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💬 Chat", "⚙️ Tasks"])

# -------------------------------
# TAB 1: DASHBOARD
# -------------------------------

with tab1:
    st.subheader("Tasks Overview")

    for t in data["tasks"]:
        st.write(f"{t['task']} | {t['status']}")

    st.subheader("Memory")

    for m in data["memory"][-5:]:
        with st.expander(m["task"]):
            st.write(m)

# -------------------------------
# TAB 2: CHAT (B)
# -------------------------------

with tab2:
    st.subheader("AI Chat")

    user_input = st.text_input("Ask something")

    if st.button("Send"):
        if user_input:
            response = model.generate(user_input)

            data["chat"].append({"user": user_input, "ai": response})
            save_data(data)

    # Load last 5 chat messages safely
    chat_history = data.get("chat", [])  # Returns [] if "chat" key does not exist
    for chat in chat_history[-5:]:
        st.write(f"👤 {chat['user']}")
        st.write(f"🤖 {chat['ai']}")

# -------------------------------
# TAB 3: TASK SYSTEM (A + D)
# -------------------------------

with tab3:
    st.subheader("Add Task")

    new_task = st.text_input("Task")

    if st.button("Add Task"):
        if new_task:
            data["tasks"].append({
                "task": new_task,
                "status": "pending",
                "time": str(datetime.now())
            })
            save_data(data)
            st.success("Task added")
            st.rerun()

    st.subheader("Processing Tasks")

    for task_obj in data["tasks"]:
        if task_obj["status"] == "pending":

            task = task_obj["task"]

            score = decision_agent(task)

            if score >= 6:

                plan = planner_agent(task)
                research = research_agent(task)
                execution = executor_agent(task)

                task_obj["status"] = "done"

                memory_entry = {
                    "task": task,
                    "score": score,
                    "plan": plan,
                    "research": research,
                    "execution": execution
                }

                data["memory"].append(memory_entry)

                msg = f"""
🚀 AI AGENT

Task: {task}
Score: {score}

Plan:
{plan}

Research:
{research}

Execution:
{execution}
"""
                asyncio.run(send_telegram(msg))

    save_data(data)