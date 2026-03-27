import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="US English Standards Auditor", page_icon="🇺🇸", layout="centered")

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
    /* Estilo para el título con bandera */
    .title-text {
        color: #444;
        font-size: 2.5rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER CON LOGO Y BANDERA (Se removió "us")
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
# Título actualizado con bandera emoji
st.markdown("<h2 class='title-text'>🇺🇸 US English Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
# ... (el resto del código permanece igual que en la versión anterior) ...
texto_input = st.text_area("Paste English standards here (one per line):", height=300)

# --- CONTADOR GLOBAL (ESTILO GLOBAL AUDITOR) ---
if texto_input:
    total_words = len(texto_input.split())
    color = "green" if total_words <= 1000 else "red"
    st.markdown(f"**Word Count:** <span style='color:{color};'>{total_words}</span> / 1000", unsafe_allow_html=True)
    if total_words > 1000:
        st.error("⚠️ Warning: You have exceeded the 1000 word limit. Results might be incomplete.")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        # Dividir por líneas reales
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            errores = []
            
            # --- REGLA: Inicio (Mayúscula o Formato Numero: 1. o 2.1.) ---
            if not re.match(r'^([A-Z]|\d+\.(\d+\.)?)', linea):
                errores.append("Does not start with a capital letter or valid number format (e.g., '1.' or '2.1.').")

            # --- REGLA: Espacios extra ---
            if "  " in linea:
                linea_limpia = re.sub(r' {2,}', ' ', linea)
                errores.append(f"Contains extra spaces. Suggestion: '{linea_limpia}'")

            # --- REGLA: Palabras cortadas o terminadas irregularmente ---
            # Detecta palabras que terminan en guion, guion bajo o símbolos pegados
            if re.search(r'\b\w+[-_]\b|\b\w+[-_]\s|\w+[-_]$', linea):
                errores.append("Detected potentially broken word (ending in '-' or '_').")

            # --- REGLA: API LanguageTool (Ortografía y Puntuación multi-dialecto) ---
            try:
                payload = {
                    'text': linea, 
                    'language': 'en',
                    'motherTag': 'en-US,en-GB,en-AU'
                }
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                for m in res.get('matches', []):
                    # Ignoramos alertas de espacios de la API para no duplicar nuestra regla local
                    if "whitespace" not in m['message'].lower():
                        sug = f" (Try: {m['replacements'][0]['value']})" if m['replacements'] else ""
                        errores.append(f"Grammar/Spelling: {m['message']}{sug}")
            except:
                pass

            # --- MOSTRAR RESULTADOS ---
            header = f"Line {i}"
            if not errores:
                st.success(f"{header} ✅ Perfect")
            else:
                with st.expander(f"{header} ⚠️ {len(errores)} issues found", expanded=True):
                    st.write(f"**Text:** {linea}")
                    for err in errores:
                        st.error(f"- {err}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
