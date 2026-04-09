import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Spanish Standards Auditor", page_icon="🇪🇸", layout="centered")

# --- CSS PERSONALIZADO (MORADO FARIA) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em;
        background-color: #4a148c; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #6a1b9a; color: white; }
    .stProgress > div > div > div > div { background-color: #4a148c; }
    .translation-box {
        background-color: #f0f2f6; border-left: 5px solid #4a148c;
        padding: 10px; margin: 10px 0; font-style: italic;
    }
    .db-info-box {
        background-color: #e3f2fd; border-left: 5px solid #2196f3;
        padding: 15px; color: #0c5460; margin: 10px 0;
        border-radius: 4px; font-weight: 500;
    }
    .highlight {
        background-color: #fff3cd; font-weight: bold; color: #d9534f;
        text-decoration: underline; padding: 0 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def translate_to_english(text):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=es&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

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
st.markdown("<h2 style='color: #444;'>Spanish Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR
texto_input = st.text_area("Paste Spanish standards here:", height=300, placeholder="")

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    st.markdown(f"**Line Count:** {len(lineas_reales)} / 2500")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Spanish Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text.")
    else:
        texto_norm = unicodedata.normalize('NFC', texto_input)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")

            # --- MANEJO DE COMANDOS Y LIMPIEZA ---
            linea_temp = re.sub(rf"(?i)(?<=[a-zA-Záéíóúüñ])(hide details|show details)", r" \1", linea)
            is_show = "show details" in linea_temp.lower()
            is_hide = "hide details" in linea_temp.lower()

            if is_show:
                st.markdown(f"<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected:</b> Verify source database content.</div>", unsafe_allow_html=True)

            alertas = []
            to_highlight = []
            
            # Limpiar símbolos para auditoría de contenido
            linea_audit = re.sub(r'^(\{\{|%%|\?\?|\$\$|<<|##|!!|\[\[|@@|&&|\*\*|<br/>)', '', linea_temp)
            linea_clean = re.sub(rf"(?i)show details|hide details", "", linea_audit).strip()

            if not linea_clean and not (is_show or is_hide): continue

            # --- REGLA: HARD RETURNS (Líneas cortadas) ---
            # Un título suele empezar con números (1.1) o ser muy corto (< 5 palabras).
            is_title = re.match(r'^\d+(\.\d+)*', linea_clean) or len(linea_clean.split()) < 5
            
            if not is_title and not (is_show or is_hide):
                # Validar si termina en puntuación correcta para español
                if not linea_clean.endswith(('.', ':', '?', '!', '"', '»', '”', '…')):
                    alertas.append("⚠️ **Hard Return:** La línea parece estar cortada o no termina en puntuación.")
                    if linea_clean.split():
                        to_highlight.append(linea_clean.split()[-1].strip('.,!?:;'))

            # --- REGLA: Símbolos de Sublime ---
            sublime_tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
            for tag in sublime_tags:
                if tag in linea:
                    triple_check = tag + tag[0] if len(tag) == 2 else tag
                    if not linea.startswith(tag) or (len(tag) == 2 and linea.startswith(triple_check)):
                        alertas.append(f"⚠️ **Format:** Symbol '{tag}' must be at the START.")

            # --- REGLA: Doble Espacio ---
            if "  " in linea_audit:
                alertas.append("❌ **Spacing:** Double space detected.")

            # --- REGLAS MANUALES ESPAÑOL ---
            if re.search(r'\b(es|son|fue|fueron)\b\s+\w+(ado|ido|ada|ida)\b', linea_clean, re.I):
                alertas.append("⚠️ **Style Suggestion:** Passive voice detected. Consider using 'pasiva refleja'.")
            
            match_pct = re.search(r'\d+%', linea_clean)
            if match_pct:
                alertas.append("❌ **Punctuation Error:** Missing space before % (e.g., '10 %').")
                to_highlight.append(match_pct.group())

            # --- API LANGUAGETOOL ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea_clean, 'language': 'es'}).json()
                for m in res.get('matches', []):
                    bad = linea_clean[m['offset']:m['offset']+m['length']]
                    if bad.lower() in ["show", "details", "hide"]: continue
                    
                    to_highlight.append(bad)
                    sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                    alertas.append(f"❌ **{m['rule']['category']['name']}:** {m['message']}{sug}")
            except: pass

            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not is_show:
                st.success(f"Line {i} ✅ Perfect")
        
        status_text.text("Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
