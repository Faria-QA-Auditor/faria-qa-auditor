import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
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

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>English Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste English standards here (one per line):", height=300)

# --- CONTADOR GLOBAL ---
if texto_input:
    total_words = len(texto_input.split())
    st.markdown(f"**Word Count:** {total_words} / 1000")
    if total_words > 1000:
        st.error("⚠️ Warning: Limit exceeded.")
    st.write("---")

# 4. PROCESAMIENTO REFORZADO
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        # Dividimos por líneas y limpiamos
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            if linea.lower() == "hide details":
                continue

            errores = []
            
            # REGLA: Show Details
            if "show details" in linea.lower():
                errores.append("ℹ️ 'Show details' detected: Verify if text is missing.")

            # REGLA: Inicio (Mayúscula o Números 1. / 2.1.)
            if not re.match(r'^([A-Z]|\d+\.(\d+\.)?)', linea):
                errores.append("Error: Does not start with a capital letter or valid number format (1. or 2.1.).")

            # REGLA: Espacios extra
            if "  " in linea:
                errores.append("Error: Contains extra spaces between words.")

            # REGLA: Palabras cortadas (detecta 'KINDERGART' o palabras sin vocales finales comunes)
            # Ahora es más sensible a palabras que terminan abruptamente en consonantes raras
            if re.search(r'\b\w+[-_]\b|\w+[-_]$|(?<!\b[aiouyAIOUY])(?<!the)(?<!and)[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{4,}$', linea):
                errores.append("Possible broken or incomplete word detected.")

            # REGLA: API LanguageTool (Ortografía estricta)
            try:
                # Forzamos la revisión de ortografía en inglés
                payload = {'text': linea, 'language': 'en-US'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                
                for m in res.get('matches', []):
                    # Capturamos 'stndards' y otros typos
                    msg = m['message']
                    sug = f" (Try: {m['replacements'][0]['value']})" if m['replacements'] else ""
                    errores.append(f"Grammar/Spelling: {msg}{sug}")
            except:
                errores.append("Could not connect to spelling service.")

            # MOSTRAR RESULTADOS
            header = f"Line {i}"
            if not errores:
                st.success(f"{header} ✅ Perfect")
            else:
                # Si hay "show details" pero no hay errores reales, usamos azul, sino rojo
                with st.expander(f"{header} ⚠️ Issues found", expanded=True):
                    st.write(f"**Text:** {linea}")
                    for err in errores:
                        if "ℹ️" in err: st.info(err)
                        else: st.error(f"- {err}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
