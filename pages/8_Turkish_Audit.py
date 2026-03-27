import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Turkish Auditor", page_icon="🇹🇷", layout="centered")

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
    .translation-box {
        background-color: #f8f9fa;
        border-left: 5px solid #007bff;
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

# --- FUNCIÓN DE TRADUCCIÓN (TR -> EN) ---
def translate_to_english(text):
    if not text or text.strip() == "": return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except:
        return "[Translation unavailable]"

# --- FUNCIÓN PARA RESALTAR ERRORES ---
def highlight_errors(text, words_to_mark):
    highlighted = text
    try:
        for word in set(words_to_mark):
            if word and len(word.strip()) > 0:
                clean_word = re.escape(word.strip())
                highlighted = re.sub(f"({clean_word})", r"<span class='highlight'>\1</span>", highlighted)
    except:
        pass
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Turkish Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste Turkish standards here (one per line):", height=300)

if texto_input:
    total_words = len(texto_input.split())
    st.markdown(f"**Word Count:** {total_words} / 1000")
    if total_words > 1000:
        st.error("⚠️ Warning: Limit exceeded.")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        try:
            lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
            st.subheader("Audit Results")

            for i, linea in enumerate(lineas, 1):
                if linea.lower() in ["hide details", "show details"]:
                    if "show" in linea.lower():
                        st.info(f"Line {i} ℹ️ 'Show details' detected: Verify if text is missing.")
                    continue

                alertas_finales = []
                words_to_highlight = []
                
                # --- REGLA 1: Sufijos Incorrectos (Mutación Consonántica) ---
                # Si termina en f,s,t,k,ç,ş,h,p no debe seguir 'da' o 'de', sino 'ta' o 'te'
                if re.search(r'[fstkçşhp][Dd][ae]', linea):
                    bad_match = re.search(r'\w*[fstkçşhp][Dd][ae]\w*', linea)
                    if bad_match:
                        word = bad_match.group()
                        alertas_finales.append(f"⚠️ **Consonant Mutation:** Incorrect suffix detected in '{word}'. After voiceless consonants, use -ta/-te instead of -da/-de.")
                        words_to_highlight.append(word)

                # --- REGLA 2: Longitud de Palabra (Aglutinación) ---
                words = linea.split()
                for w in words:
                    if len(w) > 25:
                        alertas_finales.append(f"ℹ️ **Note [Style]:** Word '{w}' is very long ({len(w)} chars). Check for readability.")
                        words_to_highlight.append(w)

                # --- REGLA 3: Mayúsculas y Números ---
                if not re.match(r'^([A-ZÇĞİIÖŞÜ]|\d+\.(\d+\.)?)', linea):
                    alertas_finales.append("❌ **Error [Format]:** Line must start with a capital letter or valid number.")

                # --- API LANGUAGETOOL + TRADUCCIÓN ---
                try:
                    res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'tr'}).json()
                    for m in res.get('matches', []):
                        offset, length = m['offset'], m['length']
                        bad_word = linea[offset:offset+length]
                        words_to_highlight.append(bad_word)
                        
                        # Traducción al vuelo de la sugerencia
                        sug_text = ""
                        if m['replacements']:
                            best_sug = m['replacements'][0]['value']
                            sug_trans = translate_to_english(best_sug)
                            sug_text = f" (Try: **{best_sug}** → *'{sug_trans}'*)"
                        
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
                        # Texto resaltado
                        linea_html = highlight_errors(linea, words_to_highlight)
                        st.markdown(f"<div style='background: #fff; padding: 15px; border: 1px solid #ddd; font-size: 16px;'>{linea_html}</div>", unsafe_allow_html=True)
                        
                        # Traducción de contexto
                        line_trans = translate_to_english(linea)
                        st.markdown(f"<div class='translation-box'><b>English Context:</b> {line_trans}</div>", unsafe_allow_html=True)
                        
                        for a in alertas_finales:
                            st.write(a)
        except Exception as e:
            st.error(f"Audit error: {e}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
