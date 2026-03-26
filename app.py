import streamlit as st
import requests
import re
from langdetect import detect, DetectorFactory

# Configuración de estabilidad
DetectorFactory.seed = 0

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Faria Global QA Auditor", page_icon="⭐", layout="centered")

# --- CSS Personalizado ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stTextArea textarea {
        border: 2px solid #4a148c !important; 
        border-radius: 8px !important;
        background-color: #ffffff !important;
    }
    .stTextArea textarea:focus {
        border-color: #ff4081 !important;
        box-shadow: 0 0 0 0.2rem rgba(255, 64, 129, 0.25) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE API
def check_text_api(text, lang_code):
    try:
        target = lang_code
        if lang_code.startswith('zh'): target = 'zh-CN'
        response = requests.post('https://api.languagetool.org/v2/check', {
            'text': text,
            'language': target,
            'motherTag': 'en-US',
            'enabledOnly': 'false'
        })
        return response.json().get('matches', [])
    except:
        return []

# 3. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=280)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h3 style='color: #444;'>Global Standards QA Auditor</h3>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 4. ÁREA DE TEXTO
texto_input = st.text_area("Paste standards here:", height=250)

if texto_input:
    count = len([l for l in texto_input.split('\n') if l.strip()])
    if count <= 1000:
        st.info(f"📊 Batch Status: {count}/1000 lines loaded.")
    else:
        st.error(f"❌ Limit Exceeded: {count}/1000 lines.")

# 5. BOTÓN Y LÓGICA DE AUDITORÍA
if st.button("🚀 Run Global Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        st.subheader("Audit Findings:")
        issues_found = 0
        
        for i, linea in enumerate(lineas, 1):
            line_errors = []
            try:
                lang = detect(linea)
            except:
                lang = 'en'

            # --- NUEVA REGLA: DETECCIÓN DE PALABRAS CORTADAS ---
            # Busca palabras separadas por guion o espacios internos raros (ej: "evalu- ación" o "co rrecto")
            broken_word_match = re.search(r'\w+-\s+\w+|\w+\s+-\w+', linea)
            if broken_word_match:
                line_errors.append(f"⚠️ **Format**: Broken word detected ('{broken_word_match.group()}'). Please merge.")

            # --- REGLAS DE FORMATO BÁSICO ---
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                line_errors.append("❌ **Format**: Must start with an Uppercase letter or a Number.")
            if "  " in linea:
                line_errors.append("⚠️ **Format**: Double spaces detected.")

            # --- REGLAS DE ORTOGRAFÍA (API) ---
            matches = check_text_api(linea, lang)
            for m in matches:
                if m['rule']['category']['id'] not in ['CASING', 'WHITESPACE', 'PUNCTUATION']:
                    start, end = m['offset'], m['offset'] + m['length']
                    bad_word = linea[start:end]
                    err_label = "Spelling" if m['rule']['category']['id'] == 'TYPOS' else "Grammar"
                    suggs = [r['value'] for r in m['replacements'][:2]]
                    sugg_txt = f" -> Suggested: **{', '.join(suggs)}**" if suggs else ""
                    
                    line_errors.append(f"⚠️ **({lang.upper()}) {err_label}**: Found '{bad_word}'{sugg_txt}")

            if line_errors:
                issues_found += 1
                st.markdown(f"**Line {i}:** {linea}")
                for e in line_errors:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                st.write("---")
        
        if issues_found == 0:
            st.success("✅ No issues detected.")
        else:
            st.success(f"🎉 Audit finished. Found issues in {issues_found} lines.")
    else:
        st.warning("Please paste text first.")

with st.sidebar:
    st.header("⭐ Global Guide")
    st.markdown("""
    - **Language Support:** Global (EN, ES, FR, AR, ZH, HI, etc.)
    - **Broken Words:** Now detects words split by hyphens or odd spaces.
    - **English Output:** All alerts are in English.
    """)
    st.divider()
    st.caption("Standards & Services Team")
