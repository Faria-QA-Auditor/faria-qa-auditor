import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Arabic Auditor", page_icon="🇸🇦", layout="centered")

# --- CSS PROFESIONAL CON RESALTADO ---
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
    .highlight {
        background-color: #fff3cd;
        font-weight: bold;
        color: #d9534f;
        text-decoration: underline;
        padding: 0 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE TRADUCCIÓN (AR -> EN) ---
def translate_to_english(text):
    if not text or text.strip() == "": return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t&q={text}"
        res = requests.get(url).json()
        return res[0][0][0]
    except:
        return "N/A"

# --- FUNCIÓN PARA RESALTAR ERRORES EN EL BLOQUE ORIGINAL ---
def highlight_errors(text, words_to_mark):
    highlighted = text
    for word in set(words_to_mark):
        if word and len(word.strip()) > 0:
            clean_word = re.escape(word.strip())
            highlighted = re.sub(f"({clean_word})", r"<span class='highlight'>\1</span>", highlighted)
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
    total_words = len(texto_input.split())
    st.markdown(f"**Word Count:** {total_words} / 1000")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            if linea.lower() in ["hide details", "show details"]:
                if "show" in linea.lower():
                    st.info(f"Line {i} ℹ️ 'Show details' detected.")
                continue

            alertas_finales = []
            words_to_highlight = []
            
            # --- REGLAS MANUALES ---
            if re.search(r'[,;]', linea):
                alertas_finales.append("⚠️ **Warning [Punctuation]:** Found western symbols.")
            
            if "األدب" in linea:
                alertas_finales.append("❌ **Error [Orthography]:** Missing Hamza. Use 'الأدب' (Literature).")
                words_to_highlight.append("األدب")

            # --- API LANGUAGETOOL + TRADUCCIÓN DE SUGERENCIAS ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'ar'}).json()
                for m in res.get('matches', []):
                    # Identificar palabra errónea
                    offset, length = m['offset'], m['length']
                    bad_word = linea[offset:offset+length]
                    words_to_highlight.append(bad_word)
                    
                    # Traducir sugerencia si existe
                    sug_text = ""
                    if m['replacements']:
                        best_sug = m['replacements'][0]['value']
                        sug_translation = translate_to_english(best_sug)
                        sug_text = f" (Try: **{best_sug}** → *'{sug_translation}'*)"
                    
                    # Traducir la palabra mala para contexto
                    bad_word_trans = translate_to_english(bad_word)
                    alertas_finales.append(f"Grammar/Spelling: Issue in '{bad_word}' ('{bad_word_trans}').{sug_text}")
            except:
                pass

            # --- RENDERIZADO ---
            header = f"Line {i}"
            if not alertas_finales:
                st.success(f"{header} ✅ Perfect")
            else:
                with st.expander(f"{header} ⚠️ Issues found", expanded=True):
                    # 1. Bloque resaltado
                    linea_html = highlight_errors(linea, words_to_highlight)
                    st.markdown(f"<div style='direction: rtl; text-align: right; background: #fff; padding: 15px; border: 1px solid #ddd; font-size: 18px;'>{linea_html}</div>", unsafe_allow_html=True)
                    
                    # 2. Traducción completa de la línea
                    line_trans = translate_to_english(linea)
                    st.markdown(f"<div class='translation-box'><b>Line Context:</b> {line_trans}</div>", unsafe_allow_html=True)
                    
                    # 3. Listado de alertas con traducciones de sugerencias
                    for a in alertas_finales:
                        st.write(a)

st
