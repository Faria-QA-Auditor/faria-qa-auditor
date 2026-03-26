import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory
import gc # Para limpiar la memoria

# Estabilidad para detección de idiomas
DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🛡️")

# Cargamos el motor de forma ultra-eficiente
@st.cache_resource
def get_tool(lang):
    try:
        return language_tool_python.LanguageTool(lang)
    except:
        return language_tool_python.LanguageTool('en-US')

# --- Header Section ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        # Intenta cargar el logo local que subiste
        st.image("logo.jpg", width=250)
    except:
        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>FARIA EDUCATION GROUP</h2>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>Global Standards Auditor</h3>", unsafe_allow_html=True)
st.write("---")

# --- Input Section ---
texto_input = st.text_area("Paste standards here (Max 1,000 lines):", height=250)

if st.button("🚀 Run Audit"):
    if texto_input:
        # Limpiamos líneas vacías
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        total = len(lineas)
        
        if total > 1000:
            st.error(f"⚠️ Batch too large! Please use max 1,000 lines (Current: {total}).")
        else:
            progress_bar = st.progress(0)
            status_info = st.empty()
            
            ok_count = 0
            error_count = 0

            for i, linea in enumerate(lineas, 1):
                line_errors = []
                
                # 1. Detección rápida de idioma
                try:
                    lang_code = detect(linea)
                    actual_lang = 'ca-ES' if lang_code == 'ca' else lang_code
                except:
                    lang_code = "en"
                    actual_lang = 'en-US'

                # 2. Reglas de Formato Faria
                if not re.match(r'^([A-Z]|[0-9])', linea): 
                    line_errors.append("❌ Must start with Uppercase or Number.")
                if not linea.endswith('.'): 
                    line_errors.append("❌ Missing period at the end.")
                if "  " in linea:
                    line_errors.append("⚠️ Double spaces detected.")

                # 3. Ortografía y Typos
                try:
                    tool = get_tool(actual_lang)
                    matches = tool.check(linea)
                    for m in matches:
                        # Usamos getattr para evitar errores de atributos inexistentes
                        rid = getattr(m, 'ruleId', '')
                        if rid not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD']:
                            msg = getattr(m, 'message', 'Potential typo')
                            line_errors.append(f"⚠️ ({lang_code.upper()}) {msg}")
                except:
                    pass

                # 4. Mostrar resultados
                if not line_errors:
                    ok_count += 1
                else:
                    error_count += 1
                    with st.expander(f"Line {i}: Issues Found", expanded=False):
                        st.write(f"**Text:** {linea}")
                        for e in line_errors:
                            st.write(e)
                
                # Actualizar progreso
                progress_bar.progress(i / total)
                if i % 10 == 0: # Actualizamos el texto cada 10 líneas para ahorrar recursos
                    status_info.text(f"Processing line {i} of {total}...")
            
            status_info.empty()
            st.success(f"🎉 Done! ✅ {ok_count} Passed | ❌ {error_count} Issues found.")
            
            # Limpieza manual de memoria al terminar
            gc.collect() 
            
    else:
        st.warning("Please paste some text first.")
