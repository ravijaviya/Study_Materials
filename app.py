import io
import os
import sys
import zipfile
import requests
import streamlit as st
import importlib

# 1. Set page config FIRST
st.set_page_config(
    page_title="PrepByRJ Portal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inject Global CSS for consistent sidebar & modernized UI styling
st.markdown("""
    <style>
    /* Global Sidebar Navigation Buttons */
    section[data-testid="stSidebar"] .stButton>button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 15px !important;
        border: none !important;
        background-color: transparent;
        color: #94a3b8;
        transition: all 0.2s ease-in-out;
    }
    section[data-testid="stSidebar"] .stButton>button:hover {
        background-color: #1e293b;
        color: #f8fafc;
    }
    /* Specifically target the Return to Gateway button to make it distinct */
    section[data-testid="stSidebar"] .stButton>button[kind="primary"] {
        color: #38bdf8 !important;
        background-color: rgba(15, 23, 42, 0.5);
        border-bottom: 1px solid #334155 !important;
        border-radius: 0px;
    }
    
    /* Modernized Glassmorphism Login & Hero */
    .glass-panel {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
    }
    
    .gradient-text {
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Bootstrapper function for private modules
@st.cache_resource(show_spinner="Initializing secure core modules...")
def initialize_core_modules():
    pat = st.secrets["GITHUB_PAT"]
    repo = st.secrets["GITHUB_REPO"]
    branch = st.secrets.get("GITHUB_BRANCH", "main")

    url = f"https://api.github.com/repos/{repo}/zipball/{branch}"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers, timeout=25)
    if response.status_code != 200:
        st.error(f"System initialization failed. (Code: {response.status_code})")
        st.stop()

    target_dir = "/tmp/omr_core_src"
    os.makedirs(target_dir, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(target_dir)

    extracted_roots = [
        os.path.join(target_dir, d)
        for d in os.listdir(target_dir)
        if os.path.isdir(os.path.join(target_dir, d))
    ]

    if extracted_roots:
        root_path = extracted_roots[0]
        if root_path not in sys.path:
            sys.path.insert(0, root_path)

    return True

# 4. Session State Management
if "current_view" not in st.session_state:
    st.session_state.current_view = "gateway"

def navigate_to(view):
    st.session_state.current_view = view

def render_gateway(email):
    AUTHORIZED_USER = "ravijaviya303@gmail.com"
    has_access = (email == AUTHORIZED_USER)

    st.markdown("""
        <style>
        .hero-container {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 3rem 2.5rem;
            border-radius: 16px;
            color: #f8fafc;
            margin-bottom: 2.5rem;
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5);
            border: 1px solid #334155;
            position: relative;
            overflow: hidden;
        }
        .hero-container::before {
            content: '';
            position: absolute;
            top: -50px; right: -50px;
            width: 250px; height: 250px;
            background: #38bdf8;
            filter: blur(120px);
            opacity: 0.15;
            border-radius: 50%;
        }
        .hero-title {
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }
        .hero-subtitle {
            font-size: 1.15rem;
            color: #94a3b8;
            max-width: 800px;
            line-height: 1.6;
        }
        .user-badge-box {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid #334155;
            padding: 15px 20px;
            border-radius: 12px;
            text-align: right;
            backdrop-filter: blur(8px);
        }
        .section-header {
            font-size: 1.4rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-top: 1rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .pro-card {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 26px;
            height: 260px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            position: relative;
            backdrop-filter: blur(10px);
        }
        .pro-card:hover {
            transform: translateY(-5px);
            border-color: #475569;
            box-shadow: 0 15px 30px -5px rgba(0, 0, 0, 0.4);
            background: rgba(30, 41, 59, 0.8);
        }
        .active-card { border-top: 4px solid #10b981; }
        .locked-card { border-top: 4px solid #ef4444; }
        
        .card-title { font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px; padding-right: 80px; }
        .card-discipline { font-size: 0.85rem; font-weight: 600; color: #38bdf8; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;}
        .card-desc { font-size: 0.95rem; color: #cbd5e1; line-height: 1.5; }
        
        .status-badge {
            position: absolute; top: 22px; right: 22px; padding: 4px 10px;
            border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;
        }
        .badge-active { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-locked { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .portal-footer {
            margin-top: 5rem; padding-top: 2rem; border-top: 1px solid #1e293b;
            text-align: center; font-size: 0.85rem; color: #64748b;
        }
        </style>
    """, unsafe_allow_html=True)

    # Hero Banner
    col_hero, col_prof = st.columns([3, 1])
    with col_hero:
        st.markdown("""
            <div class="hero-container">
                <div class="hero-title gradient-text">🚀 PrepByRJ Academy</div>
                <div class="hero-subtitle">Premium master compendiums, integrated mock engines, and PYQ analytics for advanced technical recruitment.</div>
            </div>
        """, unsafe_allow_html=True)
    with col_prof:
        st.markdown(f"""
            <div class="user-badge-box">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Authenticated Identity</div>
                <div style="font-weight: 600; font-size: 1rem; color: #e2e8f0; margin-bottom: 10px;">{email}</div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Secure Log Out", use_container_width=True):
            if hasattr(st, "logout"):
                st.logout()
            else:
                st.session_state.clear()
            st.rerun()

    if not has_access:
        st.error("🔒 **Restricted Access:** Your account is not authorized to open primary study modules.")

    # --- ACTIVE MODULES ---
    st.markdown('<div class="section-header">📚 Active Study Modules</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    card_class = "active-card" if has_access else "locked-card"
    badge_class = "badge-active" if has_access else "badge-locked"
    badge_text = "AVAILABLE" if has_access else "LOCKED"

    with col1:
        st.markdown(f"""
            <div class="pro-card {card_class}">
                <span class="status-badge {badge_class}">{badge_text}</span>
                <div class="card-title">UPSC IMD Scientist 'B'</div>
                <div class="card-discipline">Instrumentation / Electronics</div>
                <div class="card-desc">Complete 15-day syllabus covering ICT, Materials Science, Energy, Project Management, and telemetry.</div>
            </div>
        """, unsafe_allow_html=True)
        if has_access:
            if st.button("Launch Module ➔", key="imd_btn", type="primary", use_container_width=True):
                navigate_to("imd")
                st.rerun()
        else:
            st.button("🔒 Locked", key="imd_btn", disabled=True, use_container_width=True)

    with col2:
        st.markdown(f"""
            <div class="pro-card {card_class}">
                <span class="status-badge {badge_class}">{badge_text}</span>
                <div class="card-title">Gujarat Police</div>
                <div class="card-discipline">Wireless PSI & Tech Operator</div>
                <div class="card-desc">Full 11-chapter engineering compendium, formulas, radar, antennas, and state surveillance systems.</div>
            </div>
        """, unsafe_allow_html=True)
        if has_access:
            if st.button("Launch Module ➔", key="guj_btn", type="primary", use_container_width=True):
                navigate_to("gujarat")
                st.rerun()
        else:
            st.button("🔒 Locked", key="guj_btn", disabled=True, use_container_width=True)

    with col3:
        st.markdown(f"""
            <div class="pro-card {card_class}">
                <span class="status-badge {badge_class}">{badge_text}</span>
                <div class="card-title">IB / MHA</div>
                <div class="card-discipline">DCIO (Technical)</div>
                <div class="card-desc">Cyber defense, digital forensics, RF interception, cryptography, and network telemetry.</div>
            </div>
        """, unsafe_allow_html=True)
        if has_access:
            if st.button("Launch Module ➔", key="dcio_btn", type="primary", use_container_width=True):
                navigate_to("dcio")
                st.rerun()
        else:
            st.button("🔒 Locked", key="dcio_btn", disabled=True, use_container_width=True)

    st.markdown("""
        <div class="portal-footer">
            Identity verification enforced via Google OAuth 2.0.<br>
            PrepByRJ System v4.1.0
        </div>
    """, unsafe_allow_html=True)

# 5. Native Streamlit Login Handling
user = getattr(st, "experimental_user", getattr(st, "user", None))
is_logged_in = getattr(user, "is_logged_in", False)

if not is_logged_in:
    # Modernized Login Screen
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 65vh;">
            <div class="glass-panel" style="padding: 3.5rem 4rem; text-align: center; max-width: 550px;">
                <h1 class="gradient-text" style="font-size: 3.2rem; margin-bottom: 0.5rem; letter-spacing: -0.03em;">🚀 PrepByRJ</h1>
                <p style="color: #94a3b8; font-size: 1.15rem; margin-bottom: 2rem; line-height: 1.5;">Advanced Technical Recruitment & Engineering Compendium Portal.</p>
                <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid #334155; padding: 12px; border-radius: 8px; margin-bottom: 2rem;">
                    <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">🔒 Authorized Personnel Only. Secure identity verification required to proceed.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Position the login button cleanly inside the visual glass panel area
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<div style='margin-top: -6rem; padding: 0 2rem;'>", unsafe_allow_html=True)
        if st.button("Verify Identity with Google", type="primary", use_container_width=True):
            st.login("google")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    user_email = getattr(user, "email", "").strip().lower()
    initialize_core_modules()

    if st.session_state.current_view == "gateway":
        render_gateway(user_email)
    else:
        # Centralized Back Button placed at the very top of the sidebar for all modules
        with st.sidebar:
            if st.button("⬅️ Return to PrepByRJ Gateway", type="primary", use_container_width=True):
                navigate_to("gateway")
                st.rerun()
            st.markdown("---")

        # Module Routing
        if st.session_state.current_view == "imd":
            try:
                is_loaded = "IMD_scientistB_instrumentation" in sys.modules
                import IMD_scientistB_instrumentation
                if is_loaded:
                    importlib.reload(IMD_scientistB_instrumentation)
            except Exception as e:
                st.error(f"Failed to load module: {e}")

        elif st.session_state.current_view == "gujarat":
            try:
                is_loaded = "wireless_psi" in sys.modules
                import wireless_psi
                if is_loaded:
                    importlib.reload(wireless_psi)
            except Exception as e:
                st.error(f"Failed to load module: {e}")

        elif st.session_state.current_view == "dcio":
            try:
                is_loaded = "DCIO_tech" in sys.modules
                import DCIO_tech
                if is_loaded:
                    importlib.reload(DCIO_tech)
            except Exception as e:
                st.error(f"Failed to load module: {e}")