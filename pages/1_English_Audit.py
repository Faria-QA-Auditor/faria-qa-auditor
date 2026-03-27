import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA (Emoji solo en la pestaña del navegador)
st.set_page_config(page_title="English Auditor", page_icon="🇺🇸", layout="centered")

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

# 2. HEADER - SOLO LOGO Y TÍTULO LIMPIO (Removido "US" y emoji del título)
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")

# Título simplificado y limpio
st.markdown("<h2 style='color: #444;'>English Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste English standards here (one per line):", height=300)

# --- CONTADOR GLOBAL (SOBRE 1000 PALABRAS) ---
if texto_input:
    total_words = len(texto_input.split())
    color = "green" if total_words <= 1000 else "red"
    st.markdown(f"**Word Count:** <span style='color:{color};'>{total_words}</span> / 1000", unsafe_allow_html=True)
    if total_words > 1000:
        st.error("⚠️ Warning: You have exceeded the 1000 word limit.")
    st.write("---")

# 4. PROCESAMIENTO (Mismas reglas de ayer intactas)
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            if linea.lower() == "hide details":
                continue

            errores = []
            alertas_info = []

            if "show details" in linea.lower():
                alertas_info.append("ℹ️ 'Show details' detected: Please verify if there is hidden text.")

            # REGLAS DE ORO (Inalteradas)
            # Regla de inicio (Mayúscula, 1., 2.1.)
            if not re.match(r'^([A-Z]|\d+\.(\d+\.)?)', linea):
                errores.append("Does not start with a capital letter or valid number format (e.g., '1.' or '2.1.').")

            # Espacios extra
            if "  " in linea:
                errores.append("Contains extra spaces between words.")

            # Palabras cortadas
            if re.search(r'\b\w+[-_]\b|\b\w+[-_]\s|\w+[-_]$', linea):
                errores.append("Detected potentially broken word (ending in '-' or '_').")

            # Ortografía y Puntuación multi-dialecto
            try:
                payload = {'text': linea, 'language': 'en', 'motherTag': 'en-US,en-GB,en-AU'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                for m in res.get('matches', []):
                    if "whitespace" not in m['message'].lower():
                        sug = f" (Try: {m['replacements'][0]['value']})" if m['replacements'] else ""
                        errores.append(f"Grammar/Spelling: {m['message']}{sug}")
            except:
                pass

            # MOSTRAR RESULTADOS
            header = f"Line {i}"
            if not errores and not alertas_info:
                st.success(f"{header} ✅ Perfect")
            else:
                icon = "⚠️" if errores else "ℹ️"
                with st.expander(f"{header} {icon} Issues found", expanded=True):
                    st.write(f"**Text:** {linea}")
                    for info in alertas_info: st.info(info)
                    for err in errores: st.error(f"- {err}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
