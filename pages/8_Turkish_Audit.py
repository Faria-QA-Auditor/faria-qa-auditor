import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Turkish Auditor", page_icon="🇹🇷", layout="centered")

# --- CSS CON HIGHLIGHTING ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #4a148c; color: white; font-weight: bold; }
    .translation-box { background-color: #f0f2f6; border-left: 5px solid #4a148c; padding: 10px; margin: 10px 0; font-style: italic; }
    .highlight { background-color: #fff3cd; font-weight: bold; color: #d9534f; text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

def translate_to_english(text):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={requests.utils.quote(text)}"
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
try: st.image("logo.jpg", width=250)
except: st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Turkish Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT
texto_input = st.text_area("Paste Turkish standards here:", height=300)

if st.button("🚀 Run Deep Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        for i, linea in enumerate(lineas, 1):
            # Ignorar por completo si es solo "Hide details"
            if linea.lower().strip() == "hide details":
                continue
            
            # --- NOTA AZUL PRIORITARIA PARA SHOW DETAILS ---
            if "show details" in linea.lower():
                st.info(f"Line {i} ℹ️ **'Show details' detected:** Please verify if there is hidden information in the source database that needs to be expanded.")

            alertas = []
            to_highlight = []

            # --- REGLA: Inicio de línea ---
            if re.match(r'^\.', linea):
                alertas.append("❌ **Error [Format]:** Line starts with a dot. Please remove it.")
                to_highlight.append(".")

            # --- REGLA: Latinización y Errores Comunes ---
            common_errors = {
                "Ulkelere": "Ülkelere",
                "sabir": "sabır",
                "uygulalarından": "uygulamalarından",
                "Adabımuaşerei": "Adabımuaşereti"
            }
            for err, fix in common_errors.items():
                if err in linea:
                    alertas.append(f"❌ **Error [Orthography]:** Found '{err}'. Did you mean '{fix}'?")
                    to_highlight.append(err)

            # --- API LANGUAGETOOL ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'tr'}).json()
                for m in res.get('matches', []):
                    bad = linea[m['offset']:m['offset']+m['length']]
                    if bad.lower() in ["show details", "hide details"]: continue
                    to_highlight.append(bad)
                    sug = f" (Try: **{m['replacements'][0]['value']}** → *'{translate_to_english(m['replacements'][0]['value'])}'*)" if m['replacements'] else ""
                    alertas.append(f"Grammar/Spelling: Issue in '{bad}' ('{translate_to_english(bad)}').{sug}")
            except: pass

            # --- RENDER ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not "show details" in linea.lower():
                st.success(f"Line {i} ✅ Perfect")

st.caption("Standards and Services Team | Faria Education Group")
