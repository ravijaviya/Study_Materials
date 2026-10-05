import io
import os
import sys
import zipfile
import requests
import streamlit as st
import importlib

# 1. Set page config FIRST
st.set_page_config(
    page_title="TechGov Exam Gateway",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Bootstrapper function
@st.cache_resource(show_spinner="Initializing study modules...")
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
        st.error(f"System initialization failed. Please try again later. (Code: {response.status_code})")
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

# 3. Initialize session state for app routing
if "current_view" not in st.session_state:
    st.session_state.current_view = "gateway"

def navigate_to(view):
    st.session_state.current_view = view

def render_gateway():
    st.markdown("""
        <style>
        .gateway-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(90deg, #1f3c88 0%, #3a63d2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 3rem;
        }
        .exam-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            height: 100%;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s ease-in-out;
        }
        .exam-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="gateway-header">
            <h1>🏛️ TechGov Examination Portal</h1>
            <p style="font-size: 1.2rem;">Centralized Access to Technical Recruitment Study Materials</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="exam-card">
                <h3 style="color: #1f3c88;">UPSC IMD Scientist B</h3>
                <p><strong>Discipline:</strong> Instrumentation / Electronics</p>
                <p>Complete 15-day preparation guide covering ICT, Material Science, Energy, Project Management, and specialized meteorological telemetry.</p>
            </div>
            <br>
        """, unsafe_allow_html=True)
        if st.button("Access Study Portal ➔", key="imd_btn", use_container_width=True):
            navigate_to("imd")
            st.rerun()

    with col2:
        st.markdown("""
            <div class="exam-card">
                <h3 style="color: #1f3c88;">SEBI Grade A</h3>
                <p><strong>Discipline:</strong> Information Technology Officer</p>
                <p>Comprehensive coverage of database concepts, SQL, networking, programming logic, and financial market regulations.</p>
            </div>
            <br>
        """, unsafe_allow_html=True)
        st.button("Access Study Portal ➔", key="sebi_btn", disabled=True, help="Module currently under construction", use_container_width=True)

    with col3:
        st.markdown("""
            <div class="exam-card">
                <h3 style="color: #1f3c88;">UPSC CBI</h3>
                <p><strong>Discipline:</strong> Assistant Programmer</p>
                <p>Focused material on software engineering, C++/Java/Python debugging, AI model evaluation, and system architectures.</p>
            </div>
            <br>
        """, unsafe_allow_html=True)
        st.button("Access Study Portal ➔", key="cbi_btn", disabled=True, help="Module currently under construction", use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
            <div class="exam-card">
                <h3 style="color: #1f3c88;">Gujarat Police</h3>
                <p><strong>Discipline:</strong> Wireless PSI & Technical Operator</p>
                <p>Combined engineering eligibility pool materials covering communication networks, wireless protocols, and OMR evaluation methods.</p>
            </div>
            <br>
        """, unsafe_allow_html=True)
        st.button("Access Study Portal ➔", key="guj_btn", disabled=True, help="Module currently under construction", use_container_width=True)

    with col5:
        st.markdown("""
            <div class="exam-card">
                <h3 style="color: #1f3c88;">UPSC</h3>
                <p><strong>Discipline:</strong> Assistant Director (Systems)</p>
                <p>Advanced study modules on enterprise architecture, RAG pipelines, LLM deployments, and database management.</p>
            </div>
            <br>
        """, unsafe_allow_html=True)
        st.button("Access Study Portal ➔", key="ads_btn", disabled=True, help="Module currently under construction", use_container_width=True)

    with col6:
        st.empty()

    st.markdown("---")
    st.markdown("<div style='text-align: center; color: gray;'>Secure Gateway • Only authorized portal links are active.</div>", unsafe_allow_html=True)

# 4. Main Execution Logic
initialize_core_modules()

if st.session_state.current_view == "gateway":
    render_gateway()

elif st.session_state.current_view == "imd":
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("⬅️ Back to Gateway"):
            navigate_to("gateway")
            st.rerun()
    st.markdown("---")
    
    try:
        import home
        importlib.reload(home) 
    except Exception as e:
        st.error("Failed to load the selected study module. Please verify your connection or contact the administrator.")