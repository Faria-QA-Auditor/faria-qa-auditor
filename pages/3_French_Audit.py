import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="French Standards Auditor", page_icon="🇫🇷", layout="centered")

# --- CSS PERSONALIZADO ---
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
    highlighted = text
    for word in set(words):
        if word and len(word.strip()) > 0:
            highlighted = re.sub(f"({re.escape(word)})", r"<span class='highlight'>\1</span>", highlighted)
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
texto_input = st.text_area("Paste French standards here:", height=300)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 1000")
    if total_lines > 1000:
        st.error("⚠️ **Warning:** Document exceeds the 1,000-line limit.")
    st.write("---")

# 4. LÓGICA DE AUDITORÍA
if st.button("🚀 Run French Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        # Normalización NFC (Vital para acentos franceses y ligaduras)
        texto_norm = unicodedata.normalize('NFC', texto_input)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

        for i, linea in enumerate(lineas, 1):
            if linea.lower().strip() == "hide details": continue
            
            # RECUADRO AZUL: Show Details
            if "show details" in linea.lower():
                st.info(f"Line {i} ℹ️ **'Show details' detected:** Please verify if there is hidden information in the source database.")

            alertas = []
            to_highlight = []

            # --- REGLA 1: Tipografía Francesa (Espacios en signos dobles) ---
            # Detecta falta de espacio antes de : ; ! ?
            if re.search(r'[^ ]([:;!?])', linea):
                match = re.search(r'[^ ]([:;!?])', linea).group()
                alertas.append(f"⚠️ **Typographical Error:** Missing space before double punctuation mark '{match[-1]}'.")
                to_highlight.append(match)

            # --- REGLA 2: Ligaduras (oe -> œ) ---
            if re.search(r'\boe\w+', linea.lower()):
                palabras_oe = re.findall(r'\b\w*oe\w*\b', linea.lower())
                # Excluir palabras legítimas como 'coefficient'
                for p in palabras_oe:
                    if p not in ["coefficient", "moelle"]:
                        alertas.append(f"❌ **Ligature Error:** Use the special character 'œ' for words like 'sœur' or 'œuvre' instead of 'oe'.")
                        to_highlight.append(p)

            # --- REGLA 3: Mayúsculas Acentuadas ---
            if re.search(r'\b[A-Z]{2,}\b', linea):
                if any(word in linea for word in ["ETUDE", "ECOLE", "ETAT"]):
                    alertas.append("⚠️ **Orthography:** Uppercase letters must maintain accents in French (e.g., ÉTUDE).")

            # --- REGLA 4: Anglicismos Prohibidos ---
            anglicisms = {"feedback": "rétroaction", "email": "courriel", "newsletter": "infolettre"}
            for eng, fr in anglicisms.items():
                if re.search(rf'\b{eng}\b', linea.lower()):
                    alertas.append(f"⚠️ **Forbidden Anglicism:** Avoid '{eng}'. Use the French term **'{fr}'**.")
                    to_highlight.append(eng)

            # --- API LANGUAGETOOL (Francés) ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'fr'}).json()
                for m in res.get('matches', []):
                    bad = linea[m['offset']:m['offset']+m['length']]
                    if bad.lower() in ["show details", "hide details"]: continue
                    to_highlight.append(bad)
                    
                    # Traducción de mensajes de error comunes
                    msg = m['message']
                    if "orthographe" in msg.lower(): msg = "Spelling error"
                    if "accord" in msg.lower(): msg = "Agreement/Grammar issue"
                    if "infinitif" in msg.lower(): msg = "Verbal inconsistency (Check Infinitive vs Imperative)"
                    
                    sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                    alertas.append(f"❌ **{msg}:** Issue in '{bad}'.{sug}")
            except: pass

            # --- RENDERIZADO ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    # Traducción automática al vuelo para contexto
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not "show details" in linea.lower():
                st.success(f"Line {i} ✅ Perfect")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
