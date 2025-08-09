import streamlit as st
import pandas as pd
import altair as alt
import os
from datetime import datetime, timedelta
import cv2
import face_recognition
import csv
import time

# --------------------------
# Setup
# --------------------------
st.set_page_config(
    page_title="NSMC Home Security System",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page navigation
page = st.sidebar.selectbox("📂 Select Page", ["📊 Dashboard", "📁 Detection Logs"])
st.sidebar.title("🛡️ NSMC Home Security System")

# Initialize session state
if 'app_start_time' not in st.session_state:
    st.session_state.app_start_time = None
if 'seen_faces' not in st.session_state:
    st.session_state.seen_faces = set()
if 'detection_data' not in st.session_state:
    st.session_state.detection_data = pd.DataFrame(columns=["timestamp", "label", "alert_triggered"])
if 'webcam_start_time' not in st.session_state:
    st.session_state.webcam_start_time = None

# --------------------------
# Load Known Faces
# --------------------------
@st.cache_data
def load_known_faces():
    known_faces = []
    known_names = []
    for file in os.listdir("known_faces"):
        image = face_recognition.load_image_file(f"known_faces/{file}")
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_faces.append(encoding[0])
            known_names.append(file.split('.')[0])
    return known_faces, known_names

known_faces, known_names = load_known_faces()

# --------------------------
# Load Detection Data
# --------------------------
csv_path = "detections.csv"
if not os.path.exists(csv_path):
    df = pd.DataFrame(columns=["timestamp", "label", "alert_triggered"])
else:
    df = pd.read_csv(csv_path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        df = df.dropna(subset=["timestamp"])
# Merge with session state data
df = pd.concat([df, st.session_state.detection_data], ignore_index=True)

# --------------------------
# Sidebar Widgets
# --------------------------
alarm_active = st.sidebar.checkbox("Activate Alarm System", value=False)
monitoring = st.sidebar.toggle("🔍 Start Monitoring", value=False)

# Update webcam uptime
if monitoring and st.session_state.webcam_start_time is None:
    st.session_state.webcam_start_time = time.time()
elif not monitoring and st.session_state.webcam_start_time is not None:
    st.session_state.webcam_start_time = None
    st.session_state.seen_faces.clear()  # Clear seen faces when monitoring stops

# --------------------------
# Stats Calculation
# --------------------------
if not df.empty and "timestamp" in df.columns:
    today = pd.Timestamp.now().normalize()
    detections_today = df[df["timestamp"] >= today]
    total_detections_today = len(detections_today)
    intrusion_attempts_today = len(detections_today[detections_today["label"] == "Unknown"])

    known_today = total_detections_today - intrusion_attempts_today
    success_pct = int((known_today / total_detections_today * 100) if total_detections_today > 0 else 0)
    vuln_pct = int((intrusion_attempts_today / total_detections_today * 100) if total_detections_today > 0 else 0)

    unknowns = df[df["label"] == "Unknown"]
    last_alert = unknowns["timestamp"].max() if not unknowns.empty else "No alert yet"
else:
    total_detections_today = 0
    intrusion_attempts_today = 0
    success_pct = 0
    vuln_pct = 0
    last_alert = "No data"

# --------------------------
# Donut Chart Function
# --------------------------
def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    elif input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    elif input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    elif input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    else:
        chart_color = ['#cccccc', '#888888']

    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100 - input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })

    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N", scale=alt.Scale(domain=[input_text, ''], range=chart_color), legend=None),
    ).properties(width=130, height=130)

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N", scale=alt.Scale(domain=[input_text, ''], range=chart_color), legend=None),
    ).properties(width=130, height=130)

    text = plot.mark_text(
        align='center',
        color=chart_color[0],
        font="Lato",
        fontSize=22,
        fontWeight=700
    ).encode(text=alt.value(f"{input_response}%"))

    return plot_bg + plot + text

