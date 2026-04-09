import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Arabic Auditor", page_icon="🇦🇪", layout="centered")

# --- CSS PROFESIONAL ---
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
    .stProgress > div > div > div > div {
        background-color: #4a148c;
    }
    textarea {
        direction: rtl;
        text-align: right;
    }
    .translation-box {
        background-color: #f0f2f6;
        border-left: 5px solid #4a148c;
        padding: 10px;
        margin: 10px 0;
        font-style: italic;
        color: #333;
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
    .highlight {
        background-color: #fff3cd;
        font-weight: bold;
        color: #d9534f;
        text-decoration: underline;
        padding: 0 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE SOPORTE ---
def translate_to_english(text):
    if not text or text.strip() == "": return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except Exception:
        return "[Translation N/A]"

def highlight_errors(text, words_to_mark):
    highlighted = text
    try:
        for word in sorted(set(words_to_mark), key=len, reverse=True):
            if word and len(word.strip()) > 0:
                clean_word = re.escape(word.strip())
                pattern = rf"({clean_word})"
                highlighted = re.sub(pattern, r"<span class='highlight'>\1</span>", highlighted)
    except: pass
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Arabic Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste Arabic standards here:", height=300)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    st.markdown(f"**Line Count:** {len(lineas_reales)} / 2500")

# 4. PROCESAMIENTO
if st.button("🚀 Run Arabic Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        try:
            lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, linea in enumerate(lineas, 1):
                progress_bar.progress(i / len(lineas))
                status_text.text(f"Auditing line {i} of {len(lineas)}...")

                # --- MANEJO DE COMANDOS Y ESPACIADO ---
                # Parche para asegurar que show/hide details no estén pegados al texto árabe
                linea_temp = re.sub(rf"(?i)(?<=[^\x00-\x7F])(hide details|show details)", r" \1", linea)
                is_show = "show details" in linea_temp.lower()
                is_hide = "hide details" in linea_temp.lower()

                if is_show:
                    st.markdown(f"<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected:</b> Verify database content.</div>", unsafe_allow_html=True)

                alertas_finales = []
                words_to_highlight = []
                
                # Limpieza de símbolos para auditoría
                linea_audit = re.sub(r'^(\{\{|%%|\?\?|\$\$|<<|##|!!|\[\[|@@|&&|\*\*|<br/>)', '', linea_temp)
                linea_clean = re.sub(rf"(?i)show details|hide details", "", linea_audit).strip()

                if not linea_clean and not (is_show or is_hide): continue

                # --- REGLA: HARD RETURNS (Líneas cortadas) ---
                # Ignorar títulos numerados o líneas muy breves
                is_title = re.match(r'^[\d\u0660-\u0669]+(\.[\d\u0660-\u0669]+)*', linea_clean) or len(linea_clean.split()) < 4
                
                if not is_title and not (is_show or is_hide):
                    # Puntuación final incluyendo el punto árabe
                    if not linea_clean.endswith(('.', ':', '؟', '!', '"', '”', '»', '…', '؛')):
                        alertas_finales.append("⚠️ **Hard Return:** Line ends without proper punctuation (possible cut).")
                        if linea_clean.split():
                            words_to_highlight.append(linea_clean.split()[-1])

                # --- REGLA: Símbolos de Sublime ---
                sublime_tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
                for tag in sublime_tags:
                    if tag in linea:
                        triple_check = tag + tag[0] if len(tag) == 2 else tag
                        if not linea.startswith(tag) or (len(tag) == 2 and linea.startswith(triple_check)):
                            alertas_finales.append(f"⚠️ **Format:** Symbol '{tag}' must be at the START.")

                # --- REGLA: Doble Espacio ---
                if "  " in linea_audit:
                    alertas_finales.append("❌ **Spacing:** Double space detected.")

                # --- REGLAS MANUALES ÁRABE ---
                if re.search(r'[,;]', linea_audit):
                    alertas_finales.append("⚠️ **Punctuation:** Western symbols found (use Arabic '،' or '؛').")
                
                if "األدب" in linea_audit:
                    alertas_finales.append("❌ **Orthography:** Missing Hamza. Use 'الأدب'.")
                    words_to_highlight.append("األدب")

                # --- API LANGUAGETOOL ---
                try:
                    res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea_clean, 'language': 'ar'}, timeout=5).json()
                    for m in res.get('matches', []):
                        bad_word = linea_clean[m['offset']:m['offset']+m['length']]
                        if bad_word.lower() in ["show", "details", "hide"] or len(bad_word.strip()) <= 1: continue
                        
                        sug_text = ""
                        if m['replacements']:
                            best_sug = m['replacements'][0]['value']
                            if best_sug.strip() != bad_word.strip():
                                sug_text = f" (Try: **{best_sug}**)"
                        
                        words_to_highlight.append(bad_word)
                        alertas_finales.append(f"❌ **Grammar/Spelling:** '{bad_word}'.{sug_text}")
                except: pass

                # --- RENDERIZADO ---
                if alertas_finales:
                    with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                        linea_html = highlight_errors(linea, words_to_highlight)
                        st.markdown(f"<div style='direction: rtl; text-align: right; background: #fff; padding: 15px; border: 1px solid #ddd; font-size: 18px;'>{linea_html}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='translation-box'><b>Line Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                        for a in alertas_finales: st.write(a)
                elif not is_show:
                    st.success(f"Line {i} ✅ Perfect")
            
            status_text.text("Audit complete!")
        except Exception as e:
            st.error(f"Error: {e}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
