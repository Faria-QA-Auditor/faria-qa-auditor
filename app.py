import streamlit as st
import requests
import re
from langdetect import detect, DetectorFactory

# Configuración de estabilidad para detección de idiomas
DetectorFactory.seed = 0

# 1. CONFIGURACIÓN DE PÁGINA (Estrella ⭐ y Layout)
st.set_page_config(page_title="Faria Global QA Auditor", page_icon="⭐", layout="centered")

# --- CSS Personalizado: Identidad Faria (Bordes Morados/Rosa) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stTextArea textarea {
        border: 2px solid #4a148c !important; 
        border-radius: 8px !important;
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    .stTextArea textarea:focus {
        border-color: #ff4081 !important;
        box-shadow: 0 0 0 0.2rem rgba(255, 64, 129, 0.25) !important;
    }
    .stButton>button {
        border-radius: 20px;
        padding: 10px 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN DEL MOTOR (SOPORTE GLOBAL EXPANDIDO)
def check_text_api(text, lang_code):
    try:
        # Simplificamos: Si es chino usamos el tag general, si no, usamos el código detectado
        # La API de LanguageTool soporta AR, ZH, HI, TL (Tagalog), etc.
        target = lang_code
        if lang_code.startswith('zh'): target = 'zh-CN'
        
        response = requests.post('https://api.languagetool.org/v2/check', {
            'text': text,
            'language': target,
            'motherTag': 'en-US', # Forzamos explicaciones en inglés
            'enabledOnly': 'false'
        })
        return response.json().get('matches', [])
    except:
        return []

# 3. HEADER (Logo y Título centrado)
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=280)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h3 style='color: #444;'>Global Standards QA Auditor</h3>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 4. ÁREA DE TEXTO Y CONTADOR
texto_input = st.text_area("Paste standards here:", height=250)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    count = len(lineas_reales)
    if count > 1000:
        st.error(f"❌ **Limit Exceeded:** {count}/1000 lines.")
    else:
        st.info(f"📊 **Batch Status:** {count}/1000 lines loaded.")

# 5. PROCESAMIENTO DE AUDITORÍA
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
                
                # Identificación automática (Soporta +50 idiomas)
                try:
                    lang = detect(linea)
                except:
                    lang = 'en'

                # --- REGLA A: FORMATO ---
                if not re.match(r'^([A-Z]|[0-9])', linea): 
                    line_errors.append("❌ **Format**: Must start with an Uppercase letter or a Number.")
                if "  " in linea:
                    line_errors.append("⚠️ **Format**: Double spaces detected.")

                # --- REGLA B: ORTOGRAFÍA GLOBAL ---
                matches = check_text_api(linea, lang)
                for m in matches:
                    if m['rule']['category']['id'] not in ['CASING', 'WHITESPACE', 'PUNCTUATION']:
                        # EXTRACCIÓN DE PALABRA
                        start = m['offset']
                        end = m['offset'] + m['length']
                        bad_word = linea[start:end]
                        
                        err_label = "Spelling" if m['rule']['category']['id'] == 'TYPOS' else "Grammar"
                        
                        suggs = [r['value'] for r in m['replacements'][:2]]
                        sugg_txt = f" -> Suggested: **{', '.join(suggs)}**" if suggs else ""
                        
                        # Alerta unificada en Inglés
                        line_errors.append(f"⚠️ **({lang.upper()}) {err_label}**: Found '{bad_word}'{sugg_txt}")

                if line_errors:
                    issues_found += 1
                    st.markdown(f"**Line {i}:** {linea}")
                    for e in line_errors:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                    st.write("---")
            
            if issues_found == 0:
                st.success("✅ Perfect! No spelling or format issues detected.")
            else:
                st.success(f"🎉 Audit finished. Found issues in {issues_found} lines.")
    else:
        st.warning("Please paste some text first.")

# 6. SIDEBAR
with st.sidebar:
    st.header("⭐ Global Guide")
    st.markdown("""
    - **Language Support:** Now supporting EN, ES, FR, DE, IT, PT, AR, ZH, HI, TL, and more.
    - **English Output:** Error descriptions are always in English.
    - **Precision:** Extracts the exact word in the native script.
    """)
    st.divider()
    st.caption("Standards & Services Team")
