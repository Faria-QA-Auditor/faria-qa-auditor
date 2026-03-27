import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA (Emoji solo en la pestaña del navegador)
st.set_page_config(page_title="French Auditor", page_icon="🇫🇷", layout="centered")

# --- CSS PROFESIONAL (Estilo Faria) ---
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

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>French Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste French standards here (one per line):", height=300)

# --- CONTADOR GLOBAL (SOBRE 1000 PALABRAS) ---
if texto_input:
    total_words = len(texto_input.split())
    st.markdown(f"**Word Count:** {total_words} / 1000")
    if total_words > 1000:
        st.error("⚠️ Warning: Limit exceeded (1000 words max).")
    st.write("---")

# 4. PROCESAMIENTO REFORZADO PARA FRANCÉS
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            # Omitir "Hide details"
            if linea.lower() == "hide details":
                continue

            errores = []
            alertas_info = []

            # REGLA: Show Details
            if "show details" in linea.lower():
                alertas_info.append("ℹ️ 'Show details' detected: Please verify if there is hidden text not included in this audit.")

            # REGLA: Inicio (Mayúscula, números 1. / 2.1. e incluye caracteres franceses À, È, Ç, etc.)
            if not re.match(r'^([A-ZÀ-Ÿ]|\d+\.(\d+\.)?)', linea):
                errores.append("Error: Does not start with a capital letter or valid number format.")

            # REGLA: Espacios extra
            if "  " in linea:
                errores.append("Error: Contains extra spaces between words.")

            # REGLA: Palabras cortadas o irregulares
            if re.search(r'\b\w+[-_]\b|\b\w+[-_]\s|\w+[-_]$', linea):
                errores.append("Possible broken or incomplete word detected.")

            # REGLA: API LanguageTool (Francés Global + Traducción de alertas al Inglés)
            try:
                # 'fr' cubre variantes de Francia, Canadá y África
                payload = {'text': linea, 'language': 'fr'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                
                for m in res.get('matches', []):
                    msg_orig = m['message'].lower()
                    
                    # Ignorar espacios (regla local propia)
                    if any(word in msg_orig for word in ["espace", "whitespace"]):
                        continue
                    
                    # TRADUCCIÓN "AL VUELO" A INGLÉS
                    if any(word in msg_orig for word in ["orthographe", "spelling"]):
                        final_msg = "Possible spelling error found."
                    elif any(word in msg_orig for word in ["accent", "tilde"]):
                        final_msg = "Accent issue detected (Check acute, grave, circumflex, etc.)."
                    elif any(word in msg_orig for word in ["grammaire", "grammatical"]):
                        final_msg = "Grammatical issue found."
                    else:
                        final_msg = "Potential grammar/style issue."

                    sug = f" (Try: {m['replacements'][0]['value']})" if m['replacements'] else ""
                    errores.append(f"Grammar/Spelling: {final_msg}{sug}")
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
