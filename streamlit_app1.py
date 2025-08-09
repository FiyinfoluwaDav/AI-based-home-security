import streamlit as st
import requests
import pandas as pd
import altair as alt
import os
from datetime import datetime, timedelta
import cv2
import face_recognition
import csv
import time
import numpy as np

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
if 'capture_snapshot' not in st.session_state:
    st.session_state.capture_snapshot = False
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'video_writer' not in st.session_state:
    st.session_state.video_writer = None

# CallMeBot API configuration
CALLMEBOT_API_KEY = "7646080"  # Replace with your actual API key
WHATSAPP_NUMBER = "+2349160947850"

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
        else:
            st.warning(f"No face encoding found for {file}")
    if not known_faces:
        st.error("No known faces loaded. Please add images to the 'known_faces' directory.")
    return known_faces, known_names

known_faces, known_names = load_known_faces()

# --------------------------
# Load Detection Data
# --------------------------
csv_path = "detections.csv"
if not os.path.exists(csv_path):
    df = pd.DataFrame(columns=["timestamp", "label", "alert_triggered"])
else:
    try:
        df = pd.read_csv(csv_path)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
            df = df.dropna(subset=["timestamp"])
        else:
            st.warning("Invalid columns in detections.csv. Initializing empty DataFrame.")
            df = pd.DataFrame(columns=["timestamp", "label", "alert_triggered"])
    except (pd.errors.EmptyDataError, pd.errors.ParserError, Exception) as e:
        st.warning(f"Error reading detections.csv: {str(e)}. Initializing empty DataFrame.")
        df = pd.DataFrame(columns=["timestamp", "label", "alert_triggered"])
# Merge with session state data, avoiding empty concatenation
if not st.session_state.detection_data.empty:
    df = pd.concat([df, st.session_state.detection_data], ignore_index=True)

# --------------------------
# Sidebar Widgets
# --------------------------
alarm_active = st.sidebar.checkbox("Activate Alarm System", value=False)
st.session_state.monitoring = st.sidebar.toggle("🔍 Start Monitoring", value=st.session_state.monitoring)

# Update webcam uptime
if st.session_state.monitoring and st.session_state.webcam_start_time is None:
    st.session_state.webcam_start_time = time.time()
