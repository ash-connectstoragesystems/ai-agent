# ultimate_ai_agent.py

import streamlit as st
import json
import os
import asyncio
from gpt4all import GPT4All

# -------------------------------
# CONFIGURATION
# -------------------------------

# Model paths
ALPACA_MODEL_PATH = r"C:\Users\ash\PyCharmMiscProject\models\alpaca-ggml-model-q4_0.bin"
MISTRAL_MODEL_PATH = r"C:\Users\ash\PyCharmMiscProject\models\mistral-7b-instruct-v0.1.Q4_K_M\mistral-local.gguf"

# Approved & pending actions files
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

# --- Dashboard ---
st.subheader("📊 Dashboard")

st.write("⚙️ Tasks")
for task in data["tasks"]:
    st.write(f"{task['task']} | {task.get('status', 'pending')}")

st.subheader("Memory")
if data["memory"]:
    for mem in data["memory"]:
        st.write(f"- {mem['task']} | Score: {mem.get('score', 0)}")
else:
    st.write("No memory yet.")

# --- Model selection ---
model_choice = st.selectbox("Choose AI Model", ["Alpaca 7B", "Mistral 7B"])
st.write("Loading AI model. This may take a while...")

# TEMP: Use FakeModel for cloud deployment
class FakeModel:
    def generate(self, prompt):
        return "AI response for: " + prompt

model = FakeModel()
st.success("Model loaded!")

# -------------------------------
# EXECUTOR AGENT (REAL AUTOMATION)
# -------------------------------

def executor_agent(task):
    task_lower = task.lower()

    # Open website
    if "open google" in task_lower:
        os.system("start https://www.google.com")
        return "Opened Google"

    # Create file
    if "create file" in task_lower:
        with open("ai_file.txt", "w") as f:
            f.write("Created by AI")
        return "File created"

    # Run Python script
    if "run script" in task_lower:
        os.system("python test.py")
        return "Script executed"

    # Block dangerous commands
    if "shutdown" in task_lower or "delete system32" in task_lower:
        return "⚠️ Blocked dangerous command"

    return "No action matched"

# -------------------------------
# Add new task
# -------------------------------
st.subheader("Add New Task")
new_task = st.text_input("Task description")
if st.button("Add Task"):
    if new_task.strip():
        data["tasks"].append({"task": new_task.strip(), "status": "pending"})
        save_json(DATA_FILE, data)
        st.success(f"Added new task: {new_task}")
        st.experimental_rerun()

# -------------------------------
# Approve & Execute Task
# -------------------------------
st.subheader("Approve Tasks")
for i, task in enumerate(data["tasks"]):
    if st.button(f"Approve {task['task']}"):
        # Update memory with AI suggestion
        mem_entry = {
            "task": task["task"],
            "score": 0,
            "plan": model.generate(f"Create step-by-step plan: {task['task']}"),
            "research": model.generate(f"Give insights or ideas for: {task['task']}"),
            "execution": executor_agent(task["task"])
        }
        data["memory"].append(mem_entry)
        task["status"] = "done"
        save_json(DATA_FILE, data)
        st.success(f"Task '{task['task']}' executed and added to memory.")
        st.experimental_rerun()

# -------------------------------
# Chat simulation (optional)
# -------------------------------
st.subheader("💬 Chat")
chat_input = st.text_input("Ask your AI Agent")
if st.button("Send"):
    if chat_input.strip():
        response = model.generate(chat_input)
        data["chat"].append({"user": chat_input.strip(), "ai": response})
        save_json(DATA_FILE, data)
        st.success("AI responded!")
        st.write(f"**AI:** {response}")