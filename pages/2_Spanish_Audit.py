import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Spanish Standards Auditor", page_icon="🇪🇸", layout="centered")

# --- CSS PERSONALIZADO ---
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
    .translation-box {
        background-color: #f0f2f6;
        border-left: 5px solid #4a148c;
        padding: 10px;
        margin: 10px 0;
        font-style: italic;
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
    for word in set(words):
        if word and len(word.strip()) > 0:
            highlighted = re.sub(f"({re.escape(word)})", r"<span class='highlight'>\1</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Spanish Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR (2500 Líneas)
texto_input = st.text_area("Paste Spanish standards here:", height=300, placeholder="")

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit.")
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

            linea_lower = linea.lower().strip()

            # --- REGLA: HIDE DETAILS (Ignorar por completo) ---
            if "hide details" in linea_lower:
                continue

            # --- REGLA: SHOW DETAILS (Recuadro Azul e Interrumpir Auditoría) ---
            if "show details" in linea_lower:
                st.markdown(f"""
                    <div class='db-info-box'>
                        Line {i} ℹ️ <b>'Show details' detected:</b> There is hidden information in this line that was not fully expanded. 
                        Please verify the missing content in the source database.
                    </div>
                """, unsafe_allow_html=True)
                continue

            alertas = []
            to_highlight = []

            # --- REGLAS MANUALES ---
            if re.search(r'\b(es|son|fue|fueron)\b\s+\w+(ado|ido|ada|ida)\b', linea, re.I):
                alertas.append("⚠️ **Style Suggestion:** Passive voice detected. Consider using 'pasiva refleja' (e.g., 'se realiza').")
            if re.search(r'\d+%', linea):
                alertas.append("❌ **Punctuation Error:** Missing space before % (e.g., '10 %').")
                to_highlight.append(re.search(r'\d+%', linea).group())

            # --- API LANGUAGETOOL (Traducción de Alertas) ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'es'}).json()
                for m in res.get('matches', []):
                    bad = linea[m['offset']:m['offset']+m['length']]
                    # Doble validación para no marcar palabras de la DB
                    if bad.lower() in ["show", "details", "hide"]: continue
                    
                    to_highlight.append(bad)
                    
                    # Mapeo a Inglés
                    msg_orig = m['message'].lower()
                    if "ortografía" in msg_orig or "spelling" in msg_orig: msg_en = "Spelling error"
                    elif "gramática" in msg_orig or "grammar" in msg_orig: msg_en = "Grammatical issue"
                    elif "concordancia" in msg_orig or "agreement" in msg_orig: msg_en = "Agreement issue"
                    else: msg_en = "Linguistic issue"
                    
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
