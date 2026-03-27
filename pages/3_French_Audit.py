import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="French Standards Auditor", page_icon="🇫🇷", layout="centered")

# --- CSS PERSONALIZADO (Estética Faria) ---
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
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=fr&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

def highlight_errors(text, words):
    # Normalizamos el texto base para asegurar que el replace funcione con tildes
    highlighted = unicodedata.normalize('NFC', text)
    for word in set(words):
        if word and len(word.strip()) > 0:
            norm_word = unicodedata.normalize('NFC', word.strip())
            highlighted = re.sub(f"({re.escape(norm_word)})", r"<span class='highlight'>\1</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>French Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR POR LÍNEA
texto_raw = st.text_area("Paste French standards here:", height=300)

if texto_raw:
    # Contamos líneas reales
    lineas_reales = [l for l in texto_raw.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 1000")
    if total_lines > 1000:
        st.error("⚠️ **Warning:** Document exceeds the 1,000-line limit.")
    st.write("---")

# 4. LÓGICA DE AUDITORÍA
if st.button("🚀 Run French Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text first.")
    else:
        # BLOQUE DE NORMALIZACIÓN (Arregla el error de la imagen 0ec0ff)
        texto_norm = unicodedata.normalize('NFC', texto_raw)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

        for i, linea in enumerate(lineas, 1):
            if linea.lower().strip() == "hide details": continue
            
            # RECUADRO AZUL: Show Details (Se mantiene intacto)
            if "show details" in linea.lower():
                st.info(f"Line {i} ℹ️ **'Show details' detected:** Please verify if there is hidden information in the source database.")

            alertas = []
            to_highlight = []

            # --- REGLA 1: Espacios en signos dobles (Regex propia) ---
            if re.search(r'[^ ]([:;!?])', linea):
                match = re.search(r'[^ ]([:;!?])', linea).group()
                alertas.append(f"⚠️ **Typographical Error:** Missing non-breaking space before double punctuation mark '{match[-1]}'.")
                to_highlight.append(match)

            # --- REGLA 2: Ligaduras (œ) ---
            if re.search(r'\boe\w+', linea.lower()):
                palabras_oe = re.findall(r'\b\w*oe\w*\b', linea.lower())
                for p in palabras_oe:
                    if p not in ["coefficient", "moelle"]:
                        alertas.append(f"❌ **Ligature Error:** Use the special character 'œ' (e.g., 'sœur') instead of 'oe'.")
                        to_highlight.append(p)

            # --- API LANGUAGETOOL CON TRADUCCIÓN DE ALERTAS ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'fr'}).json()
                for m in res.get('matches', []):
                    bad_raw = linea[m['offset']:m['offset']+m['length']]
                    bad = unicodedata.normalize('NFC', bad_raw)
                    
                    if bad.lower() in ["show details", "hide details"]: continue
                    to_highlight.append(bad)
                    
                    # TRADUCCIÓN DE ALERTAS AL INGLÉS (Para equipo no francófono)
                    msg_fr = m['message'].lower()
                    msg_en = "Grammar/Spelling issue" # Default
                    
                    if "espace" in msg_fr or "ponctuation" in msg_fr:
                        msg_en = "Punctuation/Spacing error"
                    elif "accord" in msg_fr:
                        msg_en = "Grammatical agreement error (Gender/Number)"
                    elif "orthographe" in msg_fr:
                        msg_en = "Spelling error"
                    elif "majuscule" in msg_fr:
                        msg_en = "Capitalization error"
                    elif "infinitif" in msg_fr:
                        msg_en = "Verbal mood error (Infinitive required)"
                    
                    sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                    alertas.append(f"❌ **{msg_en}:** Issue in '{bad}'.{sug}")
            except: pass

            # --- RENDERIZADO ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    linea_final = highlight_errors(linea, to_highlight)
                    st.markdown(f"<div>{linea_final}</div>", unsafe_allow_html=True)
                    # Traducción automática para que entiendan el contexto
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not "show details" in linea.lower():
                st.success(f"Line {i} ✅ Perfect")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
