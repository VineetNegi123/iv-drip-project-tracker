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

# --- App UI ---
st.set_page_config(page_title="IV Drip Startup Tracker", layout="wide")

# Inject CSS styling for startup feel
st.markdown("""
<style>
body {
    background-color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
section.main > div {
    padding: 20px;
}
.block-container {
    padding-top: 1rem;
}
.header-box {
    background: linear-gradient(90deg, #003366, #007acc);
    color: white;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 30px;
}
.metric-box {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='header-box'>
    <h1>💧 IV Drip Startup Project Tracker</h1>
    <p style='font-size:18px;'>Accelerating healthcare innovation — guided by industry mentors and professors</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("📌 Navigation")
page = st.sidebar.radio("View:", [
    "🏠 Overview", 
    "✅ Tasks", 
    "🎯 Milestones", 
    "🚀 Stages",
    "📷 Media", 
    "📎 Uploads"])

# Load data
tasks, milestones, stages = load_data()

# --- Overview ---
if page == "🏠 Overview":
    st.markdown("<h2 style='color:#003366;'>📊 Project Summary</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-box'><h3>Total Tasks</h3><p>{len(tasks)}</p></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-box'><h3>Tasks Completed</h3><p>{(tasks['Status'] == 'Done').sum()}</p></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-box'><h3>Milestones Done</h3><p>{(milestones['Status'] == '✅ Done').sum()}</p></div>", unsafe_allow_html=True)

    progress = (tasks['Status'] == 'Done').sum() / len(tasks) if len(tasks) > 0 else 0
    st.markdown("<br><h4 style='color:#007acc;'>Project Progress</h4>", unsafe_allow_html=True)
    st.progress(progress)
    st.write(f"🔧 Current Completion: **{round(progress * 100, 1)}%**")

    st.markdown("<h4 style='color:#003366;'>🧠 Mentor-Guided Innovation Stages</h4>", unsafe_allow_html=True)
    for _, row in stages.iterrows():
        st.markdown(f"""
        <div style='padding:10px;margin:10px 0;border-left:5px solid #007acc;background:#f9f9f9;'>
            <b>{row['Stage']}</b> — <i>{row['Status']}</i><br>
            <small>{row['Notes']}</small>
        </div>
        """, unsafe_allow_html=True)

# --- Tasks ---
elif page == "✅ Tasks":
    st.markdown("<h2 style='color:#003366;'>🛠️ Task Management</h2>", unsafe_allow_html=True)
    status_filter = st.selectbox("Filter by Status", ["All"] + tasks['Status'].unique().tolist())
    view = tasks if status_filter == "All" else tasks[tasks['Status'] == status_filter]

    for _, row in view.iterrows():
        with st.expander(f"📌 {row['Task']} — {row['Status']}"):
            st.write(f"👤 Assigned To: {row['Owner']}")
            st.write(f"📅 Due Date: {row['Deadline']}")

    st.markdown("### ➕ Add New Task")
    with st.form("task_form"):
        t = st.text_input("Task")
        o = st.text_input("Owner")
        s = st.selectbox("Status", ["To Do", "In Progress", "Done"])
        d = st.date_input("Deadline")
        submit = st.form_submit_button("Add Task")
        if submit:
            new = pd.DataFrame([[t, o, s, d]], columns=tasks.columns)
            tasks = pd.concat([tasks, new], ignore_index=True)
            save_data(tasks, milestones, stages)
            st.success("✅ Task added!")

# --- Milestones ---
elif page == "🎯 Milestones":
    st.markdown("<h2 style='color:#003366;'>📅 Milestone Timeline</h2>", unsafe_allow_html=True)
    for _, row in milestones.iterrows():
        st.markdown(f"<div style='padding:10px;background:#eef5ff;border-left:5px solid #007acc;'>📍 <b>{row['Milestone']}</b> — {row['Date']} — {row['Status']}</div>", unsafe_allow_html=True)

    st.markdown("### ➕ Add Milestone")
    with st.form("milestone_form"):
        m = st.text_input("Milestone")
        d = st.date_input("Date")
        s = st.selectbox("Status", ["✅ Done", "🟡 In Progress", "⏳ Upcoming"])
        submit = st.form_submit_button("Add Milestone")
        if submit:
            new = pd.DataFrame([[m, d, s]], columns=milestones.columns)
            milestones = pd.concat([milestones, new], ignore_index=True)
            save_data(tasks, milestones, stages)
            st.success("📍 Milestone added!")

# --- Stages ---
elif page == "🚀 Stages":
    st.markdown("<h2 style='color:#003366;'>📐 Startup Development Stages</h2>", unsafe_allow_html=True)
    for _, row in stages.iterrows():
        with st.expander(f"🔧 {row['Stage']} — {row['Status']}"):
            st.write(row['Notes'])

    st.markdown("### ➕ Add or Update Stage")
    with st.form("stage_form"):
        stage = st.text_input("Stage")
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        notes = st.text_area("Description or updates")
        submit = st.form_submit_button("Save Stage")
        if submit:
            stages = stages[stages.Stage != stage]
            stages = pd.concat([stages, pd.DataFrame([[stage, status, notes]], columns=stages.columns)], ignore_index=True)
            save_data(tasks, milestones, stages)
            st.success("🔁 Stage saved!")

# --- Media ---
elif page == "📷 Media":
    st.markdown("<h2 style='color:#003366;'>🖼️ Upload Product Media</h2>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload CAD, renders, photos", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded:
        file_path = os.path.join("data", uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.image(file_path, caption=uploaded.name)
        st.success("📸 Media uploaded!")

# --- Uploads ---
elif page == "📎 Uploads":
    st.markdown("<h2 style='color:#003366;'>📎 File Uploads</h2>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload documentation, business plan, budget sheets etc.", type=["jpg", "jpeg", "png", "pdf", "docx", "xlsx"])
    if uploaded:
        file_path = os.path.join("data", uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"✅ File '{uploaded.name}' uploaded!")
