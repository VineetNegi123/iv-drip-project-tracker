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
st.markdown("""
<style>
body {
    background-color: #ffffff;
}
section.main > div {
    padding: 20px;
}
.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; padding: 20px; border-bottom: 2px solid #ccc;'>
    <h1 style='color:#003366;'>💧 IV Drip Startup Dashboard</h1>
    <p style='font-size:18px;'>Track your innovation from design to deployment</p>
</div>
""", unsafe_allow_html=True)

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
    st.markdown("<h2 style='color:#003366;'>📈 Project Overview</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(tasks))
    col2.metric("Completed Tasks", (tasks['Status'] == 'Done').sum())
    col3.metric("Milestones Done", (milestones['Status'] == '✅ Done').sum())

    progress = (tasks['Status'] == 'Done').sum() / len(tasks) if len(tasks) > 0 else 0
    st.progress(progress)
    st.write(f"🔧 Progress: **{round(progress * 100, 1)}%**")

    st.markdown("<h3 style='color:#003366;'>📋 Stage Completion</h3>", unsafe_allow_html=True)
    for _, row in stages.iterrows():
        st.markdown(f"""
            <div style='padding:10px; margin:10px 0; border-left:5px solid #003366; background:#f9f9f9;'>
                <b>🧩 {row['Stage']}</b> — {row['Status']}<br>
                <span style='font-size:14px;'>{row['Notes']}</span>
            </div>
        """, unsafe_allow_html=True)

# --- Task Board ---
elif page == "🗂️ Task Board":
    st.markdown("<h2 style='color:#003366;'>✅ Team Tasks</h2>", unsafe_allow_html=True)
    status_filter = st.selectbox("Filter by Status", ["All"] + tasks['Status'].unique().tolist())
    view = tasks if status_filter == "All" else tasks[tasks['Status'] == status_filter]

    for _, row in view.iterrows():
        with st.expander(f"📝 {row['Task']} — {row['Status']}"):
            st.write(f"👤 Owner: {row['Owner']}")
            st.write(f"📅 Deadline: {row['Deadline']}")

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
            st.success("✅ Task added successfully!")

# --- Milestones ---
elif page == "📅 Milestones":
    st.markdown("<h2 style='color:#003366;'>🎯 Milestone Tracker</h2>", unsafe_allow_html=True)
    for _, row in milestones.iterrows():
        st.markdown(f"<div style='padding:10px; background:#eef5ff; border-left: 5px solid #3366cc;'>📌 <b>{row['Milestone']}</b> — {row['Date']} — {row['Status']}</div>", unsafe_allow_html=True)

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
            st.success("📌 Milestone added!")

# --- Stages ---
elif page == "🔧 Project Stages":
    st.markdown("<h2 style='color:#003366;'>🛠️ Project Lifecycle Stages</h2>", unsafe_allow_html=True)
    for _, row in stages.iterrows():
        with st.expander(f"🧩 {row['Stage']} — {row['Status']}"):
            st.write(row['Notes'])

    st.markdown("### ➕ Add or Update Stage")
    with st.form("new_stage"):
        stage = st.text_input("Stage")
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        notes = st.text_area("Notes (e.g. CAD plan, SolidWorks, code plan, etc.)")
        submit = st.form_submit_button("Save")
        if submit:
            stages = stages[stages.Stage != stage]
            stages = pd.concat([stages, pd.DataFrame([[stage, status, notes]], columns=stages.columns)], ignore_index=True)
            save_data(tasks, milestones, stages)
            st.success("Stage saved!")

# --- Media ---
elif page == "📷 Product Media":
    st.markdown("<h2 style='color:#003366;'>📸 Product Media</h2>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload product photo or CAD render", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded:
        file_path = os.path.join("data", uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.image(file_path, caption=uploaded.name)
        st.success("Media uploaded!")

# --- Upload Files ---
elif page == "📎 Upload Files":
    st.markdown("<h2 style='color:#003366;'>📎 General Upload Zone</h2>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload design docs, budget sheets, etc.", type=["jpg", "jpeg", "png", "pdf", "docx", "xlsx"])
    if uploaded:
        file_path = os.path.join("data", uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"✅ Uploaded {uploaded.name}")
