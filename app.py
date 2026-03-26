import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory

# Para que los resultados sean consistentes
DetectorFactory.seed = 0

# Configuración de página
st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🌍")

# Diccionario de motores para ahorrar memoria
@st.cache_resource
def get_tool(lang_code):
    try:
        return language_tool_python.LanguageTool(lang_code)
    except:
        return language_tool_python.LanguageTool('en-US') # Fallback a inglés si falla

st.title("🌍 Faria Universal Standards Auditor")
st.write("Revisión automática de formato y ortografía en cualquier idioma.")

texto_input = st.text_area("Pega tus estándares aquí (En/Es/Ca/Fr/De...):", height=300)

if st.button("🚀 Iniciar Auditoría Maestra"):
    if texto_input:
        lineas = texto_input.strip().split('\n')
        progreso = st.progress(0)
        
        for i, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if not linea: continue
            
            # 1. DETECCIÓN AUTOMÁTICA DE IDIOMA
            try:
                codigo_iso = detect(linea) # Detecta 'es', 'en', 'ca', etc.
                # Ajuste para catalán/valenciano que usa LanguageTool
                if codigo_iso == 'ca': motor_lang = 'ca-ES'
                elif codigo_iso == 'es': motor_lang = 'es'
                else: motor_lang = 'en-US'
            except:
                motor_lang = 'en-US'

            tool = get_tool(motor_lang)
            errores = []
            
            # 2. REGLAS DE FORMATO FARIA (Universales)
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                errores.append("❌ Error de inicio: Debe empezar con Mayúscula o Número.")
            if not linea.endswith('.'): 
                errores.append("❌ Falta punto final.")
            if "  " in linea:
                errores.append("⚠️ Espacios dobles detectados.")

            # 3. REVISIÓN LINGÜÍSTICA
            matches = tool.check(linea)
            for m in matches:
                rid = getattr(m, 'ruleId', '')
                # Ignorar errores de mayúscula inicial (ya los validamos arriba)
                if rid not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD']:
                    errores.append(f"⚠️ ({codigo_iso.upper()}) {m.message} -> '{linea[m.offset:m.offset+m.errorLength]}'")

            # 4. MOSTRAR RESULTADOS
            if not errores:
                st.success(f"Línea {i} [OK - {codigo_iso.upper()}]: {linea[:50]}...")
            else:
                with st.expander(f"Línea {i}: Errores encontrados ({codigo_iso.upper()})", expanded=True):
                    st.write(f"**Texto:** {linea}")
                    for e in errores:
                        st.write(e)
            
            progreso.progress(i / len(lineas))
            
    else:
        st.warning("El cuadro está vacío.")
