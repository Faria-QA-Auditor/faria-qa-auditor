import streamlit as st
import requests
import re

# 1. CONFIGURACION
st.set_page_config(page_title="English QA Auditor", page_icon="🇺🇸")

# --- CSS SEGURO ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #4a148c;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff4081;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🇺🇸 English Standards Auditor")

# 2. ENTRADA DE TEXTO
texto_input = st.text_area("Paste English standards here (one per line):", height=300)

# 3. LOGICA DE AUDITORIA
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\\n') if l.strip()]
        
        st.subheader("Audit Results")
        
        for i, linea in enumerate(lineas, 1):
            errores = []
            word_count = len(linea.split())
            
            # REGLA: Inicio (Mayuscula o Numero tipo 1. o 2.1.)
            if not re.match(r'^([A-Z]|\d+\.(\d+\.)?)', linea):
                errores.append("Does not start with a capital letter or valid number format (e.g., '1.' or '2.1.').")

            # REGLA: Espacios extra
            if "  " in linea:
                errores.append("Contains extra spaces between words.")

            # REGLA: Palabras cortadas (ej. word- o word_)
            if re.search(r'\\w+[-_]\\s|\\w+[-_]$', linea):
                errores.append("Detected potentially broken word (ending in hyphen or underscore).")

            # REGLA: Ortografia y Puntuacion (API)
            try:
                payload = {'text': linea, 'language': 'en', 'motherTag': 'en-US,en-GB,en-AU'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                for m in res.get('matches', []):
                    errores.append(f"Grammar: {m['message']}")
            except:
                pass

            # MOSTRAR RESULTADOS
            header = f"Line {i} | {word_count} words"
            
            if not errores:
                st.success(f"{header} ✅ Perfect")
            else:
                with st.expander(f"{header} ⚠️ {len(errores)} issues found"):
                    st.write(f"**Text:** {linea}")
                    for err in errores:
                        st.error(f"- {err}")
