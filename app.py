import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Load Data ---
def load_data():
    if not os.path.exists("data"):
        os.makedirs("data")

    task_file = "data/tasks.csv"
    milestone_file = "data/milestones.csv"

    if not os.path.exists(task_file):
        tasks = pd.DataFrame(columns=["Task", "Owner", "Status", "Deadline"])
        tasks.to_csv(task_file, index=False)
    else:
        tasks = pd.read_csv(task_file)

    if not os.path.exists(milestone_file):
        milestones = pd.DataFrame(columns=["Milestone", "Date", "Status"])
        milestones.to_csv(milestone_file, index=False)
    else:
        milestones = pd.read_csv(milestone_file)

    return tasks, milestones

# --- Save Data ---
def save_data(tasks, milestones):
    tasks.to_csv("data/tasks.csv", index=False)
    milestones.to_csv("data/milestones.csv", index=False)

# --- App Setup ---
st.set_page_config(page_title="IV Drip Project Tracker", layout="wide")
st.title("💧 IV Drip Project Tracker")

st.sidebar.header("🚀 Project Navigation")
page = st.sidebar.radio("Select Section", ["📊 Dashboard", "🗂️ Task Board", "📅 Milestones", "📎 Upload Files"])

# Load data
tasks, milestones = load_data()

# --- Dashboard ---
if page == "📊 Dashboard":
    st.subheader("📈 Project Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(tasks))
    col2.metric("Completed Tasks", (tasks['Status'] == 'Done').sum())
    col3.metric("Upcoming Milestones", (pd.to_datetime(milestones['Date']) > datetime.today()).sum())

    completed_ratio = round((tasks['Status'] == 'Done').sum() / len(tasks) * 100, 1) if len(tasks) > 0 else 0
    st.progress(completed_ratio / 100)
    st.write(f"✅ **{completed_ratio}%** of tasks completed")

    st.markdown("---")
    st.markdown("### 🔔 Milestones")
    for _, row in milestones.iterrows():
        st.info(f"**{row['Milestone']}** — {row['Date']} — {row['Status']}")

# --- Task Board ---
elif page == "🗂️ Task Board":
    st.subheader("✅ Project Task Tracker")

    status_filter = st.selectbox("Filter by Status", ["All"] + tasks['Status'].unique().tolist())
    if status_filter != "All":
        filtered_tasks = tasks[tasks['Status'] == status_filter]
    else:
        filtered_tasks = tasks

    for idx, row in filtered_tasks.iterrows():
        with st.expander(f"📝 {row['Task']} — {row['Status']}"):
            st.write(f"👤 **Owner**: {row['Owner']}")
            st.write(f"📅 **Deadline**: {row['Deadline']}")

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
            save_data(tasks, milestones)
            st.success("✅ Task added successfully!")

# --- Milestone Timeline ---
elif page == "📅 Milestones":
    st.subheader("📅 Milestone Timeline")

    for idx, row in milestones.iterrows():
        st.success(f"🎯 **{row['Milestone']}** — {row['Date']} — {row['Status']}")

    st.markdown("---")
    st.markdown("### ➕ Add New Milestone")
    with st.form("new_milestone"):
        milestone = st.text_input("Milestone")
        date = st.date_input("Target Date")
        status = st.selectbox("Status", ["✅ Done", "🟡 In Progress", "⏳ Upcoming"])
        submit = st.form_submit_button("Add Milestone")
        if submit:
            new = pd.DataFrame([[milestone, date, status]], columns=milestones.columns)
            milestones = pd.concat([milestones, new], ignore_index=True)
            save_data(tasks, milestones)
            st.success("📌 Milestone added!")

# --- Upload Files ---
elif page == "📎 Upload Files":
    st.subheader("📎 Upload Design Files or Notes")
    uploaded_file = st.file_uploader("Upload your file (PDF, image, doc, etc.)")
    if uploaded_file:
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Uploaded {uploaded_file.name}")
