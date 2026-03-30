import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Turkish Auditor", page_icon="🇹🇷", layout="centered")

# --- CSS CON HIGHLIGHTING Y BARRA MORADA ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #4a148c; color: white; font-weight: bold; height: 3em; }
    /* Barra de Progreso Morada */
    .stProgress > div > div > div > div { background-color: #4a148c; }
    .translation-box { background-color: #f0f2f6; border-left: 5px solid #4a148c; padding: 10px; margin: 10px 0; font-style: italic; }
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
    highlighted = text
    for word in sorted(set(words), key=len, reverse=True):
        if word and len(word.strip()) > 0:
            highlighted = re.sub(f"({re.escape(word)})", r"<span class='highlight'>\1</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: st.image("logo.jpg", width=250)
except: st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Turkish Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR (2500 Líneas)
texto_input = st.text_area("Paste Turkish standards here:", height=300)

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit.")

if st.button("🚀 Run Deep Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        
        # --- BARRA DE PROGRESO ---
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, linea in enumerate(lineas, 1):
            # Actualización visual
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")

            linea_lower = linea.lower().strip()
            
            # HIDE DETAILS: Ignorar
            if "hide details" in linea_lower: continue
            
            # SHOW DETAILS: Recuadro Azul
            if "show details" in linea_lower:
                st.markdown(f"""
                    <div class='db-info-box'>
                        Line {i} ℹ️ <b>'Show details' detected:</b> Please verify if there is hidden information in the source database.
                    </div>
                """, unsafe_allow_html=True)
                continue

            alertas = []
            to_highlight = []

            # --- REGLA: Inicio de línea ---
            if re.match(r'^\.', linea):
                alertas.append("❌ **Error [Format]:** Line starts with a dot. Please remove it.")
                to_highlight.append(".")

            # --- REGLA: Latinización y Errores Comunes ---
            common_errors = {
                "Ulkelere": "Ülkelere",
                "sabir": "sabır",
                "uygulalarından": "uygulamalarından",
                "Adabımuaşerei": "Adabımuaşereti"
            }
            for err, fix in common_errors.items():
                if err in linea:
                    alertas.append(f"❌ **Error [Orthography]:** Found '{err}'. Did you mean '{fix}'?")
                    to_highlight.append(err)

            # --- API LANGUAGETOOL ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'tr'}).json()
                for m in res.get('matches', []):
                    bad = linea[m['offset']:m['offset']+m['length']]
                    
                    if bad.lower() in ["show details", "hide details"] or bad in to_highlight: 
                        continue
                    
                    # Filtro de sugerencia idéntica
                    if m['replacements']:
                        best_sug = m['replacements'][0]['value']
                        if best_sug.strip() == bad.strip():
                            continue
                        
                        sug = f" (Try: **{best_sug}** → *'{translate_to_english(best_sug)}'*)"
                    else:
                        sug = ""

                    to_highlight.append(bad)
                    alertas.append(f"❌ **Grammar/Spelling:** Issue in '{bad}' ('{translate_to_english(bad)}').{sug}")
            except: pass

            # --- RENDER ---
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
