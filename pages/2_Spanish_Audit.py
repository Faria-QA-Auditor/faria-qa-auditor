import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA (Emoji solo en la pestaña)
st.set_page_config(page_title="Spanish Auditor", page_icon="🇪🇸", layout="centered")

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

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Spanish Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste Spanish standards here (one per line):", height=300)

# --- CONTADOR GLOBAL (SOBRE 1000 PALABRAS) ---
if texto_input:
    total_words = len(texto_input.split())
    st.markdown(f"**Word Count:** {total_words} / 1000")
    if total_words > 1000:
        st.error("⚠️ Warning: Limit exceeded.")
    st.write("---")

# 4. PROCESAMIENTO REFORZADO PARA ESPAÑOL
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

            # REGLA: Show Details
            if "show details" in linea.lower():
                alertas_info.append("ℹ️ 'Show details' detected: Verify if text is missing.")

            # REGLA: Inicio (Mayúscula o Números 1. / 2.1.) - Incluye tildes y Ñ
            if not re.match(r'^([A-ZÁÉÍÓÚÑ]|\d+\.(\d+\.)?)', linea):
                errores.append("Error: Does not start with a capital letter or valid number format.")

            # REGLA: Punto Final Obligatorio
            if not linea.endswith('.'):
                errores.append("Error: The line does not end with a full stop (period).")

            # REGLA: Espacios extra
            if "  " in linea:
                errores.append("Error: Contains extra spaces between words.")

            # REGLA: Palabras cortadas
            if re.search(r'\b\w+[-_]\b|\b\w+[-_]\s|\w+[-_]$', linea):
                errores.append("Possible broken or incomplete word detected.")

            # REGLA: API LanguageTool con TRADUCCIÓN AL INGLÉS
            try:
                payload = {'text': linea, 'language': 'es'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                
                for m in res.get('matches', []):
                    msg_orig = m['message'].lower()
                    
                    # Ignorar espacios (ya tenemos regla local)
                    if any(word in msg_orig for word in ["espacios", "whitespace"]):
                        continue
                    
                    # Traducción lógica para el equipo global
                    if any(word in msg_orig for word in ["ortográfico", "spelling"]):
                        final_msg = "Possible spelling error found."
                    elif any(word in msg_orig for word in ["tild", "acentuación", "accent"]):
                        final_msg = "Accent/Tilde issue detected."
                    elif "gramatical" in msg_orig:
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
