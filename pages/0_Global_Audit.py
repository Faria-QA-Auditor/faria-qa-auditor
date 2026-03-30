import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Global Mixed Auditor", page_icon="🌎", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1a237e; color: white; font-weight: bold; }
    .translation-box { background-color: #f8f9fa; border-left: 5px solid #1a237e; padding: 12px; margin: 10px 0; font-style: italic; border-radius: 4px; }
    /* Estilo para el Recuadro Azul de Base de Datos */
    .informativo { background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 15px; color: #0c5460; margin: 10px 0; border-radius: 4px; font-weight: 500; }
    /* Estilo para Advertencias Amarillas */
    .advertencia { background-color: #fff4e0; border-left: 5px solid #ffa500; padding: 10px; color: #856404; margin-bottom: 5px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES CORE ---
def normalize_text(text):
    return unicodedata.normalize('NFC', text)

def translate_to_english(text, lang='auto'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={lang}&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

# 2. INTERFAZ
st.title("🌎 Global Mixed Standards Auditor")
st.write("This tool automatically detects the language of each line and applies the corresponding QA rules.")

texto_raw = st.text_area("Paste mixed standards here:", height=300, placeholder="Example: \nLearning Objective 1\nShow details\nStandard en Español...")

if st.button("🚀 Run Global Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text to begin.")
    else:
        # --- LÓGICA DE CONTEO DE LÍNEAS CORREGIDA ---
        texto_norm = normalize_text(texto_raw)
        # Dividimos por salto de línea y eliminamos líneas vacías para el conteo real
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]
        
        # Usamos st.info para resaltar el conteo de líneas
        st.info(f"📊 **Total Lines Detected:** {len(lineas)}")
        st.write("---")

        for i, linea in enumerate(lineas, 1):
            linea_lower = linea.lower()

            # --- REGLA: INTERCEPTOR DE MARCADORES (DATABASE NOISE) ---
            
            if "hide details" in linea_lower:
                continue # Ignora por completo, no es un error

            if "show details" in linea_lower:
                st.markdown(f"""
                    <div class='informativo'>
                        Line {i} ℹ️ <b>Show details detected:</b> There is hidden information in this line that was not fully expanded. 
                        Please verify if any content is missing from the source database.
                    </div>
                """, unsafe_allow_html=True)
                continue # Salta el análisis gramatical para esta línea

            # --- AUDITORÍA LINGÜÍSTICA ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'auto'}).json()
                detected_lang = res.get('language', {}).get('code', 'en-US')[:2]
                
                alertas = []

                for m in res.get('matches', []):
                    r_id = m['rule']['id']
                    # Filtro de ruido técnico
                    if any(x in r_id for x in ["FRENCH_WHITESPACE", "FR_PUNCTUATION", "WHITESPACE"]):
                        continue
                    
                    bad = normalize_text(linea[m['offset']:m['offset']+m['length']])
                    
                    # Ignorar si marca fragmentos de palabras técnicas por error
                    if bad.lower() in ["show", "details", "hide"] or len(bad) <= 1:
                        continue
                    
                    # Traducir categorías de error al inglés (Smart Triage)
                    msg_low = m['message'].lower()
                    msg_en = "Grammar/Spelling issue"
                    if "accord" in msg_low or "concordancia" in msg_low: msg_en = "Agreement issue"
                    elif "orthographe" in msg_low or "ortografía" in msg_low: msg_en = "Spelling error"
                    
                    sug = f" (Try: <b>{m['replacements'][0]['value']}</b>)" if m['replacements'] else ""
                    alertas.append(f"<div class='advertencia'>🟡 <b>{msg_en}:</b> Issue in '{bad}'.{sug}</div>")

                # --- RENDERIZADO ---
                if alertas:
                    with st.expander(f"Line {i} ⚠️ ({detected_lang.upper()})", expanded=True):
                        st.markdown(f"**Text:** {linea}")
                        if detected_lang != 'en':
                            st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea, detected_lang)}</div>", unsafe_allow_html=True)
                        for a in alertas:
                            st.markdown(a, unsafe_allow_html=True)
                else:
                    st.success(f"Line {i} ✅ Clear ({detected_lang.upper()})")

            except:
                st.error(f"Line {i}: Connection error with the audit service.")

st.write("---")
st.caption("Standards and Services | Faria Education Group | 2026")
