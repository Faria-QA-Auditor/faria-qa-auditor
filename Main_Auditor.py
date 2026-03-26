import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Faria Global QA Dashboard", page_icon="⭐", layout="centered")

# --- CSS Personalizado para Botones Grandes y Identidad Faria ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #f8f9fa;
        border: 2px solid #4a148c;
        color: #4a148c;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #4a148c;
        color: white;
        border-color: #ff4081;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=300)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Global Standards QA Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #666;'>Select a specialized auditor to begin your quality check.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. FILAS DE BOTONES (Organizados por columnas)
# Fila 1
col1, col2 = st.columns(2)
with col1:
    if st.button("🇺🇸 English Auditor"):
        st.switch_page("pages/1_English_Audit.py")
with col2:
    if st.button("🇪🇸 Spanish Auditor"):
        st.switch_page("pages/2_Spanish_Audit.py")

# Fila 2
col3, col4 = st.columns(2)
with col3:
    if st.button("🇫🇷 French Auditor"):
        st.switch_page("pages/3_French_Audit.py")
with col4:
    if st.button("🇮🇹 Italian Auditor"):
        st.switch_page("pages/4_Italian_Audit.py")

# Fila 3
col5, col6 = st.columns(2)
with col5:
    if st.button("🇩🇪 German Auditor"):
        st.switch_page("pages/5_German_Audit.py")
with col6:
    if st.button("🇸🇦 Arabic Auditor"):
        st.switch_page("pages/6_Arabic_Audit.py")

# Fila 4
col7, col8 = st.columns(2)
with col7:
    if st.button("🇨🇳 Chinese Auditor"):
        st.switch_page("pages/7_Chinese_Audit.py")
with col8:
    if st.button("🇹🇷 Turkish Auditor"):
        st.switch_page("pages/8_Turkish_Audit.py")

# 4. PIE DE PÁGINA
st.write("---")
st.caption("Standards & Services Team | Faria Education Group 2026")
