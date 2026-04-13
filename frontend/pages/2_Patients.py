import streamlit as st
import utils.api as api
import pandas as pd

if "token" not in st.session_state or not st.session_state["token"]:
    st.warning("⚠️ Please log in first.")
    st.stop()

# Premium CSS matching the dashboard style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top left, #1a1e29, #0e1117 40%);
    }

    .patient-card {
        background: rgba(30, 33, 41, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 20px 24px;
        border-radius: 14px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s ease;
    }

    .patient-card:hover {
        border: 1px solid rgba(75, 139, 252, 0.3);
        box-shadow: 0 12px 40px rgba(75, 139, 252, 0.1);
        transform: translateY(-2px);
    }

    .patient-name {
        font-size: 18px;
        font-weight: 700;
        color: #FAFAFA;
    }

    .patient-meta {
        font-size: 13px;
        color: #a1a1aa;
        margin-top: 4px;
    }

    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .badge-phone {
        background: rgba(75, 139, 252, 0.15);
        color: #4b8bfc;
        border: 1px solid rgba(75, 139, 252, 0.3);
    }

    .badge-nophone {
        background: rgba(161, 161, 170, 0.1);
        color: #a1a1aa;
        border: 1px solid rgba(161, 161, 170, 0.2);
    }

    .section-header {
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 20px;
    }

    /* Form styling */
    div[data-testid="stForm"] {
        background: rgba(30, 33, 41, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(12px);
    }
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown("""
<h1 style='font-weight:800; background: linear-gradient(90deg, #4b8bfc, #b400ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px;'>
    👥 Patient Management
</h1>
<p style='color: #a1a1aa; font-size: 15px; margin-bottom: 32px;'>
    Register and manage patients monitored by the asthma risk system.
</p>
""", unsafe_allow_html=True)

# ── Add Patient Form ─────────────────────────────────────────────────────────
st.markdown("<h3 class='section-header'>➕ Register New Patient</h3>", unsafe_allow_html=True)

with st.form("add_patient_form", clear_on_submit=True):
    name = st.text_input("Full Name", placeholder="e.g. Jane Doe")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
    with col2:
        phone = st.text_input(
            "Emergency Phone (for SMS Alerts)",
            placeholder="+1234567890  (include country code)"
        )

    submitted = st.form_submit_button("✅ Register Patient", use_container_width=True, type="primary")
    if submitted:
        if not name.strip():
            st.error("❌ Patient name is required.")
        elif phone and not phone.startswith("+"):
            st.warning("⚠️ Phone number should include country code (e.g. +1234567890).")
        else:
            if api.create_patient(name.strip(), age, phone):
                st.success(f"✅ Patient **{name}** registered successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to register patient. Please try again.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Patient List ─────────────────────────────────────────────────────────────
st.markdown("<h3 class='section-header'>🏥 Registered Patients</h3>", unsafe_allow_html=True)

patients = api.get_patients()

if not patients:
    st.info("🔍 No patients registered yet. Use the form above to add your first patient.")
else:
    st.markdown(f"<p style='color:#a1a1aa; margin-bottom:16px;'>Showing <strong style='color:#fafafa;'>{len(patients)}</strong> registered patient(s)</p>", unsafe_allow_html=True)

    for p in patients:
        phone_display = p.get("phone_number", "")
        has_phone = bool(phone_display and phone_display.strip())

        phone_badge = (
            f"<span class='badge badge-phone'>📱 {phone_display}</span>"
            if has_phone
            else "<span class='badge badge-nophone'>📵 No SMS</span>"
        )

        st.markdown(f"""
        <div class='patient-card'>
            <div>
                <div class='patient-name'>{p['name']}</div>
                <div class='patient-meta'>ID: #{p['id']} &nbsp;·&nbsp; Age: {p['age']} yrs</div>
            </div>
            <div>{phone_badge}</div>
        </div>
        """, unsafe_allow_html=True)

    # Also provide a raw dataframe export option
    with st.expander("📊 View as Table / Export"):
        df = pd.DataFrame(patients)
        if "owner_id" in df.columns:
            df = df.drop(columns=["owner_id"])
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="patients.csv",
            mime="text/csv"
        )
