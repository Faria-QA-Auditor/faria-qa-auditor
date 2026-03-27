import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN
st.set_page_config(page_title="French Standards Auditor", page_icon="🇫🇷", layout="centered")

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #4a148c; color: white; font-weight: bold; border: none; }
    .translation-box { background-color: #f0f2f6; border-left: 5px solid #4a148c; padding: 10px; margin: 10px 0; font-style: italic; }
    .highlight { background-color: #fff3cd; font-weight: bold; color: #d9534f; text-decoration: underline; padding: 0 2px; }
    </style>
    """, unsafe_allow_html=True)

def translate_to_english(text):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=fr&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

def highlight_errors(text, words):
    # Normalizamos el texto base
    highlighted = unicodedata.normalize('NFC', text)
    # Ordenamos por longitud (palabras más largas primero) para no romper el HTML
    for word in sorted(set(words), key=len, reverse=True):
        if len(word.strip()) <= 1: continue # IGNORAR LETRAS SUELTAS PARA EVITAR EL ERROR DE LA IMAGEN
        norm_word = unicodedata.normalize('NFC', word.strip())
        # Usamos word boundaries (\b) para que solo resalte palabras completas
        highlighted = re.sub(rf"\b({re.escape(norm_word)})\b", r"<span class='highlight'>\1</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: st.image("logo.jpg", width=250)
except: st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>French Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT
texto_raw = st.text_area("Paste French standards here:", height=300)

if texto_raw:
    lineas_reales = [l for l in texto_raw.split('\n') if l.strip()]
    st.markdown(f"**Line Count:** {len(lineas_reales)} / 1000")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run French Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text.")
    else:
        texto_norm = unicodedata.normalize('NFC', texto_raw)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

        for i, linea in enumerate(lineas, 1):
            linea_lower = linea.lower().strip()
            
            if "hide details" in linea_lower: continue

            if "show details" in linea_lower:
                st.info(f"Line {i} ℹ️ **'Show details' detected:** Please confirm the missing content.")

            alertas = []
            to_highlight = []

            # --- API LANGUAGETOOL ---
            try:
                # Forzamos el lenguaje 'fr' para que no intente corregir como inglés
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'fr'}).json()
                for m in res.get('matches', []):
                    # OMITIR REGLAS DE ESPACIADO Y LETRAS SUELTAS
                    r_id = m.get('rule', {}).get('id', '')
                    if any(x in r_id for x in ["FRENCH_WHITESPACE", "FR_PUNCTUATION", "WHITESPACE"]):
                        continue

                    bad_raw = linea[m['offset']:m['offset']+m['length']]
                    bad = unicodedata.normalize('NFC', bad_raw)
                    
                    if len(bad) <= 1: continue # FILTRO CRÍTICO: No marcar letras solas como la 'a'
                    if bad.lower() in ["show details", "hide details"]: continue
                    
                    to_highlight.append(bad)
                    
                    # Traducción de alertas
                    msg_fr = m['message'].lower()
                    msg_en = "Grammar/Spelling issue"
                    if "accord" in msg_fr: msg_en = "Grammatical agreement"
                    elif "orthographe" in msg_fr: msg_en = "Spelling error"
                    
                    sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                    alertas.append(f"❌ **{msg_en}:** Issue in '{bad}'.{sug}")
            except: pass

            # --- RENDERIZADO ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif "show details" not in linea_lower:
                st.success(f"Line {i} ✅ Perfect")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
