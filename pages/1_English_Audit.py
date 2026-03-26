import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="English QA Auditor", page_icon="🇺🇸", layout="centered")

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
    .stButton>button:hover {
        background-color: #ff4081;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🇺🇸 English Standards Auditor")
st.markdown("---")

# 2. ENTRADA DE TEXTO
texto_input = st.text_area("Paste English standards here (one per line):", height=300)

# 3. PROCESAMIENTO
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        # Dividir por líneas reales
        lineas_puras = texto_input.split('\n')
        lineas = [l.strip() for l in lineas_puras if l.strip()]
        
        st.subheader("Audit Results")
        st.write(f"Analyzed {len(lineas)} standards.")

        for i, linea in enumerate(lineas, 1):
            errores = []
            
            # --- CONTADOR DE PALABRAS ---
            word_count = len(linea.split())
            
            # --- REGLA: Inicio (Mayúscula o Formato Numero) ---
            # Acepta: "Text", "1.", "2.1."
            if not re.match(r'^([A-Z]|\d+\.(\d+\.)?)', linea):
                errores.append("Does not start with a capital letter or valid number format (e.g., '1.' or '2.1.').")

            # --- REGLA: Espacios extra ---
            if "  " in linea:
                linea_limpia = re.sub(r' {2,}', ' ', linea)
                errores.append(f"Contains extra spaces. Suggestion: '{linea_limpia}'")

            # --- REGLA: Palabras cortadas ---
            if re.search(r'\b\w+[-_]\b|\b\w+[-_]\s', linea):
                errores.append("Detected potentially broken word (ending in '-' or '_').")

            # --- REGLA: API LanguageTool (Ortografía y Puntuación) ---
            try:
                payload = {
                    'text': linea, 
                    'language': 'en',
                    'motherTag': 'en-US,en-GB,en-AU'
                }
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                for m in res.get('matches', []):
                    # Solo agregar si no es un error de espacios que ya detectamos arriba
                    if "whitespace" not in m['message'].lower():
                        sug = f" (Try: {m['replacements'][0]['value']})" if m['replacements'] else ""
                        errores.append(f"Grammar/Spelling: {m['message']}{sug}")
            except:
                pass

            # --- MOSTRAR RESULTADOS POR LÍNEA ---
            header = f"Line {i} | {word_count} words"
            
            if not errores:
                st.success(f"{header} ✅ Perfect")
            else:
                with st.expander(f"{header} ⚠️ {len(errores)} issues found", expanded=True):
                    st.write(f"**Text:** {linea}")
                    for err in errores:
                        st.error(f"- {err}")
