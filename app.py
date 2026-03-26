import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory

# Estabilidad para la detección
DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA", page_icon="🌍")

@st.cache_resource
def get_tool(lang):
    # Intentamos cargar el idioma específico, si falla usamos inglés
    try:
        return language_tool_python.LanguageTool(lang)
    except:
        return language_tool_python.LanguageTool('en-US')

st.title("🌍 Faria Universal QA Auditor")
st.write("Auditoría multilingüe a prueba de errores.")

texto_input = st.text_area("Pega tus estándares aquí:", height=300)

if st.button("🚀 Iniciar Auditoría"):
    if texto_input:
        lineas = texto_input.strip().split('\n')
        progreso = st.progress(0)
        
        for i, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if not linea: continue
            
            errores = []
            
            # 1. Detección de idioma segura
            try:
                lang_code = detect(linea)
                # Ajuste para catalán
                actual_lang = 'ca-ES' if lang_code == 'ca' else lang_code
            except:
                lang_code = "unknown"
                actual_lang = 'en-US'

            # 2. Validación de Formato (Faria Rules)
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                errores.append("❌ Debe empezar con Mayúscula o Número.")
            if not linea.endswith('.'): 
                errores.append("❌ Falta punto final.")

            # 3. Validación Gramatical Protegida
            try:
                tool = get_tool(actual_lang)
                matches = tool.check(linea)
                for m in matches:
                    # Usamos getattr para evitar el error de la pantalla roja
                    rule_id = getattr(m, 'ruleId', '')
                    if rule_id not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD']:
                        msg = getattr(m, 'message', 'Error gramatical')
                        errores.append(f"⚠️ ({lang_code.upper()}) {msg}")
            except Exception as e:
                errores.append(f"ℹ️ Nota: No se pudo completar la revisión gramatical en esta línea.")

            # 4. Mostrar Resultados
            if not errores:
                st.success(f"Línea {i} OK: {linea[:50]}...")
            else:
                with st.expander(f"Línea {i}: Revisar ({lang_code.upper()})", expanded=True):
                    st.write(f"**Texto:** {linea}")
                    for err in errores:
                        st.write(err)
            
            progreso.progress(i / len(lineas))
    else:
        st.warning("Pega el texto antes de iniciar.")
