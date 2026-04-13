import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import utils.api as api

if "token" not in st.session_state or not st.session_state["token"]:
    st.warning("⚠️ Please log in first.")
    st.stop()

# Premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top left, #1a1e29, #0e1117 40%);
    }

    .stat-card {
        background: rgba(30, 33, 41, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 22px 24px;
        border-radius: 14px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        text-align: center;
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 40px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .stat-label {
        font-size: 12px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #a1a1aa;
        margin-bottom: 8px;
    }

    .stat-value {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #a1a1aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .section-header {
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown("""
<h1 style='font-weight:800; background: linear-gradient(90deg, #ff5e00, #ffa421);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px;'>
    📊 Advanced Analytics
</h1>
<p style='color: #a1a1aa; font-size: 15px; margin-bottom: 32px;'>
    Aggregated sensor telemetry and risk intelligence across all monitored patients.
</p>
""", unsafe_allow_html=True)

# Fetch patients
patients = api.get_patients()
if not patients:
    st.info("No patients found. Please register a patient first.")
    st.stop()

patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients}

col_sel, col_hrs = st.columns([3, 1])
with col_sel:
    selected_name = st.selectbox("Select Patient:", list(patient_options.keys()), label_visibility="collapsed")
with col_hrs:
    hours = st.selectbox("Time Window:", [1, 6, 12, 24, 48, 72], index=3, format_func=lambda x: f"Last {x}h")

patient_id = patient_options[selected_name]
history = api.get_patient_history(patient_id, hours=hours)

if not history:
    st.info(f"No data available for the last {hours} hours. Try running the simulator.")
    st.stop()

df = pd.DataFrame(history)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')

# ── Summary Statistics ───────────────────────────────────────────────────────
st.markdown("<h3 class='section-header'>📈 Session Summary</h3>", unsafe_allow_html=True)

total = len(df)
risk_counts = df['risk_level'].value_counts()
high_count = risk_counts.get('High', 0)
mod_count = risk_counts.get('Moderate', 0)
low_count = risk_counts.get('Low', 0)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Total Readings</div><div class='stat-value'>{total}</div></div>", unsafe_allow_html=True)
with c2:
    avg_spo2 = df['spo2'].mean()
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Avg SpO₂</div><div class='stat-value'>{avg_spo2:.1f}%</div></div>", unsafe_allow_html=True)
with c3:
    avg_hr = df['heart_rate'].mean()
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Avg Heart Rate</div><div class='stat-value'>{avg_hr:.0f}</div></div>", unsafe_allow_html=True)
with c4:
    avg_aqi = df['aqi'].mean()
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Avg AQI</div><div class='stat-value'>{avg_aqi:.0f}</div></div>", unsafe_allow_html=True)
with c5:
    high_pct = (high_count / total * 100) if total > 0 else 0
    st.markdown(f"<div class='stat-card'><div class='stat-label'>High Risk %</div><div class='stat-value' style='background: linear-gradient(90deg,#ff4b4b,#ff8f8f); -webkit-background-clip:text;'>{high_pct:.1f}%</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Risk Distribution ────────────────────────────────────────────────────────
st.markdown("<h3 class='section-header'>🎯 Risk Level Distribution</h3>", unsafe_allow_html=True)

col_pie, col_bar = st.columns(2)

with col_pie:
    labels = ['Low', 'Moderate', 'High']
    values = [low_count, mod_count, high_count]
    colors = ['#00c04b', '#ffa421', '#ff4b4b']

    fig_pie = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color='rgba(0,0,0,0)', width=0)),
        textfont=dict(family="Inter, sans-serif", size=13),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>"
    )])

    fig_pie.update_layout(
        title=dict(text="Readings by Risk Category", font=dict(family="Inter", size=15, color="#FAFAFA")),
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#a1a1aa")),
        annotations=[dict(text=f"<b>{total}</b><br>total", x=0.5, y=0.5, font_size=16, font_color="#FAFAFA", showarrow=False)],
        margin=dict(l=10, r=10, t=50, b=10),
        height=320
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    # Risk over time bar chart
    df['risk_color'] = df['risk_level'].map({'Low': '#00c04b', 'Moderate': '#ffa421', 'High': '#ff4b4b'})
    df['risk_num'] = df['risk_level'].map({'Low': 0, 'Moderate': 1, 'High': 2})

    fig_risk = go.Figure()
    for level, color in [('Low', '#00c04b'), ('Moderate', '#ffa421'), ('High', '#ff4b4b')]:
        mask = df['risk_level'] == level
        fig_risk.add_trace(go.Scatter(
            x=df.loc[mask, 'timestamp'],
            y=df.loc[mask, 'risk_num'],
            mode='markers',
            name=level,
            marker=dict(color=color, size=9, opacity=0.85),
            hovertemplate=f"<b>{level}</b><br>%{{x}}<extra></extra>"
        ))

    fig_risk.update_layout(
        title=dict(text="Risk Level Timeline", font=dict(family="Inter", size=15, color="#FAFAFA")),
        yaxis=dict(tickvals=[0,1,2], ticktext=['Low','Moderate','High'], gridcolor='rgba(255,255,255,0.08)'),
        xaxis=dict(showgrid=False),
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#a1a1aa")),
        margin=dict(l=10, r=10, t=50, b=10),
        height=320
    )
    st.plotly_chart(fig_risk, use_container_width=True)

# ── Correlation Matrix ───────────────────────────────────────────────────────
st.markdown("<h3 class='section-header'>🔬 Feature Correlation Heatmap</h3>", unsafe_allow_html=True)

numeric_cols = ['spo2', 'heart_rate', 'respiration_rate', 'aqi', 'temperature', 'humidity', 'activity']
corr_df = df[numeric_cols].corr()

fig_corr = go.Figure(data=go.Heatmap(
    z=corr_df.values,
    x=corr_df.columns.tolist(),
    y=corr_df.columns.tolist(),
    colorscale='RdBu',
    zmid=0,
    text=[[f"{v:.2f}" for v in row] for row in corr_df.values],
    texttemplate="%{text}",
    hovertemplate="<b>%{x} vs %{y}</b><br>Correlation: %{z:.2f}<extra></extra>"
))

fig_corr.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=20, b=10),
    height=380,
    font=dict(family="Inter, sans-serif", color="#FAFAFA")
)
st.plotly_chart(fig_corr, use_container_width=True)

# ── Raw Data Table ───────────────────────────────────────────────────────────
with st.expander("📋 View Raw Telemetry Data"):
    display_df = df.drop(columns=['risk_color', 'risk_num'], errors='ignore')
    st.dataframe(display_df.sort_values('timestamp', ascending=False), use_container_width=True)
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name=f"history_patient_{patient_id}.csv", mime="text/csv")
