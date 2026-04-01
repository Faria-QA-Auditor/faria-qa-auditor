import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN
st.set_page_config(page_title="French Standards Auditor", page_icon="🇫🇷", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #4a148c; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #6a1b9a; color: white; }
    .stProgress > div > div > div > div { background-color: #4a148c; }
    .translation-box { background-color: #f0f2f6; border-left: 5px solid #4a148c; padding: 12px; margin: 10px 0; font-style: italic; border-radius: 0 8px 8px 0; }
    .db-info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        color: #0c5460;
        margin: 10px 0;
        border-radius: 4px;
        font-weight: 500;
    }
    .highlight { background-color: #fff3cd; font-weight: bold; color: #d9534f; text-decoration: underline; padding: 0 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- TRADUCCIÓN ---
def translate_to_english(text):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=fr&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

# --- RESALTADOR ---
def highlight_errors(text, words):
    highlighted = unicodedata.normalize('NFC', text)
    for word in sorted(set(words), key=len, reverse=True):
        if word and len(word.strip()) > 0:
            clean_word = re.escape(word.strip())
            pattern = rf"(?i)\b{clean_word}\b"
            if len(word) <= 2 or "." in word:
                highlighted = highlighted.replace(word, f"<span class='highlight'>{word}</span>", 1)
            else:
                highlighted = re.sub(pattern, rf"<span class='highlight'>{word}</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: st.image("logo.jpg", width=250)
except: st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>French Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR
texto_raw = st.text_area("Paste French standards here:", height=300, placeholder="")

if texto_raw:
    lineas_reales = [l for l in texto_raw.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 2500")

if st.button("🚀 Run French Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text.")
    else:
        texto_norm = unicodedata.normalize('NFC', texto_raw)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")

            linea_lower = linea.lower().strip()
            if "hide details" in linea_lower: continue
            if "show details" in linea_lower:
                st.markdown(f"<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected:</b> Verify database.</div>", unsafe_allow_html=True)
                continue

            alertas = []
            to_highlight = []
            linea_audit = linea

            # --- REGLA: Símbolos de Sublime (Pares al inicio) ---
            sublime_tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
            for tag in sublime_tags:
                if tag in linea:
                    triple_check = tag + tag[0] if len(tag) == 2 else tag
                    if not linea.startswith(tag) or (len(tag) == 2 and linea.startswith(triple_check)):
                        alertas.append(f"⚠️ **Format:** Symbol '{tag}' must be a PAIR at the START of the line.")
                    linea_audit = linea_audit.replace(tag, "")

            # --- REGLA: Doble Espacio ---
            if "  " in linea_audit:
                alertas.append("❌ **Spacing:** Double space detected.")

            # --- API LANGUAGETOOL ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea_audit.strip(), 'language': 'fr'}).json()
                for m in res.get('matches', []):
                    r_id = m.get('rule', {}).get('id', '')
                    
                    # Eliminamos UPPERCASE_SENTENCE_START de esta lista para que SÍ marque la mayúscula faltante
                    if any(x in r_id for x in ["FRENCH_WHITESPACE", "FR_PUNCTUATION", "MORFOLOGIK_RULE_FR_FR"]):
                        continue

                    bad = unicodedata.normalize('NFC', linea_audit[m['offset']:m['offset']+m['length']])
                    if bad.lower() in ["show", "details", "hide"] or len(bad.strip()) <= 1:
                        continue
                    
                    to_highlight.append(bad)
                    msg_fr = m['message'].lower()
                    msg_en = "Grammar/Spelling issue"
                    if "accord" in msg_fr: msg_en = "Grammatical agreement"
                    elif "orthographe" in msg_fr: msg_en = "Spelling error"
                    elif "majuscule" in msg_fr or "uppercase" in msg_fr: msg_en = "Capitalization error"
                    
                    sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                    alertas.append(f"❌ **{msg_en}:** Issue in '{bad}'.{sug}")
            except: pass

            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            else:
                st.success(f"Line {i} ✅ Perfect")
        
        status_text.text("Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
