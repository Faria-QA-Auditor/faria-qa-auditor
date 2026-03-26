import streamlit as st
import requests
import re
from langdetect import detect, DetectorFactory

# Estabilidad para la detección de idiomas
DetectorFactory.seed = 0

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Faria Global QA Auditor", page_icon="⭐", layout="centered")

# --- CSS Personalizado para el Borde del Cuadro de Texto ---
# Usamos un tono morado oscuro inspirado en el fondo de tu imagen
st.markdown("""
    <style>
    /* Estilo para el cuadro de texto (textarea) */
    .stTextArea textarea {
        border: 2px solid #4a148c; /* Morado oscuro corporativo */
        border-radius: 8px; /* Bordes ligeramente redondeados */
    }
    /* Estilo cuando el cuadro de texto está enfocado (haces clic) */
    .stTextArea textarea:focus {
        border-color: #ff4081; /* Rosa vibrante para el enfoque, inspirado en el logo */
        box-shadow: 0 0 0 0.2rem rgba(255, 64, 129, 0.25); /* Resplandor suave rosa */
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN DEL MOTOR (API EXTERNA - ALTA PRECISIÓN)
def check_text_api(text, lang_code):
    try:
        lang_map = {'en': 'en-US', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt'}
        target = lang_map.get(lang_code, 'en-US')
        response = requests.post('https://api.languagetool.org/v2/check', {
            'text': text,
            'language': target,
            'enabledOnly': 'false'
        })
        return response.json().get('matches', [])
    except:
        return []

# 3. HEADER PERSONALIZADO
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=280)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h3 style='color: #444;'>Global Standards QA Auditor</h3>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 4. ÁREA DE TEXTO (EN BLANCO, CON BORDE PERSONALIZADO) Y CONTADOR
# Hemos mantenido el cuadro vacío, y el CSS de arriba se encargará del borde.
texto_input = st.text_area("Paste standards here:", height=250)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    count = len(lineas_reales)
    
    if count > 1000:
        st.error(f"❌ **Limit Exceeded:** {count}/1000 lines.")
    elif count > 800:
        st.warning(f"⚠️ **High Volume:** {count}/1000 lines.")
    else:
        st.info(f"📊 **Batch Status:** {count}/1000 lines loaded.")

# 5. BOTÓN Y PROCESAMIENTO
if st.button("🚀 Run Global Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        
        if len(lineas) > 1000:
            st.error("Please reduce the batch to 1,000 lines or fewer.")
        else:
            st.subheader("Audit Findings:")
            issues_found = 0
            
            for i, linea in enumerate(lineas, 1):
                line_errors = []
                
                try:
                    lang = detect(linea)
                except:
                    lang = 'en'

                # Formato
                if not re.match(r'^([A-Z]|[0-9])', linea): 
                    line_errors.append("❌ **Format**: Must start with an Uppercase letter or a Number.")
                if "  " in linea:
                    line_errors.append("⚠️ **Format**: Double spaces detected.")

                # Ortografía/Gramática (Alertas en Inglés)
                matches = check_text_api(linea, lang)
                for m in matches:
                    if m['rule']['category']['id'] not in ['CASING', 'WHITESPACE', 'PUNCTUATION']:
                        msg = m['message']
                        line_errors.append(f"⚠️ **({lang.upper()}) Spelling/Grammar**: {msg}")

                # Resultados
                if line_errors:
                    issues_found += 1
                    st.markdown(f"**Line {i}:** {linea}")
                    for e in line_errors:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                    st.write("---")
            
            if issues_found == 0:
                st.success("✅ Perfect! No issues detected.")
            else:
                st.success(f"🎉 Audit finished. Found issues in {issues_found} lines.")
    else:
        st.warning("Please paste some text first.")

# 6. SIDEBAR
with st.sidebar:
    st.header("⭐ Quick Guide")
    st.markdown("""
    - **Capacity:** Max 1,000 lines.
    - **Language:** Auto-detects EN, ES, FR, DE, IT, PT.
    - **Alerts:** Provided in English for global consistency.
    """)
    st.divider()
    st.caption("Faria Education Group - Standards & Services Team")
