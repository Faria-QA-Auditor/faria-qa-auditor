import streamlit as st
import requests
import re
from langdetect import detect, DetectorFactory

# Estabilidad para la detección de idiomas
DetectorFactory.seed = 0

# 1. CONFIGURACIÓN DE PÁGINA (Estrella ⭐ y Layout)
st.set_page_config(page_title="Faria Global QA Auditor", page_icon="⭐", layout="centered")

# 2. FUNCIÓN DEL MOTOR (CÓDIGO DE ALTA PRECISIÓN - API EXTERNA)
def check_text_api(text, lang_code):
    try:
        # Mapeo de idiomas para la API
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

# 3. HEADER PERSONALIZADO (Logo y Estética)
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    # Intenta cargar el logo de Faria
    st.image("logo.jpg", width=280)
except:
    # Respaldo si el archivo no carga
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h3 style='color: #444;'>Global Standards QA Auditor</h3>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 4. ÁREA DE TEXTO Y CONTADOR DINÁMICO
texto_input = st.text_area("Paste standards here:", height=250, placeholder="Example:\nDrgs\n.2 Standards\n2.2 Travaillee")

# Lógica del contador visual (No afecta la auditoría)
if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    count = len(lineas_reales)
    
    if count > 1000:
        st.error(f"❌ **Limit Exceeded:** {count}/1000 lines. Please reduce the batch.")
    elif count > 800:
        st.warning(f"⚠️ **High Volume:** {count}/1000 lines loaded.")
    else:
        st.info(f"📊 **Batch Status:** {count}/1000 lines loaded.")

# 5. BOTÓN Y PROCESAMIENTO
if st.button("🚀 Run Global Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        
        # Bloqueo de seguridad por volumen
        if len(lineas) > 1000:
            st.error("Please reduce the batch to 1,000 lines or fewer.")
        else:
            st.subheader("Audit Findings:")
            issues_found = 0
            
            for i, linea in enumerate(lineas, 1):
                line_errors = []
                
                # Identificación de idioma por línea
                try:
                    lang = detect(linea)
                except:
                    lang = 'en'

                # --- REGLA 1: FORMATO (Mayúscula/Número) ---
                if not re.match(r'^([A-Z]|[0-9])', linea): 
                    line_errors.append("❌ **Format**: Must start with an Uppercase letter or a Number.")
                
                # --- REGLA 2: ESPACIOS DOBLES ---
                if "  " in linea:
                    line_errors.append("⚠️ **Format**: Double spaces detected.")

                # --- REGLA 3: ORTOGRAFÍA/GRAMÁTICA (API EXTERNA) ---
                # Esta es la lógica que detecta "estándares", "travaillée" y "drgs"
                matches = check_text_api(linea, lang)
                for m in matches:
                    # Filtramos reglas que no queremos (como la del punto final que pediste quitar)
                    if m['rule']['category']['id'] not in ['CASING', 'WHITESPACE', 'PUNCTUATION']:
                        msg = m['message']
                        # Reporte siempre en inglés para el equipo global
                        line_errors.append(f"⚠️ **({lang.upper()}) Spelling/Grammar**: {msg}")

                # MOSTRAR RESULTADOS (Vista Abierta)
                if line_errors:
                    issues_found += 1
                    st.markdown(f"**Line {i}:** {linea}")
                    for e in line_errors:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                    st.write("---")
            
            # Resumen final
            if issues_found == 0:
                st.success("✅ Perfect! No spelling or format issues detected in this batch.")
            else:
                st.success(f"🎉 Audit finished. Found issues in {issues_found} lines.")
    else:
        st.warning("Please paste some text first.")

# 6. SIDEBAR (Instru
