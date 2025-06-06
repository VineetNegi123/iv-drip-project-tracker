import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Load Data ---
def load_data():
    if not os.path.exists("data/tasks.csv"):
        tasks = pd.DataFrame(columns=["Task", "Owner", "Status", "Deadline"])
        tasks.to_csv("data/tasks.csv", index=False)
    else:
        tasks = pd.read_csv("data/tasks.csv")

    if not os.path.exists("data/milestones.csv"):
        milestones = pd.DataFrame(columns=["Milestone", "Date", "Status"])
        milestones.to_csv("data/milestones.csv", index=False)
    else:
        milestones = pd.read_csv("data/milestones.csv")

    return tasks, milestones

# --- Save Data ---
def save_data(tasks, milestones):
    tasks.to_csv("data/tasks.csv", index=False)
    milestones.to_csv("data/milestones.csv", index=False)

# --- Main App ---
st.set_page_config(page_title="IV Drip Project Tracker", layout="wide")
st.title("💧 IV Drip Project Tracker")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Task Board", "Timeline", "Upload Zone"])

# Load data
tasks, milestones = load_data()

# --- Overview ---
if page == "Overview":
    st.subheader("📊 Project Summary")
    st.write("Welcome to the IV Drip Project Tracker. Monitor progress, tasks, and key milestones.")
    st.metric("Total Tasks", len(tasks))
    st.metric("Completed Tasks", (tasks['Status'] == 'Done').sum())
    st.metric("Upcoming Milestones", (pd.to_datetime(milestones['Date']) > datetime.today()).sum())

# --- Task Board ---
elif page == "Task Board":
    st.subheader("📋 Team Task List")

    status_filter = st.selectbox("Filter by status", ["All", "To Do", "In Progress", "Done"])
    if status_filter != "All":
        filtered_tasks = tasks[tasks['Status'] == status_filter]
    else:
        filtered_tasks = tasks

    st.dataframe(filtered_tasks)

    st.markdown("### ➕ Add New Task")
    with st.form("add_task"):
        task = st.text_input("Task")
        owner = st.text_input("Owner")
        status = st.selectbox("Status", ["To Do", "In Progress", "Done"])
        deadline = st.date_input("Deadline")
        submit = st.form_submit_button("Add Task")
        if submit:
            new_task = pd.DataFrame([[task, owner, status, deadline]], columns=tasks.columns)
            tasks = pd.concat([tasks, new_task], ignore_index=True)
            save_data(tasks, milestones)
            st.success("Task added.")

# --- Timeline ---
elif page == "Timeline":
    st.subheader("📅 Project Milestones")
    st.dataframe(milestones)

    st.markdown("### ➕ Add Milestone")
    with st.form("add_milestone"):
        milestone = st.text_input("Milestone")
        date = st.date_input("Date")
        status = st.selectbox("Status", ["✅ Done", "🟡 In Progress", "⏳ Upcoming"])
        submit = st.form_submit_button("Add Milestone")
        if submit:
            new_milestone = pd.DataFrame([[milestone, date, status]], columns=milestones.columns)
            milestones = pd.concat([milestones, new_milestone], ignore_index=True)
            save_data(tasks, milestones)
            st.success("Milestone added.")

# --- Upload Zone ---
elif page == "Upload Zone":
    st.subheader("📎 Upload Files")
    uploaded_file = st.file_uploader("Upload design files, images or documents")
    if uploaded_file:
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name}")
