import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Load Data ---
def load_data():
    if not os.path.exists("data"):
        os.makedirs("data")

    files = {
        "tasks": "data/tasks.csv",
        "milestones": "data/milestones.csv",
        "stages": "data/stages.csv"
    }

    for file in files.values():
        if not os.path.exists(file):
            if "tasks" in file:
                pd.DataFrame(columns=["Task", "Owner", "Status", "Deadline"]).to_csv(file, index=False)
            elif "milestones" in file:
                pd.DataFrame(columns=["Milestone", "Date", "Status"]).to_csv(file, index=False)
            elif "stages" in file:
                pd.DataFrame(columns=["Stage", "Status", "Notes"]).to_csv(file, index=False)

    return (
        pd.read_csv(files["tasks"]),
        pd.read_csv(files["milestones"]),
        pd.read_csv(files["stages"])
    )

# --- Save Data ---
def save_data(tasks, milestones, stages):
    tasks.to_csv("data/tasks.csv", index=False)
    milestones.to_csv("data/milestones.csv", index=False)
    stages.to_csv("data/stages.csv", index=False)

# --- App Setup ---
st.set_page_config(page_title="IV Drip Project Tracker", layout="wide")
st.title("💧 IV Drip Project Tracker")

st.sidebar.header("🚀 Project Navigation")
page = st.sidebar.radio("Select Section", [
    "📊 Dashboard", 
    "🗂️ Task Board", 
    "📅 Milestones", 
    "🔧 Project Stages",
    "📷 Product Media", 
    "📎 Upload Files"])

# Load data
tasks, milestones, stages = load_data()

# --- Dashboard ---
if page == "📊 Dashboard":
    st.subheader("📈 Project Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(tasks))
    col2.metric("Completed Tasks", (tasks['Status'] == 'Done').sum())
    col3.metric("Milestones Done", (milestones['Status'] == '✅ Done').sum())

    progress = (tasks['Status'] == 'Done').sum() / len(tasks) if len(tasks) > 0 else 0
    st.progress(progress)
    st.write(f"🔧 Progress: **{round(progress * 100, 1)}%**")

    st.markdown("---")
    st.markdown("### 📋 Stage Completion")
    for _, row in stages.iterrows():
        st.info(f"🧩 **{row['Stage']}** — {row['Status']} — {row['Notes']}")

# --- Task Board ---
elif page == "🗂️ Task Board":
    st.subheader("✅ Team Tasks")
    status_filter = st.selectbox("Filter by Status", ["All"] + tasks['Status'].unique().tolist())
    view = tasks if status_filter == "All" else tasks[tasks['Status'] == status_filter]

    for _, row in view.iterrows():
        with st.expander(f"📝 {row['Task']} — {row['Status']}"):
            st.write(f"👤 Owner: {row['Owner']}")
            st.write(f"📅 Deadline: {row['Deadline']}")

    st.markdown("---")
    st.markdown("### ➕ Add New Task")
    with st.form("new_task"):
        task = st.text_input("Task")
        owner = st.text_input("Owner")
        status = st.selectbox("Status", ["To Do", "In Progress", "Done"])
        deadline = st.date_input("Deadline")
        submit = st.form_submit_button("Add Task")
        if submit:
            new = pd.DataFrame([[task, owner, status, deadline]], columns=tasks.columns)
            tasks = pd.concat([tasks, new], ignore_index=True)
            save_data(tasks, milestones, stages)
            st.success("Task added!")

# --- Milestones ---
elif page == "📅 Milestones":
    st.subheader("🎯 Milestone Tracker")
    for _, row in milestones.iterrows():
        st.success(f"📌 {row['Milestone']} — {row['Date']} — {row['Status']}")

    st.markdown("### ➕ Add Milestone")
    with st.form("new_milestone"):
        m = st.text_input("Milestone")
        d = st.date_input("Date")
        s = st.selectbox("Status", ["✅ Done", "🟡 In Progress", "⏳ Upcoming"])
        submit = st.form_submit_button("Add Milestone")
        if submit:
            new = pd.DataFrame([[m, d, s]], columns=milestones.columns)
            milestones = pd.concat([milestones, new], ignore_index=True)
            save_data(tasks, milestones, stages)
            st.success("Milestone added!")

# --- Stages ---
elif page == "🔧 Project Stages":
    st.subheader("🛠️ Project Lifecycle Stages")
    for _, row in stages.iterrows():
        with st.expander(f"🧩 {row['Stage']} — {row['Status']}"):
            st.write(row['Notes'])

    st.markdown("### ➕ Add/Update Stage")
    with st.form("new_stage"):
        stage = st.text_input("Stage")
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        notes = st.text_area("Notes (e.g. CAD plan, SolidWorks, code plan, etc.)")
        submit = st.form_submit_button("Add / Update")
        if submit:
            stages = stages[stages.Stage != stage]
            stages = pd.concat([stages, pd.DataFrame([[stage, status, notes]], columns=stages.columns)], ignore_index=True)
            save_data(tasks, milestones, stages)
            st.success("Stage saved!")

# --- Media ---
elif page == "📷 Product Media":
    st.subheader("📸 Upload Product Images")
    uploaded = st.file_uploader("Upload product photo or CAD render", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded:
        file_path = os.path.join("data", uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.image(file_path, caption=uploaded.name)
        st.success("Media uploaded!")

# --- General Upload ---
elif page == "📎 Upload Files":
    st.subheader("📎 Upload Design Docs / Plans / Budget")
    uploaded = st.file_uploader("Upload file", type=["jpg", "jpeg", "png", "pdf", "docx", "xlsx"])
    if uploaded:
        file_path = os.path.join("data", uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"Uploaded {uploaded.name}")
