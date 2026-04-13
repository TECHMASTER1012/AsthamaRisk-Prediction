import streamlit as st
import pandas as pd
import utils.api as api
from components.charts import plot_time_series
import time

if "token" not in st.session_state or not st.session_state["token"]:
    st.warning("Please log in first.")
    st.stop()

# Premium CSS for Glassmorphism
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top left, #1a1e29, #0e1117 40%);
    }

    .metric-card {
        background: rgba(30, 33, 41, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        text-align: center;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .metric-title {
        font-size: 13px;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #a1a1aa;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #a1a1aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .status-High { 
        background: linear-gradient(90deg, #ff4b4b, #ff8f8f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 32px; 
    }
    .status-Moderate { 
        background: linear-gradient(90deg, #ffa421, #ffc770);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 32px; 
    }
    .status-Low { 
        background: linear-gradient(90deg, #00c04b, #59f293);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 32px; 
    }

    /* Subheader styles */
    h3 {
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

col_title, col_action = st.columns([3, 1])
with col_title:
    st.markdown("<h1 style='font-weight:800; background: linear-gradient(90deg, #00d4ff, #b400ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🫁 Real-Time Asthma Monitor</h1>", unsafe_allow_html=True)

patients = api.get_patients()
if not patients:
    st.info("No patients found. Please add a patient in the Patients tab.")
    st.stop()

patient_options = {f"{p['name']} (Age: {p['age']})": p['id'] for p in patients}

col_sel, col_tgl = st.columns([3, 1])
with col_sel:
    selected_patient_name = st.selectbox("Monitoring Subject:", list(patient_options.keys()), label_visibility="collapsed")
with col_tgl:
    auto_refresh = st.toggle("Live Telemetry", value=False)
    
selected_patient_id = patient_options[selected_patient_name]

# Fetch data
history = api.get_patient_history(selected_patient_id, hours=24)
alerts = api.get_patient_alerts(selected_patient_id)

if not history:
    st.info("Awaiting telemetry link from ESP32 Edge Device...")
    if auto_refresh:
        time.sleep(2)
        st.rerun()
    st.stop()

df = pd.DataFrame(history)
df['timestamp'] = pd.to_datetime(df['timestamp'])

latest = df.iloc[-1]

# Top KPI Cards - Section 1: Clinical Vitals
st.markdown("### Clinical Vitals")
v1, v2, v3, v4, v5 = st.columns(5)

with v1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Blood Oxygen</div>
        <div class="metric-value">{latest['spo2']:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
with v2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Heart Rate</div>
        <div class="metric-value">{latest['heart_rate']:.0f} bpm</div>
    </div>
    """, unsafe_allow_html=True)
with v3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Resp. Rate</div>
        <div class="metric-value">{latest['respiration_rate']:.0f} /min</div>
    </div>
    """, unsafe_allow_html=True)
with v4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Resp Raw</div>
        <div class="metric-value">{latest['resp_raw']:.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with v5:
    risk_color = "status-Low" if latest['risk_level'] == "Low" else "status-Moderate" if latest['risk_level'] == "Moderate" else "status-High"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Asthma Risk AI</div>
        <div class="{risk_color}">{latest['risk_level']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# Top KPI Cards - Section 2: Environment & Activity
st.markdown("### Environmental & Activity")
e1, e2, e3, e4 = st.columns(4)

with e1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Air Quality</div>
        <div class="metric-value">{latest['aqi']:.0f} AQI</div>
    </div>
    """, unsafe_allow_html=True)
with e2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Temperature</div>
        <div class="metric-value">{latest['temperature']:.1f}°C</div>
    </div>
    """, unsafe_allow_html=True)
with e3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Humidity</div>
        <div class="metric-value">{latest['humidity']:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
with e4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Activity</div>
        <div class="metric-value">{latest['activity']:.2f} g</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts
st.markdown("### Intelligent Telemetry Trends")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(plot_time_series(df, 'spo2', 'SpO2 (%)', '#00d4ff'), use_container_width=True)
    st.plotly_chart(plot_time_series(df, 'respiration_rate', 'Respiration Rate (/min)', '#ff5e00'), use_container_width=True)

with c2:
    st.plotly_chart(plot_time_series(df, 'heart_rate', 'Heart Rate (bpm)', '#ff0055'), use_container_width=True)
    st.plotly_chart(plot_time_series(df, 'aqi', 'Air Quality (AQI)', '#b400ff'), use_container_width=True)

# Recent Alerts
st.markdown("### Edge Device Alerts")
if alerts:
    for alert in alerts[:5]: # Show top 5
        icon = "🚨" if "HIGH" in alert["message"] else "⚠️"
        color = "#ff4b4b" if "HIGH" in alert["message"] else "#ffa421"
        bg_col = "rgba(255, 75, 75, 0.1)" if "HIGH" in alert["message"] else "rgba(255, 164, 33, 0.1)"
        
        st.markdown(f"""
        <div style="background-color: {bg_col}; border-left: 4px solid {color}; padding: 12px 20px; border-radius: 4px; margin-bottom: 10px;">
            <strong style="color: {color};">{icon} Alert Event</strong> <span style="color: #a1a1aa; font-size: 0.9em;">- {alert['timestamp'][:19]}</span><br/>
            <span style="color: #fafafa;">{alert['message']}</span> 
            <span style="float: right; font-size: 0.8em; padding: 2px 8px; border-radius: 10px; background-color: rgba(255,255,255,0.1);">{alert['status']}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.write("No alert triggers recorded in this window.")

if auto_refresh:
    time.sleep(3)
    st.rerun()
