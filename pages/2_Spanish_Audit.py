import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Spanish Standards Auditor", page_icon="🇪🇸", layout="centered")

# --- CSS PERSONALIZADO (Mantiene estética Faria) ---
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
    .translation-box {
        background-color: #f0f2f6;
        border-left: 5px solid #4a148c;
        padding: 10px;
        margin: 10px 0;
        font-style: italic;
    }
    .highlight {
        background-color: #fff3cd;
        font-weight: bold;
        color: #d9534f;
        text-decoration: underline;
        padding: 0 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def translate_to_english(text):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=es&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

def highlight_errors(text, words):
    highlighted = text
    for word in set(words):
        if word and len(word.strip()) > 0:
            highlighted = re.sub(f"({re.escape(word)})", r"<span class='highlight'>\1</span>", highlighted)
    return highlighted

# 2. HEADER (Logo e Identidad)
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Spanish Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR DE LÍNEAS
texto_input = st.text_area("Paste Spanish standards here:", height=300)

if texto_input:
    # Contamos líneas reales (párrafos/líneas escritas)
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 1000")
    if total_lines > 1000:
        st.error("⚠️ **Warning:** Document exceeds the 1,000-line limit. Please audit in smaller batches.")
    st.write("---")

# 4. LÓGICA DE AUDITORÍA
if st.button("🚀 Run Spanish Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text.")
    else:
        # NORMALIZACIÓN NFC (Arregla el conflicto de tildes/encoding)
        texto_norm = unicodedata.normalize('NFC', texto_input)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

        for i, linea in enumerate(lineas, 1):
            if linea.lower().strip() == "hide details": continue
            
            # RECUADRO AZUL: Show Details
            if "show details" in linea.lower():
                st.info(f"Line {i} ℹ️ **'Show details' detected:** Please verify if there is hidden information in the source database that needs to be expanded.")

            alertas = []
            to_highlight = []

            # --- REGLA 1: Estilo y Voz Pasiva ---
            if re.search(r'\b(es|son|fue|fueron)\b\s+\w+(ado|ido|ada|ida)\b', linea, re.I):
                alertas.append("⚠️ **Style Suggestion:** Passive voice detected ('is/are realized'). Consider using 'pasiva refleja' (e.g., 'se realiza') for better flow.")

            # --- REGLA 2: Cifras y Símbolos (Espacio en % y °C) ---
            if re.search(r'\d+%', linea):
                alertas.append("❌ **Punctuation Error:** Missing space between number and percentage (e.g., '10 %').")
                to_highlight.append(re.search(r'\d+%', linea).group())
            if re.search(r'\d+°C', linea):
                alertas.append("❌ **Punctuation Error:** Missing space between number and Celsius symbol (e.g., '18 °C').")
                to_highlight.append(re.search(r'\d+°C', linea).group())

            # --- REGLA 3: Prefijos unidos ---
            prefijos_error = re.findall(r'\b(pre|ex|sub|post|vice)\b\s+', linea, re.I)
            if prefijos_error:
                alertas.append("❌ **Grammar Error:** Prefixes should be joined to the base word (e.g., 'preescolar', not 'pre escolar').")

            # --- REGLA 4: Mayúsculas tildadas (Check básico) ---
            if re.search(r'\b[A-ZÁÉÍÓÚÑ]{2,}\b', linea):
                if "ACION " in linea or "UCACION " in linea: # Ejemplo común
                     alertas.append("⚠️ **Orthography:** Ensure all-caps words maintain their accents (e.g., EDUCACIÓN).")

            # --- API LANGUAGETOOL (Ortografía y Gramática RAE) ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'es'}).json()
                for m in res.get('matches', []):
                    bad = linea[m['offset']:m['offset']+m['length']]
                    if bad.lower() in ["show details", "hide details"]: continue
                    
                    to_highlight.append(bad)
                    # Traducción de mensajes de la API al vuelo
                    msg = m['message']
                    if "ortografía" in msg.lower(): msg = "Possible spelling error"
                    if "gramática" in msg.lower(): msg = "Grammatical issue"
                    
                    sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                    alertas.append(f"❌ **{msg}:** Issue in '{bad}'.{sug}")
            except: pass

            # --- RENDERIZADO FINAL ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not "show details" in linea.lower():
                st.success(f"Line {i} ✅ Perfect")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
