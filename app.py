import streamlit as st
import requests
import re
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🛡️")

st.markdown("<h2 style='text-align: center;'>Faria Global Standards Auditor</h2>", unsafe_allow_html=True)

# Función para consultar la API de LanguageTool (Mucho más estable y potente)
def check_text_api(text, lang_code):
    try:
        # Mapeo básico para la API
        lang_map = {'en': 'en-US', 'es': 'es', 'fr': 'fr', 'de': 'de'}
        target = lang_map.get(lang_code, 'en-US')
        
        response = requests.post('https://api.languagetool.org/v2/check', {
            'text': text,
            'language': target,
            'enabledOnly': 'false'
        })
        return response.json().get('matches', [])
    except:
        return []

texto_input = st.text_area("Paste standards here (Global Support):", height=250)

if st.button("🚀 Run Global Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        
        st.subheader("Audit Findings:")
        
        for i, linea in enumerate(lineas, 1):
            line_errors = []
            
            # Detectar idioma
            try:
                lang = detect(linea)
            except:
                lang = 'en'

            # 1. Reglas manuales (Formato)
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                line_errors.append("❌ Format: Must start with Uppercase or Number.")
            if "  " in linea:
                line_errors.append("⚠️ Format: Double spaces detected.")

            # 2. Análisis Ortográfico via API (Infalible)
            matches = check_text_api(linea, lang)
            for m in matches:
                # Filtrar reglas irrelevantes
                if m['rule']['category']['id'] not in ['CASING', 'WHITESPACE']:
                    msg = m['message']
                    # Traducir errores comunes a inglés
                    line_errors.append(f"⚠️ ({lang.upper()}) Spelling/Grammar: {msg}")

            # Mostrar
            if line_errors:
                st.markdown(f"**Line {i}:** {linea}")
                for e in line_errors:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                st.write("---")
        
        st.success("✅ Audit finished.")
    else:
        st.warning("Please paste text first.")
