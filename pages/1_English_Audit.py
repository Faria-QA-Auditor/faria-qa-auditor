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
            alertas = []
            to_highlight = []
            
            linea_audit = re.sub(r'^(\{\{|%%|\?\?|\$\$|<<|##|!!|\[\[|@@|&&|\*\*|<br/>)', '', linea_temp)
            linea_clean = re.sub(rf"(?i)show details|hide details", "", linea_audit).strip()

            if not linea_clean: continue

            # --- REGLA: HARD RETURNS (Evitando Títulos) ---
            # Un título suele empezar con números (1.1) o ser muy corto.
            is_title = re.match(r'^\d+(\.\d+)*', linea_clean) or len(linea_clean.split()) < 5
            
            if not is_title:
                if not linea_clean.endswith(('.', ':', '?', '!', '"', '”', '…')):
                    alertas.append("⚠️ **Hard Return:** Line ends without punctuation (possible cut).")
                    # Resaltamos la última palabra para indicar el error visualmente
                    last_word = linea_clean.split()[-1].strip('.,!?:;')
                    to_highlight.append(last_word)

            # --- REGLA: Símbolos de Sublime ---
            sublime_tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
            for tag in sublime_tags:
                if tag in linea:
                    double_tag = tag + tag[0] if len(tag) == 2 else tag
                    if not linea.startswith(tag) or (len(tag) == 2 and linea.startswith(double_tag)):
                        alertas.append(f"⚠️ **Format:** Symbol '{tag}' must be at the START.")

            # --- REGLA: Doble Espacio ---
            if "  " in linea_audit:
                alertas.append("❌ **Spacing:** Double space detected.")

            # --- REGLA 1: Dialecto ---
            if "US" in dialect:
                ise_matches = re.findall(r'\b\w+ise\b', linea_clean, re.IGNORECASE)
                for word in ise_matches:
                    if word.lower() not in ["revise", "supervise", "exercise", "surprise", "expertise", "promise", "advise"]:
                        alertas.append(f"⚠️ **Dialect:** Use '-ize' for US English.")
                        to_highlight.append(word)
                if re.search(r'\b\w+our\b', linea_clean, re.IGNORECASE):
                    alertas.append("⚠️ **Dialect:** Use '-or' for US English.")

            # --- API LANGUAGETOOL ---
            lang_code = "en-US" if "US" in dialect else "en-GB"
            try:
                payload = {'text': linea_clean, 'language': lang_code, 'disabledRules': 'MCI_OXFORD_SPELLING_Z_NOT_S,OXFORD_SPELLING_Z_NOT_S'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                for m in res.get('matches', []):
                    bad = linea_clean[m['offset']:m['offset']+m['length']]
                    if "US" in dialect and bad.lower() in ["revise", "supervise", "exercise", "surprise"]: continue
                    if bad.strip():
                        to_highlight.append(bad)
                        alertas.append(f"❌ **{m['rule']['category']['name']}:** {m['message']}")
            except: pass

            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            else:
                st.success(f"Line {i} ✅ Perfect")

        status_text.text("Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
