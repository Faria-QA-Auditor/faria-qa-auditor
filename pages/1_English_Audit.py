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

# 2. HEADER CON LOGO
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>🇺🇸 English Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste English standards here:", height=300)

# --- CONTADOR GLOBAL (ESTILO GLOBAL AUDITOR) ---
if texto_input:
    total_words = len(texto_input.split())
    color = "green" if total_words <= 1000 else "red"
    st.markdown(f"**Word Count:** <span style='color:{color};'>{total_words}</span> / 1000", unsafe_allow_html=True)
    if total_words > 1000:
        st.error("⚠️ Limit exceeded (1000 words). Please reduce the text for a complete audit.")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            # Omitir líneas que sean exactamente "Hide details"
            if linea.lower() == "hide details":
                continue

            errores = []
            alertas_info = []

            # --- REGLA: Show Details (Información oculta) ---
            if "show details" in linea.lower():
                alertas_info.append("ℹ️ 'Show details' detected: Please verify if there is hidden text not included in this audit.")

            # --- REGLA: Inicio (Mayúscula o Formato Numero: 1. o 2.1.) ---
            if not re.match(r'^([A-Z]|\d+\.(\d+\.)?)', linea):
                errores.append("Does not start with a capital letter or valid number format (e.g., '1.' or '2.1.').")

            # --- REGLA: Espacios extra ---
            if "  " in linea:
                errores.append("Contains extra spaces between words.")

            # --- REGLA: Palabras cortadas ---
            if re.search(r'\b\w+[-_]\b|\b\w+[-_]\s|\w+[-_]$', linea):
                errores.append("Detected potentially broken word (ending in '-' or '_').")

            # --- REGLA: API LanguageTool (Ortografía y Puntuación multi-dialecto) ---
            try:
                payload = {'text': linea, 'language': 'en', 'motherTag': 'en-US,en-GB,en-AU'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                for m in res.get('matches', []):
                    # Ignorar errores de espacios de la API para usar nuestra regla local
                    if "whitespace" not in m['message'].lower():
                        sug = f" (Try: {m['replacements'][0]['value']})" if m['replacements'] else ""
                        errores.append(f"Grammar/Spelling: {m['message']}{sug}")
            except:
                pass

            # --- MOSTRAR RESULTADOS ---
            header = f"Line {i}"
            if not errores and not alertas_info:
                st.success(f"{header} ✅ Perfect")
            else:
                icon = "⚠️" if errores else "ℹ️"
                with st.expander(f"{header} {icon} Issues/Notes found", expanded=True):
                    st.write(f"**Text:** {linea}")
                    for info in alertas_info:
                        st.info(info)
                    for err in errores:
                        st.error(f"- {err}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
