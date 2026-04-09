import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="English Standards Auditor", page_icon="🇺🇸", layout="centered")

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em;
        background-color: #4a148c; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #6a1b9a; color: white; }
    .stProgress > div > div > div > div { background-color: #4a148c; }
    .highlight {
        background-color: #fff3cd; font-weight: bold; color: #d9534f;
        text-decoration: underline; padding: 0 2px;
    }
    .db-info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        color: #0c5460;
        margin: 10px 0;
        border-radius: 4px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

def highlight_errors(text, words):
    highlighted = text
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
st.markdown("<h2 style='color: #444;'>English Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. DIALECT SWITCH
dialect = st.radio("Select Regional Standard:", ["US (American English)", "UK (British English)"], horizontal=True)

# 4. INPUT
texto_input = st.text_area("Paste English standards here (one per line):", height=300)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    st.markdown(f"**Line Count:** {len(lineas_reales)} / 2500")
    st.write("---")

# LISTA MAESTRA DE EXCEPCIONES (Raíces léxicas fijas)
EXCEPTIONS_LIST = [
    "advise", "apprise", "arise", "chastise", "comprise", "compromise", 
    "demise", "despise", "devise", "disguise", "exercise", "exorcise", 
    "improvise", "incise", "merchandise", "premise", "revise", 
    "supervise", "surmise", "surprise", "televise", "expertise", "promise"
]

if st.button("🚀 Run English Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        texto_norm = unicodedata.normalize('NFC', texto_input)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i}...")
            
            linea_temp = re.sub(rf"(?i)(?<=[a-zA-Záéíóúüñ])(hide details|show details)", r" \1", linea)
            is_show = "show details" in linea_temp.lower()
            is_hide = "hide details" in linea_temp.lower()
            
            if is_show:
                st.markdown(f"<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected:</b> Review for potentially hidden text.</div>", unsafe_allow_html=True)

            alertas = []
            to_highlight = []
            
            linea_audit = re.sub(r'^(\{\{|%%|\?\?|\$\$|<<|##|!!|\[\[|@@|&&|\*\*|<br/>)', '', linea_temp)
            linea_clean = re.sub(rf"(?i)show details|hide details", "", linea_audit).strip()

            if not linea_clean and not (is_show or is_hide): continue

            # --- REGLA: HARD RETURNS ---
            is_title = re.match(r'^\d+(\.\d+)*', linea_clean) or len(linea_clean.split()) < 5
            if not is_title and not (is_show or is_hide):
                if not linea_clean.endswith(('.', ':', '?', '!', '"', '”', '…')):
                    alertas.append("⚠️ **Hard Return:** Line ends without punctuation.")
                    if linea_clean.split():
                        to_highlight.append(linea_clean.split()[-1].strip('.,!?:;'))

            # --- REGLA: Símbolos de Sublime ---
            sublime_tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
            for tag in sublime_tags:
                if tag in linea and not (linea.startswith(tag) or (len(tag) == 2 and linea.startswith(tag + tag[0]))):
                    alertas.append(f"⚠️ **Format:** Symbol '{tag}' must be at the START.")

            # --- REGLA: Dialecto US (Excepciones Aplicadas) ---
            if "US" in dialect:
                ise_words = re.findall(r'\b\w+ise\b', linea_clean, re.IGNORECASE)
                for word in ise_words:
                    if word.lower() not in EXCEPTIONS_LIST:
                        alertas.append(f"⚠️ **Dialect:** Use '-ize' for '{word}' in US English.")
                        to_highlight.append(word)
                if re.search(r'\b\w+our\b', linea_clean, re.IGNORECASE):
                    alertas.append("⚠️ **Dialect:** Use '-or' for US English.")
            else: # UK
                if any(x in linea_clean.lower() for x in ["color", "behavior", "center", "honor"]):
                    alertas.append("⚠️ **Dialect:** US spelling detected. Use UK conventions.")

            # --- API LANGUAGETOOL (Sincronizada con EXCEPTIONS_LIST) ---
            lang_code = "en-US" if "US" in dialect else "en-GB"
            try:
                payload = {'text': linea_clean, 'language': lang_code, 'disabledRules': 'MCI_OXFORD_SPELLING_Z_NOT_S,OXFORD_SPELLING_Z_NOT_S'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                for m in res.get('matches', []):
                    bad = linea_clean[m['offset']:m['offset']+m['length']]
                    # Bloqueo de falsos positivos en API usando nuestra lista maestra
                    if "US" in dialect and bad.lower() in EXCEPTIONS_LIST: continue
                    if bad.strip():
                        to_highlight.append(bad)
                        alertas.append(f"❌ **{m['rule']['category']['name']}:** {m['message']}")
            except: pass

            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not is_show: 
                st.success(f"Line {i} ✅ Perfect")

        status_text.text("Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