# --------------------------
# Page 1: Dashboard
# --------------------------
if page == "📊 Dashboard":
    st.title("🏠 NSMC Home Security System Dashboard")
    st.write(f"**Alarm System Active:** {'✅ Yes' if alarm_active else '❌ No'}")
    st.write(f"**Monitoring Status:** {'🟢 Running' if monitoring else '🔴 Stopped'}")

    col1, col2, col3 = st.columns([1, 2, 1])

    # Column 1: System Stats
    with col1:
        st.markdown("### 📊 System Summary")

        # Real-time timer fragment
        @st.experimental_fragment(run_every=1)
        def display_timer():
            if st.session_state.webcam_start_time is not None:
                uptime_seconds = int(time.time() - st.session_state.webcam_start_time)
                uptime_str = str(timedelta(seconds=uptime_seconds))
            else:
                uptime_str = "00:00:00"
            st.markdown(f"""
                <div style="background-color:#062c78; padding:1rem; border-radius:8px; text-align:center; font-size:1.3rem;">
                    Camera Uptime: {uptime_str}
                </div>
            """, unsafe_allow_html=True)

        # Real-time stats fragment
        @st.experimental_fragment(run_every=5)
        def display_stats():
            today = pd.Timestamp.now().normalize()
            detections_today = st.session_state.detection_data[st.session_state.detection_data["timestamp"] >= today]
            total_detections = len(detections_today)
            intrusion_attempts = len(detections_today[detections_today["label"] == "Unknown"])
            known_detections = total_detections - intrusion_attempts
            success_pct = int((known_detections / total_detections * 100) if total_detections > 0 else 0)
            vuln_pct = int((intrusion_attempts / total_detections * 100) if total_detections > 0 else 0)

            st.markdown("**Total Detections Today**")
            st.markdown(f"""
                <div style="background-color:#062c78; padding:1rem; border-radius:8px; text-align:center; font-size:1.8rem;">
                    {total_detections}
                </div>
            """, unsafe_allow_html=True)

            st.markdown("**Intrusion Attempts Today**")
            st.markdown(f"""
                <div style="background-color:#062c78; padding:1rem; border-radius:8px; text-align:center; font-size:1.8rem;">
                    {intrusion_attempts}
                </div>
            """, unsafe_allow_html=True)

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.markdown("**✅ Successful Identification**")
                st.altair_chart(make_donut(success_pct, "Success", "green"), use_container_width=True)
            with d_col2:
                st.markdown("**⚠️ Vulnerability Level**")
                st.altair_chart(make_donut(vuln_pct, "Vuln", "red"), use_container_width=True)

        display_stats()
        display_timer()

    # Column 2: Webcam Feed with OpenCV
    with col2:
        st.markdown("### 🎥 Webcam Feed")
        if monitoring:
            run_webcam = st.button("Start Webcam")
            stop_webcam = st.button("Stop Webcam")
            if run_webcam:
                st.session_state.webcam_running = True
            if stop_webcam:
                st.session_state.webcam_running = False

            if st.session_state.get("webcam_running", False):
                frame_placeholder = st.empty()
                cap = cv2.VideoCapture(0)
                while st.session_state.get("webcam_running", False):
                    ret, frame = cap.read()
                    if not ret:
                        st.warning("Failed to capture frame from webcam.")
                        break
                    # Optionally, add face recognition here
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(rgb_frame, channels="RGB")
                    # Add a small sleep to avoid high CPU usage
                    time.sleep(0.05)
                cap.release()
        else:
            st.info("Monitoring is stopped.")

        # Button row: Capture Snapshot & Test Notification
        btn_col3, btn_col4 = st.columns(2)
        with btn_col3:
            if st.button("📸 Capture Snapshot"):
                st.session_state.capture_snapshot = True
        with btn_col4:
            st.button("📢 Test Notification")

    # Column 3: Controls
    with col3:
        st.markdown("### ⚙️ Controls")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        if not df.empty:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📁 Export Data (CSV)",
                data=csv,
                file_name="detection_data.csv",
                mime="text/csv"
            )

        st.markdown("---")
        st.button("🎥 Record Video Clip")

        if st.button("🧹 Remove Detections"):
            st.warning("⚠️ This would delete detection records (not implemented).")

        st.markdown("---")
        st.toggle("🌗 Switch Theme", value=False)

        if st.button("🔓 Sign Out"):
            st.success("✅ Signed out. (Placeholder action)")

    # After webcam processing, handle logging and snapshot saving ONLY if monitoring is active
    if monitoring:
        if "pending_detections" in st.session_state and st.session_state.pending_detections:
            new_detection = pd.DataFrame(st.session_state.pending_detections)
            st.session_state.detection_data = pd.concat([st.session_state.detection_data, new_detection], ignore_index=True)
            file_exists = os.path.isfile("detections.csv")
            with open("detections.csv", "a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["timestamp", "label", "alert_triggered"])
                for det in st.session_state.pending_detections:
                    writer.writerow([det["timestamp"].strftime("%Y-%m-%d %H:%M:%S"), det["label"], det["alert_triggered"]])
            st.session_state.pending_detections = []

        if "snapshot_img" in st.session_state:
            cv2.imwrite(f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg", st.session_state.snapshot_img)
            del st.session_state.snapshot_img

# --------------------------
# Page 2: Detection Logs
# --------------------------
elif page == "📁 Detection Logs":
    st.title("📁 Detection Logs & Trend Analysis")

    if not df.empty:
        st.subheader("🔍 Recent Detections")
        st.dataframe(df.tail(10), use_container_width=True)

        if "timestamp" in df.columns and "label" in df.columns:
            st.subheader("📈 Detection Trend Over Time")
            chart = alt.Chart(df).mark_bar().encode(
                x='timestamp:T',
                y='count()',
                color='label:N'
            ).properties(width=800, height=300)
            st.altair_chart(chart, use_container_width=True)
else:
    st.info("No detection data available yet.")
