import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Faria Global QA Dashboard", page_icon="⭐", layout="centered")

# --- CSS Personalizado para Botones Limpios y Estilo Faria ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #ffffff;
        border: 2px solid #4a148c;
        color: #4a148c;
        font-weight: bold;
        font-size: 1.1em; /* Un poco más grande para que se lea mejor sin las letras pequeñas */
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #4a148c;
        color: white;
        border-color: #ff4081;
    }
    /* Estilo resaltado para el Auditor Global */
    div[data-testid="stVerticalBlock"] > div:nth-child(3) .stButton>button {
        background-color: #4a148c;
        color: white;
        height: 4.5em;
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

# 3. BOTÓN GLOBAL
st.markdown("### 🌍 Mixed Languages Auditor")
if st.button("RUN GLOBAL AUDIT"):
    st.switch_page("pages/0_Global_Audit.py")

st.write("---")
st.markdown("### 🎯 Specialized Auditors")

# 4. FILAS DE BOTONES (Solo Nombres de Idiomas)
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

# 5. FOOTER
st.write("---")
st.caption("Standards & Services Team | Bogotá, Colombia 2026")
