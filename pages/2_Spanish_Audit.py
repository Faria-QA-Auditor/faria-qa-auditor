import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Spanish Auditor", page_icon="🇪🇸", layout="centered")

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
    .highlight {
        background-color: #fff3cd;
        font-weight: bold;
        color: #d9534f;
        text-decoration: underline;
        padding: 0 2px;
    }
    </style>
    """, unsafe_allow_html=True)

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
st.markdown("<h2 style='color: #444;'>Spanish Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste Spanish standards here (one per line):", height=300)

# --- CONTADOR DE LÍNEAS (CORREGIDO) ---
if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    
    st.markdown(f"**Line Count:** {total_lines} / 1000")
    
    if total_lines > 1000:
        st.error("⚠️ **Warning:** The document exceeds the 1,000-line limit. Please audit in smaller batches.")
    st.write("---")

# 4. PROCESAMIENTO
if st.button("🚀 Run Spanish Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        try:
            lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
            st.subheader("Audit Results")

            for i, linea in enumerate(lineas, 1):
                # Manejo de Meta-tags
                if linea.lower().strip() == "hide details":
                    continue
                
                if "show details" in linea.lower():
                    st.info(f"Line {i} ℹ️ **'Show details' detected:** Please verify if there is hidden information.")

                alertas_finales = []
                words_to_highlight = []
                
                # Regla de punto final (Común en estándares de español)
                if not linea.endswith('.'):
                    alertas_finales.append("⚠️ **Punctuation:** Line does not end with a period.")
                
                # Regla de inicio con mayúscula
                if linea and not linea[0].isupper() and not linea[0].isdigit():
                    alertas_finales.append("❌ **Format:** Line should start with a capital letter.")
                    words_to_highlight.append(linea[0])

                # API LanguageTool para Ortografía y Gramática
                try:
                    res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': 'es'}).json()
                    for m in res.get('matches', []):
                        bad_word = linea[m['offset']:m['offset']+m['length']]
                        if bad_word.lower() in ["show details", "hide details"]: continue
                        
                        words_to_highlight.append(bad_word)
                        sug = f" (Try: **{m['replacements'][0]['value']}**)" if m['replacements'] else ""
                        alertas_finales.append(f"Grammar/Spelling: Issue in '{bad_word}'.{sug}")
                except:
                    pass

                # Renderizado de resultados
                header = f"Line {i}"
                if not alertas_finales:
                    if not "show details" in linea.lower():
                        st.success(f"{header} ✅ Perfect")
                else:
                    with st.expander(f"{header} ⚠️ Issues found", expanded=True):
                        linea_html = highlight_errors(linea, words_to_highlight)
                        st.markdown(f"<div style='background: #fff; padding: 15px; border: 1px solid #ddd; font-size: 16px;'>{linea_html}</div>", unsafe_allow_html=True)
                        for a in alertas_finales:
                            st.write(a)
                            
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
