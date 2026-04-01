import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Turkish Auditor", page_icon="🇹🇷", layout="centered")

# --- CSS CON HIGHLIGHTING Y BARRA MORADA ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #4a148c; color: white; font-weight: bold; height: 3em; border: none; }
    .stButton>button:hover { background-color: #6a1b9a; color: white; }
    .stProgress > div > div > div > div { background-color: #4a148c; }
    .translation-box { background-color: #f0f2f6; border-left: 5px solid #4a148c; padding: 10px; margin: 10px 0; font-style: italic; }
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

def translate_to_english(text):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

def highlight_errors(text, words):
    highlighted = unicodedata.normalize('NFC', text)
    for word in sorted(set(words), key=len, reverse=True):
        if word and len(word.strip()) > 0:
            clean_word = re.escape(word.strip())
            pattern = rf"(?i)\b{clean_word}\b"
            if len(word) <= 1 or not word[0].isalnum():
                highlighted = highlighted.replace(word, f"<span class='highlight'>{word}</span>", 1)
            else:
                highlighted = re.sub(pattern, rf"<span class='highlight'>{word}</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: st.image("logo.jpg", width=250)
except: st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Turkish Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR
texto_input = st.text_area("Paste Turkish standards here:", height=300)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 2500")

if st.button("🚀 Run Turkish Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")

            alertas = []
            to_highlight = []
            
            # 1. Identificar comandos especiales sin romper la línea
            is_show = "show details" in linea.lower()
            
            # 2. Limpiar la línea para auditoría (Quitamos tags de Sublime y comandos de ClickUp)
            linea_audit = re.sub(r'^(\{\{|%%|\?\?|\$\$|<<|##|!!|\[\[|@@|&&|\*\*|<br/>)', '', linea)
            linea_clean = re.sub(rf"(?i)show details|hide details", "", linea_audit).strip()

            if is_show:
                st.markdown(f"<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected.</b></div>", unsafe_allow_html=True)

            # --- REGLA DE ORO: VALIDACIÓN MECÁNICA DE CARACTERES TURCOS ---
            # Buscamos letras que suelen ser errores de latinización (i, g, c, s, o, u) 
            # y que la API a veces ignora.
            latinizadas = {
                r'\baskim\b': 'aşkım',
                r'\bogrenci\b': 'öğrenci',
                r'\bisik\b': 'ışık',
                r'\bcalismalar\b': 'çalışmalar'
            }
            for pattern, fix in latinizadas.items():
                if re.search(pattern, linea_clean, re.IGNORECASE):
                    alertas.append(f"❌ **Alphabet:** Detected Latin version. Did you mean '{fix}'?")
                    found_word = re.search(pattern, linea_clean, re.IGNORECASE).group()
                    to_highlight.append(found_word)

            # Bloqueo total de Q, W, X
            forbidden = re.findall(r'[qwxQWX]', linea_clean)
            if forbidden:
                alertas.append(f"❌ **Non-Turkish Letters:** {set(forbidden)} are not allowed.")
                to_highlight.extend(forbidden)

            # --- API LANGUAGETOOL ---
            if linea_clean:
                try:
                    res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea_clean, 'language': 'tr'}).json()
                    for m in res.get('matches', []):
                        bad = linea_clean[m['offset']:m['offset']+m['length']]
                        if len(bad.strip()) <= 1: continue
                        
                        sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                        to_highlight.append(bad)
                        alertas.append(f"❌ **Grammar/Spelling:** Issue in '{bad}'.{sug}")
                except: pass

            # --- RENDER ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea_clean)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            else:
                st.success(f"Line {i} ✅ Perfect")

        status_text.text("Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
