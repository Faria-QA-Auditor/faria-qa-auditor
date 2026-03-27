import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Arabic Auditor", page_icon="🇸🇦", layout="centered")

# --- CSS PROFESIONAL ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #4a148c;
        color: white;
        font-weight: bold;
        border: none;
    }
    textarea {
        direction: rtl;
        text-align: right;
    }
    .translation-box {
        background-color: #f0f2f6;
        border-left: 5px solid #4a148c;
        padding: 10px;
        margin: 10px 0;
        font-style: italic;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE TRADUCCIÓN AL VUELO ---
def translate_to_english(text):
    try:
        # Servicio gratuito de traducción para referencia rápida
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t&q={text}"
        res = requests.get(url).json()
        return res[0][0][0]
    except:
        return "Translation unavailable"

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Arabic Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste Arabic standards here:", height=300)

if texto_input:
    total_words = len(texto_input.split())
    st.markdown(f"**Word Count:** {total_words} / 1000")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            if linea.lower() in ["hide details", "show details"]:
                if "show" in linea.lower():
                    st.info(f"Line {i} ℹ️ 'Show details' detected: Verify if text is missing.")
                continue

            # --- ALERTAS PERSONALIZADAS ---
            alertas_locales = []
            
            if re.search(r'[,;]', linea):
                alertas_locales.append("⚠️ **Warning [Punctuation]:** Found western comma (,) or semicolon (;) instead of Arabic (، / ؛).")

            if re.search(r'[0-9]', linea) and re.search(r'[٠-٩]', linea):
                alertas_locales.append("❌ **Error [Format]:** Mixed number systems detected. Please use only one.")

            if re.search(r'\sو\s', linea) or linea.startswith('و '):
                alertas_locales.append("❌ **Error [Syntax]:** Space detected after conjunction 'Waw' (و).")

            if "األدب" in linea:
                alertas_locales.append("❌ **Error [Orthography]:** Missing Hamza on Alif. Use 'الأدب' instead of 'األدب'.")

            if len(linea.split()) > 40:
                alertas_locales.append("ℹ️ **Note [Style]:** Sentence exceeds 40 words.")

            # --- API LANGUAGETOOL ---
            errores_api = []
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'ar'}).json()
                for m in res.get('matches', []):
                    msg = m['message'].lower()
                    if any(x in msg for x in ["space", "comma", "espacio"]): continue
                    sug = f" (Try: {m['replacements'][0]['value']})" if m['replacements'] else ""
                    errores_api.append(f"Grammar/Spelling: Potential issue found.{sug}")
            except:
                pass

            # --- RENDERIZADO DE RESULTADOS ---
            header = f"Line {i}"
            todas_las_alertas = alertas_locales + errores_api

            if not todas_las_alertas:
                st.success(f"{header} ✅ Perfect")
            else:
                with st.expander(f"{header} ⚠️ Issues found", expanded=True):
                    # Texto original (RTL)
                    st.markdown(f"<div style='direction: rtl; text-align: right; background: #fff; padding: 10px; border: 1px solid #ddd;'>{linea}</div>", unsafe_allow_html=True)
                    
                    # TRADUCCIÓN AUTOMÁTICA
                    eng_translation = translate_to_english(linea)
                    st.markdown(f"<div class='translation-box'><b>English Translation:</b> {eng_translation}</div>", unsafe_allow_html=True)
                    
                    # Errores
                    for a in todas_las_alertas:
                        st.write(a)

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
