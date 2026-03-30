import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Spanish Standards Auditor", page_icon="🇪🇸", layout="centered")

# --- CSS PERSONALIZADO (Incluye Barra de Progreso Morada) ---
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
    /* Barra de Progreso Morada */
    .stProgress > div > div > div > div {
        background-color: #4a148c;
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

# 3. INPUT Y CONTADOR DE LÍNEAS (Actualizado a 2500)
texto_input = st.text_area("Paste Spanish standards here:", height=300, placeholder="")

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit. Please audit in smaller batches.")
    st.write("---")

# 4. LÓGICA DE AUDITORÍA
if st.button("🚀 Run Spanish Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text.")
    else:
        texto_norm = unicodedata.normalize('NFC', texto_input)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

        # --- BARRA DE PROGRESO ---
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, linea in enumerate(lineas, 1):
            # Actualización visual del progreso
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")

            if linea.lower().strip() == "hide details": continue
            
            if "show details" in linea.lower():
                st.info(f"Line {i} ℹ️ **'Show details' detected:** Please verify if there is hidden information in the source database.")

            alertas = []
            to_highlight = []

            # --- REGLA 1: Estilo y Voz Pasiva ---
            if re.search(r'\b(es|son|fue|fueron)\b\s+\w+(ado|ido|ada|ida)\b', linea, re.I):
                alertas.append("⚠️ **Style Suggestion:** Passive voice detected. Consider using 'pasiva refleja' (e.g., 'se realiza').")

            # --- REGLA 2: Cifras y Símbolos ---
            if re.search(r'\d+%', linea):
                alertas.append("❌ **Punctuation Error:** Missing space before % (e.g., '10 %').")
                to_highlight.append(re.search(r'\d+%', linea).group())
            if re.search(r'\d+°C', linea):
                alertas.append("❌ **Punctuation Error:** Missing space before °C (e.g., '18 °C').")
                to_highlight.append(re.search(r'\d+°C', linea).group())

            # --- REGLA 3: Prefijos ---
            prefijos_error = re.findall(r'\b(pre|ex|sub|post|vice)\b\s+', linea, re.I)
            if prefijos_error:
                alertas.append("❌ **Grammar Error:** Prefixes should be joined (e.g., 'preescolar').")

            # --- REGLA 4: Mayúsculas tildadas ---
            if re.search(r'\b[A-ZÁÉÍÓÚÑ]{2,}\b', linea):
                if "ACION " in linea or "UCACION " in linea:
                     alertas.append("⚠️ **Orthography:** Ensure all-caps words maintain accents (EDUCACIÓN).")

            # --- API LANGUAGETOOL ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'es'}).json()
                for m in res.get('matches', []):
                    bad = linea[m['offset']:m['offset']+m['length']]
                    if bad.lower() in ["show", "details", "hide"]: continue
                    
                    to_highlight.append(bad)
                    msg = m['message']
                    if "ortografía" in msg.lower(): msg = "Possible spelling error"
                    if "gramática" in msg.lower(): msg = "Grammatical issue"
                    
                    sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                    alertas.append(f"❌ **{msg}:** Issue in '{bad}'.{sug}")
            except: pass

            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not "show details" in linea.lower():
                st.success(f"Line {i} ✅ Perfect")
        
        status_text.text("Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
