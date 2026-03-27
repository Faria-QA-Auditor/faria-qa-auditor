import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="English Standards Auditor", page_icon="🇺🇸", layout="centered")

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
    .highlight {
        background-color: #fff3cd;
        font-weight: bold;
        color: #d9534f;
        text-decoration: underline;
        padding: 0 2px;
    }
    .complexity-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE RESALTADO ---
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
st.markdown("<h2 style='color: #444;'>English Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. DIALECT SWITCH (Simplificado a US/UK)
dialect = st.radio("Select Regional Standard:", ["US (American English)", "UK (British English)"], horizontal=True)
st.info(f"Targeting: **{dialect}** rules and spelling conventions.")

# 4. INPUT Y CONTADOR POR LÍNEA
texto_input = st.text_area("Paste English standards here (one per line):", height=300)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 1000")
    if total_lines > 1000:
        st.error("⚠️ **Warning:** Document exceeds the 1,000-line limit.")
    st.write("---")

# 5. PROCESAMIENTO
if st.button("🚀 Run English Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        # Normalización NFC para evitar errores de tildes/caracteres especiales
        texto_norm = unicodedata.normalize('NFC', texto_input)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]
        
        p_errors = 0 # Contador para Triage de Paralelismo
        
        for i, linea in enumerate(lineas, 1):
            if linea.lower().strip() == "hide details": continue
            
            # RECUADRO AZUL: Show Details
            if "show details" in linea.lower():
                st.info(f"Line {i} ℹ️ **'Show details' detected:** Please verify if there is hidden information in the source database.")

            alertas = []
            to_highlight = []

            # --- REGLA 1: Dialecto (Spelling) ---
            if "US" in dialect:
                if re.search(r'\b\w+ise\b', linea): 
                    alertas.append("⚠️ **Dialect:** Detected '-ise' (UK). Use '-ize' for US (e.g., 'organize').")
                if re.search(r'\b\w+our\b', linea):
                    alertas.append("⚠️ **Dialect:** Detected '-our' (UK). Use '-or' for US (e.g., 'behavior').")
            else: # UK
                if re.search(r'\b\w+ize\b', linea):
                    alertas.append("⚠️ **Dialect:** Detected '-ize' (US). Preferred '-ise' for UK standards.")

            # --- REGLA 2: Paralelismo y Tono Académico ---
            words = linea.split()
            if words and words[0].lower().endswith('ing'):
                p_errors += 1
                alertas.append("❌ **Parallelism Failure:** Line starts with a Gerund (-ing). Check consistency.")
            
            forbidden = {"get": "acquire", "thing": "element", "stuff": "material", "a lot": "significantly"}
            for word, sug in forbidden.items():
                if re.search(rf'\b{word}\b', linea.lower()):
                    alertas.append(f"⚠️ **Academic Tone:** Avoid '{word}'. Use **{sug}** instead.")
                    to_highlight.append(word)

            # --- API LANGUAGETOOL (US o UK) ---
            lang_code = "en-US" if "US" in dialect else "en-GB"
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': lang_code}).json()
                for m in res.get('matches', []):
                    bad = linea[m['offset']:m['offset']+m['length']]
                    if bad.lower() in ["show details", "hide details"]: continue
                    to_highlight.append(bad)
                    alertas.append(f"❌ **{m['rule']['category']['name']}:** {m['message']}")
            except: pass

            # --- RENDERIZADO ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not "show details" in linea.lower():
                st.success(f"Line {i} ✅ Perfect")

        # ZENDESK-STYLE TRIAGE
        if p_errors > 3:
            st.markdown("---")
            st.markdown("<div class='complexity-badge'>🚩 High Complexity Review: Multiple parallelism issues detected.</div>", unsafe_allow_html=True)

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
