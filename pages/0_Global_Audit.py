import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Global Mixed Auditor", page_icon="🌍", layout="centered")

# --- CSS CORPORATIVO FARIA (FUCSIA) ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #e91e63; 
        color: white; font-weight: bold; height: 3em; border: none;
    }
    .stButton>button:hover { background-color: #d81b60; color: white; }
    .stProgress > div > div > div > div { background-color: #e91e63; }
    .translation-box { background-color: #f8f9fa; border-left: 5px solid #e91e63; padding: 12px; margin: 10px 0; font-style: italic; }
    .highlight { background-color: #fff3cd; font-weight: bold; color: #d9534f; text-decoration: underline; padding: 0 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES ---
def translate_to_english(text, source_lang='auto'):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: st.image("logo.jpg", width=250)
except: st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Global Mixed Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR
texto_raw = st.text_area("Paste mixed standards here:", height=350, placeholder="Supports Spanish, French, Arabic, Turkish...")

if texto_raw:
    lineas_reales = [l for l in texto_raw.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Total Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit.")

# 4. BOTÓN Y PROCESAMIENTO
if st.button("🚀 Run Global Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text.")
    else:
        # Normalización para evitar errores de acentos/caracteres especiales
        texto_norm = unicodedata.normalize('NFC', texto_raw)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")
            
            # --- AQUÍ DEBES ASEGURARTE DE TENER TU LÓGICA DE DETECCIÓN ---
            # Si el botón no hacía nada, revisa que este bucle no esté vacío.
            
            # Ejemplo rápido de integración con LanguageTool (Auto-detect):
            try:
                res = requests.post('https://api.languagetool.org/v2/check', 
                                    data={'text': linea, 'language': 'auto'}).json()
                
                # Renderizado de resultados (similar a tus otros auditores)
                if res.get('matches'):
                    with st.expander(f"Line {i} ⚠️ Issues", expanded=False):
                        st.write(linea)
                        st.info(f"Context: {translate_to_english(linea)}")
                else:
                    st.success(f"Line {i} ✅ OK")
            except:
                pass
        
        status_text.text("Audit complete!")
