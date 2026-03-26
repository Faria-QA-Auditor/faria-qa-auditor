import streamlit as st
import language_tool_python
import re

# Inicializar motor (se hace una sola vez)
@st.cache_resource
def get_tool():
    return language_tool_python.LanguageTool('en-US')

tool = get_tool()

st.title("🛡️ Faria Standards QA Auditor")
st.write("Pega tus estándares aquí para una auditoría instantánea.")

# Área de texto para pegar los estándares
texto_input = st.text_area("Estándares (1 por línea):", height=300)

if st.button("Ejecutar Auditoría"):
    if texto_input:
        lineas = texto_input.strip().split('\n')
        for i, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if not linea: continue
            
            errores = []
            # Regla de inicio
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                errores.append("❌ Error de inicio: Debe empezar con Mayúscula o Número.")
            
            # Regla de punto final
            if not linea.endswith('.'): 
                errores.append("❌ Falta punto final")
            
            # Regla de ortografía (Ignorando mayúsculas iniciales que ya validamos)
            matches = tool.check(linea)
            for m in matches:
                rule_id = getattr(m, 'ruleId', '')
                if rule_id != 'UPPERCASE_SENTENCE_START':
                    errores.append(f"⚠️ {m.message} (Sugerencia: {m.replacements})")

            if not errores:
                st.success(f"Línea {i}: OK - {linea[:50]}...")
            else:
                st.error(f"Línea {i}: {linea}")
                for e in errores: 
                    st.write(e)
                st.divider()
    else:
        st.warning("Por favor, pega algo primero.")
