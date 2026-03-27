import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Spanish Standards Auditor", page_icon="🇪🇸", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #4a148c; color: white; font-weight: bold; border: none; }
    .highlight { background-color: #fff3cd; font-weight: bold; color: #d9534f; text-decoration: underline; padding: 0 2px; }
    </style>
    """, unsafe_allow_html=True)

def highlight_errors(text, words):
    highlighted = unicodedata.normalize('NFC', text)
    # Ordenar por longitud para no romper etiquetas HTML
    for word in sorted(set(words), key=len, reverse=True):
        if len(word.strip()) <= 1: continue 
        norm_word = unicodedata.normalize('NFC', word.strip())
        highlighted = re.sub(rf"\b({re.escape(norm_word)})\b", r"<span class='highlight'>\1</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: st.image("logo.jpg", width=250)
except: st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Spanish Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR
texto_raw = st.text_area("Paste Spanish standards here:", height=300)

if texto_raw:
    lineas_reales = [l for l in texto_raw.split('\n') if l.strip()]
    st.markdown(f"**Line Count:** {len(lineas_reales)} / 1000")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Spanish Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text.")
    else:
        # NORMALIZACIÓN INICIAL (Soluciona error de imagen 03f2c2)
        texto_norm = unicodedata.normalize('NFC', texto_raw)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

        for i, linea in enumerate(lineas, 1):
            linea_lower = linea.lower().strip()
            
            # --- REGLA: HIDE DETAILS (Ignorar) ---
            if "hide details" in linea_lower: continue

            # --- REGLA: SHOW DETAILS (RECUADRO AZUL) ---
            # Se detecta antes que cualquier error de la API
            show_detected = False
            if "show details" in linea_lower:
                st.info(f"Line {i} ℹ️ **'Show details' detected:** There is hidden information in this line. Please verify in the source database.")
                show_detected = True

            alertas = []
            to_highlight = []

            # --- API LANGUAGETOOL ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'es'}).json()
                for m in res.get('matches', []):
                    bad_raw = linea[m['offset']:m['offset']+m['length']]
                    bad = unicodedata.normalize('NFC', bad_raw)
                    
                    # FILTRO CRÍTICO: No marcar meta-tags ni letras sueltas como error
                    if bad.lower() in ["show", "details", "show details"] or len(bad) <= 1:
                        continue
                    
                    to_highlight.append(bad)
                    
                    # Traducción de alertas al inglés (para el equipo global)
                    msg_es = m['message'].lower()
                    msg_en = "Grammar/Spelling issue"
                    if "ortografía" in msg_es: msg_en = "Spelling error"
                    elif "concordancia" in msg_es: msg_en = "Grammatical agreement"
                    
                    sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                    alertas.append(f"❌ **{msg_en}:** Issue in '{bad}'.{sug}")
            except: pass

            # --- RENDERIZADO FINAL ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            elif not show_detected:
                st.success(f"Line {i} ✅ Perfect")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