elif not st.session_state.monitoring and st.session_state.webcam_start_time is not None:
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
    st.write(f"**Monitoring Status:** {'🟢 Running' if st.session_state.monitoring else '🔴 Stopped'}")

    col1, col2, col3 = st.columns([1, 2, 1])

    # Column 1: System Stats
    with col1:
        st.markdown("### 📊 System Summary")

        # Real-time timer fragment
        @st.fragment(run_every=1)
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
        @st.fragment(run_every=5)
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
        @st.fragment(run_every=0.1)
        def webcam_feed():
            if st.session_state.monitoring:
                cap = cv2.VideoCapture(0)  # Open webcam
                if not cap.isOpened():
                    st.error("Failed to access webcam.")
                    return
                placeholder = st.empty()  # Placeholder for frame updates
                frame_count = 0
                # Get webcam properties for video recording
                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = 20  # Standard frame rate for recording

                while st.session_state.monitoring and cap.isOpened():
                    ret, img = cap.read()
                    if not ret:
                        st.error("Failed to capture frame.")
                        break
                    frame_count += 1

                    # Process every 5th frame for face recognition
                    if frame_count % 5 == 0:
                        # Resize frame to 50% for faster processing
                        small_frame = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
                        # Convert to RGB for face_recognition
                        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                        # Perform face detection
                        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                            # Scale coordinates back to original size
                            top, right, bottom, left = [int(coord * 2) for coord in (top, right, bottom, left)]

                            # Compare with known faces
                            matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.6)
                            name = "Unknown"
                            if True in matches:
                                index = matches.index(True)
                                name = known_names[index]

                            # Only log new detections
                            face_id = f"{name}_{hash(str(face_encoding))}"
                            if face_id not in st.session_state.seen_faces:
                                st.session_state.seen_faces.add(face_id)

                                # Log detection
                                new_detection = pd.DataFrame({
                                    "timestamp": [datetime.now()],
                                    "label": [name],
                                    "alert_triggered": ["Yes" if name == "Unknown" else "No"]
                                })
                                if not new_detection.empty:
                                    st.session_state.detection_data = pd.concat([st.session_state.detection_data, new_detection], ignore_index=True)

                                    # Save to CSV
                                    file_exists = os.path.isfile(csv_path)
                                    with open(csv_path, "a", newline="") as f:
                                        writer = csv.writer(f)
                                        if not file_exists:
                                            writer.writerow(["timestamp", "label", "alert_triggered"])
                                        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, "Yes" if name == "Unknown" else "No"])

                            # Draw rectangle and name on original frame
                            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                            cv2.putText(img, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                        # Debug: Log if no faces were detected
                        if not face_locations:
                            print("No faces detected in this frame")

                    # Capture snapshot if requested
                    if st.session_state.capture_snapshot:
                        # Create snapshots folder if it doesn't exist
                        os.makedirs("snapshots", exist_ok=True)
                        snapshot_path = os.path.join("snapshots", f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                        cv2.imwrite(snapshot_path, img)
                        # Send snapshot to WhatsApp
                        try:
                            with open(snapshot_path, "rb") as file:
                                files = {"file": (os.path.basename(snapshot_path), file, "image/jpeg")}
                                response = requests.post(
                                    f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_NUMBER}&text=Snapshot&apikey={CALLMEBOT_API_KEY}",
                                    files=files
                                )
                                if response.status_code == 200:
                                    # Log response for debugging
                                    st.write(f"WhatsApp API response: {response.text}")
                                    st.success("Snapshot sent to WhatsApp")
                                else:
                                    st.error(f"Failed to send snapshot to WhatsApp: {response.text}")
                        except Exception as e:
                            st.error(f"Error sending snapshot to WhatsApp: {str(e)}")
                        st.session_state.capture_snapshot = False
                        st.success(f"Snapshot saved as {snapshot_path}")

                    # Record video if requested
                    if st.session_state.recording:
                        if st.session_state.video_writer is None:
                            # Initialize video writer
                            os.makedirs("video_records", exist_ok=True)
                            video_path = os.path.join("video_records", f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                            st.session_state.video_writer = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))
                        # Write frame to video
                        st.session_state.video_writer.write(img)

                    # Convert BGR to RGB for Streamlit
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    placeholder.image(img_rgb, channels="RGB", use_container_width=True)

                    # Brief sleep to prevent excessive CPU usage
                    time.sleep(0.05)

                # Release video writer if recording
                if st.session_state.recording and st.session_state.video_writer is not None:
                    st.session_state.video_writer.release()
                    st.session_state.video_writer = None
                    st.success(f"Video saved as {video_path}")

                cap.release()
            else:
                st.info("Monitoring is stopped.")

        webcam_feed()

        # Button row: Capture Snapshot & Test Notification
        btn_col3, btn_col4 = st.columns(2)
        with btn_col3:
            if st.button("📸 Capture Snapshot"):
                st.session_state.capture_snapshot = True
        with btn_col4:
            if st.button("📱 Test WhatsApp Notification"):
                # Send "Alert Test" to WhatsApp
                try:
                    response = requests.get(
                        f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_NUMBER}&text=Alert%20Test&apikey={CALLMEBOT_API_KEY}"
                    )
                    if response.status_code == 200:
                        st.success("Test notification sent to WhatsApp")
                    else:
                        st.error(f"Failed to send test notification: {response.text}")
                except Exception as e:
                    st.error(f"Error sending test notification: {str(e)}")

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
        else:
            st.info("No data to export.")

        st.markdown("---")
        if st.button("🎥 Record Video Clip"):
            if st.session_state.recording:
                # Stop recording
                st.session_state.recording = False
                if st.session_state.video_writer is not None:
                    st.session_state.video_writer.release()
                    st.session_state.video_writer = None
                    st.success(f"Video saved as {video_path}")
            else:
                # Start recording
                if st.session_state.monitoring:
                    st.session_state.recording = True
                    st.success("Started recording video")
                else:
                    st.error("Cannot record video: Monitoring is not active")

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