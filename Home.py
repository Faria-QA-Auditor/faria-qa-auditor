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
    .highlight { background-color: #fff3cd; font-weight: bold; color: #d9534f; text-decoration: underline; padding: 0 2px; }
    /* Smart Triage: Recuadro Azul */
    .informativo { background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 15px; color: #0c5460; margin: 10px 0; border-radius: 4px; font-weight: 500; }
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
st.write("This tool automatically detects the language of each line and applies the corresponding scrub rules.")

texto_raw = st.text_area("Paste mixed standards here:", height=300)

if st.button("🚀 Run Global Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text.")
    else:
        texto_norm = normalize_text(texto_raw)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]
        
        st.write(f"**Line Count:** {len(lineas)} / 1000")
        st.write("---")

        for i, linea in enumerate(lineas, 1):
            linea_lower = linea.lower()

            # --- NUEVA REGLA: INTERCEPTOR DE BASE DE DATOS ---
            
            # 1. Caso "Hide details": Silencio total, no es un error.
            if "hide details" in linea_lower:
                continue

            # 2. Caso "Show details": Recuadro azul informativo y saltar auditoría gramatical.
            if "show details" in linea_lower:
                st.markdown(f"""
                    <div class='informativo'>
                        Line {i} ℹ️ <b>Show details detected:</b> There is hidden information in this line that was not fully expanded. 
                        Please confirm if any content is missing from the source.
                    </div>
                """, unsafe_allow_html=True)
                # Opcional: mostrar la traducción solo por si el resto de la línea tiene texto útil
                st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                continue # IMPORTANTE: Aquí cortamos el análisis para esta línea.

            # --- CAPA 2: AUDITORÍA DE IDIOMA (Solo si no fue interceptada arriba) ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'auto'}).json()
                detected_lang = res.get('language', {}).get('code', 'en-US')[:2]
                
                alertas = []
                to_highlight = []

                for m in res.get('matches', []):
                    r_id = m['rule']['id']
                    # Filtros de ruido conocidos
                    if any(x in r_id for x in ["FRENCH_WHITESPACE", "FR_PUNCTUATION", "WHITESPACE"]):
                        continue
                    
                    bad = normalize_text(linea[m['offset']:m['offset']+m['length']])
                    
                    # Ignorar si por alguna razón la API marca fragmentos de las palabras clave
                    if bad.lower() in ["show", "details", "hide"] or len(bad) <= 1:
                        continue
                    
                    to_highlight.append(bad)
                    
                    msg_low = m['message'].lower()
                    msg_en = "Grammar/Spelling issue"
                    if "accord" in msg_low or "concordancia" in msg_low: msg_en = "Agreement issue"
                    elif "orthographe" in msg_low or "ortografía" in msg_low: msg_en = "Spelling error"
                    
                    sug = f" (Try: <b>{m['replacements'][0]['value']}</b>)" if m['replacements'] else ""
                    alertas.append(f"<div class='advertencia'>🟡 <b>{msg_en}:</b> Issue in '{bad}'.{sug}</div>")

                # --- RENDERIZADO DE RESULTADOS ---
                if alertas:
                    with st.expander(f"Line {i} ⚠️ ({detected_lang.upper()})", expanded=True):
                        st.markdown(linea)
                        if detected_lang != 'en':
                            st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea, detected_lang)}</div>", unsafe_allow_html=True)
                        for a in alertas:
                            st.markdown(a, unsafe_allow_html=True)
                else:
                    st.success(f"Line {i} ✅ Perfect ({detected_lang.upper()})")

            except Exception as e:
                st.error(f"Line {i}: Error connecting to the Audit API.")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group | 2026")
