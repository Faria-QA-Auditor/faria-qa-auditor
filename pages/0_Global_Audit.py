import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Global Standards Auditor", page_icon="🌐", layout="centered")

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
st.markdown("<h2 style='color: #444;'>🌐 Global Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO Y SELECCIÓN DE IDIOMA
idioma_dict = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Portuguese": "pt",
    "Catalan": "ca"
}

idioma_seleccionado = st.selectbox("Select Language:", list(idioma_dict.keys()))
texto_input = st.text_area("Paste standards here (one per line):", height=300)

# --- CONTADOR GLOBAL (SOBRE 1000 PALABRAS) ---
if texto_input:
    total_words = len(texto_input.split())
    color = "green" if total_words <= 1000 else "red"
    st.markdown(f"**Word Count:** <span style='color:{color};'>{total_words}</span> / 1000", unsafe_allow_html=True)
    if total_words > 1000:
        st.error("⚠️ Limit exceeded (1000 words).")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Global Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            # REGLA: Omitir "Hide details"
            if linea.lower() == "hide details":
                continue

            errores = []
            alertas_info = []

            # REGLA: Show Details (Alerta informativa)
            if "show details" in linea.lower():
                alertas_info.append("ℹ️ 'Show details' detected: Please verify if there is hidden text not included in this audit.")

            # REGLA: API LanguageTool con TRADUCCIÓN AL VUELO
            try:
                lang_code = idioma_dict[idioma_seleccionado]
                payload = {'text': linea, 'language': lang_code}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                
                for m in res.get('matches', []):
                    msg_orig = m['message'].lower()
                    
                    # Ignorar errores de espacios para no saturar
                    if "whitespace" in msg_orig or "espacios" in msg_orig or "espaces" in msg_orig:
                        continue
                    
                    # TRADUCCIÓN LÓGICA DE MENSAJES (Inglés, Español, Francés, etc. -> Inglés)
                    if any(word in msg_orig for word in ["ortográfico", "spelling", "faute d'orthographe", "rechtschreib"]):
                        final_msg = "Possible spelling error found."
                    elif any(word in msg_orig for word in ["tild", "acentuación", "accent"]):
                        final_msg = "Accent/Tilde issue detected."
                    elif any(word in msg_orig for word in ["gramatical", "grammar", "grammaire", "grammatik"]):
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
                with st.expander(f"{header} {icon} Issues/Notes found", expanded=True):
                    st.write(f"**Text:** {linea}")
                    for info in alertas_info:
                        st.info(info)
                    for err in errores:
                        st.error(f"- {err}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
