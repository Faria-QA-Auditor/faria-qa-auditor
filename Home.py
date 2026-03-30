import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Faria Global Auditor", page_icon="🌎", layout="wide")

# --- CSS PARA EL LOOK & FEEL PROFESIONAL ---
st.markdown("""
    <style>
    .main-title { color: #1a237e; font-size: 3em; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-title { color: #444; font-size: 1.5em; text-align: center; margin-top: 0px; margin-bottom: 30px; }
    .feature-card { 
        background-color: #f8f9fa; 
        border-radius: 10px; 
        padding: 25px; 
        border-left: 8px solid #1a237e; 
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    h3 { color: #1a237e; margin-top: 0; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
# Intentamos cargar el logo, si no, ponemos el nombre en grande
try:
    st.image("logo.jpg", width=350)
except:
    st.markdown("<h1 style='color: #1a237e; font-family: sans-serif;'>FARIA EDUCATION GROUP</h1>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='main-title'>Global Standards Auditor</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Advanced Data Scrubbing & Linguistic Validation Suite</div>", unsafe_allow_html=True)

st.write("---")

# 3. CONTENIDO PRINCIPAL
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
    <div class='feature-card'>
        <h3>📝 Project Purpose</h3>
        <p>Developed specifically for the <b>Standards and Services Team</b>, this auditor automates 
        the detection of formatting, spelling, and structural issues in educational standards 
        across our global databases.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Core Capabilities")
    st.markdown("""
    * **Smart Triage:** Instant categorization of issues (Critical, Warning, Info).
    * **NFC Shield:** Automatic fixing of invisible character encoding errors.
    * **Database Markers:** Native detection of <i>'Show/Hide details'</i> to prevent data loss.
    * **Pedagogical Guard:** Verification of infinitive verbs (Bloom's Taxonomy) in objectives.
    """)

with col2:
    st.markdown("### 🛠️ Quick Start Guide")
    st.info("""
    1.  **Navigate:** Use the **Sidebar** on the left to select the specific language auditor or the 'Global Mixed' mode.
    2.  **Input:** Paste your raw data from Atlas, ManageBac, or Pamoja.
    3.  **Process:** Click the 'Run Audit' button.
    4.  **Review:** Examine the yellow warnings for errors or the **blue boxes** for missing information.
    """)
    
    st.markdown("### 🌍 Linguistic Scope")
    st.success("English • Spanish • French • Arabic • Turkish • Mixed Mode")

st.write("---")
st.markdown("<div style='text-align: center; color: #888;'>Standards and Services | Faria Education Group | 2026</div>", unsafe_allow_html=True)
