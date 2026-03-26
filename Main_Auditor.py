import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Faria Global QA Dashboard", page_icon="⭐", layout="centered")

# --- CSS DEFINITIVO (Sin errores de color) ---
st.markdown("""
    <style>
    /* Estilo base para todos los botones */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #ffffff !important;
        border: 2px solid #4a148c !important;
        color: #4a148c !important;
        font-weight: bold;
        font-size: 1.1em;
        transition: 0.3s;
    }

    /* Efecto Hover */
    .stButton>button:hover {
        background-color: #4a148c !important;
        color: white !important;
        border-color: #ff4081 !important;
    }

    /* El único botón morado: el Global */
    .global-btn button {
        background-color: #4a148c !important;
        color: white !important;
        height: 4.5em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=300)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Standards QA Dashboard</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. SECCIÓN GLOBAL
st.markdown("### 🌍 Mixed Languages Auditor")
st.markdown('<div class="global-btn">', unsafe_allow_html=True)
if st.button("RUN GLOBAL AUDIT (Auto-Detect)"):
    st.switch_page("pages/0_Global_Audit.py")
st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 4. SECCIÓN ESPECIALIZADA
st.markdown("### 🎯 Specialized Auditors")
col1, col2 = st.columns(2)
with col1:
    if st.button("English"): st.switch_page("pages/1_English_Audit.py")
    if st.button("French"): st.switch_page("pages/3_French_Audit.py")
    if st.button("German"): st.switch_page("pages/5_German_Audit.py")
    if st.button("Chinese"): st.switch_page("pages/7_Chinese_Audit.py")
with col2:
    if st.button("Spanish"): st.switch_page("pages/2_Spanish_Audit.py")
    if st.button("Italian"): st.switch_page("pages/4_Italian_Audit.py")
    if st.button("Arabic"): st.switch_page("pages/6_Arabic_Audit.py")
    if st.button("Turkish"): st.switch_page("pages/8_Turkish_Audit.py")

# 5. FOOTER (Globalizado)
st.write("---")
st.markdown("<div style='text-align: center; color: #888; font-size: 0.85em;'>Standards and Services Team | Faria Education Group</div>", unsafe_allow_html=True)
