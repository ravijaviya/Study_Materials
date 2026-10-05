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
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "https://rj-techgov.streamlit.app")

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
    # Determine Access Level
    AUTHORIZED_USER = "ravijaviya303@gmail.com"
    has_access = (email == AUTHORIZED_USER)

    # Premium Enterprise CSS
    st.markdown("""
        <style>
        .hero-container {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            padding: 3rem 2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 2.5rem;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);
            border-bottom: 4px solid #fbbf24;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }
        .hero-subtitle {
            font-size: 1.15rem;
            font-weight: 400;
            color: #93c5fd;
            max-width: 800px;
        }
        .user-profile {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: right;
        }
        .section-header {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e293b;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }
        .pro-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 24px;
            height: 240px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            transition: all 0.2s ease-in-out;
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
        }
        .pro-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 20px -5px rgba(0,0,0,0.1);
            border-color: #cbd5e1;
        }
        .pro-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
        }
        .pro-card.active-card::before { background: #10b981; }
        .pro-card.locked-card::before { background: #ef4444; }
        .pro-card.dev-card::before { background: #f59e0b; }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 4px;
        }
        .card-discipline {
            font-size: 0.9rem;
            font-weight: 600;
            color: #1e3a8a;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .card-desc {
            font-size: 0.95rem;
            color: #475569;
            line-height: 1.5;
        }
        .status-badge {
            position: absolute;
            top: 16px;
            right: 16px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
        }
        .badge-active { background: #d1fae5; color: #065f46; border: 1px solid #34d399; }
        .badge-locked { background: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
        .badge-dev { background: #fef3c7; color: #92400e; border: 1px solid #fbbf24; }
        .portal-footer {
            margin-top: 4rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 0.85rem;
            color: #64748b;
        }
        </style>
    """, unsafe_allow_html=True)

    # Hero Section with User Profile
    col_hero, col_prof = st.columns([3, 1])
    with col_hero:
        st.markdown("""
            <div style="padding: 2rem 1rem; color: white;">
                <div class="hero-title">🏛️ TechGov Examination Portal</div>
                <div class="hero-subtitle">Secure, centralized access to highly specialized technical recruitment study materials, master notes, and formula compendiums.</div>
            </div>
        """, unsafe_allow_html=True)
    with col_prof:
        st.markdown(f"""
            <div style="padding: 2rem 1rem; color: white; text-align: right;">
                <div style="font-size: 0.9rem; color: #93c5fd;">Logged in as:</div>
                <div style="font-weight: 600; margin-bottom: 10px;">{email}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Log Out", use_container_width=True):
            logout()
    
    st.markdown('<div class="hero-container" style="margin-top: -120px; z-index: -1; position: relative; height: 160px;"></div>', unsafe_allow_html=True)

    if not has_access:
        st.error("🔒 **Access Denied:** Your account does not have authorization to view the active study modules. Please contact the administrator.")

    # --- PRIMARY MODULES SECTION ---
    st.markdown('<div class="section-header">📚 Primary Study Modules</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        card_class = "active-card" if has_access else "locked-card"
        badge_class = "badge-active" if has_access else "badge-locked"
        badge_text = "AVAILABLE" if has_access else "LOCKED"
        
        st.markdown(f"""
            <div class="pro-card {card_class}">
                <span class="status-badge {badge_class}">{badge_text}</span>
                <div class="card-title">UPSC IMD Scientist 'B'</div>
                <div class="card-discipline">Instrumentation / Electronics</div>
                <div class="card-desc">Comprehensive 15-day preparation guide covering ICT, Material Science, Energy, Project Management, and telemetry.</div>
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
                <div class="card-desc">Combined engineering eligibility pool materials covering communication networks, wireless protocols, and architectures.</div>
            </div>
        """, unsafe_allow_html=True)
        
        if has_access:
            if st.button("Launch Module ➔", key="guj_btn", type="primary", use_container_width=True):
                navigate_to("gujarat")
                st.rerun()
        else:
            st.button("🔒 Locked", key="guj_btn", disabled=True, use_container_width=True)

    with col3:
        st.empty()

    # --- UPCOMING MODULES SECTION ---
    st.markdown('<div class="section-header">🟠 Modules In Development</div>', unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
            <div class="pro-card dev-card">
                <span class="status-badge badge-dev">IN PROGRESS</span>
                <div class="card-title">SEBI Grade A</div>
                <div class="card-discipline">IT Officer</div>
                <div class="card-desc">Coverage of enterprise database concepts, SQL, core networking, programming logic, and financial market regulations.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Under Construction", key="sebi_btn", disabled=True, use_container_width=True)

    with col5:
        st.markdown("""
            <div class="pro-card dev-card">
                <span class="status-badge badge-dev">IN PROGRESS</span>
                <div class="card-title">UPSC CBI</div>
                <div class="card-discipline">Assistant Programmer</div>
                <div class="card-desc">Focused material on software engineering methodologies, C++/Java debugging, AI model evaluation, and architectures.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Under Construction", key="cbi_btn", disabled=True, use_container_width=True)

    with col6:
        st.markdown("""
            <div class="pro-card dev-card">
                <span class="status-badge badge-dev">PLANNED</span>
                <div class="card-title">UPSC</div>
                <div class="card-discipline">Asst. Director (Systems)</div>
                <div class="card-desc">Advanced study modules on enterprise architecture, RAG pipelines, LLM deployments, and database management.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Under Construction", key="ads_btn", disabled=True, use_container_width=True)

    st.markdown("""
        <div class="portal-footer">
            <strong>Secure Gateway Protocol Active</strong><br>
            Identity verification enforced via Google OAuth 2.0. Unauthorized access attempts are logged.<br>
            System v2.5.0
        </div>
    """, unsafe_allow_html=True)

# 6. Main Execution & Routing Logic
if not st.session_state.user_email:
    # Render Login Screen
    st.markdown("""
        <div style="text-align: center; margin-top: 10vh;">
            <h1 style="color: #1e3a8a; font-size: 3rem;">🏛️ TechGov Portal</h1>
            <p style="color: #64748b; font-size: 1.2rem; margin-bottom: 2rem;">Authorized Personnel Only</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        result = oauth2.authorize_button(
            name="Secure Login with Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google_auth",
            extras_params={"prompt": "consent", "access_type": "offline"}
        )
        
        if result:
            # Exchange token for user info
            token = result["token"]["access_token"]
            resp = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {token}"})
            if resp.status_code == 200:
                st.session_state.user_email = resp.json().get("email")
                st.rerun()
            else:
                st.error("Authentication failed. Could not retrieve email from Google.")
else:
    # User is authenticated, initialize core and render app
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
            st.error(f"Failed to load the module. Error: {e}")

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
            st.error(f"Failed to load the module. Error: {e}")