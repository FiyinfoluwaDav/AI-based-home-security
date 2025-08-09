# NSMC Home Security System

Real-time AI-powered home surveillance with face recognition and WhatsApp alerts.

---

![Alt text](https://github.com/FiyinfoluwaDav/AI-based-home-security/blob/main/dashboard.png)

## Overview

The **NSMC Home Security System** is a Python-based application built with Streamlit that leverages AI-driven face recognition to monitor environments in real-time. It detects known and unknown individuals, logs detection events, records videos, captures snapshots, and sends alerts via WhatsApp using the CallMeBot API. The user-friendly interface includes a dashboard for live monitoring and analytics, plus a logs page for trend analysis, ideal for home or small-scale security applications.

---

## Table of Contents

- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Usage](#usage)  
- [File Structure](#file-structure)  
- [Contact](#contact)  

---

## Features

- **Real-Time Webcam Monitoring**: Live video feed with face detection and recognition using the `face_recognition` library.  
- **Face Recognition**: Identifies known individuals from images in the `known_faces/` directory; labels unknown faces.  
- **Video Recording**: Records timestamped video clips to `video_records/` (e.g., `video_20250809_173405.mp4`).  
- **Snapshot Capture**: Saves snapshots to `snapshots/` (e.g., `snapshot_20250809_173405.jpg`) and sends them via WhatsApp.  
- **WhatsApp Notifications**: Sends snapshots and test alerts to a specified number via CallMeBot API.  
- **Detection Logging**: Records detections (timestamp, label, alert status) to `detections.csv`.  
- **Dashboard Analytics**: Real-time stats (total detections, intrusion attempts, success/vulnerability percentages) displayed with Altair donut charts.  
- **Detection Logs Page**: Shows recent detections and a bar chart of trends over time.  
- **Responsive Interface**: Built with Streamlit, featuring a sidebar for controls and two pages: Dashboard and Detection Logs.

---

## Prerequisites

- **Operating System**: Windows, macOS, or Linux  
- **Python**: 3.8 or higher  
- **Webcam**: A connected webcam for live monitoring  
- **WhatsApp Account**: For receiving notifications via CallMeBot API  

### Python Dependencies

- `streamlit`  
- `pandas`  
- `altair`  
- `opencv-python`  
- `face_recognition`  
- `requests`  
- `numpy`  

---

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/FiyinfoluwaDav/AI-based-home-security.git
    cd AI-based-home-security
    ```

2. **Set up a virtual environment (recommended):**

    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install streamlit pandas altair opencv-python face_recognition requests numpy
    ```

4. **Prepare known faces:**

    - Create a `known_faces/` folder in the project root.
    - Add images of known individuals (e.g., `john.jpg`, `jane.png`).
    - Ensure each image contains a single, clear face. Filenames (without extension) are used as labels.

5. **Configure CallMeBot API:**

    - Obtain an API key by messaging **+34 644 58 95 12** on WhatsApp with `/api`.
    - Update `CALLMEBOT_API_KEY` in `app.py`:

      ```python
      CALLMEBOT_API_KEY = "your_api_key_here"
      ```

6. **Create required directories:**

    ```bash
    mkdir snapshots video_records
    ```

---

## Usage

Run the application:

```bash
streamlit run streamlit_app1.py


nsmc-home-security/
├── streamlit_app1.py                 # Main application script
├── detections.csv         # Detection log file (auto-generated)
├── known_faces/           # Known face images
├── snapshots/             # Captured snapshots
├── video_records/         # Recorded videos
├── README.md              # This file
└── LICENSE                # License file (e.g., MIT)


Contact
Email: osokoyafiyinfoluwa@gmail.com

GitHub: FiyinfoluwaDav

Twitter/X: @OsokoyaF

Issues: Use GitHub Issues on this repository.
⭐ Star the repository if you find it useful!
