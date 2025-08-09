NSMC Home Security System
Real-time AI-powered home surveillance with face recognition and WhatsApp alerts.

The NSMC Home Security System is a Python-based application built with Streamlit, leveraging AI-driven face recognition to monitor environments in real-time. It detects known and unknown individuals, logs detection events, records videos, captures snapshots, and sends alerts via WhatsApp using the CallMeBot API. The user-friendly interface includes a dashboard for live monitoring and analytics, and a logs page for trend analysis, making it ideal for home or small-scale security applications.
Table of Contents

Features
Prerequisites
Installation
Usage
File Structure
Troubleshooting
Contributing
License
Contact

Features

Real-Time Webcam Monitoring: Live video feed with face detection and recognition using the face_recognition library.
Face Recognition: Identifies known individuals from images in the known_faces/ directory and labels unknown faces.
Video Recording: Records timestamped video clips to video_records/ (e.g., video_20250809_173405.mp4).
Snapshot Capture: Saves snapshots to snapshots/ (e.g., snapshot_20250809_173405.jpg) and sends them to WhatsApp.
WhatsApp Notifications: Sends snapshots and test alerts to a specified number via CallMeBot API.
Detection Logging: Records detections (timestamp, label, alert status) to detections.csv.
Dashboard Analytics: Displays real-time stats (total detections, intrusion attempts, success/vulnerability percentages) with Altair donut charts.
Detection Logs Page: Shows recent detections and a bar chart of trends over time.
Responsive Interface: Built with Streamlit, featuring a sidebar for controls and two pages: Dashboard and Detection Logs.

Prerequisites

Operating System: Windows, macOS, or Linux.
Python: 3.8 or higher.
Webcam: A connected webcam for live monitoring.
WhatsApp Account: For receiving notifications via CallMeBot API.
Dependencies:
streamlit: Web interface
pandas: Data handling
altair: Visualizations
opencv-python: Webcam and image processing
face_recognition: Face detection and recognition
requests: WhatsApp API calls
numpy: Numerical operations


Directory: A known_faces/ folder with .jpg or .png images of known individuals.

Installation

Clone the Repository:
git clone https://github.com/your-username/nsmc-home-security.git
cd nsmc-home-security


Set Up a Virtual Environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install streamlit pandas altair opencv-python face_recognition requests numpy

Note: face_recognition may require cmake and dlib:
pip install cmake
pip install dlib


Set Up known_faces Directory:

Create a known_faces/ folder in the project root.
Add images of known individuals (e.g., john.jpg, jane.png).
Ensure each image contains a single, clear face. Filenames (without extension) are used as labels.


Configure CallMeBot API:

Obtain an API key by messaging +34 644 58 95 12 on WhatsApp with /api.
Update CALLMEBOT_API_KEY in app.py:CALLMEBOT_API_KEY = "your_api_key_here"


Set WHATSAPP_NUMBER to your phone number (e.g., +234xxxxxxxxxx).


Create Required Directories:
mkdir snapshots video_records



Usage

Run the Application:
streamlit run streamlit_app1.py


Open the URL (e.g., http://localhost:8501) in a browser.


Dashboard Page:

Start Monitoring: Toggle "Start Monitoring" in the sidebar to activate the webcam feed.
View Stats: Check real-time stats in the left column (total detections, intrusion attempts, success/vulnerability percentages).
Capture Snapshot: Click "Capture Snapshot" to save an image to snapshots/ and send it to WhatsApp.
Test WhatsApp Notification: Click "Test WhatsApp Notification" to send an "Alert Test" message.
Record Video: Click "Record Video Clip" to start/stop recording, saved to video_records/.
Refresh Data: Click "Refresh Data" to clear cached data and reload.
Export Data: Download detection logs as detection_data.csv if available.


Detection Logs Page:

View the 10 most recent detections in a table.
Analyze detection trends in a bar chart.


Tips:

Ensure the webcam is connected before starting monitoring.
Add clear face images to known_faces/ for accurate recognition.
Check WhatsApp for snapshots and alerts.



File Structure
nsmc-home-security/
├── app.py                 # Main application script
├── detections.csv         # Detection log file (auto-generated)
├── known_faces/           # Directory for known face images
├── snapshots/             # Directory for captured snapshots
├── video_records/         # Directory for recorded videos
├── README.md              # This file
└── LICENSE                # License file (e.g., MIT)

Troubleshooting

Webcam Issues:

Ensure the webcam is connected and not in use by other apps.
Test the device index: python -c "import cv2; print(cv2.VideoCapture(0).isOpened())". Try 1 or 2 if 0 fails.
Update cv2.VideoCapture(0) in app.py if needed.


CSV Errors:

If detections.csv is corrupted, delete it; the app will create a new one with headers timestamp,label,alert_triggered.
Check for valid CSV format using a text editor.


WhatsApp Notification Failures:

Verify CALLMEBOT_API_KEY:curl -X POST -F "file=@snapshots/snapshot_20250809_173405.jpg" "https://api.callmebot.com/whatsapp.php?phone=+2349160947850&text=Snapshot&apikey=your_api_key"


Check Streamlit’s response (e.g., WhatsApp API response: ...).
Ensure snapshot files exist in snapshots/.
Alternative: Use Twilio (requires account):from twilio.rest import Client
account_sid = "YOUR_TWILIO_SID"
auth_token = "YOUR_TWILIO_TOKEN"
client = Client(account_sid, auth_token)
message = client.messages.create(
    from_="whatsapp:+14155238886",
    to="whatsapp:+2349160947850",
    media_url=f"file://snapshots/snapshot_20250809_173405.jpg"
)




Face Recognition Issues:

Ensure known_faces/ contains valid images with clear faces.
Check console for No faces detected in this frame.
Adjust tolerance=0.6 in face_recognition.compare_faces for stricter/looser matching.


Performance:

Increase time.sleep(0.05) to 0.1 in the webcam loop to reduce CPU usage.
Reduce frame size in cv2.resize(..., fx=0.5, fy=0.5) for faster processing.



Contributing
We welcome contributions! To contribute:

Fork the repository.
Create a feature branch: git checkout -b feature-name.
Commit changes: git commit -m "Add feature-name".
Push to the branch: git push origin feature-name.
Open a pull request with a detailed description.

Please follow PEP 8 and include comments. Report issues or suggest features via GitHub Issues.
License
This project is licensed under the MIT License. See LICENSE for details.
Contact
For questions, feedback, or support:

Email: osokoyafiyinfoluwa@gmail.com
GitHub: FiyinfoluwaDav
X:OsokoyaF
Issues: GitHub Issues

Star ⭐ the repository if you find it useful!
