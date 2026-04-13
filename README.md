# Intelligent Asthma Risk Prediction System

A full-stack, real-time asthma risk monitoring platform combining **IoT edge intelligence**, **TinyML inference on ESP32**, a **FastAPI backend**, and a **Streamlit clinical dashboard**.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│              Streamlit Dashboard (Port 8501)                    │
│   Login │ Real-Time Monitor │ Patient Mgmt │ Analytics          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (JWT Auth)
┌──────────────────────────▼──────────────────────────────────────┐
│                     FASTAPI BACKEND (Port 8000)                 │
│   Auth Router │ Sensor Ingest │ Dashboard API │ Twilio Alerts   │
│                     SQLite Database                             │
└──────────────────────────▲──────────────────────────────────────┘
                           │ HTTP POST (JSON)
┌──────────────────────────┴──────────────────────────────────────┐
│               ESP32-S3 EDGE DEVICE / Python Simulator           │
│   MPU6050 (Accel) │ DHT22 (Temp/Humid) │ MAX30102 (SpO2/HR)    │
│   MQ Gas Sensor │ TFLite Micro Inference → risk_level           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Sensors_Project/
├── backend/                  # FastAPI Backend
│   ├── main.py               # App entry point
│   ├── database.py           # SQLAlchemy setup
│   ├── models.py             # ORM models (User, Patient, SensorReading, Alert)
│   ├── schemas.py            # Pydantic validation schemas
│   ├── requirements.txt      # Backend dependencies
│   ├── .env.example          # Environment variables template
│   ├── routers/
│   │   ├── auth.py           # JWT login/register
│   │   ├── sensor.py         # ESP32 data ingestion + alert triggering
│   │   └── dashboard.py      # Patient CRUD + history API
│   └── services/
│       └── twilio_service.py # SMS alert delivery
│
├── frontend/                 # Streamlit Dashboard
│   ├── app.py                # Login page + home screen
│   ├── requirements.txt      # Frontend dependencies
│   ├── pages/
│   │   ├── 1_Dashboard.py    # Real-time telemetry monitor
│   │   ├── 2_Patients.py     # Patient registration & management
│   │   └── 3_Analytics.py    # Aggregated analytics & insights
│   ├── components/
│   │   └── charts.py         # Plotly chart builders
│   └── utils/
│       └── api.py            # API calls to FastAPI backend
│
├── ml_pipeline/              # TinyML Training Pipeline
│   ├── train_model.py        # Synthetic data gen + model training
│   └── tflite_converter.py   # TFLite + C array export
│
├── firmware/                 # ESP32-S3 Arduino Firmware
│   ├── main.ino              # Main sensor loop + TFLite inference
│   ├── model_data.cpp        # Auto-generated TFLite model array
│   └── model_data.h          # Header file
│
├── simulator.py              # Python-based ESP32 sensor simulator
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Clone & Set Up Virtual Environment

```bash
cd Sensors_Project
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
```

### 2. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables

```bash
copy backend\.env.example backend\.env
# Edit backend\.env with your Twilio credentials
```

### 4. Start the FastAPI Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```
> API docs available at: http://localhost:8000/docs

### 5. Install Frontend Dependencies

```bash
pip install -r frontend/requirements.txt
```

### 6. Launch the Streamlit Dashboard

```bash
cd frontend
streamlit run app.py
```
> Dashboard available at: http://localhost:8501

### 7. Run the Simulator (optional — substitute for real ESP32)

```bash
# First create a patient via the Patients page, then:
python simulator.py --patient 1 --server http://127.0.0.1:8000
```

---

## 🤖 ML Pipeline (Re-training)

To retrain the TinyML model and regenerate firmware files:

```bash
pip install tensorflow scikit-learn pandas numpy
cd ml_pipeline
python train_model.py
```

This will:
1. Generate 10,000 synthetic physiological samples
2. Train a lightweight neural network (7 → 16 → 8 → 3 classes)
3. Quantize to INT8 TFLite format
4. Export `model_data.cpp` and `model_data.h` directly to `firmware/`

---

## ⚡ ESP32 Firmware Setup

### Arduino Library Dependencies
Install via Arduino Library Manager:
- `TensorFlowLite_ESP32`
- `Adafruit MPU6050`
- `Adafruit Unified Sensor`
- `DHTesp` or `DHT sensor library`
- `ArduinoJson`

### Configuration
Edit `firmware/main.ino`:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverName = "http://YOUR_SERVER_IP:8000/api/sensors/ingest";
const int patient_id = 1; // Must match a patient registered via the dashboard
```

### Scaler Constants
After running `train_model.py`, update these arrays in `main.ino` with values from `ml_pipeline/data/scaler_mean.csv` and `scaler_scale.csv`:
```cpp
float feature_means[7] = { ... };
float feature_scales[7] = { ... };
```

---

## 🔑 Key Features

| Feature | Details |
|---|---|
| **Edge AI** | TFLite Micro model runs entirely on ESP32-S3 (no cloud inference) |
| **Real-time streaming** | 5-second sensor push cadence with live dashboard refresh |
| **JWT Authentication** | Secure login with password strength enforcement |
| **SMS Alerts** | Twilio-powered emergency notifications on HIGH risk events |
| **Multi-patient** | Each clinician account manages multiple patient profiles |
| **Analytics** | Risk distribution, correlation heatmap, historical trends |

---

## 🌐 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register a new clinician account |
| `POST` | `/auth/token` | ❌ | Login — returns JWT token |
| `GET` | `/auth/me` | ✅ | Get current user info |
| `POST` | `/api/patients` | ✅ | Register a new patient |
| `GET` | `/api/patients` | ✅ | List all patients for this user |
| `GET` | `/api/patients/{id}/history` | ✅ | Sensor reading history |
| `GET` | `/api/patients/{id}/alerts` | ✅ | Alert log for patient |
| `POST` | `/api/sensors/ingest` | ❌ | ESP32 data ingestion (no auth) |

---

## 📱 SMS Alert Configuration

1. Sign up at [twilio.com](https://www.twilio.com)
2. Get a Twilio phone number
3. Copy Account SID, Auth Token, and phone number to `backend/.env`
4. Alerts are automatically triggered when `risk_level == "High"`
