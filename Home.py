import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Faria Global Auditor", page_icon="🌎", layout="wide")

# --- CSS PARA ESTILO PROFESIONAL ---
st.markdown("""
    <style>
    .main-title { color: #1a237e; font-size: 3em; font-weight: bold; text-align: center; margin-bottom: 0px; }
    .sub-title { color: #444; font-size: 1.5em; text-align: center; margin-top: 0px; margin-bottom: 30px; }
    .feature-card { background-color: #f8f9fa; border-radius: 10px; padding: 20px; border-left: 5px solid #1a237e; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; background-color: #1a237e; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER CON LOGO
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=300)
except:
    st.markdown("<h1 style='color: #1a237e;'>FARIA EDUCATION GROUP</h1>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='main-title'>Global Standards Auditor</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Internal Data Scrubbing & Validation Suite</div>", unsafe_allow_html=True)

st.write("---")

# 3. DESCRIPCIÓN PROFESIONAL (EN INGLÉS)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 About the Tool")
    st.write("""
    The **Global Standards Auditor** is a specialized tool developed for the **Standards and Services Team**. 
    It ensures high-quality data migration and maintenance by auditing educational standards across 
    multiple languages using professional linguistic APIs and custom pedagogical rules.
    """)
    
    st.markdown("### 🚀 Key Features")
    st.markdown("""
    - **NFC Normalization:** Eliminates invisible character errors in accents and diacritics.
    - **Smart Triage:** Categorizes issues by severity (Critical, Warning, Informative).
    - **Pedagogical Alignment:** Validates Bloom's Taxonomy (Infinitive verbs) in learning objectives.
    - **Live Translation:** Provides instant English context for non-English standards.
    """)

with col2:
    st.markdown("### 🛠️ How to use")
    st.info("""
    1. **Select an Auditor:** Use the sidebar on the left to choose the language you need to scrub.
    2. **Paste Data:** Copy your standards from Atlas, ManageBac, or your source database.
    3. **Run Audit:** The system will process each line and provide a detailed diagnostic.
    4. **Validate Markers:** Pay attention to the **Blue Informative Boxes** regarding 'Show details' markers.
    """)
    
    st.markdown("### 🌍 Supported Languages")
    st.success("English • Spanish • French • Arabic • Turkish • Mixed Mode")

st.write("---")
st.caption("Developed for the Data & Service Team | Faria Education Group | 2026")
