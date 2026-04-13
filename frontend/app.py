import streamlit as st
import utils.api as api
import streamlit.components.v1 as components
import re

st.set_page_config(
    page_title="Asthma Risk System",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 20% 20%, #1a1e29, #0e1117 60%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 17, 23, 0.85);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Login card */
    .login-container {
        background: rgba(30, 33, 41, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 40px 36px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }

    /* Welcome card on home screen */
    .home-card {
        background: rgba(30, 33, 41, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }

    .home-card:hover {
        border: 1px solid rgba(75, 139, 252, 0.3);
        transform: translateY(-3px);
        box-shadow: 0 14px 40px rgba(75,139,252,0.1);
    }

    .home-card h4 {
        margin: 0 0 6px 0;
        font-size: 16px;
        font-weight: 700;
        color: #fafafa;
    }

    .home-card p {
        margin: 0;
        font-size: 13px;
        color: #a1a1aa;
        line-height: 1.6;
    }

    .status-High { color: #ff4b4b; font-weight: bold; }
    .status-Moderate { color: #ffa421; font-weight: bold; }
    .status-Low { color: #00c04b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if "token" not in st.session_state:
    st.session_state["token"] = None

def is_password_strong(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

def trigger_popup(message):
    js = f"<script>alert('{message}');</script>"
    components.html(js, height=0, width=0)

def login_page():
    st.markdown("""
    <div style='text-align:center; padding: 40px 0 20px 0;'>
        <div style='font-size: 56px; margin-bottom: 12px;'>🫁</div>
        <h1 style='font-weight:800; font-size:2.2rem; background: linear-gradient(90deg, #4b8bfc, #b400ff);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;'>
            Asthma Risk System
        </h1>
        <p style='color:#a1a1aa; font-size:15px; margin-top:8px; margin-bottom:40px;'>
            Real-Time TinyML Clinical Monitor
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])

    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        with tab1:
            st.markdown("<p style='color:#a1a1aa; font-size:14px; margin-bottom:16px;'>Welcome back. Sign in to continue monitoring.</p>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_usr", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            if st.button("Sign In →", use_container_width=True, type="primary"):
                if username and password:
                    if api.login(username, password):
                        st.success("✅ Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")
                else:
                    st.warning("⚠️ Please enter both username and password.")

        with tab2:
            st.markdown("<p style='color:#a1a1aa; font-size:14px; margin-bottom:16px;'>Create an account to start monitoring patients.</p>", unsafe_allow_html=True)
            new_usr = st.text_input("Username", key="reg_usr", placeholder="Choose a username")
            new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Min. 8 chars, uppercase, digit, symbol")
            confirm_pass = st.text_input("Confirm Password", type="password", key="reg_pass_conf", placeholder="Repeat your password")

            if st.button("Create Account →", use_container_width=True, type="primary"):
                if not new_usr or not new_pass or not confirm_pass:
                    st.warning("⚠️ Please fill in all fields.")
                elif new_pass != confirm_pass:
                    trigger_popup("Passwords do not match!")
                    st.error("❌ Passwords do not match!")
                else:
                    is_strong, msg = is_password_strong(new_pass)
                    if not is_strong:
                        trigger_popup(f"Weak Password: {msg}")
                        st.error(f"🔒 Weak Password: {msg}")
                    else:
                        if api.register(new_usr, new_pass):
                            st.success("✅ Account created! You can now sign in.")
                            st.balloons()
                        else:
                            st.error("❌ Registration failed. Username may already exist.")

        st.markdown("</div>", unsafe_allow_html=True)

def home_page():
    username = st.session_state.get("username", "Clinician")

    # Sidebar
    st.sidebar.markdown(f"""
    <div style='padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 16px;'>
        <div style='font-size: 14px; color: #a1a1aa;'>Signed in as</div>
        <div style='font-size: 17px; font-weight: 700; color: #fafafa;'>👤 {username}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["token"] = None
        st.session_state["username"] = None
        st.rerun()

    # Main welcome area
    st.markdown(f"""
    <h1 style='font-weight:800; background: linear-gradient(90deg, #00d4ff, #b400ff);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:4px;'>
        🫁 Welcome, {username}
    </h1>
    <p style='color:#a1a1aa; font-size:15px; margin-bottom:32px;'>
        Intelligent asthma risk monitoring powered by TinyML edge inference.
    </p>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class='home-card'>
            <h4>📡 Real-Time Dashboard</h4>
            <p>Live telemetry from ESP32 edge device — SpO₂, heart rate, respiration, AQI, and AI risk classification.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='home-card'>
            <h4>👥 Patient Management</h4>
            <p>Register new patients and configure emergency phone numbers for SMS alerts on critical events.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='home-card'>
            <h4>📊 Advanced Analytics</h4>
            <p>Risk distributions, feature correlations, and aggregated sensor trend analysis across time windows.</p>
        </div>
        """, unsafe_allow_html=True)

    # System status
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: rgba(0,192,75,0.08); border: 1px solid rgba(0,192,75,0.25);
        border-radius: 12px; padding: 16px 24px; display: flex; align-items: center; gap: 12px;'>
        <span style='font-size: 20px;'>🟢</span>
        <span style='color: #fafafa; font-size: 14px;'>
            <strong>System Online</strong> — Navigate using the sidebar to access the Dashboard, Patients, and Analytics.
        </span>
    </div>
    """, unsafe_allow_html=True)

def main():
    if not st.session_state["token"]:
        login_page()
    else:
        home_page()

if __name__ == "__main__":
    main()
