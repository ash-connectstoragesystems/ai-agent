import streamlit as st
import json
import os
import asyncio
from gpt4all import GPT4All
from telegram import Bot
from telegram.error import RetryAfter

# -------------------------------
# CONFIGURATION
# -------------------------------

BOT_TOKEN = "8739715981:AAHPojn9d8kU-uKzmk3w-I_m0CFCI2twsVA"
CHAT_ID = 8675971003  # Your Telegram chat ID

DATA_FILE = "agent_data.json"

# -------------------------------
# LOAD DATA
# -------------------------------

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {"tasks": [], "memory": [], "chat": []}

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

data = load_json(DATA_FILE)

# -------------------------------
# STREAMLIT APP
# -------------------------------

st.title("🚀 Ultimate AI Agent")
st.write("AI Loaded ✅")

st.subheader("📊 Dashboard")

# -------------------------------
# FAKE GPT4All for Streamlit Cloud
# -------------------------------
class FakeModel:
    def generate(self, prompt):
        return "AI response for: " + prompt

model = FakeModel()  # TEMP for Streamlit Cloud

# -------------------------------
# TELEGRAM FUNCTION (with flood control)
# -------------------------------
async def send_telegram(msg):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=f"✅ Approved Action:\n- {msg}")
    except RetryAfter as e:
        wait_time = e.retry_after
        st.warning(f"Telegram flood control active. Wait {wait_time} seconds.")
        await asyncio.sleep(wait_time)
        await bot.send_message(chat_id=CHAT_ID, text=f"✅ Approved Action:\n- {msg}")
    await bot.close()

# -------------------------------
# TASKS
# -------------------------------
st.subheader("⚙️ Tasks")

pending_tasks = data.get("tasks", [])
approved_memory = data.get("memory", [])

for i, task in enumerate(pending_tasks):
    col1, col2 = st.columns([4, 1])
    col1.write(f"{task['task']} | {task.get('status', 'pending')}")
    if col2.button(f"Approve {i}"):
        # Add to approved memory
        approved_memory.append({
            "task": task["task"],
            "score": 0,
            "plan": model.generate(f"Create step-by-step plan: {task['task']}"),
            "research": model.generate(f"Give insights or ideas for: {task['task']}"),
            "execution": "No real execution"
        })
        # Remove from pending
        pending_tasks.pop(i)
        data["tasks"] = pending_tasks
        data["memory"] = approved_memory
        save_json(DATA_FILE, data)

        # Send Telegram safely
        asyncio.run(send_telegram(task["task"]))
        st.success(f"Action approved and sent to Telegram: {task['task']}")
        st.experimental_rerun()

# -------------------------------
# MEMORY DISPLAY
# -------------------------------
st.subheader("Memory")
if approved_memory:
    for mem in approved_memory:
        st.write(f"- Task: {mem['task']}")
        st.write(f"  Score: {mem.get('score',0)}")
        st.write(f"  Plan: {mem.get('plan','')}")
        st.write(f"  Research: {mem.get('research','')}")
        st.write(f"  Execution: {mem.get('execution','')}")
else:
    st.write("No memory yet.")

# -------------------------------
# ADD NEW TASK
# -------------------------------
st.subheader("Add New Task")
new_task = st.text_input("Task description")
if st.button("Add Task"):
    if new_task.strip():
        pending_tasks.append({
            "task": new_task.strip(),
            "project": "General",
            "status": "pending",
            "created": str(os.path.getmtime(DATA_FILE))
        })
        data["tasks"] = pending_tasks
        save_json(DATA_FILE, data)
        st.success(f"Added new task: {new_task}")
        st.experimental_rerun()