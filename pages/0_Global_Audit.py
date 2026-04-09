import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="General Languages Auditor", page_icon="🌍", layout="centered")

# --- CSS PERSONALIZADO (MORADO FARIA) ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #4a148c; 
        color: white; font-weight: bold; height: 3em; border: none;
    }
    .stButton>button:hover { background-color: #6a1b9a; color: white; }
    .stProgress > div > div > div > div { background-color: #4a148c; }
    .translation-box { 
        background-color: #f8f9fa; border-left: 5px solid #4a148c; 
        padding: 12px; margin: 10px 0; font-style: italic; color: #333;
    }
    .db-info-box { 
        background-color: #e3f2fd; border-left: 5px solid #2196f3; 
        padding: 15px; color: #0c5460; margin: 10px 0; border-radius: 4px; font-weight: 500; 
    }
    .highlight { 
        background-color: #fff3cd; font-weight: bold; color: #d9534f; 
        text-decoration: underline; padding: 0 2px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE SOPORTE ---
def translate_to_english(text):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

def highlight_errors(text, words):
    highlighted = text
    for word in sorted(set(words), key=len, reverse=True):
        if not word or len(word.strip()) == 0: continue
        clean_word = re.escape(word.strip())
        if len(word.strip()) <= 2 or "." in word:
            pattern = rf"(?i)\b{clean_word}\b"
            highlighted = re.sub(pattern, rf"<span class='highlight'>{word}</span>", highlighted, count=1)
        else:
            highlighted = re.sub(f"({clean_word})", r"<span class='highlight'>\1</span>", highlighted, flags=re.IGNORECASE)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: 
    st.image("logo.jpg", width=250)
except: 
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>General Languages Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR (2500 LÍNEAS)
texto_raw = st.text_area("Paste your standards here:", height=350, placeholder="Supports different languages...")

if texto_raw:
    texto_raw = unicodedata.normalize('NFC', texto_raw)
    lineas_reales = [l for l in texto_raw.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Total Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit.")

# 4. BOTÓN Y PROCESAMIENTO
if st.button("🚀 Run General Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_raw.split('\n') if l.strip()]
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")
            
            # --- MANEJO DE COMANDOS ---
            linea_temp = re.sub(rf"(?i)(?<=[a-zA-Záéíóúüñ])(hide details|show details)", r" \1", linea)
            is_show = "show details" in linea_temp.lower()
            is_hide = "hide details" in linea_temp.lower()
            
            if is_show:
                st.markdown(f"<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected:</b> Verify database content.</div>", unsafe_allow_html=True)

            alertas = []
            to_highlight = []
            
            # Limpiar símbolos para auditoría
            linea_audit = re.sub(r'^(\{\{|%%|\?\?|\$\$|<<|##|!!|\[\[|@@|&&|\*\*|<br/>)', '', linea_temp)
            linea_clean = re.sub(rf"(?i)show details|hide details", "", linea_audit).strip()

            if not linea_clean and not (is_show or is_hide): continue

            # --- REGLA: HARD RETURNS (Líneas cortadas) ---
            # Excluimos títulos o líneas muy breves
            is_title = re.match(r'^\d+(\.\d+)*', linea_clean) or len(linea_clean.split()) < 5
            
            if not is_title and not (is_show or is_hide):
                # Validar puntuación final multilingüe
                if not linea_clean.endswith(('.', ':', '?', '!', '"', '”', '»', '…')):
                    alertas.append("⚠️ **Hard Return:** Line ends without proper punctuation (possible cut).")
                    if linea_clean.split():
                        to_highlight.append(linea_clean.split()[-1].strip('.,!?:;'))

            # --- REGLA: SÍMBOLOS DE SUBLIME ---
            tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
            for tag in tags:
                if tag in linea:
                    double_tag = tag + tag[0] if len(tag) == 2 else tag
                    if not linea.startswith(tag) or (len(tag) == 2 and linea.startswith(double_tag)):
                        alertas.append(f"⚠️ **Format:** Symbol '{tag}' must be at the START.")

            # --- REGLA: DOBLE ESPACIO ---
            if "  " in linea_audit:
                alertas.append("❌ **Spacing:** Double space detected.")

            # --- API LANGUAGETOOL ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', 
                                    data={'text': linea_clean, 'language': 'auto'}, timeout=8).json()
                
                for m in res.get('matches', []):
                    bad = linea_clean[m['offset']:m['offset']+m['length']]
                    if bad.lower() in ["show", "details", "hide"]: continue
                    if m['replacements']:
                        best_sug = m['replacements'][0]['value']
                        if best_sug.strip() == bad.strip(): continue
                        sug_text = f" (Try: **{best_sug}**)"
                    else:
                        sug_text = ""

                    to_highlight.append(bad)
                    alertas.append(f"❌ **{m['rule']['category']['name']}:** {m['message']}{sug_text}")
            except: pass

            # --- RENDERIZADO ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    linea_html = highlight_errors(linea, to_highlight)
                    st.markdown(f"<div style='background: white; padding: 15px; border: 1px solid #ddd; border-radius: 8px;'>{linea_html}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not is_show:
                st.success(f"Line {i} ✅ Perfect")

        status_text.text("General Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
