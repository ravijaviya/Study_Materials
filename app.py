import io
import os
import sys
import zipfile
import requests
import streamlit as st
import importlib
from streamlit_oauth import OAuth2Component

# 1. Set page config FIRST
st.set_page_config(
    page_title="TechGov Exam Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Bootstrapper function for private modules
@st.cache_resource(show_spinner="Authenticating and initializing secure modules...")
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
        st.error(f"Secure system initialization failed. Please try again later. (Code: {response.status_code})")
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

# 3. Google OAuth Setup
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "https://prepbyrj.streamlit.app/")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_TOKEN_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_TOKEN_URL)

# 4. Session State Management
if "current_view" not in st.session_state:
    st.session_state.current_view = "gateway"
if "user_email" not in st.session_state:
    st.session_state.user_email = None

def navigate_to(view):
    st.session_state.current_view = view

def logout():
    st.session_state.user_email = None
    st.session_state.current_view = "gateway"
    st.rerun()

# 5. Gateway UI Rendering
def render_gateway(email):
    AUTHORIZED_USER = "ravijaviya303@gmail.com"
    has_access = (email == AUTHORIZED_USER)

    # Aggressive Dark Theme CSS Injection
    st.markdown("""
        <style>
        /* Force Dark Backgrounds & Typography */
        .stApp, .main {
            background-color: #0f172a !important;
            color: #f8fafc !important;
        }
        
        /* Hero Section */
        .hero-container {
            background: linear-gradient(135deg, #020617 0%, #1e3a8a 100%);
            padding: 2.5rem 2rem;
            border-radius: 12px;
            color: #f8fafc;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            border: 1px solid #1e293b;
            border-bottom: 4px solid #f59e0b;
        }
        .hero-title {
            font-size: 2.4rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 0.4rem;
            letter-spacing: -0.02em;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            font-weight: 400;
            color: #93c5fd;
            max-width: 850px;
            line-height: 1.5;
        }
        .user-badge-box {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid #334155;
            padding: 12px 18px;
            border-radius: 8px;
            text-align: right;
            backdrop-filter: blur(4px);
        }

        /* Section Headings */
        .section-header {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-top: 2rem;
            margin-bottom: 1.2rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #334155;
        }

        /* Cards in Dark Mode */
        .pro-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 22px;
            height: 245px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            transition: all 0.25s ease-in-out;
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
        }
        .pro-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px -5px rgba(0, 0, 0, 0.6);
            border-color: #475569;
        }
        .pro-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
        }
        .pro-card.active-card::before { background: #10b981; }
        .pro-card.locked-card::before { background: #ef4444; }
        .pro-card.dev-card::before { background: #f59e0b; }

        .card-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 3px;
            padding-right: 75px;
        }
        .card-discipline {
            font-size: 0.82rem;
            font-weight: 600;
            color: #38bdf8;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .card-desc {
            font-size: 0.9rem;
            color: #cbd5e1;
            line-height: 1.5;
        }

        /* Status Badges */
        .status-badge {
            position: absolute;
            top: 18px;
            right: 18px;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.05em;
        }
        .badge-active { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #059669; }
        .badge-locked { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #b91c1c; }
        .badge-dev { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #d97706; }

        /* Footer */
        .portal-footer {
            margin-top: 4rem;
            padding-top: 1.5rem;
            border-top: 1px solid #1e293b;
            text-align: center;
            font-size: 0.85rem;
            color: #64748b;
        }
        </style>
    """, unsafe_allow_html=True)

    # Hero Banner
    col_hero, col_prof = st.columns([3, 1])
    with col_hero:
        st.markdown("""
            <div class="hero-container">
                <div class="hero-title">🏛️ TechGov Examination Portal</div>
                <div class="hero-subtitle">Centralized access to specialized technical recruitment study compendiums, systems architecture, and engineering notes.</div>
            </div>
        """, unsafe_allow_html=True)
    with col_prof:
        st.markdown(f"""
            <div class="user-badge-box">
                <div style="font-size: 0.8rem; color: #94a3b8;">Authenticated Identity</div>
                <div style="font-weight: 600; font-size: 0.95rem; color: #e2e8f0; margin-bottom: 8px;">{email}</div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Log Out", use_container_width=True):
            logout()

    if not has_access:
        st.error("🔒 **Restricted Access:** Your account is not authorized to open primary study modules. Please contact the administrator.")

    # --- ROW 1: PRIMARY MODULES ---
    st.markdown('<div class="section-header">🟢 Active Study Modules</div>', unsafe_allow_html=True)
    
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
                <div class="card-desc">Cyber defense, network forensics, microwave links, cryptanalysis, and tactical telecommunications.</div>
            </div>
        """, unsafe_allow_html=True)
        if has_access:
            if st.button("Launch Module ➔", key="dcio_btn", type="primary", use_container_width=True):
                navigate_to("dcio")
                st.rerun()
        else:
            st.button("🔒 Locked", key="dcio_btn", disabled=True, use_container_width=True)

    # --- ROW 2: OTHER PROGRAMMED MODULES ---
    st.markdown('<div class="section-header">🟠 Additional Technical Cadres</div>', unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
            <div class="pro-card dev-card">
                <span class="status-badge badge-dev">IN PROGRESS</span>
                <div class="card-title">Income Tax / CBDT</div>
                <div class="card-discipline">Assistant Director (Systems)</div>
                <div class="card-desc">Enterprise relational & distributed databases, data warehousing, cloud infrastructure, and IT governance.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Under Construction", key="ads_btn", disabled=True, use_container_width=True)

    with col5:
        st.markdown("""
            <div class="pro-card dev-card">
                <span class="status-badge badge-dev">IN PROGRESS</span>
                <div class="card-title">SEBI Grade A</div>
                <div class="card-discipline">IT Officer</div>
                <div class="card-desc">Enterprise databases, SQL querying, network topologies, programming logic, and financial regulations.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Under Construction", key="sebi_btn", disabled=True, use_container_width=True)

    with col6:
        st.markdown("""
            <div class="pro-card dev-card">
                <span class="status-badge badge-dev">PLANNED</span>
                <div class="card-title">UPSC CBI</div>
                <div class="card-discipline">Assistant Programmer</div>
                <div class="card-desc">System debugging, code verification, algorithms, and application architectures.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Under Construction", key="cbi_btn", disabled=True, use_container_width=True)

    st.markdown("""
        <div class="portal-footer">
            Identity verification enforced via Google OAuth 2.0. Unauthorized access attempts are monitored.<br>
            System v3.0.0
        </div>
    """, unsafe_allow_html=True)

# 6. Main Execution & Routing Logic
if not st.session_state.user_email:
    st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
        </style>
        <div style="text-align: center; margin-top: 12vh;">
            <h1 style="color: #60a5fa; font-size: 3rem; font-weight: 800; letter-spacing: -0.02em;">🏛️ TechGov Portal</h1>
            <p style="color: #94a3b8; font-size: 1.15rem; margin-bottom: 2rem;">Authorized Personnel Only • Identity Verification Required</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        result = oauth2.authorize_button(
            name="Authenticate with Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google_auth",
            extras_params={"prompt": "consent", "access_type": "offline"}
        )
        
        if result:
            # FIX: Clear query params immediately to break the infinite reload loop!
            if hasattr(st, "query_params"):
                st.query_params.clear()
            else:
                st.experimental_set_query_params() # Fallback for older Streamlit versions
                
            if "token" in result:
                token = result["token"]["access_token"]
                try:
                    with st.spinner("Verifying identity..."):
                        resp = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {token}"}, timeout=10)
                        if resp.status_code == 200:
                            st.session_state.user_email = resp.json().get("email")
                            st.rerun()
                        else:
                            st.error(f"Authentication failed with Google (Status {resp.status_code}).")
                except Exception as e:
                    st.error(f"Network error during verification: {e}")
            else:
                st.error("Authentication canceled or token missing.")
else:
    initialize_core_modules()

    if st.session_state.current_view == "gateway":
        render_gateway(st.session_state.user_email)

    elif st.session_state.current_view == "imd":
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("⬅️ Return to Gateway"):
                navigate_to("gateway")
                st.rerun()
        st.markdown("---")
        try:
            import IMD_scientistB_instrumentation
            importlib.reload(IMD_scientistB_instrumentation)
        except Exception as e:
            st.error(f"Failed to load module: {e}")

    elif st.session_state.current_view == "gujarat":
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("⬅️ Return to Gateway"):
                navigate_to("gateway")
                st.rerun()
        st.markdown("---")
        try:
            import wireless_psi
            importlib.reload(wireless_psi)
        except Exception as e:
            st.error(f"Failed to load module: {e}")

    elif st.session_state.current_view == "dcio":
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("⬅️ Return to Gateway"):
                navigate_to("gateway")
                st.rerun()
        st.markdown("---")
        try:
            import DCIO_tech
            importlib.reload(DCIO_tech)
        except Exception as e:
            st.error(f"Failed to load module: {e}")