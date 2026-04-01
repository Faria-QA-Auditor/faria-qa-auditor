import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Arabic Auditor", page_icon="🇸🇦", layout="centered")

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
    /* Barra de Progreso Morada */
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
    /* Estilo para el Recuadro Azul de Base de Datos */
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

# --- FUNCIÓN DE TRADUCCIÓN SEGURA ---
def translate_to_english(text):
    if not text or text.strip() == "": return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except Exception:
        return "[Translation service temporarily unavailable]"

# --- PARCHE: Función highlight_errors mejorada ---
def highlight_errors(text, words_to_mark):
    highlighted = text
    try:
        # Ordenamos por longitud para evitar el efecto dálmata en sub-palabras
        for word in sorted(set(words_to_mark), key=len, reverse=True):
            if word and len(word.strip()) > 0:
                clean_word = re.escape(word.strip())
                # Resaltado con límites de palabra para precisión
                pattern = rf"({clean_word})"
                highlighted = re.sub(pattern, r"<span class='highlight'>\1</span>", highlighted)
    except:
        pass
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

# 3. ENTRADA DE TEXTO Y CONTADOR (2500 Líneas)
texto_input = st.text_area("Paste Arabic standards here:", height=300)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit.")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Arabic Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        try:
            lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
            
            # --- BARRA DE PROGRESO ---
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, linea in enumerate(lineas, 1):
                progress_bar.progress(i / len(lineas))
                status_text.text(f"Auditing line {i} of {len(lineas)}...")

                linea_lower = linea.lower().strip()

                # --- REGLA: HIDE/SHOW DETAILS ---
                if "hide details" in linea_lower: continue

                if "show details" in linea_lower:
                    st.markdown(f"""<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected:</b> Verify source database content.</div>""", unsafe_allow_html=True)
                    continue

                alertas_finales = []
                words_to_highlight = []
                linea_audit = linea

                # --- REGLA: Símbolos de Sublime (Pares al inicio) ---
                sublime_tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
                for tag in sublime_tags:
                    if tag in linea:
                        # Triple check: evitar más de 2 símbolos seguidos
                        triple_check = tag + tag[0] if len(tag) == 2 else tag
                        if not linea.startswith(tag) or (len(tag) == 2 and linea.startswith(triple_check)):
                            alertas_finales.append(f"⚠️ **Format:** Symbol '{tag}' must be a PAIR at the START of the line.")
                        linea_audit = linea_audit.replace(tag, "")

                # --- REGLA: Doble Espacio ---
                if "  " in linea_audit:
                    alertas_finales.append("❌ **Spacing:** Double space detected within the phrase.")
                
                # --- REGLAS MANUALES ÁRABE ---
                if re.search(r'[,;]', linea_audit):
                    alertas_finales.append("⚠️ **Warning [Punctuation]:** Found western symbols (use Arabic ، o ؛).")
                
                if "األدب" in linea_audit:
                    alertas_finales.append("❌ **Error [Orthography]:** Missing Hamza. Use 'الأدب'.")
                    words_to_highlight.append("األدب")

                # API LanguageTool
                try:
                    res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea_audit, 'language': 'ar'}, timeout=5).json()
                    for m in res.get('matches', []):
                        offset, length = m['offset'], m['length']
                        bad_word = linea_audit[offset:offset+length]
                        
                        if bad_word.lower() in ["show", "details", "hide"] or len(bad_word.strip()) <= 1: continue
                        if bad_word in words_to_highlight: continue
                        
                        sug_text = ""
                        if m['replacements']:
                            best_sug = m['replacements'][0]['value']
                            if best_sug.strip() != bad_word.strip():
                                sug_translation = translate_to_english(best_sug)
                                sug_text = f" (Try: **{best_sug}** → *'{sug_translation}'*)"
                        
                        words_to_highlight.append(bad_word)
                        bad_word_trans = translate_to_english(bad_word)
                        alertas_finales.append(f"❌ **Grammar/Spelling:** Issue in '{bad_word}' ('{bad_word_trans}').{sug_text}")
                except:
                    pass

                # Renderizado
                header = f"Line {i}"
                if not alertas_finales:
                    st.success(f"{header} ✅ Perfect")
                else:
                    with st.expander(f"{header} ⚠️ Issues found", expanded=True):
                        linea_html = highlight_errors(linea, words_to_highlight)
                        st.markdown(f"<div style='direction: rtl; text-align: right; background: #fff; padding: 15px; border: 1px solid #ddd; font-size: 18px;'>{linea_html}</div>", unsafe_allow_html=True)
                        
                        line_trans = translate_to_english(linea)
                        st.markdown(f"<div class='translation-box'><b>Line Context:</b> {line_trans}</div>", unsafe_allow_html=True)
                        
                        for a in alertas_finales:
                            st.write(a)
            
            status_text.text("Audit complete!")
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
